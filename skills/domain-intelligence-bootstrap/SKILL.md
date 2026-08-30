---
name: domain-intelligence-bootstrap
description: "Use when a user wants to bootstrap an information radar for a new domain, reconstruct expert attention, benchmark sources at historical cutoffs, optimize a source portfolio, audit coverage gaps, or package a domain-specific daily brief."
---

# Domain Intelligence Bootstrap

把“领域 → 信息生态”落成可审计的 Source Portfolio 和 Daily Brief。它适用于新领域建模、来源发现与评价、历史回放、覆盖审计和方法论/工程交接。

## 先读

- `docs/DOMAIN_INTELLIGENCE_V0_1.md`：方法论、指标、状态机和边界。
- `docs/PROJECT_SCOPE_AND_ATTRIBUTION.md`：本项目核心与外部 AI News Radar 兼容层的归属、来源和版权边界。
- `packages/domain-intelligence/README.md`：安装、输入 Bundle 和验证命令。
- `packages/domain-intelligence/examples/data-elements.json`：完整最小示例。
- `packages/domain-intelligence/src/domain_intelligence/models/`：边界 Schema。

如果任务同时涉及现有 AI News Radar 的采集、RSS、OPML、GitHub Actions 或 Pages，再读 `skills/ai-news-radar/SKILL.md`、`docs/SOURCE_COVERAGE.md` 和 `scripts/update_news.py`。采集层与情报判断层保持分离。

## 产品归属边界

本 Skill 是本项目的核心入口。`skills/ai-news-radar/` 和 `skills/radar/` 是来自或基于 LearnPrompt/ai-news-radar 的可选兼容适配层，不得把它们称为本项目原创的伯乐 Skill，也不得让 AI 新闻采集能力取代需求建模、历史回放、信源组合和覆盖审计。

## 工作流

1. 先把用户目的写成 `DomainProfile`，明确 PIR、EIE、主题权重和事件优先级。
2. 将 Expert、Source、typed Attention Edge 和证据时间整理成 `BootstrapInput`；每条边保留关系类型、主题相关性、证据置信度、观察时间和证据 URL。
3. 用 `dib <input.json> --output-dir <dir>` 运行 EAR、point-in-time replay、Portfolio、Coverage Audit 和 Daily Brief。
4. 先看 `bootstrap-report.json` 的结构化结果，再用 Markdown 报告交接；不以来源数量或单一总分宣称覆盖完成。
5. 来源进入长期组合前，确认它有角色、EIE 映射、稳定获取路径和历史回放证据；不稳定、登录态、私有邮箱和需要 token 的来源放到用户自己的边界适配器。
6. 新增来源或领域适配时，补充一个最小行为测试和一个可运行 Bundle；不修改现有 AI News Radar 默认来源，除非用户明确要求。

## 关键判据

- `available_at` 是回放的唯一可见性门槛，不能用事后上传时间或最终内容替代。
- Source Role 和 Reliability 分开；官方源、解释源、前沿传感器和广覆盖源承担不同职责。
- 覆盖率分母来自声明的 EIE，不来自搜索结果数量。
- 组合优化允许 `SourceBundle` 表示互补效应，启发式选择应标注为基线而非数学最优。
- Daily Brief 必须保留原始证据 URL；标题、摘要和排序不能取代证据。

## 验证

```bash
uv run --project packages/domain-intelligence pytest -q packages/domain-intelligence/tests
uv run --project packages/domain-intelligence ruff check packages/domain-intelligence/src packages/domain-intelligence/tests
python /Users/a1-6/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/domain-intelligence-bootstrap
```

Skill 负责路由和交接；真正的结构化计算以包内 Schema 和函数为准。
