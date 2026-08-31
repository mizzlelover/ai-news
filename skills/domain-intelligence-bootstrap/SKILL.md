---
name: domain-intelligence-bootstrap
description: "Use when a user wants to build a domain intelligence knowledge domain from a new field, reconstruct expert attention, benchmark sources at historical cutoffs, optimize a source portfolio, audit coverage gaps, or package a domain-specific daily brief."
---

# 私人情报所核心入口：Domain Intelligence Bootstrap

把“一个领域关键词 → 领域知识域 → 信息生态”落成可审计的 Domain Map、Source Portfolio 和 Daily Brief。它把给出一个领域作为唯一入口，尤其帮助刚进入领域、没有知识背景且不知道该找谁和该信谁的人先搭起底图；已有的专家、网站、报告或项目材料可以在底图建立后再加入。它也适用于工程协作者在底图之上继续做来源发现与评价、历史回放、覆盖审计和方法论/工程交接。

## 先读

- `docs/DOMAIN_INTELLIGENCE_V0_1.md`：方法论、指标、状态机和边界。
- `docs/PROJECT_SCOPE_AND_ATTRIBUTION.md`：本项目核心与 AI News Radar 采集参考的归属、来源和版权边界。
- `packages/domain-intelligence/README.md`：安装、输入 Bundle 和验证命令。
- `packages/domain-intelligence/examples/data-elements.json`：完整最小示例。
- `packages/domain-intelligence/examples/digital-twin-expanded.json`：117 个来源入口的规模化领域样例。
- `docs/SOURCE_PORTFOLIO_SCALE.md`：来源网络的分层、规模和激活规则。
- `packages/domain-intelligence/src/domain_intelligence/models/`：边界 Schema。

如果任务同时涉及仓库中的 AI News Radar 采集、RSS、OPML、GitHub Actions 或 Pages，再读 `skills/ai-news-radar/SKILL.md`、`docs/SOURCE_COVERAGE.md` 和 `scripts/update_news.py`。它们是独立的采集参考，不是产品入口；采集层与情报判断层保持分离。

## 产品归属边界

本 Skill 是私人情报所的核心入口。`skills/ai-news-radar/` 和 `skills/radar/` 是来自或基于 LearnPrompt/ai-news-radar 的采集参考，不得把它们称为本项目原创的伯乐 Skill，也不得让 AI 新闻采集能力取代需求建模、历史回放、信源组合和覆盖审计。

## 领域优先的入口契约

- **只需要一个领域名称或关键词**：不要求使用者先有知识背景、完整问题、PIR 或信源清单；先建立 Domain Map、人物/机构和来源角色。
- **初进入领域是最重要的使用场景**：系统先回答“这个领域由什么组成、该看谁、该信什么、哪里还没有证据”，把不会开始的问题变成可继续工作的底图。
- **已有信源是后续补充**：专家、网站、报告或材料可以在底图建立后直接告诉 AI 加入，由 `attention_graph` 作为扩展种子进入，不改变入口。
- **非目标用户**：已经能够独立用 AI 配置信源、搭建日报并维护知识引擎的人，不是本 Skill 的主要服务对象；他们可以复用工程组件，但不应改变领域优先的入口。

## 工作流

1. 先用一个领域名称或关键词初始化 `DomainProfile`；不要要求使用者先写专业问题或准备信源清单。
2. 从 Domain Seed 建立领域边界、词典、观察面、人物/机构和来源候选；领域底图完成后，再按指令加入已有信源，并明确 PIR、EIE、主题权重和事件优先级。
3. 将 Expert、Source、typed Attention Edge 和证据时间整理成 `BootstrapInput`；每条边保留关系类型、主题相关性、证据置信度、观察时间和证据 URL。
4. 用 `dib <input.json> --output-dir <dir>` 运行 EAR、point-in-time replay、Portfolio、Coverage Audit 和 Daily Brief。
5. 先看 `bootstrap-report.json` 的结构化结果，再用 Markdown 报告交接；不以来源数量或单一总分宣称覆盖完成。
6. 来源进入长期组合前，确认它有角色、EIE 映射、稳定获取路径和历史回放证据；不稳定、登录态、私有邮箱和需要 token 的来源放到用户自己的边界适配器。
7. 新增来源或领域适配时，补充一个最小行为测试和一个可运行 Bundle；不要把 AI News Radar 的默认来源、栏目或阈值直接当成新领域方案。

宽领域不要在首轮把来源网络缩减为少数日报入口。以公开数字孪生样例为基准，第一轮候选雷达可以从约 80–150 个可独立采集的入口起步，再用历史回放、来源角色和覆盖审计决定进入每日组合的来源；来源数量本身不等于覆盖或权威。

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
