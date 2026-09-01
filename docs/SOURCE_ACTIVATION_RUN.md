# 私人情报所：来源激活运行

## 这一步解决什么

来源网络建立以后，私人情报所不能直接把来源名称当成情报。下一步必须把每次采集变成可审计的运行记录和证据记录，再由核心引擎把证据送入日报与知识域。

```text
Source Profile
→ Source Acquisition Run
→ Evidence Record
→ Daily Signal
→ Knowledge-domain Delta
→ Daily Brief / Knowledge Domain
```

这是候选来源网络建立后的第一条生产链路。公开 HTTP 入口可以由核心包的 `--fetch` 适配器直接采集；浏览器渲染、登录态、私有凭证和领域专属解析仍然属于外部边界。任何边界都必须返回同一套运行、内容和证据契约。

当前内置公开采集边界的行为如下：

| 入口格式 | 内置行为 | 条目级证据 |
| --- | --- | --- |
| RSS / Atom | 获取端点、发现 feed item，并尝试获取 item URL 的规范化全文 | 满足时间窗口、正文和映射条件时产生 |
| PDF | 提取可读文本为规范化全文，同时保留原始 PDF | 有可读文本且满足映射条件时产生 |
| JSON / Sitemap / OPML / API | 获取并归档端点响应，登记内容资产 | 需要领域适配器解析条目并建立映射 |
| 稳定静态页面 | 获取页面、规范化全文和原始响应 | 页面不会因为抓取成功自动进入日报 |
| 浏览器渲染、登录态、私有凭证 | 保留阻断/失败状态 | 由外部适配器接入 |

因此，`captured` 只说明内容资产已归档；`EvidenceRecord` 还必须有来源、时间、内容哈希和可回读的 `content_ref`。

## 采集器提交什么

在 Bundle 顶层增加两个字段：

- `acquisition_runs`：本次来源运行的结果，一来源一条运行记录；
- `evidence`：本次获得的原始证据摘要和时间记录。

`SourceAcquisitionRun` 只记录采集结果，不把“采集成功”误写成“事实已经确认”：

| 状态 | 含义 |
| --- | --- |
| `succeeded` | 获取成功，并可能带有证据记录 |
| `empty` | 获取成功，但当前窗口没有可入选内容 |
| `failed` | 获取失败，必须保留失败原因以便维护来源 |

`EvidenceRecord` 至少保留：

- 来源 ID、原始 URL、标题和摘要；
- `published_at`：来源标注的发布时间；
- `available_at`：系统客观上最早可以获得该信息的时间；
- `retrieved_at`：本次采集实际获得它的时间；
- `content_hash`：用于去重、审计和后续回放；
- `content_ref`、`content_type`、`content_char_count`：把证据映射回本次运行的规范化全文；
- 主题、EIE、事件类型、重要性、原创性和确认状态。

其中 `available_at` 仍然是 point-in-time 回放的时间依据，不能用 `retrieved_at` 替代。

采集结果还会生成 `ContentArtifact` 和 `ContentInventory`：

| 内容状态 | 含义 |
| --- | --- |
| `captured` | 已保存规范化全文和原始响应，可通过 `relative_path`、`raw_relative_path` 回读 |
| `failed` | 已尝试获取但请求、状态码、解析或大小限制失败，保留 `error_code` |
| `blocked` | 因未批准、不稳定、需要浏览器或不支持的获取方式没有执行请求 |

来源入口成功抓取只说明内容资产可回读，不自动等价于证据。只有有明确 `evidence_id` 的内容才会生成 `EvidenceRecord`，进入知识图谱、知识域增量和日报。

## 核心引擎做什么

`build_activation_report` 会完成四件事：

1. 检查证据和运行记录是否属于来源图，拒绝悬空来源和重复证据；
2. 为来源网络生成本次运行状态：`blocked`、`ready`、`observed`、`empty` 或 `failed`，并把每条 `SourceAcquisitionRun` 原样写入报告；
3. 把窗口内的证据转换成 `DailySignal`，交给去重、聚类、排序和日报生成；
4. 为每条证据产生一个 `KnowledgeDomainDelta`，把主题和 EIE 映射带回领域知识域更新入口。

这一步不把一条网页自动包装成最终事实。事件抽取、跨来源印证、权威确认和人工判断仍然需要由领域适配器、模型或审核流程完成；核心会保存证据和时间，确保判断可以回溯。

## 最小输入片段

下面的片段可以直接合并进一个现有 Bootstrap Bundle：

```json
{
  "acquisition_runs": [
    {
      "id": "run-policy-20260831T080000Z",
      "source_id": "official-policy",
      "status": "succeeded",
      "retrieved_at": "2026-08-31T08:00:00Z",
      "evidence_ids": ["evidence-policy-20260831"]
    }
  ],
  "evidence": [
    {
      "id": "evidence-policy-20260831",
      "source_id": "official-policy",
      "title": "New policy published",
      "url": "https://example.com/policy/2026-08-31",
      "summary": "A policy update entered the public record.",
      "published_at": "2026-08-31T07:00:00Z",
      "available_at": "2026-08-31T07:00:00Z",
      "retrieved_at": "2026-08-31T08:00:00Z",
      "content_hash": "sha256:replace-with-adapter-hash",
      "topic_ids": ["policy"],
      "element_ids": ["e-policy"],
      "event_type": "policy_change",
      "importance": 0.9,
      "originality": 1.0,
      "confirmed": true,
      "event_id": "event-policy"
    }
  ]
}
```

运行后，`source-activation.json` 和 `bootstrap-report.json` 会包含 `activation` 节点，阅读版报告会显示证据数、生成信号数、知识域增量数和来源状态分布。

```bash
uv run --project packages/domain-intelligence dib \
  --domain "data-elements" \
  --bundle packages/domain-intelligence/examples/data-elements.json \
  --snapshots /path/to/local/snapshots \
  --output-dir /tmp/private-intelligence-activation
```

直接做公开来源真实采集时：

```bash
uv run --project packages/domain-intelligence dib \
  --domain "your domain" \
  --bundle /path/to/local/domain-seed.json \
  --fetch \
  --snapshots /path/to/local/capture \
  --output-dir /tmp/private-intelligence-activation
```

运行结束后，打开仓库的 `demo/workbench.html`，点击“导入运行目录”，可以在浏览器里查看本次运行的完整产物链路。工作台按 `run-manifest.json` 识别运行范围，按 `content-inventory.json` 回读全文，按 `source-activation.json` 回链证据，再把 `daily-brief.json` 的推荐落回来源和内容。

验收时先看 `run-manifest.json`，再按下面的顺序回读：

```text
source-map.json
→ content-inventory.json / content-inventory.md
→ content/<artifact>.md 与原始响应
→ source-activation.json 的 evidence.content_ref
→ knowledge-graph.json / knowledge-graph.md 的 evidence/publishes/supports_element 边
→ bootstrap-report.json 的 attention_recommendations / portfolio
→ daily-brief.json / daily-brief.md
```

`--fetch` 运行会把输入 Bundle 中的 seed signals 当作待验证的公开页面线索；只有成功回读并建立全文引用的信号才会进入本次日报，避免把预先写入 Bundle 的标题误报成实时采集结果。

## 与候选来源网络的关系

候选雷达规模不是每次日报的条数。每次来源激活运行都应同时看四个层次：

| 层次 | 要回答的问题 |
| --- | --- |
| 来源健康 | 这次是否成功获取，是否为空，是否失败 |
| 证据生产 | 获得了哪些可回溯的原始证据 |
| 知识域变化 | 哪些主题和必需信息要素发生了增量 |
| 日报交付 | 哪些事件经过去重和排序后值得今天阅读 |

只有经过连续运行、历史回放、来源质量评价和覆盖审计的来源，才适合进入长期日报组合。来源激活解决的是“来源开始生产证据”，不是一次性宣布整个领域已经覆盖完成。

## 后续工程边界

当前核心已经实现公开 HTTP 采集、本地全文/原始响应归档、本地快照回放，以及从内容到证据、知识域增量和日报的确定性转换。后续按这个顺序扩展：

1. 为浏览器渲染、登录态和领域专属页面增加外部边界适配器；
2. 增加事件/信息要素抽取与多源印证记录；
3. 增加领域知识域的持久化更新和变更历史；
4. 接入调度、邮件/消息推送和用户反馈；
5. 用真实运行数据补齐候选来源的历史回放，再重新计算来源组合。

这条边界保留了成熟采集轮子的可替换性，同时确保采集结果必须经过私人情报所自己的证据、知识域、组合和覆盖规则。
