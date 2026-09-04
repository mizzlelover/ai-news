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

## 面向使用者的本地网站

如果使用者没有技术背景，不需要先准备 Bundle 或理解命令行参数。由 AI 或协作者在仓库根目录启动：

```bash
uv run --project packages/domain-intelligence private-intelligence
```

然后打开 <http://127.0.0.1:8787/>，在页面中填写一次 OpenAI 兼容 AI 接口和模型名称，输入一个领域即可开始建立本地运行。网站会把领域建模、来源网络、公开入口采集、全文归档、知识图谱、推荐回测和日报接成同一条任务链；完成后自动进入运行工作台。AI 接口密钥只保存在当前进程，不写入 Bundle 或仓库。

本地网站是真实入口，不是静态演示表单。静态演示和工作台说明页只负责解释方法与回读方式；如果没有配置 AI，网站会明确要求先完成连接设置，不会伪造运行结果。

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

要直接采集公开来源并留存内容资产，使用：

```bash
uv run --project packages/domain-intelligence dib \
  --domain "your domain" \
  --bundle /path/to/local/domain-seed.json \
  --fetch \
  --snapshots /path/to/local/capture \
  --output-dir /tmp/private-intelligence-run
```

`--fetch` 使用内置公开 HTTP 适配器获取 RSS/Atom 端点，并对符合条件的 feed item 继续抓取规范化全文；HTML、JSON 和 PDF 入口会归档可读的规范化全文，原始响应单独保留。Sitemap、OPML、API 和静态页面目前作为端点采集边界，只有领域适配器提供条目展开与证据映射时才会继续形成条目级证据。`--snapshots` 是采集目录或可复现快照目录。需要浏览器渲染、登录态、私有凭证或不稳定路径的来源会留下明确的 blocked/failed 结果。领域 seed、快照、采集全文和输出目录都属于本地运行数据，不应提交到公共仓库。

输出目录包含：

- `domain-profile.json`：领域边界、主题和信息要素；
- `source-map.json`：专家、来源和 typed attention edges；
- `acquisition-plan.json`：每个来源的获取方式、入口和可执行状态；
- `source-activation.json`：本次运行、证据、信号和知识域增量；
- `knowledge-graph.json` / `knowledge-graph.md`：带来源和时间证据的领域知识图谱，以及可读的证据追踪摘要；
- `content-inventory.json` / `content-inventory.md`：每个内容资产的来源、证据映射、状态、全文路径、原始响应路径和失败原因；
- `content/`：本次运行复制出的规范化全文 Markdown 与原始响应文件；
- `daily-brief.json` / `daily-brief.md`：日报交付；
- `bootstrap-report.json` / `bootstrap-report.md`：完整机器版和阅读版报告；
- `run-manifest.json`：本次运行的范围、计数和交付物清单。

如果不提供 `--snapshots` 或 `--fetch`，运行会使用 Bundle 中已有的 `acquisition_runs` 和 `evidence`。`--fetch` 会把真实采集结果替换为本次运行的激活输入，并清除仅作为发现线索的 seed signals；因此日报只能由本次采集后实际建立了内容引用的证据产生。来源入口抓取成功不等于证据产生：没有明确证据映射的静态页面只进入 `content-inventory`，不会自动进入日报。

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
7. `evidence`：带有来源 URL、可获得时间、实际获取时间、内容哈希和可选全文引用的证据记录；
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
snapshot.py   reproducible local snapshot adapter and content validation
capture/      public capture orchestration, transport, archive, and planning
feed_discovery.py RSS/Atom item discovery and XML boundary parsing
public_capture.py compatibility facade for the public capture entry point
capture_parser.py HTML/JSON/XML visible-text and date extraction
knowledge_graph.py typed domain knowledge graph assembly
acquisition.py source acquisition plan
run.py        domain input and complete delivery orchestration
daily.py      URL + title deduplication / domain ranking
pipeline.py   end-to-end orchestration
io.py         JSON and Markdown report surface
```

## `--fetch` 的格式边界

| 来源入口 | 核心内置行为 | 什么时候形成条目级全文/证据 |
| --- | --- | --- |
| RSS / Atom | 获取 feed，发现条目，按条目 URL 继续获取公开全文 | 条目有可用 URL、正文通过解析且来源映射允许入选 |
| PDF | 提取可读文本并保存规范化全文，同时保留原始 PDF | 有可读文本且来源映射允许入选 |
| JSON / Sitemap / OPML / API | 保存端点响应并登记内容资产 | 需要领域适配器负责 schema 解析、条目展开和 evidence mapping |
| 稳定静态页面 | 获取页面并保存规范化全文与原始响应 | 页面本身不自动成为日报证据；需要明确证据映射 |
| 浏览器、登录态、私有凭证或不稳定入口 | 留下 blocked/failed 状态和原因 | 由外部边界适配器按同一契约接入 |

因此，`source-activation.json` 的来源状态、`content-inventory.json` 的内容状态和 `daily-brief.json` 的证据引用必须一起阅读；“端点已抓取”不等于“日报已有事实”。

## 与采集适配器的关系

仓库中的 `scripts/update_news.py` 面向公开 AI/文旅场景提供采集与静态数据发布；本包提供通用的来源激活契约、情报判断层和一个面向公开 HTTP 入口的基础采集器。`--fetch` 会将公开响应存为原始文件，同时生成规范化全文和 `ContentArtifact`；只有被证据记录引用的内容才进入日报和知识域增量。需要浏览器渲染、登录态、私有凭证或领域专属解析的适配器仍可在外部边界实现，并提交同一契约。AI News Reader 兼容界面不属于本项目当前发布面。

这个边界允许：

- 保留 RSS、OPML、公开 JSON 和 GitHub Actions 的成熟采集逻辑；
- 为数据要素、网络安全、教育、文旅等领域替换 `DomainProfile`，而不重写回测和组合算法；
- 将私有 API、邮箱、登录态和浏览器适配器留在用户自己的边界配置中。
