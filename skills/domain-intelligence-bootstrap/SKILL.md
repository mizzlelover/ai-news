---
name: domain-intelligence-bootstrap
description: "Use when a user wants to build a domain intelligence knowledge domain from a new field, reconstruct expert attention, benchmark sources at historical cutoffs, optimize a source portfolio, audit coverage gaps, or package a domain-specific daily brief."
---

# 私人情报所核心入口：Domain Intelligence Bootstrap

把“一个领域关键词 → 领域知识域 → 信息生态”落成可审计的 Domain Map、Source Portfolio 和 Daily Brief。它首先服务刚进入领域、没有知识背景且不知道该找谁和该信谁的人，也服务已经在领域里、手上有一些信源但覆盖不够广的人。两类使用者都先建立领域底图，再让工具负责更新、日报、推送和后续问题追踪。它也适用于工程协作者在底图之上继续做来源发现与评价、历史回放、覆盖审计和方法论/工程交接。

## 先读

- `docs/DOMAIN_INTELLIGENCE_V0_1.md`：方法论、指标、状态机和边界。
- `docs/PROJECT_SCOPE_AND_ATTRIBUTION.md`：本项目核心与早期 AI News Radar 采集参考的归属、来源和版权边界。
- `packages/domain-intelligence/README.md`：安装、输入 Bundle 和验证命令。
- `packages/domain-intelligence/examples/data-elements.json`：完整最小示例。
- `packages/domain-intelligence/src/domain_intelligence/models/`：边界 Schema。

如果任务同时涉及仓库中保留的早期 AI News Radar 采集、RSS、OPML、GitHub Actions 或 Pages，再读 `skills/ai-news-radar/SKILL.md`、`docs/SOURCE_COVERAGE.md` 和 `scripts/update_news.py`。它们是历史或实验性的采集参考，不是产品入口；采集层与情报判断层保持分离。

## 产品归属边界

本 Skill 是私人情报所的核心入口。`skills/ai-news-radar/` 和 `skills/radar/` 是来自或基于 LearnPrompt/ai-news-radar 的历史或实验性采集参考，不得把它们称为本项目原创的伯乐 Skill，也不得让 AI 新闻采集能力取代需求建模、历史回放、信源组合和覆盖审计。

## 先判断使用者所处阶段

- **刚进入领域的人（第一优先级）**：通常只有一个领域名称，没有知识背景，不知道领域边界、权威专家和可信来源，也不要求他先写 PIR 或完整问题。先建立 Domain Map、人物/机构和来源角色。
- **已经在领域里但覆盖不够广的人**：保留已有专家、来源和材料作为种子，用领域地图、EAR 和 Coverage Audit 向外发现相邻参与者、早期信号和缺口，不把已有信源当成完整答案。
- **共同目标**：两类人都要得到一套领域情报知识域；日报、推送和知识引擎是知识域建立后的更新与交付层。
- **非目标用户**：已经能够独立用 AI 配置信源、搭建日报并维护知识引擎的人，不是本 Skill 的主要服务对象；他们可以复用工程组件，但不应改变领域优先的入口。

## 工作流

1. 先用一个领域名称或关键词初始化 `DomainProfile`；已有从业者可以同时提供现有信源和材料，但不要要求新进入者先写专业问题或准备信源清单。
2. 从 Domain Seed 建立领域边界、词典、观察面、人物/机构和来源候选；领域底图完成后，再明确 PIR、EIE、主题权重和事件优先级。
3. 将 Expert、Source、typed Attention Edge 和证据时间整理成 `BootstrapInput`；每条边保留关系类型、主题相关性、证据置信度、观察时间和证据 URL。
4. 用 `dib <input.json> --output-dir <dir>` 运行 EAR、point-in-time replay、Portfolio、Coverage Audit 和 Daily Brief。
5. 先看 `bootstrap-report.json` 的结构化结果，再用 Markdown 报告交接；不以来源数量或单一总分宣称覆盖完成。
6. 来源进入长期组合前，确认它有角色、EIE 映射、稳定获取路径和历史回放证据；不稳定、登录态、私有邮箱和需要 token 的来源放到用户自己的边界适配器。
7. 新增来源或领域适配时，补充一个最小行为测试和一个可运行 Bundle；不要把早期 AI News Radar 的默认来源、栏目或阈值直接当成新领域方案。

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
