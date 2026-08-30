# 私人情报所：领域情报方法论 V0.1

本文件描述私人情报所的核心领域情报方法论。它服务于希望用 AI 建立自己专业情报体系的从业者，不要求使用者先成为工程师。仓库内早期保留的 AI News Radar 采集脚本、Radar Skill 和伯乐 Skill 仅是历史或实验性边界参考，不是本方法论的来源或替代品；旧阅读界面已从发布面移除。详见 [项目范围与来源/版权说明](PROJECT_SCOPE_AND_ATTRIBUTION.md)。

## 1. 定位

这不是把更多 RSS 堆到一个页面，也不是要求刚进入行业的人先写出专业问题，而是把“一个领域关键词 → 可持续的信息生态”变成一条可复盘的工程流水线：

```text
Domain Seed
→ Domain Boundary / Vocabulary / Map
→ Topic and Essential Information Elements
→ Expert Attention Reconstruction
→ Source Archetypes and Temporal Benchmark
→ Source Portfolio
→ Knowledge Graph / Domain Memory
→ Coverage Audit
→ Domain-ranked Daily Brief
→ Optional Focused Watch / Feedback
```

本版本把可证伪的核心机制落成了一个离线、确定性的 Python 包。它允许只用一个 `domain` 初始化领域底图；当用户从底图中选出具体方向后，再补充 `decision_context`、PIR 和更细的 EIE。公开的 AI/文旅日报站仍由既有 `scripts/update_news.py` 负责采集；新包负责把已结构化的来源、证据和信号转成可审计的情报资产。

## 2. 方法论原则

### 2.1 领域入口先于具体问题

每个领域先声明一个最小 `DomainProfile`：

- `domain`：行业、产业、知识域或细分领域的名称；
- `domain_aliases`：同义词、旧称、上下游称呼和检索变体；
- `domain_intent`：用户为什么想进入或了解它，可暂缺；
- `mode`：默认是 `domain_foundation`，需要长期追踪某个判断时切换为 `focused_watch`。

领域底图建立后，再逐步声明：

- `decision_context`：情报要服务什么判断；
- `IntelligenceRequirement`：必须回答的问题；
- `EssentialInformationElement`：回答问题必须掌握的具体信息；
- `EventPriority`：哪些事件类型应该进入日报优先级。

覆盖率的分母就是已经确认的 EIE 数量或权重，不用“找到多少网页”替代。领域初始化阶段可以暂时没有 EIE；此时系统的任务是发现和整理观察面，而不是伪造覆盖率。

### 2.2 两层工作模式

私人情报所把“建立领域体系”和“追踪具体问题”分开，但让两者可以衔接：

| 层级 | 输入 | 主要输出 | 适用时机 |
| --- | --- | --- | --- |
| `domain_foundation` | 一个领域名称或关键词 | 领域边界、词典、参与者、来源地图、知识引擎底图和基础日报 | 刚进入领域，或希望先了解全貌 |
| `focused_watch` | 领域底图 + 一个判断/问题 | PIR、细化 EIE、事件优先级、历史回放和专项推送 | 已经知道要持续盯住哪条线 |

普通 AI 深度研究通常回答一次具体问题；私人情报所先让使用者拥有一个可持续更新的领域系统，再把一次性问题纳入长期观察。`decision_context` 不是入口门槛，而是第二层的定向器。

### 2.3 Source 与 Acquisition 分离

`SourceProfile` 描述信息生产者的角色、权威性、可靠性、主题和历史表现；`AcquisitionCapability` 描述 RSS、Atom、JSON、Sitemap、API 等获取路径。登录态、私有邮箱和不稳定桥接源必须留在外部适配层，不进入公共默认配置。

### 2.4 Source Role 不等于 Reliability

同一个组合需要不同角色：

| 角色 | 作用 |
| --- | --- |
| `official_primary` | 原始发布和权威确认 |
| `expert_interpreter` | 解释机制、影响与背景 |
| `frontier_sensor` | 发现尚未进入主流视野的信号 |
| `broad_coverage` | 防漏和广覆盖 |
| `community` | 观察使用、讨论和早期反馈 |

角色组合解决的是信息盲区，可靠性解决的是信号能否被信任，两者不能合并成一个“权威分”。

## 3. 工程实现映射

| 方法论模块 | 工程入口 | 输出 |
| --- | --- | --- |
| EAR 注意力图 | `graph.rank_attention_sources` | 跨圈层来源推荐 |
| 历史回放 | `backtest.replay_benchmark` | `Event × Nugget × Cutoff` 单元与指标向量 |
| 来源组合 | `portfolio.optimize_portfolio` | 预算约束下的来源组合与互补 Bundle |
| 覆盖审计 | `coverage.audit_coverage` | EIE 分母、覆盖率、机器可读缺口原因 |
| 日报排序 | `daily.build_daily_brief` | 去重后的故事线与证据链接 |
| 全链路 | `pipeline.build_bootstrap_report` | 一份 JSON + 一份 Markdown 报告 |

## 4. EAR：从专家种子重建注意力网络

每条边必须是 typed edge，并保存关系强度、主题相关性、证据置信度和观察时间。候选来源排名采用：

```text
typed relation weight
× topic relevance
× evidence confidence
× temporal decay
→ personalized propagation
→ degree correction
→ cross-cluster convergence
```

当前实现使用 Personalized PageRank 传播，按入边度数做校正，并单独输出 `cross_cluster_support`。因此“很多同圈层的人都关注”不会自动等于“跨圈层收敛”。

## 5. Historical Replay：严格 point-in-time

每个 Nugget 有两个独立时间：

- `available_at`：系统客观上最早可以获得该事实的时间；
- `authoritative_at`：权威确认时间。

回放只允许使用：

```text
observation.available_at <= cutoff
```

不能用文件日期、最终修订后的内容或事后建立的完整数据库替代 `available_at`。报告同时保留 Event Recall、Nugget Recall、Lead Time、Precision、False Alarm Burden、Originality、Credibility、Cross-role Confirmation、Acquisition Reliability 和 Decision Utility。

## 6. Portfolio：优化组合，不是排列高分榜

组合选择以边际覆盖为主，同时考虑质量、角色多样性、采集成本和 Bundle synergy。输入可以显式声明来源组合的互补价值，避免贪心算法因为单源边际价值低而漏掉“组合后才有用”的信号。

工程实现是可解释的启发式基线，不把启发式结果包装成最优解。后续可以用冻结的历史 Benchmark 学习权重，再进行 Source Ablation 和 Marginal Portfolio Gain 回测。

## 7. Coverage Audit：知道自己不知道什么

每个 EIE 都生成一行：

```text
element_id
coverage_ratio
source_ids
gap_reasons[]
```

当前缺口枚举包括：

- `no_capable_source`
- `insufficient_source_count`
- `no_approved_source`
- `no_historical_evidence`
- `no_acquisition_path`
- `insufficient_role_diversity`

报告区分“有候选来源”和“已批准、可稳定获取、具有历史证据的来源”，不会把发现结果直接伪装成生产覆盖。

## 8. Source Lifecycle

推荐的状态机：

```text
discovered → candidate → approved → observing → validated → active
                    ├→ rejected             └→ watchlist → retired
```

进入 `active` 前至少要有：来源角色、主题/EIE 映射、获取路径、证据记录和历史回放结果。来源健康下降时进入 `watchlist`，不自动删除；删除是维护者明确决策。

## 9. 运行示例

```bash
uv run --project packages/domain-intelligence \
  dib packages/domain-intelligence/examples/data-elements.json \
  --output-dir /tmp/domain-intelligence-preview
```

输出：

- `bootstrap-report.json`：供程序、后续 Agent 和审计流水线读取；
- `bootstrap-report.md`：供人阅读、交接和评审。

示例故意保留一个海外 EIE 缺口，便于验证系统不会用“来源数量”掩盖未覆盖区域。

## 10. 当前边界与下一阶段

V0.1 已实现领域情报的评价内核，并在 `DomainProfile` 中支持“只给领域名称”的最小初始化；它没有把外部搜索、爬虫、LLM 语义判断、数据库或调度器硬编码进核心。这样可以在边界上复用早期采集工程的成熟零件，也能把私有来源和不同领域适配器隔离在边界上；这些零件不构成私人情报所的产品入口。

下一阶段应按冻结 Benchmark 推进：

1. 选一个公开资料丰富的领域，从 Domain Seed 生成领域边界、词典和 6～10 个观察面；
2. 为每个观察面建立 15～20 个异质 Expert Seed、人物/机构和来源候选；
3. 记录每条关系边的来源 URL、观察时间和证据置信度；
4. 冻结历史 cutoff，补齐 Event × Nugget 标注；
5. 比较普通热门列表与 EAR 的跨圈层来源及 Marginal Portfolio Gain；
6. 只有通过回放和覆盖审计的来源，才进入长期采集组合；再从底图中选择具体问题建立 Focused Watch。
