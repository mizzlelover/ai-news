# 私人情报所：演示站设计契约

这是 `demo/` 面向专业从业者与技术协作者的共同设计契约。演示站不是 AI 新闻仪表盘，也不是把外部 Skill 重新包装成新产品；它要让第一次接触项目的人先理解“为什么需要私人情报所、它如何帮助我”，再决定是否进入技术实现。

## 0. Research Log

### Embedded references

- `gpt-tasteskill.md`：采用 AIDA 顺序、宽阔且可读的主标题、真实视觉锚点、少量有职责的卡片和有意义的动效。
- `stripe.md`：采用浅色纸张画布、深海军蓝文字、紫色与红宝石色作为信号色、保守圆角、8px 间距基线和轻量多层阴影；不复制 Stripe 的品牌、图形或文案。

### Lazyweb research

- 查询：`professional research workspace landing`，桌面端，8 个结果。
- 可复用的布局语法：研究工作区的清晰入口、来源/数据导航、进度式建立流程、编辑部式洞察区域和少量证据卡片。
- 结果中观察到 Dovetail、Hex、Codex research screen、WeWork 等页面的工作区/来源组织方式；只借鉴信息层级和留白，不复制截图、资产或品牌语言。
- 截图下载端点在当前环境中出现超时，因此没有将第三方截图作为设计或仓库资产；视觉判断以现场结果描述和下方 Imagen 概念稿共同校准。

### Imagen concept research

使用内置图像生成工具制作了三个独立的横向概念稿，并逐张检查构图、留白、材质和可实现性：

1. `demo/assets/observatory-hero.png`：右侧为圆形观测孔径、证据卡片和信号弧线，左侧形成大面积深色留白，适合作为首屏背景。
2. `demo/assets/field-notes.png`：领域从业者在地图、笔记、来源卡片前工作，左侧有人的尺度，右侧留白适合解释“从一个专业问题开始”。
3. `demo/assets/aperture-map.png`：俯视的同心孔径、六条信号线和稀疏证据 tile，适合承载方法论的抽象隐喻。

选用第一稿作为 Hero 主视觉，第二稿作为应用场景视觉，第三稿作为方法论章节的视觉背景。图像不承载可读文字，所有方法论标签由 HTML/SVG 原生绘制，以确保中文准确、可访问和可维护。

## 1. Atmosphere and signature

整体气质是“安静、专业、有人在认真判断”，而不是“AI 炫技”。核心视觉隐喻是观测孔径：不同来源的信号并非平铺在页面上，而是经过问题、时间和证据的筛选，汇聚到一个可行动的判断。

签名组件：

1. `aperture mark`：品牌标记由同心圆和一个偏心信号点组成。
2. `signal arc`：用于连接判断、信息要素和来源的细线，不承担装饰性渐变。
3. `editorial brief card`：一张卡只回答一个专业问题，显示信号、来源角色和“为什么现在出现”。
4. `method spine`：横向方法链在桌面端舒展，在移动端变成可滚动的垂直序列。

## 2. Color tokens

所有 UI 颜色必须从以下 token 取值，避免散落的临时颜色：

| Token | Value | 用途 |
| --- | --- | --- |
| `--ink` | `#061B31` | 主要文字、深色 CTA |
| `--ink-soft` | `#36516A` | 次级文字 |
| `--paper` | `#F8F6F1` | 页面主背景 |
| `--paper-strong` | `#FFFCF7` | 卡片和输入面 |
| `--line` | `#D9E0E7` | 分隔线、边框 |
| `--violet` | `#533AFD` | 主强调、交互焦点 |
| `--violet-soft` | `#E7E4FF` | 浅色信号面 |
| `--ruby` | `#EA2261` | 风险/变化/第二强调 |
| `--magenta` | `#F96BEE` | 仅用于深色面上的微弱光晕 |
| `--amber` | `#C58A3A` | 证据时间、暖光点 |
| `--white` | `#FFFFFF` | 深色面反白文字 |

深色段落使用 `--ink` 作为底色，浅色页面使用 `--paper`。渐变只允许出现在 Hero/深色 CTA 的背景氛围中，不用于文字或信息卡片。

## 3. Typography

- 中文显示与正文：`-apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif`。
- 等宽辅助：`"Source Code Pro", "SFMono-Regular", Consolas, monospace`，只用于技术术语、来源角色和状态，不用于大段中文。
- 标题采用轻量字重和紧凑行高；正文保持 1.7 左右行高，避免专业内容变成密集说明书。
- 桌面标题范围 `clamp(2.6rem, 6vw, 6.5rem)`，首屏控制在 2–3 行；移动端标题不低于 `2.35rem`。
- 交互文本最小 14px；正文最小 16px；不依赖极细字体表达层级。

## 4. Spacing and breakpoints

- 基线：8px；常用间距为 8/16/24/32/48/64/96/128px。
- 内容最大宽度：1200px；长文段最大宽度：660px。
- 桌面：`min-width: 1024px`；平板：`640px–1023px`；移动：`max-width: 639px`。
- 每个章节拥有明显的上下呼吸空间；信息卡片之间不使用过密的 bento 拼贴。

## 5. Primitives and states

- `topbar`：品牌、三个锚点、一个主 CTA；滚动后保留半透明纸张面。
- `eyebrow`：使用自然语言短语，如“先从一个判断开始”，不使用无意义的 `SECTION 01`。
- `hero`：深色背景图、宽标题、双入口 CTA、一个可读的日报样例窗。
- `signal-card`：信号标题、证据角色、时间和解释；hover 只发生位移与阴影变化。
- `method-step`：编号、自然语言动作、对应技术名；当前步骤由边框和信号点显示。
- `scenario-selector`：四个可键盘操作的领域场景，选中后同步更新日报样例。
- `evidence-card`：显示“发生了什么 / 为什么重要 / 下一步查什么”，不伪造外部实时数据。
- `coverage-gap`：诚实展示系统不知道什么，避免把“覆盖率”包装成自信分数。
- `cta-band`：深色、明确的下一步，链接到 demo/方法论/仓库三类路径。

状态必须包括默认、hover/focus、selected、disabled（仅在必要时）和 reduced-motion。焦点态使用可见的 `outline`，不可只靠颜色区分。

## 6. Motion and interaction

- 进入视口：`opacity` + `transform: translateY()`，时长 520ms，分组错峰最多 80ms。
- hover：卡片最多 `translateY(-4px)`；信号点最多 `scale(1.05)`；不动画布局尺寸。
- 场景选择：内容区域用 opacity 淡入与小幅位移切换，立即更新 `aria-live` 文本。
- 方法链：进入视口后信号线渐显，表示信息从问题流向判断；不做持续旋转或自动播放。
- 所有动效只使用 GPU 友好的 `transform`、`opacity`、必要时的 `filter`；`prefers-reduced-motion: reduce` 下关闭位移与延迟，保留清晰的状态变化。
- 不引入动效库：当前静态演示只需要 CSS transition 和 IntersectionObserver，避免为营销页增加运行时成本。

## 7. Depth and material

使用纸张、玻璃和深色桌面三种材质：浅色页面以纸张纹理和细边框建立层次，深色 Hero 以摄影背景和暗色蒙版承载空间感。阴影使用低对比蓝灰色多层阴影；圆角以 4px/8px 为主，不使用满屏胶囊化容器。

## 8. Audience and accessibility constraints

主要 persona：

- 专业领域负责人：需要长期盯住政策、项目、竞争、供应链或技术变化，但不想先学会搭建数据工程。
- 研究/内容工作者：需要知道哪些来源值得跟、哪些变化值得写，不满足于一堆链接。
- 普通行业从业者：只有一个现实判断要做，希望从一句话开始，而不是面对一套黑话配置表。
- 工程协作者：希望看到可复用的模型、边界、数据结构和来源归属，能把采集器接入自己的系统。

约束：

- 首屏必须在不懂代码的情况下完成理解：用户是谁、痛点是什么、下一步点哪里。
- 所有图片都有替代文本；方法论图示不把关键信息藏在图片里。
- 场景选择器使用真实按钮、可见焦点和 `aria-pressed`；日报动态内容用 `aria-live="polite"`。
- 颜色对比按普通文本 4.5:1 目标设计；不使用 emoji 作为图标。
- HTML 保持语义章节、标题层级和跳转锚点；移动端不依赖 hover 才能发现核心信息。

## 9. Accepted debt and review evidence

- 当前仓库根目录的 AI News Radar 页面属于保留的兼容适配层，本次不把它改造成主产品；通过顶部入口、README 和来源说明明确分层。
- 演示站使用静态示例数据，不宣称实时情报；真实采集和推送仍由可替换适配器接入核心引擎。
- 首版不引入账号、后端或在线配置向导；目标是让用户理解方法并能进入工程，而不是在演示站伪装成完整 SaaS。
- 视觉验收记录在发布前补入本节，必须包含 375/768/1280 三个宽度、场景切换、锚点跳转和 reduced-motion 结果。
