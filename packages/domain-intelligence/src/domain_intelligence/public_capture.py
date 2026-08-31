from __future__ import annotations

import hashlib
import json
import logging
import re
import socket
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Final, assert_never
from urllib.parse import urlparse

import anyio
import httpx2

from domain_intelligence.capture_parser import parse_document
from domain_intelligence.models import (
    AcquisitionBatch,
    AcquisitionMethod,
    AcquisitionRunStatus,
    BootstrapInput,
    ContentArtifact,
    ContentCaptureStatus,
    ContentInventory,
    DailySignal,
    EvidenceRecord,
    SourceAcquisitionRun,
    SourceProfile,
)

LOGGER = logging.getLogger(__name__)
MAX_BODY_BYTES: Final = 12_000_000
MAX_CONCURRENT_REQUESTS: Final = 12
USER_AGENT: Final = "PrivateIntelligenceObservatory/0.1 public-capture"
LIMITS: Final = httpx2.Limits(
    max_connections=200,
    max_keepalive_connections=40,
    keepalive_expiry=30.0,
)
TIMEOUT: Final = httpx2.Timeout(connect=5.0, read=30.0, write=10.0, pool=10.0)
SOCKET_OPTIONS: Final[list[tuple[int, int, int]]] = [
    (socket.IPPROTO_TCP, socket.TCP_NODELAY, 1),
]


@dataclass(frozen=True, slots=True)
class _CaptureTarget:
    source: SourceProfile
    url: str
    signal: DailySignal | None
    evidence_template: EvidenceRecord | None


@dataclass(frozen=True, slots=True)
class _CaptureOutcome:
    artifact: ContentArtifact
    evidence: EvidenceRecord | None


@dataclass(frozen=True, slots=True)
class _CaptureContext:
    capture_root: Path
    as_of: datetime
    max_body_bytes: int


@dataclass(frozen=True, slots=True)
class _CapturedDocument:
    text: str
    content_type: str
    content_hash: str
    relative_path: str


async def _request_started(request: httpx2.Request) -> None:
    request.extensions["capture_started_at"] = time.perf_counter()


async def _response_received(response: httpx2.Response) -> None:
    started = response.request.extensions.get("capture_started_at")
    elapsed = time.perf_counter() - started if isinstance(started, float) else 0.0
    LOGGER.info(
        "captured %s %s -> %s in %.2fs (%s)",
        response.request.method,
        response.request.url,
        response.status_code,
        elapsed,
        response.http_version,
    )


def _create_client() -> httpx2.AsyncClient:
    transport = httpx2.AsyncHTTPTransport(
        http2=True,
        retries=3,
        limits=LIMITS,
        socket_options=SOCKET_OPTIONS,
    )
    return httpx2.AsyncClient(
        transport=transport,
        timeout=TIMEOUT,
        follow_redirects=True,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/json,application/xml;q=0.9,*/*;q=0.1",
        },
        event_hooks={"request": [_request_started], "response": [_response_received]},
    )


def _content_id(target: _CaptureTarget) -> str:
    digest = hashlib.sha256(
        f"{target.source.id}|{target.url}|{target.signal.id if target.signal else ''}".encode(),
    ).hexdigest()[:16]
    source = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(target.source.id)).strip("-") or "source"
    return f"content-{source}-{digest}"


def _raw_extension(content_type: str) -> str:
    normalized_type = content_type.casefold()
    if "json" in normalized_type:
        return ".json"
    if "xml" in normalized_type or "rss" in normalized_type or "atom" in normalized_type:
        return ".xml"
    if "html" in normalized_type:
        return ".html"
    return ".txt"


def _failure(
    target: _CaptureTarget,
    as_of: datetime,
    status: ContentCaptureStatus,
    error_code: str,
    content_type: str = "application/octet-stream",
) -> _CaptureOutcome:
    artifact = ContentArtifact(
        id=_content_id(target),
        source_id=target.source.id,
        title=target.signal.title if target.signal else target.source.name,
        url=target.url,
        captured_at=as_of,
        content_type=content_type,
        status=status,
        error_code=error_code,
    )
    return _CaptureOutcome(artifact=artifact, evidence=None)


def _source_blocker(source: SourceProfile) -> str | None:
    if not source.approved:
        return "SOURCE_NOT_APPROVED"
    if not source.acquisition.stable:
        return "ACQUISITION_NOT_STABLE"
    if not source.acquisition.endpoint:
        return "NO_PUBLIC_ENDPOINT"
    match source.acquisition.method:
        case (
            AcquisitionMethod.RSS
            | AcquisitionMethod.ATOM
            | AcquisitionMethod.JSON
            | AcquisitionMethod.SITEMAP
            | AcquisitionMethod.STATIC_HTML
            | AcquisitionMethod.API
            | AcquisitionMethod.OPML
        ):
            return None
        case AcquisitionMethod.BROWSER:
            return "BROWSER_ADAPTER_REQUIRED"
        case AcquisitionMethod.MANUAL | AcquisitionMethod.UNKNOWN:
            return "ACQUISITION_METHOD_UNSUPPORTED"
        case unreachable:
            assert_never(unreachable)


def _targets_for_source(
    source: SourceProfile,
    signals: tuple[DailySignal, ...],
    evidence_by_id: dict[str, EvidenceRecord],
) -> tuple[_CaptureTarget, ...]:
    endpoint = source.acquisition.endpoint
    if endpoint is None:
        return ()
    targets = [_CaptureTarget(source=source, url=endpoint, signal=None, evidence_template=None)]
    for signal in signals:
        target = _CaptureTarget(
            source=source,
            url=signal.url,
            signal=signal,
            evidence_template=evidence_by_id.get(str(signal.id)),
        )
        if signal.url == endpoint:
            targets[0] = target
        else:
            targets.append(target)
    return tuple(targets)


def _content_type(response: httpx2.Response) -> str:
    return response.headers.get("content-type", "application/octet-stream").split(";", 1)[0]


def _evidence_from_capture(
    target: _CaptureTarget,
    document: _CapturedDocument,
    as_of: datetime,
) -> EvidenceRecord | None:
    signal = target.signal
    if signal is None or not document.text.strip() or signal.available_at > as_of:
        return None
    summary = signal.summary or document.text[:400]
    return EvidenceRecord(
        id=signal.id,
        source_id=signal.source_id,
        title=signal.title,
        url=signal.url,
        summary=summary,
        published_at=signal.published_at,
        available_at=signal.available_at,
        retrieved_at=as_of,
        content_hash=document.content_hash,
        topic_ids=signal.topic_ids,
        element_ids=(
            target.evidence_template.element_ids
            if target.evidence_template
            else target.source.element_ids
        ),
        event_type=signal.event_type,
        importance=signal.importance,
        originality=signal.originality,
        confirmed=signal.confirmed,
        event_id=signal.event_id,
        content_ref=document.relative_path,
        content_type=document.content_type,
        content_char_count=len(document.text),
    )


def _write_capture_files(
    capture_root: Path,
    target: _CaptureTarget,
    body: bytes,
    text: str,
    content_type: str,
) -> tuple[str, str]:
    content_dir = capture_root / "content"
    content_dir.mkdir(parents=True, exist_ok=True)
    content_id = _content_id(target)
    text_relative_path = f"content/{content_id}.md"
    raw_relative_path = f"content/{content_id}{_raw_extension(content_type)}"
    (capture_root / text_relative_path).write_text(text + "\n", encoding="utf-8")
    (capture_root / raw_relative_path).write_bytes(body)
    return text_relative_path, raw_relative_path


async def _fetch_one(
    client: httpx2.AsyncClient,
    limiter: anyio.CapacityLimiter,
    target: _CaptureTarget,
    context: _CaptureContext,
) -> _CaptureOutcome:
    async with limiter:
        parsed_url = urlparse(target.url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            return _failure(
                target,
                context.as_of,
                ContentCaptureStatus.BLOCKED,
                "INVALID_PUBLIC_URL",
            )
        try:
            response = await client.get(target.url)
            response.raise_for_status()
            body = response.content
            content_type = _content_type(response)
            if len(body) > context.max_body_bytes:
                return _failure(
                    target,
                    context.as_of,
                    ContentCaptureStatus.FAILED,
                    "RESPONSE_TOO_LARGE",
                    content_type,
                )
            encoding = response.encoding or "utf-8"
            raw_text = body.decode(encoding, errors="replace")
            parsed = parse_document(raw_text, content_type)
            parsed_text = raw_text.strip() if not parsed.text else parsed.text
            content_hash = f"sha256:{hashlib.sha256(parsed_text.encode()).hexdigest()}"
            relative_path, raw_relative_path = _write_capture_files(
                context.capture_root,
                target,
                body,
                parsed_text,
                content_type,
            )
            document = _CapturedDocument(parsed_text, content_type, content_hash, relative_path)
            evidence = _evidence_from_capture(target, document, context.as_of)
            artifact = ContentArtifact(
                id=_content_id(target),
                source_id=target.source.id,
                evidence_id=evidence.id if evidence else None,
                title=(target.signal.title if target.signal else parsed.title)
                or target.source.name,
                url=target.url,
                published_at=parsed.published_at,
                captured_at=context.as_of,
                content_type=content_type,
                relative_path=relative_path,
                raw_relative_path=raw_relative_path,
                content_hash=content_hash,
                character_count=len(parsed_text),
                status=ContentCaptureStatus.CAPTURED,
            )
            return _CaptureOutcome(artifact=artifact, evidence=evidence)
        except httpx2.HTTPStatusError as error:
            return _failure(
                target,
                context.as_of,
                ContentCaptureStatus.FAILED,
                f"HTTP_{error.response.status_code}",
            )
        except httpx2.RequestError:
            return _failure(
                target,
                context.as_of,
                ContentCaptureStatus.FAILED,
                "REQUEST_ERROR",
            )
        except (OSError, UnicodeError, ValueError):
            return _failure(
                target,
                context.as_of,
                ContentCaptureStatus.FAILED,
                "CONTENT_PARSE_ERROR",
            )


async def _fetch_targets(
    targets: tuple[_CaptureTarget, ...],
    context: _CaptureContext,
) -> tuple[_CaptureOutcome, ...]:
    limiter = anyio.CapacityLimiter(MAX_CONCURRENT_REQUESTS)
    async with _create_client() as client, anyio.create_task_group() as task_group:
        handles = [
            task_group.create_task(_fetch_one(client, limiter, target, context))
            for target in targets
        ]
        return tuple([await handle for handle in handles])


def _blocked_outcome(
    source: SourceProfile,
    error_code: str,
    as_of: datetime,
) -> _CaptureOutcome | None:
    endpoint = source.acquisition.endpoint
    if endpoint is None:
        return None
    target = _CaptureTarget(
        source=source,
        url=endpoint,
        signal=None,
        evidence_template=None,
    )
    return _failure(target, as_of, ContentCaptureStatus.BLOCKED, error_code)


def _write_source_snapshots(
    capture_root: Path,
    sources: tuple[SourceProfile, ...],
    outcomes_by_source: dict[str, tuple[_CaptureOutcome, ...]],
) -> None:
    for source in sources:
        evidence = tuple(
            outcome.evidence
            for outcome in outcomes_by_source.get(str(source.id), ())
            if outcome.evidence is not None
        )
        payload = [record.model_dump(mode="json") for record in evidence]
        (capture_root / f"{source.id}.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def _source_run(
    source: SourceProfile,
    outcomes: tuple[_CaptureOutcome, ...],
    as_of: datetime,
) -> SourceAcquisitionRun:
    evidence_ids = tuple(
        outcome.evidence.id for outcome in outcomes if outcome.evidence is not None
    )
    captured = any(outcome.artifact.status is ContentCaptureStatus.CAPTURED for outcome in outcomes)
    if evidence_ids:
        status = AcquisitionRunStatus.SUCCEEDED
        error_code = None
    elif captured:
        status = AcquisitionRunStatus.EMPTY
        error_code = None
    else:
        status = AcquisitionRunStatus.FAILED
        error_code = next(
            (
                outcome.artifact.error_code
                for outcome in outcomes
                if outcome.artifact.error_code is not None
            ),
            "NO_CAPTURED_CONTENT",
        )
    return SourceAcquisitionRun(
        id=f"live-{source.id}",
        source_id=source.id,
        status=status,
        retrieved_at=as_of,
        evidence_ids=evidence_ids,
        error_code=error_code,
    )


def capture_public_sources(
    inputs: BootstrapInput,
    capture_root: Path,
    *,
    max_body_bytes: int = MAX_BODY_BYTES,
) -> AcquisitionBatch:
    capture_root.mkdir(parents=True, exist_ok=True)
    source_by_id = {str(source.id): source for source in inputs.attention_graph.sources}
    evidence_by_id = {record.id: record for record in inputs.evidence}
    signals_by_source: dict[str, list[DailySignal]] = {}
    for signal in inputs.signals:
        if str(signal.source_id) in source_by_id:
            signals_by_source.setdefault(str(signal.source_id), []).append(signal)
    outcomes_by_source: dict[str, tuple[_CaptureOutcome, ...]] = {}
    targets: list[_CaptureTarget] = []
    target_source_ids: list[str] = []
    for source in inputs.attention_graph.sources:
        blocker = _source_blocker(source)
        if blocker is not None:
            blocked = _blocked_outcome(source, blocker, inputs.as_of)
            outcomes_by_source[str(source.id)] = (blocked,) if blocked else ()
            continue
        source_targets = _targets_for_source(
            source,
            tuple(signals_by_source.get(str(source.id), [])),
            evidence_by_id,
        )
        targets.extend(source_targets)
        target_source_ids.extend(str(source.id) for _ in source_targets)
    fetched = anyio.run(
        _fetch_targets,
        tuple(targets),
        _CaptureContext(capture_root, inputs.as_of, max_body_bytes),
    )
    for source_id, outcome in zip(target_source_ids, fetched, strict=True):
        outcomes_by_source.setdefault(source_id, ())
        outcomes_by_source[source_id] += (outcome,)
    sources = tuple(sorted(inputs.attention_graph.sources, key=lambda item: str(item.id)))
    _write_source_snapshots(capture_root, sources, outcomes_by_source)
    inventory_items = tuple(
        outcome.artifact
        for source in sources
        for outcome in outcomes_by_source.get(str(source.id), ())
    )
    inventory = tuple(
        outcome.evidence
        for source in sources
        for outcome in outcomes_by_source.get(str(source.id), ())
        if outcome.evidence is not None
    )
    content_inventory = ContentInventory(generated_at=inputs.as_of, items=inventory_items)
    (capture_root / "content-inventory.json").write_text(
        content_inventory.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    return AcquisitionBatch(
        runs=tuple(
            _source_run(source, outcomes_by_source.get(str(source.id), ()), inputs.as_of)
            for source in sources
        ),
        evidence=inventory,
        contents=inventory_items,
    )
