# 私人情报所

## Private Intelligence Observatory

**给我一个领域。私人情报所帮你把这个领域应有的知识体系与情报体系搭起来，再让它持续更新。**

[![Private Intelligence Observatory CI](https://github.com/mizzlelover/private-intelligence-observatory/actions/workflows/domain-intelligence.yml/badge.svg)](https://github.com/mizzlelover/private-intelligence-observatory/actions/workflows/domain-intelligence.yml)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)

[先看演示站](https://mizzlelover.github.io/private-intelligence-observatory/demo/) · [运行工作台](https://mizzlelover.github.io/private-intelligence-observatory/demo/workbench.html) · [可视化阅读室](https://mizzlelover.github.io/private-intelligence-observatory/demo/reading.html) · [数字孪生真实验收记录](docs/VERIFICATION_DIGITAL_TWIN.md) · [使用者指南](docs/PRIVATE_INTELLIGENCE_FOR_PRACTITIONERS.md) · [核心方法论](docs/DOMAIN_INTELLIGENCE_V0_1.md) · [来源规模与激活规则](docs/SOURCE_PORTFOLIO_SCALE.md) · [来源激活运行](docs/SOURCE_ACTIVATION_RUN.md) · [领域情报引擎](packages/domain-intelligence/README.md) · [项目范围与来源/版权](docs/PROJECT_SCOPE_AND_ATTRIBUTION.md) · [NOTICE](NOTICE.md) · [English](README.en.md)

---

## 这不是又一个 AI 日报项目

现在网上的 AI 助手、日报和知识引擎，大多围绕 AI 从业者自己的信息需求搭建。做文旅、制造、教育、农业、医疗、能源、城市建设，或其他专业工作的用户，同样需要持续掌握政策、项目、技术、竞争、供应链和市场变化，却很少有人帮他们把这件事做成一套能长期运行的机制。

真正的断层，不只是“有没有工具”，而是最需要这套能力的人往往还没有进入情报工作的起点：他不知道这个领域由什么组成，不知道该看谁、该信谁，也不知道应该先提出什么问题。现成的 AI 工具通常从“提问、配置信源或订阅日报”开始，却把最关键的领域底图留给使用者自己摸索。

**私人情报所把入口收敛成一件事：你只要给出一个领域，它就帮你把这个领域应有的知识体系与情报体系搭起来。**你可以输入“数字文旅产业”“机器人产业”或任何一个专业领域。系统先展开领域边界、词典、观察面、人物与机构、专家、信源角色、证据和知识缺口，再接上日报、推送与知识引擎。尤其适合刚进入一个领域、还不知道该看谁和该信谁的人。

你已经有的专家、网站、报告或项目材料，不需要在入口处整理成一套配置；之后直接告诉 AI 把它们加入这个领域即可。它们是对领域底图的补充，不是开始使用的前提。

已经能够独立使用 AI 配置信源、搭建日报并维护知识引擎的人，不是本项目的主要目标用户；他们可以借鉴工程实现，但不构成私人情报所要解决的核心矛盾。

日报、网页和推送只是交付形式。真正的产品是方法论：先建立领域边界、人物与专家、来源角色和证据结构，验证哪些来源过去有效、目前还缺什么，再把这些信息用于下一步判断。

## 核心方法论

~~~text
Domain Seed
→ Domain Map / Vocabulary / Participants
→ Intelligence Requirement Graph
→ Essential Information Elements
→ Expert Attention Reconstruction
→ Point-in-time Source Benchmark
→ Source Portfolio
→ Source Activation / Evidence Records
→ Knowledge-domain Delta
→ Coverage Audit
→ Domain-ranked Daily Brief
→ Focused Watch / 人工反馈
~~~

它先把“我只知道一个领域”变成一张可持续扩展的底图，再把其中的方向变成可审计的问题：

- 这个领域由哪些板块、参与者、术语和业务链组成？
- 哪些人物、机构、项目和资料正在定义或改变这个领域？
- 哪些信息要素必须长期掌握，哪些来源分别承担确认、解释、发现和反馈？
- 如果我已经有具体判断，它需要什么 PIR 和 EIE？
- 哪些专家、机构、论文、项目和事件能暴露早期信号？
- 一个来源在当时是否真的可获得，过去是否证明过价值？
- 当前组合覆盖了什么，仍然不知道什么？
- 每日简报是否保留证据、时间和下一步查证路径？

因此，同一套工程可以服务机器人、数据要素、文旅、网络安全、教育、农业或任何新领域；每个领域都从自己的 Domain Seed 开始，再逐步形成决策目的、信息要素和观察规则，而不是把 AI 领域的栏目和阈值直接复制过去。

## 私人情报所必须有规模化来源网络

私人情报所不是“二十几条链接加一份日报”。一个领域要真正形成情报网络，至少要同时观察标准与政策、研究与专家、项目采购与交付、平台与厂商、开源生态以及 Newsletter、播客、媒体和社区等早期信号层。

这套“先起量、再回放、后激活”的规则写在[来源规模与激活规则](docs/SOURCE_PORTFOLIO_SCALE.md)中。具体领域的来源网络、历史证据和本地采集快照属于一次运行的工作数据，不作为仓库里的产品代码或公开样例提交。

## 从一个领域开始

你可能只知道一个行业、产业、知识域或细分方向的名字，完全不知道从哪里开始，也不知道哪个专家值得信、哪个来源值得长期跟。打开[演示站](https://mizzlelover.github.io/private-intelligence-observatory/demo/)，输入一个领域关键词，例如“数字文旅产业”，查看一个领域如何从关键词展开为领域底图、观察面、参与者、专家和信源。这里是静态交互演示，不会实时联网调研或生成真实日报；要实际建立领域知识域，请按[面向领域使用者的指南](docs/PRIVATE_INTELLIGENCE_FOR_PRACTITIONERS.md)进入核心 Skill 与引擎。

在实际运行中完成领域底图后，你可以把已有的专家、网站、报告或项目材料直接告诉 AI，请它们加入这个领域；也可以进一步提出一个判断，建立 Focused Watch。两者都是底图之后的补充动作，不会改变“先给出一个领域”的入口。

### 如果你是工程协作者

从[领域情报引擎](packages/domain-intelligence/README.md)和[核心 Bootstrap Skill](skills/domain-intelligence-bootstrap/SKILL.md)开始。引擎负责 EAR、历史截点回放、信源组合、来源激活、证据转换、覆盖审计和领域日报排序；采集器、数据库、邮件、推送和网页属于可替换的边界适配器。工程实现的任务，是把从领域开始建立的知识体系可靠地更新和交付给使用者。

最小可运行示例：

~~~bash
uv run --project packages/domain-intelligence dib \
  packages/domain-intelligence/examples/data-elements.json \
  --output-dir out/domain-intelligence
~~~

完整领域运行使用 Skill 生成的本地 seed Bundle。领域名称是使用者唯一需要提出的领域输入；Bundle 和快照目录由本地运行保存，不提交到 GitHub：

~~~bash
uv run --project packages/domain-intelligence dib \
  --domain "你的领域" \
  --bundle /path/to/local/domain-seed.json \
  --snapshots /path/to/local/snapshots \
  --output-dir /tmp/private-intelligence-run
~~~

如果要在本机直接验证公开来源的真实内容采集，可以使用内置的公开 HTTP 适配器：

~~~bash
uv run --project packages/domain-intelligence dib \
  --domain "你的领域" \
  --bundle /path/to/local/domain-seed.json \
  --fetch \
  --snapshots /path/to/local/capture \
  --output-dir /path/to/local/run
~~~

`--fetch` 会尝试采集已配置且允许公开获取的来源入口，并把规范化全文、原始响应、内容哈希、失败原因和证据引用写入本地；HTML、JSON、RSS/Atom 和 PDF 入口有对应的内置文本归档边界。`--snapshots` 不带 `--fetch` 时仍然是可复现的本地快照回放；需要浏览器渲染、登录态或私有凭证的来源会明确保留为 blocked/failed，不会被伪装成已采集。

运行会生成 `domain-profile.json`、`source-map.json`、`acquisition-plan.json`、`source-activation.json`、`knowledge-graph.json`、日报 JSON/Markdown、Bootstrap 报告和 `run-manifest.json`。当本次运行有内容时，还会生成 `content-inventory.json`、`content-inventory.md` 和 `content/` 全文/原始响应目录。`content-inventory` 是“来源入口/内容资产/证据”的索引：只有带 `evidence_id` 的内容才会进入 Evidence、知识图谱和日报；仅成功抓到的静态介绍页会保留在全文库，但不会自动变成日报新闻。

### 用运行工作台查看全部产物

运行完成后，打开[运行工作台](https://mizzlelover.github.io/private-intelligence-observatory/demo/workbench.html)，先在“运行管理”页查看当前运行和待处理任务，再点击“导入运行目录”选择这次命令生成的输出目录。工作台会把运行总览、知识图谱、信源状态、内容清单、规范化全文、原始响应、证据回链和日报放在同一个可视化入口中；它读取的是你导入的本地文件，顶部显示“已导入”时才代表当前页面正在展示真实运行。

完整操作和回读顺序见[运行工作台说明](docs/WORKBENCH.md)。

## 仓库结构

| 路径 | 作用 |
| --- | --- |
| demo/ | 面向使用者的产品演示、运行工作台、使用场景和方法论图示 |
| docs/PRIVATE_INTELLIGENCE_FOR_PRACTITIONERS.md | 非技术用户的应用层使用指南 |
| docs/DOMAIN_INTELLIGENCE_V0_1.md | 领域情报方法论、指标和边界 |
| docs/SOURCE_PORTFOLIO_SCALE.md | 来源网络规模、分层和激活状态 |
| docs/SOURCE_ACTIVATION_RUN.md | 采集运行、证据记录、日报信号和知识域增量契约 |
| docs/WORKBENCH.md | 导入真实运行目录、查看全部产物与回读证据的使用说明 |
| docs/VERIFICATION_DIGITAL_TWIN.md | 数字孪生真实运行的结果、产物索引和验收记录 |
| packages/domain-intelligence/ | 可运行的领域情报核心引擎和最小 Bundle |
| skills/domain-intelligence-bootstrap/ | 将领域关键词和后续问题路由到核心流程的 Skill |
| DESIGN.md | 演示站的信息架构、视觉系统和验收契约 |
| docs/PROJECT_SCOPE_AND_ATTRIBUTION.md | 项目主次、第三方来源和版权边界 |

## 发布边界与第三方来源

当前发布面是私人情报所演示站、运行工作台与阅读室。AI News Reader / AI News Radar 兼容页面及其专属静态 assets/、site.webmanifest 不属于产品入口。

仓库中保留的 scripts/update_news.py、data/、feeds/、.github/workflows/update-news.yml 以及 skills/ai-news-radar/、skills/radar/，只作为采集或消费适配参考，不是私人情报所的核心方法论，也不是本项目原创的“伯乐 Skill”。相关内容来自或基于 [LearnPrompt/ai-news-radar](https://github.com/LearnPrompt/ai-news-radar)，采用 MIT License；具体目录、版权和再分发边界见 [NOTICE](NOTICE.md) 与[项目范围与来源/版权说明](docs/PROJECT_SCOPE_AND_ATTRIBUTION.md)。

这意味着：成熟的采集轮子可以在边界上复用，但不能替代针对具体行业重新完成的需求建模、历史评价、来源组合和覆盖审计。

## 本地运行与验证

启动演示站：

~~~bash
python3 -m http.server 8080
~~~

然后打开 http://127.0.0.1:8080/demo/。如果已有一次真实运行，打开 http://127.0.0.1:8080/demo/workbench.html 并导入运行目录。

核心引擎测试与格式检查：

~~~bash
uv run --project packages/domain-intelligence pytest -q packages/domain-intelligence/tests
uv run --project packages/domain-intelligence ruff format --check packages/domain-intelligence/src packages/domain-intelligence/tests
uv run --project packages/domain-intelligence ruff check packages/domain-intelligence/src packages/domain-intelligence/tests
~~~

根目录完整测试：

~~~bash
PYTHONPATH=packages/domain-intelligence/src:. uv run --no-project \
  --with pytest --with PyYAML --with requests --with beautifulsoup4 \
  --with feedparser --with python-dateutil pytest -q tests
~~~

## 许可证

本项目采用 MIT License。核心领域情报方法论和工程新增部分归 mizzlelover；仓库中保留的上游采集适配部分保留 [LearnPrompt/ai-news-radar](https://github.com/LearnPrompt/ai-news-radar) 的来源与 Copyright (c) 2026 LearnPrompt 声明。详见 LICENSE、NOTICE.md 和[项目范围与来源/版权说明](docs/PROJECT_SCOPE_AND_ATTRIBUTION.md)。
