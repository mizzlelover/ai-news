# 私人情报所：演示站与运行工作台设计契约

这是 `demo/` 面向领域使用者与技术协作者的共同设计契约。公开演示站不是 AI 新闻仪表盘，也不以外部 Skill 代替核心方法论；运行工作台则负责把一次真实运行的过程和产物放在同一处，让使用者可以看见“领域如何展开、来源如何激活、全文如何归档、证据如何进入日报”。

## 0. Design references

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
2. `demo/assets/field-notes.png`：领域从业者在地图、笔记、来源卡片前工作，左侧有人的尺度，右侧留白适合解释“从一个领域关键词开始”。
3. `demo/assets/aperture-map.png`：俯视的同心孔径、六条信号线和稀疏证据 tile，适合承载方法论的抽象隐喻。

选用第一稿作为 Hero 主视觉，第二稿作为应用场景视觉，第三稿作为方法论章节的视觉背景。图像不承载可读文字，所有方法论标签由 HTML/SVG 原生绘制，以确保中文准确、可访问和可维护。

## 1. Atmosphere and signature

整体气质是“安静、专业、有人在认真建立认知”，而不是“AI 炫技”。核心视觉隐喻是观测孔径：一个领域先被展开成地图，随后不同来源的信号再经过主题、时间和证据的筛选，汇聚到可行动的判断。

签名组件：

1. `aperture mark`：品牌标记由同心圆和一个偏心信号点组成。
2. `signal arc`：用于连接领域、信息要素和来源的细线，不承担装饰性渐变。
3. `editorial brief card`：一张卡只承载一个领域变化，显示所属观察面、来源角色和“为什么现在出现”；具体问题追踪是后续层。
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
| `--magenta` | `#F96BEE` | 深色面上的微弱光晕、浅色面上的强调 |
| `--magenta-light` | `#FFB1F8` | 紫色背景上的大字号强调文字，满足可读性门槛 |
| `--amber` | `#C58A3A` | 证据时间、暖光点 |
| `--white` | `#FFFFFF` | 深色面反白文字 |
| `--reading-hero-mid` | `#102B49` | 阅读室 Hero 渐变中间停点 |
| `--reading-hero-deep` | `#271A63` | 阅读室 Hero 渐变深处停点 |
| `--workbench-hero-mid` | `#102B49` | 运行工作台 Hero 渐变中间停点 |
| `--workbench-hero-deep` | `#271A63` | 运行工作台 Hero 渐变深处停点 |
| `--workbench-sidebar-width` | `232px` | 桌面端工作台导航宽度 |
| `--workbench-topbar-height` | `72px` | 工作台顶部运行上下文高度 |
| `--workbench-content-max-width` | `1440px` | 工作台主内容最大宽度 |
| `--workbench-panel-radius` | `8px` | 工作台面板圆角 |
| `--workbench-panel-padding` | `24px` | 工作台面板内边距 |
| `--workbench-grid-gap` | `16px` | 工作台卡片网格间距 |
| `--workbench-drawer-width` | `min(720px, 92vw)` | 全文与证据抽屉宽度 |
| `--workbench-nav-icon-size` | `20px` | 工作台导航线性图标尺寸 |

工作台的布局、字号和响应式边界也必须先声明为 token，再在组件规则中引用。关键契约如下：

| Token | Value | 用途 |
| --- | --- | --- |
| `--workbench-context-max-width` | `270px` | 顶部运行上下文名称最大宽度 |
| `--workbench-title-max-width` | `760px` | 工作台 Hero 标题最大宽度 |
| `--workbench-view-heading-max-width` | `920px` | 视图标题区最大宽度 |
| `--workbench-view-copy-max-width` | `700px` | 视图说明文字最大宽度 |
| `--workbench-hero-copy-max-width` | `680px` | Hero 主文案最大宽度 |
| `--workbench-hero-lede-max-width` | `620px` | Hero 导语与导入提示最大宽度 |
| `--workbench-art-card-min-width` | `112px` | Hero 结构卡片最小宽度 |
| `--workbench-graph-table-min-width` | `760px` | 图谱清单表格最小宽度 |
| `--workbench-graph-inventory-max-height` | `720px` | 图谱清单滚动区最大高度 |
| `--workbench-source-table-min-width` | `720px` | 信源清单表格最小宽度 |
| `--workbench-source-endpoint-max-width` | `240px` | 信源入口列最大宽度 |
| `--workbench-section-title-size` | `clamp(1.5rem, 2.6vw, 2.25rem)` | 工作台区块标题 |
| `--workbench-panel-title-size` | `clamp(1.35rem, 2vw, 1.8rem)` | 面板标题 |
| `--workbench-drawer-title-size` | `clamp(1.35rem, 3vw, 2rem)` | 全文抽屉标题 |
| `--workbench-mobile-art-min-height` | `250px` | 移动端 Hero 结构预览高度 |
| `--workbench-mobile-metric-min-height` | `118px` | 移动端指标卡最小高度 |
| `--workbench-mobile-graph-min-height` | `330px` | 移动端图谱区最小高度 |
| `--workbench-mobile-drawer-title-size` | `1.4rem` | 移动端抽屉标题 |

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
- `eyebrow`：使用自然语言短语，如“先从一个领域开始”，不使用无意义的 `SECTION 01`。
- `hero`：深色背景图、宽标题、双入口 CTA、一个可读的日报样例窗。
- `signal-card`：信号标题、证据角色、时间和解释；hover 只发生位移与阴影变化。
- `method-step`：编号、自然语言动作、对应技术名；当前步骤由边框和信号点显示。
- `domain-entry`：一个低门槛的领域输入入口，允许只提交行业、产业、细分领域或关键词，并用示例切换验证展开结果。
- `evidence-card`：显示“发生了什么 / 为什么重要 / 下一步查什么”，不伪造外部实时数据。
- `coverage-gap`：诚实展示系统不知道什么，避免把“覆盖率”包装成自信分数。
- `cta-band`：深色、明确的下一步，链接到 demo/方法论/仓库三类路径。
- `reading-room`：把使用者指南、核心方法、工程入口和来源边界放进同一套 HTML 阅读层；演示站不把 `.md` 文件作为使用者阅读入口。
- `workbench-shell`：运行上下文、导航、产物面板和阅读抽屉组成可复核的工作区，不把 JSON 文件路径当成用户入口。
- `status-matrix`：把 captured、failed、blocked、evidence 和 story 分开显示，状态只靠文字与颜色共同表达。
- `graph-stage`：用可缩放的 SVG 关系层呈现领域、来源和证据之间的结构，同时保留可读的列表视图。
- `content-drawer`：从内容清单打开规范化全文，并显示原始响应、哈希、证据引用和来源入口。

状态必须包括默认、hover/focus、selected、disabled（仅在必要时）和 reduced-motion。焦点态使用可见的 `outline`，不可只靠颜色区分。

## 6. Motion and interaction

- 进入视口：`opacity` + `transform: translateY()`，时长 520ms，分组错峰最多 80ms。
- hover：卡片最多 `translateY(-4px)`；信号点最多 `scale(1.05)`；不动画布局尺寸。
- 领域示例切换：内容区域用 opacity 淡入与小幅位移切换，立即更新 `aria-live` 文本；自定义领域也必须给出可读的通用展开结果。
- 方法链：进入视口后信号线渐显，表示信息从领域底图流向具体问题与判断；不做持续旋转或自动播放。
- 所有动效只使用 GPU 友好的 `transform`、`opacity`、必要时的 `filter`；`prefers-reduced-motion: reduce` 下关闭位移与延迟，保留清晰的状态变化。
- 不引入动效库：当前静态演示只需要 CSS transition 和 IntersectionObserver，避免为营销页增加运行时成本。

## 7. Depth and material

使用纸张、玻璃和深色桌面三种材质：浅色页面以纸张纹理和细边框建立层次，深色 Hero 以摄影背景和暗色蒙版承载空间感。阴影使用低对比蓝灰色多层阴影；圆角以 4px/8px 为主，不使用满屏胶囊化容器。

## 8. Audience and accessibility constraints

主要 persona：

- 领域使用者：可能正在进入一个新行业，也可能只是还没有建立领域底图；他可以只给出一个行业、产业、知识域或细分领域名称，不必先知道该看谁、该信谁或该提出什么问题。
- 专业领域负责人、研究/内容工作者：是文旅、制造、教育、农业、医疗、能源等现场中的具体使用者，不单独包装成第二套产品入口。
- 工程协作者：负责把领域知识域接入采集、历史回放、更新、推送和审计系统，但不应成为使用者的第一道门槛。

约束：

- 首屏必须在不懂代码的情况下完成理解：只要给出一个领域，私人情报所会先建立什么、解决什么起点问题、下一步点哪里。
- 页面必须明确：已经能够独立配置信源、搭建日报并维护知识引擎的人不是主要目标用户；工程入口属于支持层，不得压过领域知识域的构建主线。
- 所有图片都有替代文本；方法论图示不把关键信息藏在图片里。
- 领域示例使用真实按钮、可见焦点和 `aria-pressed`；领域展开结果用 `aria-live="polite"`。
- 颜色对比按普通文本 4.5:1 目标设计；不使用 emoji 作为图标。
- HTML 保持语义章节、标题层级和跳转锚点；移动端不依赖 hover 才能发现核心信息。
- `demo/styles.css` 统一暴露间距、字号、字重、圆角和控件高度令牌；页面组件优先消费令牌，避免各区块各自定义同一套尺寸。
- 组件级尺寸令牌继续从基础间距、字号、圆角和控件令牌组合而来；导航、Hero、领域入口、领域结果卡和方法链不得重新散落一套像素值。
- `demo/reading.css` 的阅读室专用尺寸、断点内变体和渐变停点必须先声明为 `--reading-*` 令牌，再由组件规则消费；这使阅读室继续共享同一套设计契约，而不是形成孤立页面。

## 9. Product boundary and acceptance

- AI News Radar 阅读界面和采集适配器属于独立的边界参考；私人情报所的公开产品面是演示站、阅读室和运行工作台。
- 演示站继续使用静态示例数据，不宣称实时情报；`workbench.html` 是本地运行产物的可视化阅读与复核界面，支持直接导入一次 `run` 目录。
- 当前不引入账号、远程数据库或在线配置向导；领域构建仍由 Skill、核心引擎和可替换采集器完成，工作台负责把过程和结果组织给使用者看。
- 演示站的 CTA、输入框和状态必须明确指向“查看/预览演示”；不得用“开始搭建”“生成结果”“正在建立”等文案让使用者误以为页面会实时调用 AI、检索互联网或生成领域情报。实际运行路径应明确指向核心 Skill 与引擎说明。

### Acceptance checks

- 在 375×900、768×1024、1280×900 三个视口下，领域入口、展开结果和移动端纵向布局应保持可见且没有横向溢出。
- 根首页应进入 `/demo/`；演示站的“为什么需要它”“看领域演示”“它怎么展开”和 CTA 锚点应能定位到对应章节。
- 所有指向领域入口的公开 CTA 都应说明这是静态交互演示；输入或选择领域只切换预设结果，页面应同时提供进入实际运行说明的路径。
- 默认输入为“数字文旅产业”；领域示例按钮应同步更新领域名称、地图、人物/机构、信源和知识引擎；任意非空关键词也应给出通用底图结果。
- 浏览器控制台不应出现 error 或 warning；`prefers-reduced-motion` 下内容应直接可见。
- `reading.html` 应在移动端、平板和桌面端可访问，目录锚点应能定位到使用者、方法、工程和归属四个区块，页面不应有 Markdown 直链或横向溢出。
- `workbench.html` 在 375px、768px、1280px 下均可访问；导入一个真实运行目录后，概览、知识图谱、信源网络、内容清单、全文抽屉、证据链和日报都必须能从同一份产物数据渲染。
- 工作台不能把 endpoint capture 当成 evidence；内容清单必须同时显示 captured/failed/blocked，全文入口必须能定位到 `content/` 下的规范化文件，日报卡片必须能回到对应证据和全文。
- 未导入真实运行目录时，工作台必须明确显示“演示运行”，不能把内置示例冒充用户真实运行。
