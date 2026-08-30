# 项目范围与来源/版权说明

更新时间：2026-08-30

这份说明用于解决一个容易产生误解的问题：本仓库同时保留了一个现成的 AI 日报工程和一套新建设的领域情报方法论。两者可以组合使用，但不是同一个产品，也不能把前者的作者、名称或能力包装成后者的原创成果。

## 1. 项目身份

本项目的正式定位是：**领域情报日报体系（Domain Intelligence Radar）**。

它面向互联网上长期无人系统关注的领域、知识域、行业和产业，核心任务不是“抓更多新闻”，而是把以下闭环工程化：

```text
决策目的
→ 情报需求图
→ 必需信息要素
→ 专家注意力重建
→ 历史截点回放
→ 信源组合优化
→ 覆盖缺口审计
→ 领域日报与推送
→ 人工反馈
```

日报、网页和推送都是输出与交付形态；需求建模、证据时间、信源评价、组合选择和反馈闭环才是本项目的核心价值。

## 2. 本项目新增的核心资产

以下内容构成项目主线，由本仓库作为领域情报项目持续设计和维护：

| 路径 | 作用 |
| --- | --- |
| `docs/DOMAIN_INTELLIGENCE_V0_1.md` | 方法论、指标、边界和下一阶段实验 |
| `packages/domain-intelligence/` | DomainProfile、PIR/EIE、EAR、point-in-time replay、Portfolio、Coverage 和 Daily Brief 引擎 |
| `skills/domain-intelligence-bootstrap/` | 面向新领域建模、回放、组合和审计的核心 Skill 路由 |
| `packages/domain-intelligence/examples/` | 可复现的最小领域 Bundle，不代表某个外部项目的原始数据 |

这些内容不依赖 AI News Radar 才成立。未来可以接入 RSS、数据库、搜索、邮件、企业系统或其他采集器，只要它们能在边界上提供结构化信号和证据时间。

## 3. 可直接复用但不属于核心的方法论层

仓库中以下内容作为**可选兼容适配层**保留：

| 路径/能力 | 在本项目中的位置 | 不能被误读为 |
| --- | --- | --- |
| `skills/ai-news-radar/` | AI 新闻信源判断、录入和静态日报维护适配器 | 本项目的领域情报方法论 |
| `skills/radar/` | 读取公开 AI 日报 JSON 的消费侧适配器 | 通用领域情报引擎 |
| `scripts/update_news.py`、`index.html`、`assets/` | 既有 AI/文旅页面的采集和展示运行时 | 新领域的需求、回测和覆盖内核 |
| `.github/workflows/update-news.yml` | 既有 AI/文旅数据更新任务 | 通用领域情报调度器 |

这些轮子在“公开 AI 日报、RSS/OPML、去重、静态发布”场景下确实可以直接使用，因此没有必要重新制造一个同功能的抓取器。但它们只能作为采集、展示或消费适配器，不能替代本项目针对不同领域重新建立的 PIR、EIE、信源组合和历史评价。

## 4. 外部工程来源

上述 AI News Radar 兼容层来自或基于公开的 [LearnPrompt/ai-news-radar](https://github.com/LearnPrompt/ai-news-radar) 工程保留和适配。上游工程的公开 Skill 文件是 [`skills/ai-news-radar/SKILL.md`](https://github.com/LearnPrompt/ai-news-radar/blob/master/skills/ai-news-radar/SKILL.md)，文件元数据明确将其命名为 `ai-news-radar`，并将其定位为 AI News Radar 的维护 Skill。

因此，本仓库不把 `skills/ai-news-radar/` 称为本项目原创的“伯乐 Skill”，也不把 AI News Radar 的页面、采集器和 Radar Skill 作为本项目的核心成果。相关目录内均放置了就地来源提示，打开这些文件时应先阅读提示和本说明。

## 5. 版权与许可证

上游公开工程的 [`LICENSE`](https://github.com/LearnPrompt/ai-news-radar/blob/master/LICENSE) 为 MIT License，并保留 `Copyright (c) 2026 LearnPrompt` 声明。仓库中的上游兼容层继续保留该来源和许可证要求；再发布或改动这些部分时，不得删除上游版权和 MIT 许可文本。

本仓库根目录 [`LICENSE`](../LICENSE) 同时标明：

- `LearnPrompt`：上游 AI News Radar 兼容层的版权归属；
- `mizzlelover`：本仓库新增领域情报部分的项目版权标识。

项目新增核心文件与上游兼容文件在同一 MIT 许可框架下发布，但来源和归属分层记录。许可证允许复用不等于来源相同，也不等于可以把上游工程宣传为本项目原创。

## 6. 使用边界

- 用户要为一个新领域建立情报体系：先使用 `domain-intelligence-bootstrap`，从决策目的和 EIE 开始。
- 用户需要 AI 新闻采集或公开 AI 日报：可以使用 AI News Radar 兼容层，但应在交付说明中注明上游来源和 MIT 版权。
- 用户要做新的行业、产业或知识域适配：复用采集器的接口可以，不能直接复制 AI 领域的栏目、阈值和“伯乐”叙事作为领域方法。
- 任何日报输出都应保留证据链接、来源角色、可获得时间和覆盖缺口，不以网页数量或单一热度分数宣称完成情报建设。

## 7. 以后如何判断一项新增内容属于哪一层

先问它解决的是哪一个问题：

```text
来源怎么抓、网页怎么发、AI日报怎么读
→ 兼容适配层

这个领域必须知道什么、谁最早知道、来源是否被历史证明有效、组合是否覆盖决策需求
→ 本项目核心方法论
```

如果两者都涉及，先在核心 Bundle 中定义需求和证据，再把适配器接到结构化信号边界上。这样可以继续利用成熟轮子，同时保持本项目的主次和归属清楚。
