# 智慧文旅信源接入判断（2026-07-01）

依据：用户附件《智慧文旅高价值信源清单（100个）》、本地 OPML 探针、项目 `Source Intake Reference`。

## 结论

- 默认自动化先接入 `feeds/wisdom-tourism.opml`，只放已验证可解析的 RSS/Atom 源。
- 非 RSS 网站、X 账号、微信公众号、播客、研究报告页、工具页不直接放默认 OPML。
- GitHub Actions 默认 `RSS_MAX_FEEDS` 已从 10 调到 40，避免只抓前 10 个 OPML 源。

## 直接接入

这些源已进入 `feeds/wisdom-tourism.opml`，本地探针返回 200 且能解析条目：

| 信源 | 接入方式 | 探针结果 |
|---|---|---|
| Skift | OPML/RSS | 200，10 条 |
| LODGING Magazine | OPML/RSS | 200，10 条 |
| Hotel Management | OPML/RSS | 200，10 条 |
| 36氪 | OPML/RSS | 200，30 条 |
| 虎嗅 | OPML/RSS | 200，115 条 |
| 钛媒体 | OPML/RSS | 200，17 条 |
| 界面新闻 | OPML/RSS | 200，30 条 |
| IT之家 | OPML/RSS | 200，60 条 |
| 爱范儿 | OPML/RSS | 200，20 条 |
| 少数派 | OPML/RSS | 200，10 条 |
| 品橙旅游 | OPML/RSS | 200，10 条 |
| 国家统计局 数据解读 | OPML/RSS | 200，500 条 |
| 国务院 政策文件 | OPML/RSS | 200，60 条 |
| Travel Tech Essentialist | OPML/RSS | 200，20 条 |
| That Newsletter: Hospitality, Travel & Tech | OPML/RSS | 200，20 条 |
| China Travel and Transport | OPML/RSS | 200，17 条 |

## 应进入 OPML 但暂缓

这些源理论上属于 OPML/RSS，但本地探针显示不可稳定解析，先不放默认文件：

| 信源 | 附件 URL | 当前判断 | 后续处理 |
|---|---|---|---|
| PhocusWire | `https://www.phocuswire.com/feed` | 返回 403 | 试 Jina 或站点解析 |
| Hospitality Net | `https://www.hospitalitynet.org/rss` | 返回 403 | 试 Jina 或站点解析 |
| 品玩 | `https://www.pingwest.com/feed/all` | 200 但 0 条 | 查找替代 feed |
| 环球旅讯 | `https://www.traveldaily.cn/rss` | 200 但 0 条 | 查找替代 feed 或站点解析 |
| Travel Weekly、Travel Weekly Asia、TTG Asia、TravelPulse、TravelMole、eHotelier、Travel & Hospitality Tech Outlook | 官网 URL | 附件标为网站/RSS或网站，但未给稳定 feed URL | 先做 feed discovery，再决定 OPML |
| China Innovation Watch (Tourism) | `https://www.ciw.news/t/tourism` | 可能有 newsletter/feed，但未验证 | 后续探针验证 |

## 需要 Jina 兜底

适合用 `https://r.jina.ai/http://example.com/...` 或直接 HTML 解析兜底的，是公开网页但没有稳定 RSS、或 RSS 被 403 的源：

| 信源 | 原因 |
|---|---|
| PhocusWire、Hospitality Net | feed 被 403，公开页面可能可读 |
| Hotel Tech Report、环球旅讯英文版、中国旅游新闻网、中国旅游网、中国旅游饭店业协会 | 公开网页价值高，但未发现稳定 RSS |
| 文化和旅游部、文化和旅游部 数据服务、中国旅游研究院、中国旅游研究院 数据中心、中国旅游协会 | 政策/数据源需要页面结构化，不能靠 OPML |
| 新华网 文旅频道、复旦数字文化保护实验室、北京二外 文旅产业研究院 | 公开网页，适合做定向页面解析 |
| UN Tourism 数据平台、WTTC 研究报告、PATA、Phocuswright Research、Amadeus Travel Trends、McKinsey 旅游洞察、STR/CoStar、UNESCO 世界遗产、Dragon Trail 中国洞察 | 报告/洞察页适合低频页面监控，不宜高频 RSS |
| Annals of Tourism Research、Journal of Sustainable Tourism、Tourism Management、旅游学刊 | 学术页适合低频目录/DOI监控，日报默认流先不接 |

## 需要以后用私有集成处理

这些源需要 API、账号、桥接服务或私有订阅，不能直接写入公开仓库：

| 类型 | 信源 |
|---|---|
| X 账号 | @skift、@phocuswire、@UNWTO、@WTTC、@phocuswright、@mauricioprieto、@hoteltechreport、@rafat、@travelweekly、@traveldailycn |
| 微信公众号 | 文旅之声、文旅中国、环球旅讯、迈点、新旅界、执惠、品橙旅游、闻旅、空间秘探、劲旅网、酒店高参、腾讯文旅、中国旅游报、敦煌智慧旅游官方、文化产业评论、主题公园界、旅游产业观察、中国旅游饭店业协会 |
| Newsletter/邮件订阅 | Hotel Tech Insider、Travel Tech Passport、Dragon Trail 月报、The Travel Wire、Skift Daily Lodging Report、China Trading Desk |
| 播客 | 数字文旅宇宙、闲谈文旅、文旅红星、十分吸引、天字壹号房、文旅圈内人、博物志、非遗轻创 |
| 工具/桥接 | RSSHub 自建实例、Follow App 公开列表、Kill the Newsletter、今天看啥（微信转RSS） |

## 不适合直接接入默认日报

这些不是内容源本身，或会引入账号/版权/稳定性风险：

| 信源 | 原因 |
|---|---|
| RSSHub 自建实例 | 是基础设施，不是具体内容源；适合作为后续桥接方案 |
| Kill the Newsletter | 是邮件转 RSS 工具；只在用户拥有订阅邮箱时使用 |
| 今天看啥（微信转RSS） | 微信桥接服务，稳定性和合规边界需单独确认 |
| Follow App 公开列表 | 应先导出具体 OPML，而不是抓应用首页 |
| STR/CoStar 酒店数据 | 商业数据服务，公开页不等于可抓取数据 |

## 后续私有集成建议

1. X：用 `SOCIALDATA_LIST_ID` 或官方 `X_BEARER_TOKEN` 建文旅账号列表，密钥只放 GitHub Secrets。
2. 微信：先用“今天看啥”或自建 RSSHub 生成个人可用 feed，再放入 `FOLLOW_OPML_B64`，不要提交到仓库。
3. Newsletter：用邮件转 RSS 或 AgentMail，白名单域名，摘要脱敏后再发布。
4. 网站/Jina：对政策、智库、报告页写低频 fetcher，记录失败状态，避免阻塞主流程。
