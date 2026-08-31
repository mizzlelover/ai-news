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

这是“117 个来源之后”的第一条生产链路。117 个来源可以共享同一套核心契约，但每个来源的 RSS、Atom、公开 API、静态页面、人工或登录态适配器仍然属于外部边界。

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
- 主题、EIE、事件类型、重要性、原创性和确认状态。

其中 `available_at` 仍然是 point-in-time 回放的时间依据，不能用 `retrieved_at` 替代。

## 核心引擎做什么

`build_activation_report` 会完成四件事：

1. 检查证据和运行记录是否属于来源图，拒绝悬空来源和重复证据；
2. 为 117 个来源生成本次运行状态：`blocked`、`ready`、`observed`、`empty` 或 `failed`；
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

运行后，`bootstrap-report.json` 会新增 `activation` 节点，阅读版报告会显示证据数、生成信号数、知识域增量数和来源状态分布。

```bash
uv run --project packages/domain-intelligence dib \
  packages/domain-intelligence/examples/data-elements.json \
  --output-dir /tmp/private-intelligence-activation
```

## 与 117 个来源的关系

117 是候选雷达规模，不是每次日报的条数。每次来源激活运行都应同时看四个层次：

| 层次 | 要回答的问题 |
| --- | --- |
| 来源健康 | 这次是否成功获取，是否为空，是否失败 |
| 证据生产 | 获得了哪些可回溯的原始证据 |
| 知识域变化 | 哪些主题和必需信息要素发生了增量 |
| 日报交付 | 哪些事件经过去重和排序后值得今天阅读 |

只有经过连续运行、历史回放、来源质量评价和覆盖审计的来源，才适合进入长期日报组合。来源激活解决的是“来源开始生产证据”，不是一次性宣布整个领域已经覆盖完成。

## 后续工程边界

当前核心已经实现适配器结果到情报资产的确定性转换。接下来按这个顺序扩展：

1. 为公开 RSS、Atom、JSON 和稳定静态页面接入可复用适配器；
2. 保存原始响应快照、内容哈希、抓取时间和失败状态；
3. 增加事件/信息要素抽取与多源印证记录；
4. 增加领域知识域的持久化更新和变更历史；
5. 接入调度、邮件/消息推送和用户反馈；
6. 用真实运行数据补齐 117 个来源的历史回放，再重新计算来源组合。

这条边界保留了成熟采集轮子的可替换性，同时确保采集结果必须经过私人情报所自己的证据、知识域、组合和覆盖规则。
