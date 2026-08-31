# 私人情报所：领域情报方法论 V0.1

本文件描述私人情报所的核心领域情报方法论。它把“给出一个领域”作为唯一入口：先为这个领域建立知识体系与情报体系，再借助工具持续更新、生成日报和推送。它尤其解决刚进入领域、没有知识背景且不知道该找谁和该信谁的人所面对的起点问题；已有的专家、网站、报告或项目材料可以在领域底图建立后直接加入，不是入口前提。方法不要求使用者先成为工程师；已经能够独立配置信源和维护日报的人不是本项目的主要目标用户。仓库中的 AI News Radar 采集脚本、Radar Skill 和相关 Skill 属于独立的采集与消费适配参考，不是本方法论的来源或替代品。详见 [项目范围与来源/版权说明](PROJECT_SCOPE_AND_ATTRIBUTION.md)。

## 1. 定位

这不是把更多 RSS 堆到一个页面，也不是要求刚进入行业的人先写出专业问题，更不是给已经会配置信源的人再做一个日报入口，而是把“一个领域关键词 → 领域情报知识域 → 可持续的信息生态”变成一条可复盘的工程流水线：

```text
Domain Seed
→ Domain Boundary / Vocabulary / Map
→ Topic and Essential Information Elements
→ Expert Attention Reconstruction
→ Source Archetypes and Temporal Benchmark
→ Source Portfolio
→ Source Activation / Evidence Records
→ Domain Knowledge Domain / Knowledge Graph / Domain Memory
→ Knowledge-domain Delta
→ Coverage Audit
→ Domain-ranked Daily Brief
→ Optional Focused Watch / Feedback
```

可证伪的核心机制已经落成一个离线、确定性的 Python 包。它允许只用一个 `domain` 初始化领域底图；当用户从底图中选出具体方向后，再补充 `decision_context`、PIR 和更细的 EIE。来源适配器提交采集运行和证据记录后，核心会把它们转换为来源状态、日报信号和知识域增量；公开的 AI/文旅日报站由 `scripts/update_news.py` 负责采集，但不是私人情报所的方法论入口。

## 2. 方法论原则

### 2.1 领域优先，一个入口

私人情报所不要求使用者先拥有一批信源、一个成熟问题或一套工具配置。使用者只需要给出一个领域名称或关键词，系统就从领域底图开始建立情报知识域。这个入口尤其为刚进入领域、还不知道该看谁和该信谁的人降低门槛；已有的专家、网站、报告或项目材料，之后可以直接作为补充告诉 AI 加入。

| 入口输入 | 系统先搭建 | 使用者随后得到 |
| --- | --- | --- |
| 一个行业、产业、知识域或细分领域名称 | 领域边界、词典、观察面、参与者、人物与机构 | 知道这个领域由什么组成、先看哪些方向 |
| 一个尚未整理的关键词 | 专家注意力、来源角色、证据时间和知识缺口 | 知道该看谁、该信什么、哪里还没有证据 |
| 底图建立后的补充指令 | 已有信源、报告、项目材料与具体判断的映射 | 形成来源组合、持续更新、日报、推送和 Focused Watch |

领域知识域至少要能回答：这个领域由什么组成，谁在持续产生信息，什么来源分别负责确认、解释、发现和反馈，目前还不知道什么。只有这张底图和来源结构建立起来，更新、日报、推送和知识引擎才有稳定的对象。

已经能够独立使用 AI 配置信源、搭建日报并维护知识引擎的人，不是私人情报所的主要目标用户。工程组件可以被他们复用，但方法论的核心价值在于降低“需要情报却无法开始构建领域知识域”的门槛。

### 2.2 领域入口先于具体问题

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

### 2.3 两层工作模式

私人情报所把“建立领域体系”和“追踪具体问题”分开，但让两者可以衔接：

| 层级 | 输入 | 主要输出 | 适用时机 |
| --- | --- | --- | --- |
| `domain_foundation` | 一个领域名称或关键词；已有信源可在底图建立后补充 | 领域边界、词典、参与者、专家、来源地图、知识引擎底图和基础日报 | 需要从领域开始建立情报体系时 |
| `focused_watch` | 领域底图 + 一个判断/问题 | PIR、细化 EIE、事件优先级、历史回放和专项推送 | 已经知道要持续盯住哪条线 |

普通 AI 深度研究通常回答一次具体问题；私人情报所先让使用者拥有一个可持续更新的领域系统，再把一次性问题纳入长期观察。`decision_context` 不是入口门槛，而是第二层的定向器。

### 2.4 Source 与 Acquisition 分离

`SourceProfile` 描述信息生产者的角色、权威性、可靠性、主题和历史表现；`AcquisitionCapability` 描述 RSS、Atom、JSON、Sitemap、API 等获取路径。登录态、私有邮箱和不稳定桥接源必须留在外部适配层，不进入公共默认配置。

### 2.5 Source Role 不等于 Reliability

同一个组合需要不同角色：

| 角色 | 作用 |
| --- | --- |
| `official_primary` | 原始发布和权威确认 |
| `expert_interpreter` | 解释机制、影响与背景 |
| `frontier_sensor` | 发现尚未进入主流视野的信号 |
| `broad_coverage` | 防漏和广覆盖 |
| `community` | 观察使用、讨论和早期反馈 |

角色组合解决的是信息盲区，可靠性解决的是信号能否被信任，两者不能合并成一个“权威分”。

### 2.6 来源网络要先起量，再进入激活组合

私人情报所面对的是一个使用者一开始还不知道该看谁、该信谁的领域。因此，领域底图不能只挂少数熟悉的官方页面，也不能把一份日报里的链接数量当成领域覆盖。宽领域先建立有规模的候选雷达，再通过历史回放和来源组合收敛，是领域优先方法的必要步骤。

本项目的工程起始基线是：宽领域的第一轮候选雷达以约 80–150 个可独立采集、回放和记录证据的入口为目标；窄领域可以更小，跨行业领域可以更大。这个范围是工程设计基线，不是对所有领域机械套用的权威阈值。

必须区分三种规模：

| 层级 | 含义 |
| --- | --- |
| Candidate Radar | 发现、比较和持续验证的来源入口总面 |
| Historical Replay | 已有历史观察、可以评价提前量和可靠性的来源 |
| Daily Portfolio | 在预算、角色互补和证据约束下进入当前日报组合的来源 |

具体领域的来源网络规模不写死在方法论文档中，而由每次 Domain Seed 运行的 `source-map.json`、`acquisition-plan.json` 和 `run-manifest.json` 报告。宽领域先按来源层扩展候选面，再用历史评价、来源角色和覆盖审计决定进入日报组合的来源。

## 3. 工程实现映射

| 方法论模块 | 工程入口 | 输出 |
| --- | --- | --- |
| EAR 注意力图 | `graph.rank_attention_sources` | 跨圈层来源推荐 |
| 历史回放 | `backtest.replay_benchmark` | `Event × Nugget × Cutoff` 单元与指标向量 |
| 来源组合 | `portfolio.optimize_portfolio` | 预算约束下的来源组合与互补 Bundle |
| 来源激活 | `activation.build_activation_report` | 采集运行、证据记录、日报信号和知识域增量 |
| 覆盖审计 | `coverage.audit_coverage` | EIE 分母、覆盖率、机器可读缺口原因 |
| 日报排序 | `daily.build_daily_brief` | 去重后的故事线与证据链接 |
| 知识图谱 | `knowledge_graph.build_knowledge_graph` | 节点、typed edges、来源和时间证据 |
| 全链路 | `run.build_domain_run` | 领域底图、采集计划、激活、图谱、日报和运行清单 |

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

## 10. 来源激活与当前边界

来源网络满足角色、EIE、获取路径和历史回放条件后，进入 Source Activation Run。适配器提交 `SourceAcquisitionRun` 和 `EvidenceRecord`，核心生成来源运行状态、窗口内 `DailySignal` 和 `KnowledgeDomainDelta`，然后把信号交给去重、日报排序和后续知识域处理。字段和运行示例见 [`SOURCE_ACTIVATION_RUN.md`](SOURCE_ACTIVATION_RUN.md)。

这一层明确区分四件事：来源可以获取，不等于获得了证据；获得了证据，不等于完成了事实确认；产生了信号，不等于应该进入日报；进入日报，也不等于该来源已经通过历史质量评价。`available_at`、原始 URL、内容哈希和来源角色必须被保留，才能回到当时的证据现场。

当前核心已经实现“领域 seed → 采集计划/公开 HTTP 采集或本地快照 → 内容全文与原始响应 → 证据 → 信号/知识域增量 → 知识图谱/日报”的确定性转换，但仍然没有把外部搜索、数据库、调度器、LLM 语义抽取或邮件推送硬编码进核心。公开 RSS、Atom、JSON、Sitemap、OPML、API 和稳定静态页面可通过 `dib --fetch` 验证；浏览器渲染、登录态和私有凭证仍作为可替换边界适配器接入。它们不能取代领域需求建模、历史回放、来源组合和覆盖审计。`--snapshots` 提供可复现的本地采集边界，便于对真实内容做重复验收。

一次完整运行的交付物不是只有日报：

```text
source-map.json
  → 专家、来源、typed attention edges
content-inventory.json / .md
  → 每个来源入口和内容资产的 captured/failed/blocked 状态
content/
  → 规范化全文 Markdown与原始响应
source-activation.json
  → 运行、证据、信号和知识域增量
knowledge-graph.json
  → domain/topic/element/source/evidence/event/nugget 节点及 typed edges
bootstrap-report.json / .md
  → 来源推荐、历史评价、组合、覆盖缺口
daily-brief.json / .md
  → 本次真实证据经过筛选后的日报
```

`EvidenceRecord.content_ref` 会回指 `content/` 下的规范化全文；`content_hash` 和原始 URL 用于回读与审计。内容捕获成功不等于事实确认，也不等于一定进入日报。

接下来的工程顺序是：

1. 为公开 RSS、Atom、JSON 和稳定静态页面接入适配器，并输出统一运行记录；
2. 保存响应快照、内容哈希、获取时间、失败原因和来源版权边界；
3. 增加事件/EIE 抽取、多源印证和人工确认记录；
4. 增加领域知识域的持久化更新和变更历史；
5. 接入调度、推送与用户反馈；
6. 用真实运行数据补齐候选来源的历史回放，再重算长期组合。
