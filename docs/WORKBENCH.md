# 运行工作台：把一次领域运行的全部产物放到眼前

## 运行工作台是什么

运行工作台是私人情报所的可视化交付面。它不替代领域方法论，也不是一张新的 AI 新闻首页；它把一次真实运行留下的文件组织成一条可阅读、可回链、可复核的路径。

工作台读取的是本地运行目录。它不会把网页演示里的预设数据伪装成实时结果，也不会把“来源入口抓到了”直接包装成“已经形成证据”。打开页面时看到“演示数据”，说明还没有导入运行目录；导入后顶部会变成“已导入”，所有计数和内容来自所选目录。

## 用户能在这里看到什么

| 工作台视图 | 对应运行产物 | 用途 |
| --- | --- | --- |
| 运行管理 | `run-manifest.json`、`source-activation.json`、`content-inventory.json` | 准备下一次领域运行，查看当前运行状态、待处理任务和交付入口 |
| 运行总览 | `run-manifest.json`、`bootstrap-report.json` | 看一次运行的范围、计数、处理层次、覆盖情况和最终交付 |
| 知识图谱 | `knowledge-graph.json`、`knowledge-graph.md` | 看领域、主题、信息要素、来源、证据和事件如何连接 |
| 信源网络 | `source-map.json`、`acquisition-plan.json`、`source-activation.json` | 看来源角色、获取方式、入口、运行状态和证据数量 |
| 内容清单 | `content-inventory.json`、`content/` | 看每个内容结果是已抓取、失败还是阻断，并打开规范化全文与原始响应 |
| 日报与证据 | `daily-brief.json`、`daily-brief.md`、`source-activation.json` | 看哪些故事被推荐、判断分是什么、证据从哪里来，并回到全文 |

## 如何查看一次真实运行

先在本地完成一次领域运行。例如：

```bash
uv run --project packages/domain-intelligence dib \
  --domain "数字孪生" \
  --bundle /path/to/digital-twin-seed.json \
  --fetch \
  --snapshots /path/to/capture \
  --output-dir /path/to/digital-twin-run
```

然后在仓库根目录启动静态服务器：

```bash
python3 -m http.server 8080
```

打开 `http://127.0.0.1:8080/demo/workbench.html`，点击右上角“导入运行目录”，选择上面命令生成的 `digital-twin-run/` 文件夹。

导入时要选择运行目录本身，而不是只选择其中一个 JSON 文件。工作台会读取根目录下的 JSON 产物，并按 `content-inventory.json` 中的 `relative_path` 找到 `content/` 下的规范化全文和原始响应。

为了避免把半套文件误判为完整运行，导入目录必须同时包含 `run-manifest.json`、`domain-profile.json`、`source-map.json`、`acquisition-plan.json`、`source-activation.json`、`knowledge-graph.json`、`bootstrap-report.json`、`daily-brief.json` 和 `content-inventory.json`。缺少其中任一项时，工作台会保留当前状态并提示补齐，不会切换成“已导入”。

工作台还会校验这些 JSON 的基本结构和相互关系：领域名称、来源/内容/证据/故事计数、知识图谱节点端点、覆盖审计行，以及已抓取全文的路径、哈希和字符数。空对象、空的领域底图、计数不一致或无法确认归属的文件不会被标记为“已导入”。导入失败时会保留上一次有效运行，并清空文件选择状态，便于重新选择同一个目录。

## 建议的回读顺序

工作台里的页面顺序就是一次运行的复核顺序：

```text
运行管理
  → 运行总览
  → 知识图谱
  → 信源网络
  → 内容清单 / 打开全文
  → 日报与证据 / 回到全文
```

如果需要直接阅读机器产物或在脚本中继续处理，使用运行目录中的文件：

```text
run-manifest.json
domain-profile.json
source-map.json
acquisition-plan.json
source-activation.json
content-inventory.json / content-inventory.md
content/<normalized>.md 与对应原始响应
knowledge-graph.json / knowledge-graph.md
bootstrap-report.json / bootstrap-report.md
daily-brief.json / daily-brief.md
```

其中有三条关系最值得复核：

1. `content-inventory.json` 的 `relative_path` 是否真实存在，并且 `content_hash` 与全文归档相符；
2. `source-activation.json` 的 `evidence.content_ref` 是否回到了同一条全文；
3. `daily-brief.json` 的 `signal_ids` 和 `evidence_urls` 是否能够回到激活记录与原始来源。

## 运行管理页负责什么

“运行管理”是交付给使用者的控制层，不是一个把后台假装成实时 SaaS 的按钮页。它把一次领域构建拆成五个可观察阶段：领域底图、来源网络、采集与归档、证据与知识域、日报交付；每个阶段都根据导入运行目录中的真实计数显示“已完成”“部分完成”或“待处理”。

页面上的“生成运行指引”会把下一次领域输入整理成可复制的本地执行路径，但不会在浏览器里擅自调用 AI、联网抓取或伪造结果。真正执行完成后，用户把运行目录导入工作台，当前运行、失败/阻断任务和所有交付物就会在同一页面继续管理。

因此，完整部署可以把 Skill 执行器、调度器、采集器和推送服务接到这层控制面；只要它们继续写出本项目的运行产物契约，界面的管理对象仍然是同一条可回看的证据链，而不是另一套只显示“成功”的状态。

## 导入后的状态怎么读

- `已抓取`：已经保存规范化全文和原始响应，可以从内容抽屉打开；
- `失败`：已经尝试获取，但请求、状态码、解析或大小限制没有完成，页面会保留 `error_code`；
- `阻断`：获取方式需要浏览器、登录态、私有凭证或尚未接入适配器，页面会保留阻断原因；
- `已观察`：本次运行已经形成可供激活层使用的证据，不等于所有事实都已经确认；
- `演示数据`：工作台还在说明模式，点击“导入运行目录”后才会显示你的实际运行。

这个界面把“内容资产”“证据记录”“知识域变化”和“日报交付”分开显示。它的价值不是让页面看起来像一个产品，而是让使用者终于能回答：知识图谱在哪里、抓到什么在哪里、全文在哪里、推荐为什么出现、日报依据是什么。

## 工作台的边界

当前工作台以本地导入为默认连接方式，运行数据保留在用户自己的机器上。调度、推送、数据库、登录态和浏览器采集仍然是可替换的边界适配器；它们只要写出同一套运行产物，就可以接入运行管理页。领域情报方法论、领域底图、来源角色、证据时间、覆盖审计和日报排序仍由私人情报所核心引擎负责。
