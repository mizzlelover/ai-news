# 智慧文旅 X 与微信私有源配置指南

本指南用于把附件 100 个信源中的 X 账号和微信公众号接入当前智慧文旅日报。不要把 API Key、cookies、微信桥接后台地址或私人 OPML 直接提交到仓库。

## 1. X 账号

推荐优先使用 SocialData.tools，因为项目已经有适配器，且可以用 X List 控制账号范围。

附件中的 X 账号：

- `@skift`
- `@phocuswire`
- `@UNWTO`
- `@WTTC`
- `@phocuswright`
- `@mauricioprieto`
- `@hoteltechreport`
- `@rafat`
- `@travelweekly`
- `@traveldailycn`

### 方案 A：SocialData.tools，推荐

你需要配合完成：

1. 在 X 上建一个公开或可被 SocialData 读取的 List，把上面 10 个账号加入。
2. 拿到 SocialData API Key。
3. 在 GitHub 仓库 `Settings -> Secrets and variables -> Actions` 中设置：

Secrets：

```text
SOCIALDATA_API_KEY=你的 SocialData API Key
SOCIALDATA_ENABLED=1
```

Variables：

```text
SOCIALDATA_LIST_ID=你的 X List ID
SOCIALDATA_LIST_ENABLED=1
SOCIALDATA_LIST_MAX_RESULTS=50
SOCIALDATA_MAX_RESULTS=20
SOCIALDATA_DAILY_TWEET_LIMIT=70
SOCIALDATA_RUN_INTERVAL_HOURS=12
```

如果你还没有 X List ID，也可以先不设 `SOCIALDATA_LIST_ID`。智慧文旅 profile 会使用文旅关键词搜索，并关闭项目内置的 AI 示例 List。

### 方案 B：官方 X API

你需要配合完成：

1. 准备 `X_BEARER_TOKEN`。
2. 在 GitHub Actions Secrets 设置：

```text
X_BEARER_TOKEN=你的 Bearer Token
X_API_ENABLED=1
```

Variables 可选：

```text
X_API_MAX_RESULTS=20
X_API_DAILY_POST_LIMIT=20
X_API_RUN_UTC_HOUR=0
X_API_RUN_UTC_MINUTE_MAX=10
```

智慧文旅 profile 默认查询上面 10 个 X 账号，并排除转发和回复。

## 2. 微信公众号

项目不能直接抓微信原生公众号。微信必须先由你转换成 RSS，再通过私有 OPML 接入。

附件中的微信公众号：

- 文旅之声
- 文旅中国
- 环球旅讯
- 迈点
- 新旅界
- 执惠
- 品橙旅游
- 闻旅
- 空间秘探
- 劲旅网
- 酒店高参
- 腾讯文旅
- 中国旅游报
- 敦煌智慧旅游官方
- 文化产业评论
- 主题公园界
- 旅游产业观察
- 中国旅游饭店业协会

### 你需要提供的东西

任选一种微信转 RSS 方案：

- 今天看啥生成的 RSS 链接
- 你自建 RSSHub 生成的 RSS 链接
- 其他你能稳定访问的微信公众号 RSS 桥接链接

### 推荐接入方式

1. 复制模板：

```bash
cp feeds/wechat.example.opml /tmp/wisdom-tourism-private.opml
```

2. 把模板里的 `https://example.com/wechat/rss/...` 替换为你真实的微信公众号 RSS 链接。
3. 把现有 `feeds/wisdom-tourism.opml` 中的公开 RSS 源也合并进这个私有 OPML。
4. 转成 base64：

```bash
base64 < /tmp/wisdom-tourism-private.opml | pbcopy
```

5. 在 GitHub Actions Secrets 设置：

```text
FOLLOW_OPML_B64=上一步复制的 base64 内容
```

设置后，GitHub Actions 会优先使用这个私有 OPML；仓库里仍然不会公开你的真实微信桥接链接。

## 3. 验证

配置完成后，手动运行：

```bash
gh workflow run update-news.yml --repo mizzlelover/private-intelligence-observatory --ref master
gh run list --repo mizzlelover/private-intelligence-observatory --limit 5
```

页面状态应看到：

- X 源有 `SocialData X` 或 `X API` 状态
- RSS 健康数增加，微信桥接 RSS 会进入 RSS 明细
- `data/source-status.json` 中能看到失败的具体 RSS 或 API 错误
