# 私人情报所

## Private Intelligence Observatory

**你不必先知道该看谁。给我一个领域，私人情报所帮你把它搭成可持续的情报知识域。**

[![Private Intelligence Observatory CI](https://github.com/mizzlelover/private-intelligence-observatory/actions/workflows/domain-intelligence.yml/badge.svg)](https://github.com/mizzlelover/private-intelligence-observatory/actions/workflows/domain-intelligence.yml)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)

[先看演示站](https://mizzlelover.github.io/private-intelligence-observatory/demo/) · [可视化阅读室](https://mizzlelover.github.io/private-intelligence-observatory/demo/reading.html) · [使用者指南](docs/PRIVATE_INTELLIGENCE_FOR_PRACTITIONERS.md) · [核心方法论](docs/DOMAIN_INTELLIGENCE_V0_1.md) · [领域情报引擎](packages/domain-intelligence/README.md) · [项目范围与来源/版权](docs/PROJECT_SCOPE_AND_ATTRIBUTION.md) · [NOTICE](NOTICE.md) · [English](README.en.md)

---

## 这不是又一个 AI 日报项目

现在网上的 AI 助手、日报和知识引擎，大多围绕 AI 从业者自己的信息需求搭建。做文旅、制造、教育、农业、医疗、能源、城市建设，或其他专业工作的用户，同样需要持续掌握政策、项目、技术、竞争、供应链和市场变化，却很少有人帮他们把这件事做成一套能长期运行的机制。

真正的断层，不只是“有没有工具”，而是最需要这套能力的人往往还没有进入情报工作的起点：他不知道这个领域由什么组成，不知道该看谁、该信谁，也不知道应该先提出什么问题。即使已经在领域里工作的人，手上有一些专业信源，也常常只覆盖自己熟悉的一条线，缺少一张能发现盲区的领域地图。

**私人情报所首先服务两类人：刚进入一个领域、几乎没有知识背景的人；以及已经在领域里，但希望把信源和视野拓宽的人。**两类人的共同目标不是先订一份日报，而是从一个领域关键词开始，把“该知道什么、该看谁、该信什么”逐步搭成自己的领域知识域，再借助工具持续更新、生成日报、推送变化，最后形成可以长期使用的知识引擎。

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

## 给两类使用者的入口

### 第一类，也是最重要的一类：刚进入一个领域的人

你可能只有一个行业、产业或知识域的名字，完全不知道从哪里开始，也不知道哪个专家值得信、哪个来源值得长期跟。先打开[演示站](https://mizzlelover.github.io/private-intelligence-observatory/demo/)，输入一个领域关键词，例如“数字文旅产业”，看它如何从领域底图开始，帮你找到观察面、参与者、专家和信源。再阅读[面向领域使用者的指南](docs/PRIVATE_INTELLIGENCE_FOR_PRACTITIONERS.md)，不必先写专业问题，也不必先学会工具配置。

### 第二类：已经在领域里，但信息覆盖还不够广的人

你已经有一些专业信源、专家或工作材料，只是它们可能集中在熟悉的圈层，难以发现相邻参与者、早期信号和长期缺口。先用[演示站](https://mizzlelover.github.io/private-intelligence-observatory/demo/)建立领域底图，再把已有来源交给[核心方法论](docs/DOMAIN_INTELLIGENCE_V0_1.md)和使用者指南，比较“我已经知道什么”和“这个领域还缺什么”，最后再建立持续更新、日报和 Focused Watch。

这两类入口使用的是同一套方法：先构建想进入或已经身处其中的领域知识域，再把知识域交给工具持续更新。

### 如果你是工程协作者

从[领域情报引擎](packages/domain-intelligence/README.md)和[核心 Bootstrap Skill](skills/domain-intelligence-bootstrap/SKILL.md)开始。引擎负责 EAR、历史截点回放、信源组合、覆盖审计和领域日报排序；采集器、数据库、邮件、推送和网页属于可替换的边界适配器。工程实现的任务，是把领域知识域可靠地更新和交付给前两类使用者，而不是把现成的 AI 日报页面当成产品本身。

最小可运行示例：

~~~bash
uv run --project packages/domain-intelligence dib \
  packages/domain-intelligence/examples/data-elements.json \
  --output-dir out/domain-intelligence
~~~

## 仓库结构

| 路径 | 作用 |
| --- | --- |
| demo/ | 面向使用者的产品演示、使用场景和方法论图示 |
| docs/PRIVATE_INTELLIGENCE_FOR_PRACTITIONERS.md | 非技术用户的应用层使用指南 |
| docs/DOMAIN_INTELLIGENCE_V0_1.md | 领域情报方法论、指标和边界 |
| packages/domain-intelligence/ | 可运行的领域情报核心引擎和最小 Bundle |
| skills/domain-intelligence-bootstrap/ | 将领域关键词和后续问题路由到核心流程的 Skill |
| DESIGN.md | 演示站的信息架构、视觉系统和验收契约 |
| docs/PROJECT_SCOPE_AND_ATTRIBUTION.md | 项目主次、第三方来源和版权边界 |

## 发布边界与第三方来源

旧的 AI News Reader / AI News Radar 兼容界面来源不完整，已从本项目发布面移除。旧页面、页面专属静态 assets/ 和 site.webmanifest 不再是仓库入口，也不再作为演示产品维护；根首页只进入私人情报所演示站。

仓库中仍保留的 scripts/update_news.py、data/、feeds/、.github/workflows/update-news.yml 以及 skills/ai-news-radar/、skills/radar/，只作为历史或实验性的采集工程参考，不是私人情报所的核心方法论、产品首页或“伯乐 Skill”原创成果。相关内容来自或基于 [LearnPrompt/ai-news-radar](https://github.com/LearnPrompt/ai-news-radar)，采用 MIT License；具体目录、版权和再分发边界见 [NOTICE](NOTICE.md) 与[项目范围与来源/版权说明](docs/PROJECT_SCOPE_AND_ATTRIBUTION.md)。

这意味着：成熟的采集轮子可以在边界上复用，但不能替代针对具体行业重新完成的需求建模、历史评价、来源组合和覆盖审计。

## 本地运行与验证

启动演示站：

~~~bash
python3 -m http.server 8080
~~~

然后打开 http://127.0.0.1:8080/demo/。

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
