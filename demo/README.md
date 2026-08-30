# 私人情报所演示站

这是仓库唯一的面向使用者的产品入口。它解释私人情报所为什么存在、服务哪些专业领域从业者、如何从一个现实判断开始，以及同一套方法如何落到文旅、制造、教育和个人专业现场。

演示站不把任何现成 AI 日报页面或外部 Skill 当成产品主体。页面中的场景、信号和人物均为说明方法的示例，不代表实时采集结果；真实来源、历史回放、覆盖审计和推送需要从核心引擎与用户自己的采集适配器接入。

旧的 AI News Reader / AI News Radar 兼容界面已从发布面移除。仓库中仍保留的早期采集脚本、数据和旧 Skill 仅供历史或实验性工程参考，来源与版权见 [../NOTICE.md](../NOTICE.md) 和 [../docs/PROJECT_SCOPE_AND_ATTRIBUTION.md](../docs/PROJECT_SCOPE_AND_ATTRIBUTION.md)。

## 本地预览

在仓库根目录启动静态服务器：

~~~bash
python3 -m http.server 8080
~~~

打开 http://127.0.0.1:8080/demo/。

## 页面组成

- index.html：页面结构、SEO 元数据、结构化数据和面向使用者的叙事；
- styles.css：设计 token、响应式布局、材质、状态和 reduced-motion；
- app.js：场景选择器、键盘操作、动态简报和滚动显现；
- assets/：本项目演示站使用的 Hero、工作现场和方法流程视觉资产。
