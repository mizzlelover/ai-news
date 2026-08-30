# 私人情报所演示站

这是仓库的面向使用者的产品入口，展示“私人情报所”为什么存在、适合谁、如何从一个专业判断开始，以及同一套方法如何落到文旅、制造、教育和个人专业现场。

演示站不把外部 AI News Radar 页面或伯乐 Skill 当成产品主体。它使用仓库内的三张内置生成视觉资产，方法论流程和动态场景选择器由 HTML、CSS 和 JavaScript 原生实现，方便在 GitHub Pages 上直接访问、审阅和继续修改。

## 本地预览

在仓库根目录启动静态服务器：

```bash
python3 -m http.server 8080
```

打开 <http://127.0.0.1:8080/demo/>。

## 页面入口

- `index.html`：页面结构、SEO 元数据、结构化数据和面向使用者的叙事；
- `styles.css`：设计 token、响应式布局、材质、状态和 reduced-motion；
- `app.js`：场景选择器、键盘操作、动态简报和滚动显现；
- `assets/`：本项目为演示站生成的 Hero、工作现场和方法孔径视觉资产。

## 内容边界

页面中的文旅、制造、教育和普通专业现场均为说明方法的示例，不代表实时采集结果。真实来源、历史回放、覆盖审计和推送需要从核心引擎与用户自己的采集适配器接入。

AI News Radar、伯乐 Skill 和原有静态日报页面属于明确标注来源的兼容适配层，来源与版权见 [`../NOTICE.md`](../NOTICE.md) 和 [`../docs/PROJECT_SCOPE_AND_ATTRIBUTION.md`](../docs/PROJECT_SCOPE_AND_ATTRIBUTION.md)。
