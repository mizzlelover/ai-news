# 私人情报所核心引擎：Domain Intelligence Bootstrap

一个面向任意领域的、可审计的情报自举内核，是私人情报所的通用工程核心。

它解决的不是“再抓一批新闻”，而是：从一个行业、产业或知识域关键词开始，先建立领域地图、人物与机构、信源结构和知识引擎；当用户选出具体方向后，再声明必须掌握的信息，重建专家注意力网络，用严格的可获得时间回放信源，按预算选择互补来源，再把采集器提交的运行结果和证据记录转换为知识域增量与有证据链接的领域日报。

这是本项目的核心工程，不依赖任何现成 AI 日报页面或 Skill 才能运行。仓库中保留的 AI News Radar 页面、`ai-news-radar` Skill 和 Radar Skill 只是采集/展示/消费适配参考，来源与版权边界见 [`../../docs/PROJECT_SCOPE_AND_ATTRIBUTION.md`](../../docs/PROJECT_SCOPE_AND_ATTRIBUTION.md)。

## 面向谁

这个引擎把“给出一个领域”作为唯一入口：先建立领域边界、参与者、专家、来源角色、证据和缺口，再让采集、更新、日报与推送围绕这张知识域运行。它尤其解决刚进入领域、没有知识背景且不知道该看谁和该信谁的人所面对的起点问题。

已经能够独立配置信源、搭建日报并维护知识引擎的人，不是本项目的主要目标用户；他们可以复用本包的工程组件。`domain_foundation` 是任何领域的默认起点，`focused_watch` 则是在领域知识域建立后，对某个判断或问题做进一步追踪。已有专家、网站、报告或项目材料可以在底图建立后，通过 AI 指令映射进 Bundle 的 `attention_graph`，不是入口前提。

## 快速运行

在仓库根目录执行：

```bash
uv run --project packages/domain-intelligence \
  dib packages/domain-intelligence/examples/data-elements.json \
  --output-dir /tmp/domain-intelligence-preview
```

也可以从包目录执行：

```bash
cd packages/domain-intelligence
uv run dib examples/data-elements.json --output-dir /tmp/domain-intelligence-preview
```

## 完整领域运行

当 Skill 根据用户给出的领域建立好本地 typed seed Bundle 后，使用领域运行入口：

```bash
uv run --project packages/domain-intelligence dib \
  --domain "your domain" \
  --bundle /path/to/local/domain-seed.json \
  --snapshots /path/to/local/snapshots \
  --output-dir /tmp/private-intelligence-run
```

`--domain` 是运行时的领域输入，`--bundle` 是 Skill 在本地生成并经 Pydantic 校验的领域底图与来源网络，`--snapshots` 用于执行可复现的本地采集边界。领域 seed、快照和输出目录都属于本地运行数据，不应提交到公共仓库。

输出目录包含：

- `domain-profile.json`：领域边界、主题和信息要素；
- `source-map.json`：专家、来源和 typed attention edges；
- `acquisition-plan.json`：每个来源的获取方式、入口和可执行状态；
- `source-activation.json`：本次运行、证据、信号和知识域增量；
- `knowledge-graph.json`：带来源和时间证据的领域知识图谱；
- `daily-brief.json` / `daily-brief.md`：日报交付；
- `bootstrap-report.json` / `bootstrap-report.md`：完整机器版和阅读版报告；
- `run-manifest.json`：本次运行的范围、计数和交付物清单。

如果不提供 `--snapshots`，运行会使用 Bundle 中已有的 `acquisition_runs` 和 `evidence`；提供后，快照采集结果会替换本次运行的激活输入。RSS、Atom、JSON、浏览器和登录态适配器可以在外部采集层实现，只要向同一契约提交运行和证据。

## 运行测试

```bash
uv run --project packages/domain-intelligence pytest -q packages/domain-intelligence/tests
uv run --project packages/domain-intelligence ruff format --check packages/domain-intelligence/src packages/domain-intelligence/tests
uv run --project packages/domain-intelligence ruff check packages/domain-intelligence/src packages/domain-intelligence/tests
```

## 输入与输出

输入是一个 JSON Bundle，包含：

1. `profile`：至少包含 `domain`；也可以包含领域别名、进入动机、Focused Watch 的决策场景、PIR、EIE、主题权重和事件优先级；
2. `attention_graph`：异质 Expert、Source 和 typed Attention Edge；领域底图建立后，已有来源和专家可以从这里作为扩展种子进入；
3. `attention_query`：种子专家、主题和回放时点；
4. `benchmark`：Event、Nugget、Source、Observation 和 Cutoff；
5. `signals`：已有的结构化信号，可与激活运行生成的信号合并；
6. `acquisition_runs`：采集器本次运行的成功、空结果或失败状态；
7. `evidence`：带有来源 URL、可获得时间、实际获取时间和内容哈希的证据记录；
8. 预算、来源数量、日报窗口和输出上限。

最小的领域入口不要求先写专业问题，也不要求先准备信源清单：

```python
DomainProfile(
    domain="数字文旅产业",
    domain_aliases=("数字旅游", "文旅数字化"),
)
```

它默认处于 `domain_foundation` 模式。完成领域底图后，才按需要补充 `decision_context`、PIR 和 EIE，并切换到 `focused_watch`。

所有边界输入由 Pydantic v2 模型解析，内部算法只接收已解析对象。`examples/data-elements.json` 是安装验证用的最小 Bundle；具体领域的 seed Bundle 和来源网络由 Skill 在本地运行时生成。

## 模块

```text
graph.py      EAR / Personalized PageRank / degree correction
backtest.py   availability-time replay / metric vector
portfolio.py  budgeted portfolio / source bundle synergy
coverage.py   EIE denominator / gap audit
activation.py acquisition run, evidence, signal, and knowledge-delta intake
snapshot.py   reproducible local acquisition adapter
knowledge_graph.py typed domain knowledge graph assembly
acquisition.py source acquisition plan
run.py        domain input and complete delivery orchestration
daily.py      URL + title deduplication / domain ranking
pipeline.py   end-to-end orchestration
io.py         JSON and Markdown report surface
```

## 与采集适配器的关系

仓库中的 `scripts/update_news.py` 面向公开 AI/文旅场景提供采集与静态数据发布；本包现在提供通用的来源激活契约和情报判断层。外部适配器提交 `acquisition_runs` 与 `evidence`，本包将它们转换为来源状态、日报 signals 和知识域 deltas，再把来源组合、历史证据、覆盖缺口和日报排序纳入同一份报告。AI News Reader 兼容界面不属于本项目当前发布面。

这个边界允许：

- 保留 RSS、OPML、公开 JSON 和 GitHub Actions 的成熟采集逻辑；
- 为数据要素、网络安全、教育、文旅等领域替换 `DomainProfile`，而不重写回测和组合算法；
- 将私有 API、邮箱、登录态和浏览器适配器留在用户自己的边界配置中。
