from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlsplit

import httpx2
from pydantic import ValidationError

from domain_intelligence.io_run import write_domain_run
from domain_intelligence.models import BootstrapInput
from domain_intelligence.public_capture import capture_public_sources
from domain_intelligence.run import build_domain_run

ProgressCallback = Callable[[str, str, int], None]
MIN_SOURCE_CANDIDATES = 20
MAX_SOURCE_CANDIDATES = 200
MIN_ELEMENTS = 8
MIN_REQUIREMENTS = 5
MIN_BENCHMARK_EVENTS = 3
MAX_PROVIDER_RESPONSE_BYTES = 2_000_000


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    endpoint: str
    api_key: str
    model: str


class SeedBuilderError(RuntimeError):
    pass


def _chat_endpoint(endpoint: str) -> str:
    value = endpoint.strip().rstrip("/")
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise SeedBuilderError("AI 接口地址必须是完整的 http:// 或 https:// 地址")
    return value if value.endswith("/chat/completions") else f"{value}/chat/completions"


def _prompt(domain: str, as_of: datetime) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "你是私人情报所的领域建模器。只输出可被 JSON.parse 读取的 JSON，"
                "不要 Markdown，不要解释。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"为领域“{domain}”建立从零开始的领域情报底图。当前时间是 {as_of.isoformat()}。"
                "返回完整 BootstrapInput JSON，必须包含 profile、attention_graph、attention_query、benchmark、"
                "as_of、budget、max_sources、window_hours、daily_limit；signals、acquisition_runs、evidence、"
                "bundles 可为空。"
                f"attention_graph.sources 至少 {MIN_SOURCE_CANDIDATES} 个，理想为 80 至 150 个，覆盖官方一手、"
                "专家解释、前沿探测、广覆盖与社区等不同角色。每个来源都要有真实公开入口；能用 RSS、Atom、JSON、"
                "Sitemap 或 static_html 就使用，不能稳定获取的入口使用 manual 或 unknown 并保留 endpoint。"
                "来源 id、专家 id、主题 id、要素 id 只能使用 ASCII 字母、数字、下划线或连字符，来源 id 必须以字母或"
                "数字开头且不可重复。SourceRole 只能使用 official_primary、expert_interpreter、frontier_sensor、"
                "broad_coverage、community、other；AcquisitionMethod 只能使用 rss、atom、json、sitemap、static_html、"
                "api、opml、browser、manual、unknown。profile.elements 至少 8 个，requirements 至少 5 个。"
                "benchmark 至少包含 3 个有 nuggets 的历史或当前事件，cutoffs 至少 1 个；所有时间使用 ISO 8601。"
                "attention_query.seed_expert_ids 必须引用 attention_graph.experts 中存在的专家。"
                "请优先给出跨机构、跨角色、能帮助新进入者建立全景的来源。"
            ),
        },
    ]


def _extract_content(payload: object) -> str:
    if not isinstance(payload, dict):
        raise SeedBuilderError("AI 接口返回的不是 JSON 对象")
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise SeedBuilderError("AI 接口没有返回 choices")
    message = choices[0].get("message")
    if not isinstance(message, dict) or not isinstance(message.get("content"), str):
        raise SeedBuilderError("AI 接口没有返回文本内容")
    return message["content"]


def _parse_seed(text: str, domain: str) -> BootstrapInput:
    value = text.strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", value, flags=re.DOTALL)
    if fenced:
        value = fenced.group(1)
    try:
        payload = json.loads(value)
    except json.JSONDecodeError as error:
        raise SeedBuilderError(f"AI 返回的领域底图不是有效 JSON：{error.msg}") from error
    try:
        inputs = BootstrapInput.model_validate(payload)
    except ValidationError as error:
        location = error.errors()[0]["loc"]
        raise SeedBuilderError(f"AI 返回的领域底图未通过结构校验：{location}") from error
    if inputs.profile.domain != domain:
        raise SeedBuilderError("AI 返回的领域名称与输入不一致，请重新建立这个领域")
    source_count = len(inputs.attention_graph.sources)
    if source_count < MIN_SOURCE_CANDIDATES:
        raise SeedBuilderError(
            f"AI 返回的来源网络只有 {source_count} 个，至少需要 {MIN_SOURCE_CANDIDATES} 个才会开始运行",
        )
    if source_count > MAX_SOURCE_CANDIDATES:
        raise SeedBuilderError(
            f"AI 返回的来源网络有 {source_count} 个，超过本地运行上限 {MAX_SOURCE_CANDIDATES} 个",
        )
    source_ids = [str(source.id) for source in inputs.attention_graph.sources]
    if len(set(source_ids)) != len(source_ids):
        raise SeedBuilderError("AI 返回的来源网络存在重复 id，未开始运行")
    if len(inputs.profile.elements) < MIN_ELEMENTS:
        raise SeedBuilderError(
            f"AI 返回的信息要素只有 {len(inputs.profile.elements)} 个，至少需要 {MIN_ELEMENTS} 个",
        )
    if len(inputs.profile.requirements) < MIN_REQUIREMENTS:
        raise SeedBuilderError(
            f"AI 返回的情报需求只有 {len(inputs.profile.requirements)} 个，至少需要 {MIN_REQUIREMENTS} 个",
        )
    if len(inputs.benchmark.events) < MIN_BENCHMARK_EVENTS:
        raise SeedBuilderError(
            f"AI 返回的历史基准事件只有 {len(inputs.benchmark.events)} 个，至少需要 {MIN_BENCHMARK_EVENTS} 个",
        )
    return inputs


def build_seed(domain: str, provider: ProviderConfig) -> BootstrapInput:
    clean_domain = domain.strip()
    if not clean_domain:
        raise SeedBuilderError("领域名称不能为空")
    endpoint = _chat_endpoint(provider.endpoint)
    if not provider.model.strip():
        raise SeedBuilderError("请先填写 AI 模型名称")
    as_of = datetime.now(UTC).replace(microsecond=0)
    request = {
        "model": provider.model.strip(),
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "messages": _prompt(clean_domain, as_of),
    }
    headers = {"Content-Type": "application/json"}
    if provider.api_key:
        headers["Authorization"] = f"Bearer {provider.api_key}"
    try:
        with httpx2.Client(timeout=120.0, follow_redirects=False, headers=headers) as client:
            with client.stream("POST", endpoint, json=request, follow_redirects=False) as response:
                response.raise_for_status()
                chunks: list[bytes] = []
                total = 0
                for chunk in response.iter_bytes():
                    total += len(chunk)
                    if total > MAX_PROVIDER_RESPONSE_BYTES:
                        raise SeedBuilderError("AI 返回内容过大，未载入运行")
                    chunks.append(chunk)
                payload = json.loads(b"".join(chunks).decode("utf-8"))
                content = _extract_content(payload)
    except SeedBuilderError:
        raise
    except httpx2.HTTPError as error:
        raise SeedBuilderError(f"AI 接口请求失败：{error}") from error
    except (OSError, ValueError) as error:
        raise SeedBuilderError(f"AI 接口返回无法读取：{error}") from error
    return _parse_seed(content, clean_domain)


def build_local_run(
    domain: str,
    provider: ProviderConfig,
    output_dir: Path,
    progress: ProgressCallback,
) -> Path:
    progress("seed", "正在为这个领域建立知识底图", 12)
    inputs = build_seed(domain, provider)
    progress(
        "map",
        f"已识别 {len(inputs.attention_graph.sources)} 个来源候选，开始检查获取路径",
        28,
    )
    capture_dir = output_dir / "capture"
    progress("capture", "正在激活公开入口并归档可获得的全文", 40)
    acquisition = capture_public_sources(inputs.model_copy(update={"signals": ()}), capture_dir)
    progress("archive", f"已登记 {len(acquisition.contents)} 条内容结果，正在生成知识域与日报", 78)
    result = build_domain_run(
        domain,
        inputs.model_copy(update={"signals": ()}),
        acquisition,
        input_mode="local_domain_builder_live_capture",
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    write_domain_run(result, output_dir, content_root=capture_dir)
    progress("complete", "领域情报所已经建立，可以打开运行工作台", 100)
    return output_dir
