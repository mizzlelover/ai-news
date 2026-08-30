# 私人情报所核心引擎：Domain Intelligence Bootstrap

一个面向任意领域的、可审计的情报自举内核，是私人情报所的通用工程核心。

它解决的不是“再抓一批新闻”，而是：给定一个决策目的，声明必须掌握的信息，重建专家注意力网络，用严格的可获得时间回放信源，再按预算选择互补来源，最后生成有证据链接的领域日报。

这是本项目的核心工程，不依赖 AI News Radar 才能运行。AI News Radar、伯乐 Skill 和 Radar Skill 只是可选的采集/展示/消费适配层，来源与版权边界见 [`../../docs/PROJECT_SCOPE_AND_ATTRIBUTION.md`](../../docs/PROJECT_SCOPE_AND_ATTRIBUTION.md)。

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

输出目录包含：

- `bootstrap-report.json`：结构化结果；
- `bootstrap-report.md`：交接与阅读版报告。

## 运行测试

```bash
uv run --project packages/domain-intelligence pytest -q packages/domain-intelligence/tests
uv run --project packages/domain-intelligence ruff format --check packages/domain-intelligence/src packages/domain-intelligence/tests
uv run --project packages/domain-intelligence ruff check packages/domain-intelligence/src packages/domain-intelligence/tests
```

## 输入与输出

输入是一个 JSON Bundle，包含：

1. `profile`：决策场景、PIR、EIE、主题权重和事件优先级；
2. `attention_graph`：异质 Expert、Source 和 typed Attention Edge；
3. `attention_query`：种子专家、主题和回放时点；
4. `benchmark`：Event、Nugget、Source、Observation 和 Cutoff；
5. `signals`：待生成日报的结构化信号；
6. 预算、来源数量、日报窗口和输出上限。

所有边界输入由 Pydantic v2 模型解析，内部算法只接收已解析对象。示例文件是完整的最小可运行 Bundle：`examples/data-elements.json`。

## 模块

```text
graph.py      EAR / Personalized PageRank / degree correction
backtest.py   availability-time replay / metric vector
portfolio.py  budgeted portfolio / source bundle synergy
coverage.py   EIE denominator / gap audit
daily.py      URL + title deduplication / domain ranking
pipeline.py   end-to-end orchestration
io.py         JSON and Markdown report surface
```

## 与 AI News Radar 的关系

仓库原有 `scripts/update_news.py` 是面向公开 AI/文旅场景的采集与静态发布层；本包是通用的情报判断与评价层。前者可以产出结构化 signals，后者负责把来源组合、历史证据、覆盖缺口和日报排序纳入同一份报告。

这个边界允许：

- 保留 RSS、OPML、公开 JSON 和 GitHub Actions 的成熟采集逻辑；
- 为数据要素、网络安全、教育、文旅等领域替换 `DomainProfile`，而不重写回测和组合算法；
- 将私有 API、邮箱、登录态和浏览器适配器留在用户自己的边界配置中。
