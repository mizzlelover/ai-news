# 数字孪生扩展信源矩阵

**私人情报所扩展版 · 2026-08-31**

## 这次扩展解决什么问题

上一版的 24 个入口是领域底图的骨架，不能承担新媒体、自媒体、论文、会议、产品发布、项目采购和行业案例的持续发现。本矩阵新增 **95 个来源入口**，与原有 22 个注意力图源合计 **117 个来源入口**。

这里的“入口”按可独立采集、独立回放和独立记录证据的频道计算。同一机构的标准目录、新闻页、论文检索、Newsletter、播客和 API 可以是不同入口，但不会因此被当作不同的权威机构。机构归属、来源角色和版权边界必须保留。

### 分层统计

| 层级 | 新增入口 |
| --- | ---: |
| 标准与组织 | 12 |
| 中国政策与产业 | 10 |
| 采购与交付 | 3 |
| 研究与学术 | 18 |
| 平台与厂商 | 20 |
| 开源与数据空间 | 12 |
| 媒体与社区 | 20 |
| **新增合计** | **95** |

新增入口中，57 个已进入候选采集面，15 个已有首轮历史观察；其余是发现型入口，必须在实际运行中完成稳定性、重复性、来源偏差和历史价值验证。

## 重要的来源纪律

- official_primary 用来确认标准状态、政策、采购、项目和机构事实；
- expert_interpreter 用来解释架构、术语、研究和行业框架；
- frontier_sensor 用来发现新项目、会议、论文和前沿信号；
- broad_coverage 用来扩大行业覆盖，但不能单独确认关键事实；
- community 用来捕捉播客、Newsletter、开源讨论和专家注意力，默认需要人工复核；
- 厂商页面、商业媒体、LinkedIn 和自媒体不会被伪装成中立来源；它们的角色是发现、解释或提供带立场的案例材料。

## 新增来源清单

| ID | 来源层 | 角色 | 来源名称 | 入口 | 当前状态 | 采集方式 | 用途与边界 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `iso-sc41` | 标准与组织 | official_primary | ISO/IEC JTC 1/SC 41 数字孪生工作组 | [入口](https://www.iso.org/committee/6483279.html) | validated candidate | static_html, stable path | 标准委员会、工作组、范围和公开成果入口。 |
| `iso-sc41-catalogue` | 标准与组织 | official_primary | ISO/IEC JTC 1/SC 41 标准与项目目录 | [入口](https://www.iso.org/committee/6483279/x/catalogue/) | validated candidate | static_html, stable path | 追踪现行标准、在研项目和工作项目状态。 |
| `iso-30173` | 标准与组织 | official_primary | ISO/IEC 30173:2023 数字孪生概念与术语 | [入口](https://webstore.iec.ch/en/publication/68081) | validated + historical replay | static_html, stable path | 术语与概念基线，适合与各国定义对照。 |
| `iso-20924` | 标准与组织 | official_primary | ISO/IEC 20924:2024 物联网与数字孪生词汇 | [入口](https://webstore.iec.ch/en/publication/92254) | validated + historical replay | static_html, stable path | 词汇修订线，注意版本替代关系。 |
| `itu-y4224` | 标准与组织 | official_primary | ITU-T Y.4224 智慧城市数字孪生联邦要求 | [入口](https://www.itu.int/ITU-T/recommendations/rec.aspx?rec=15682) | validated + historical replay | static_html, stable path | 智慧城市跨域数字孪生联邦的标准入口。 |
| `itu-jca-dt` | 标准与组织 | official_primary | ITU JCA-IoT、数字孪生与可持续智慧城市社区 | [入口](https://www.itu.int/en/ITU-T/jca/iot/Pages/default.aspx) | validated candidate | static_html, stable path | 全球标准景观、会议、交付物和关联组织入口。 |
| `ieee-p2806` | 标准与组织 | official_primary | IEEE P2806.1 工厂物理对象数字表示连接要求 | [入口](https://standards.ieee.org/ieee/2806.1/10370/) | validated + historical replay | static_html, stable path | 工厂数字表示的连接、统一数据模型和访问接口项目。 |
| `ieee-p3501` | 标准与组织 | official_primary | IEEE P3501 地球数字孪生开发推荐实践 | [入口](https://standards.ieee.org/ieee/3501/11771/) | validated + historical replay | static_html, stable path | 地球及其子系统数字孪生开发与互操作项目。 |
| `opc-aas` | 标准与组织 | official_primary | OPC UA for Asset Administration Shell | [入口](https://reference.opcfoundation.org/specs/OPC-30270/4) | validated candidate | static_html, stable path | AAS 与 OPC UA 映射、信息模型和互操作实现入口。 |
| `bsi-digital-twins` | 标准与组织 | expert_interpreter | buildingSMART Digital Twins Working Group | [入口](https://www.buildingsmart.org/digital-twins/) | validated candidate | static_html, stable path | 建筑、基础设施和资产全生命周期数字孪生解释与工作组入口。 |
| `bsi-standards` | 标准与组织 | official_primary | buildingSMART openBIM 标准与解决方案 | [入口](https://www.buildingsmart.org/standards/) | validated candidate | static_html, stable path | IFC、IDS、bSDD 等建筑数据标准入口。 |
| `aii-dt-standards` | 中国政策与产业 | expert_interpreter | 工业互联网产业联盟数字孪生标准资料 | [入口](https://www.aii-alliance.org/uploads/1/20231213/2c3e81a5ba962f52ba9349c937309097.pdf) | validated candidate | static_html, stable path | 工业互联网联盟标准和数字孪生模型资料，需保留版本与版权信息。 |
| `cesi-dt-whitepaper` | 中国政策与产业 | expert_interpreter | 中国电子技术标准化研究院《数字孪生应用白皮书（2020年）》 | [入口](https://www.cesi.cn/images/editor/20201118/20201118163619265.pdf) | validated + historical replay | static_html, stable path | 中国数字孪生标准体系早期框架资料。 |
| `ndls-dt` | 标准与组织 | official_primary | 国家数字标准馆数字孪生标准检索 | [入口](https://ndls.cnis.ac.cn/standard/index?draftman=%E7%BC%AA%E7%A5%BA) | validated candidate | static_html, stable path | 国家标准馆检索与标准元数据补充入口。 |
| `cics-industrial-standard` | 中国政策与产业 | official_primary | 国家工业信息安全发展研究中心工业数字孪生标准解读 | [入口](https://www.cics-cert.org.cn/web_root/webpage/articlecontent_101002_2069717284267495426.html) | validated candidate | static_html, stable path | 工业数字孪生建设与服务商评估标准的实施解读。 |
| `caict-dt-report-2024` | 中国政策与产业 | expert_interpreter | 中国信通院《数字孪生赋能城市全域数字化转型研究报告（2024年）》 | [入口](https://www.caict.ac.cn/english/research/whitepapers/202504/P020250402570208237008.pdf) | validated candidate | static_html, stable path | 城市数字孪生底座、应用和产业趋势研究，市场数字需交叉核验。 |
| `caict-ictp-volume` | 中国政策与产业 | expert_interpreter | 《信息通信技术与政策》数字孪生城市专题期刊入口 | [入口](https://ictp.caict.ac.cn/CN/volumn/volumn_55.shtml) | validated candidate | static_html, stable path | 持续发现城市数字孪生研究、作者和引用关系。 |
| `caict-city-framework` | 中国政策与产业 | expert_interpreter | 中国信通院《数字孪生城市框架与发展建议》 | [入口](https://ictp.caict.ac.cn/CN/abstract/abstract981.shtml) | validated + historical replay | static_html, stable path | 城市数字孪生要素框架和发展建议。 |
| `caict-resilient-city` | 中国政策与产业 | expert_interpreter | 中国信通院《数字孪生赋能韧性城市场景研究》 | [入口](https://ictp.caict.ac.cn/CN/abstract/abstract1466.shtml) | validated + historical replay | static_html, stable path | 灾害预防、响应和恢复场景研究。 |
| `miit-chain-cases` | 中国政策与产业 | official_primary | 工信部工业互联网“链网协同”典型案例申报说明 | [入口](https://www.miit.gov.cn/ztzl/rdzt/gyhlw/gzdt/art/2025/art_83d98fb4dd264b9e9b8b4555f75b5746.html) | validated candidate | static_html, stable path | 从申报和典型案例中发现数字孪生实际应用与成效主张。 |
| `ccgp-home` | 采购与交付 | official_primary | 中国政府采购网 | [入口](https://www.ccgp.gov.cn/) | validated candidate | static_html, stable path | 项目招标、采购公告和结果的官方入口，需以具体公告为证据。 |
| `ccgp-intention` | 采购与交付 | official_primary | 中国政府采购网采购意向公开 | [入口](https://cgyx.ccgp.gov.cn/) | validated candidate | static_html, stable path | 在项目正式招标前发现预算、建设范围和采购意图。 |
| `ggzy-home` | 采购与交付 | official_primary | 全国公共资源交易平台 | [入口](https://www.ggzy.gov.cn/) | validated candidate | static_html, stable path | 公共资源交易、工程项目和中标结果的补充入口。 |
| `mwr-home` | 中国政策与产业 | official_primary | 中华人民共和国水利部 | [入口](https://www.mwr.gov.cn/) | discovery candidate | static_html, needs adapter/validation | 水利数字孪生流域、工程、调度和防灾信息的政策与项目入口。 |
| `mohurd-home` | 中国政策与产业 | official_primary | 中华人民共和国住房和城乡建设部 | [入口](https://www.mohurd.gov.cn/) | discovery candidate | static_html, needs adapter/validation | 城市信息模型、建筑信息模型和城市数字基础设施政策入口。 |
| `arxiv-dt` | 研究与学术 | frontier_sensor | arXiv Digital Twin 检索 | [入口](https://arxiv.org/search/?query=digital+twin&searchtype=all&abstracts=show&order=-announced_date_first&size=50) | validated candidate | static_html, stable path | 开放论文预印本发现入口，需记录版本和同行评审状态。 |
| `openalex-dt` | 研究与学术 | frontier_sensor | OpenAlex Digital Twin works query | [入口](https://api.openalex.org/works?search=digital%20twin&per-page=50) | discovery candidate | api, needs adapter/validation | 跨学科论文、作者、机构和引用网络发现入口。 |
| `crossref-dt` | 研究与学术 | frontier_sensor | Crossref Digital Twin works query | [入口](https://api.crossref.org/works?query=Digital%20Twin&rows=50) | discovery candidate | api, needs adapter/validation | DOI 元数据和出版时间发现入口，不代表论文质量判断。 |
| `semanticscholar-dt` | 研究与学术 | frontier_sensor | Semantic Scholar Digital Twin paper query | [入口](https://api.semanticscholar.org/graph/v1/paper/search?query=digital%20twin&limit=100&fields=title,authors,year,url,abstract) | discovery candidate | api, needs adapter/validation | 作者、摘要和引用关系发现入口，受 API 速率和访问条件影响。 |
| `ieee-xplore-dt` | 研究与学术 | expert_interpreter | IEEE Xplore Digital Twin 检索 | [入口](https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=digital%20twin) | discovery candidate | static_html, needs adapter/validation | 同行评审论文与会议论文发现入口，部分内容需要订阅。 |
| `acm-dt` | 研究与学术 | expert_interpreter | ACM Digital Library Digital Twin 检索 | [入口](https://dl.acm.org/action/doSearch?AllField=digital+twin) | discovery candidate | static_html, needs adapter/validation | 计算机系统、数据、网络和人机交互论文发现入口。 |
| `sciencedirect-dt` | 研究与学术 | expert_interpreter | ScienceDirect Digital Twin topic | [入口](https://www.sciencedirect.com/topics/engineering/digital-twin) | discovery candidate | static_html, needs adapter/validation | 工程学综述、主题导航和论文发现入口。 |
| `nature-dt` | 研究与学术 | expert_interpreter | Nature Digital Twins subject | [入口](https://www.nature.com/subjects/digital-twins) | discovery candidate | static_html, needs adapter/validation | 跨学科高影响力研究发现入口，不代表主题页内全部内容同等权威。 |
| `mdpi-dt` | 研究与学术 | broad_coverage | MDPI Digital Twin 检索 | [入口](https://www.mdpi.com/search?q=digital+twin&sort=pubdate) | discovery candidate | static_html, needs adapter/validation | 开放获取论文与专题发现入口，需对期刊和论文逐项评估。 |
| `itu-jfet-dt` | 研究与学术 | expert_interpreter | ITU Journal on Future and Evolving Technologies 数字孪生专题 | [入口](https://www.itu.int/en/journal/j-fet/2026/004/Pages/default.aspx) | validated candidate | static_html, stable path | 覆盖数字孪生网络、边缘、通信、隐私、安全和指标的专题入口。 |
| `ieee-dtpi-2026` | 研究与学术 | frontier_sensor | IEEE DTPI 2026 Digital Twins and Parallel Intelligence | [入口](https://ieee-dtpi-2026.org/) | validated + historical replay | static_html, stable path | 会议、征稿、组织者和论文主题入口。 |
| `aalto-digitwin-lab` | 研究与学术 | expert_interpreter | Aalto University DigiTwin Lab | [入口](https://www.aalto.fi/en/aiic/digitwin) | validated candidate | static_html, stable path | 工业物联网、数字孪生 Web、XR 和互操作研究实验室。 |
| `sjsu-dt-lab` | 研究与学术 | expert_interpreter | San José State University Digital Twin Lab | [入口](https://www.sjsu.edu/information-data-society/centers-labs/digital-twin/index.php) | validated + historical replay | static_html, stable path | 跨学科数字孪生、仿真、物理 AI、传感器和决策支持实验室。 |
| `melbourne-dt-platform` | 研究与学术 | expert_interpreter | University of Melbourne Digital Twin platform | [入口](https://research.unimelb.edu.au/facilities/infrastructure/digital-twin) | validated candidate | static_html, stable path | 城市基础设施、空间数据和政府/产业合作案例入口。 |
| `utoronto-ibdt` | 研究与学术 | expert_interpreter | University of Toronto Center for Intelligent Buildings Digital Twinning | [入口](https://ibdt.ca/) | validated candidate | static_html, stable path | 建筑运维、BIM、合同、能耗、数据治理和决策场景研究。 |
| `sdu-dt-lab` | 研究与学术 | expert_interpreter | SDU Digital Twin and Agentic AI Infrastructure Lab | [入口](https://www.sdu.dk/en/forskning/centreforenergyinformatics/research-labs/digital-twin-and-agentic-ai-infrastructure-lab) | validated candidate | static_html, stable path | 能源系统数字孪生、AI、智能体和数据基础设施实验环境。 |
| `ucsd-armor-dt` | 研究与学术 | expert_interpreter | UC San Diego ARMOR Lab digital twin research | [入口](https://armor.ucsd.edu/research) | validated candidate | static_html, stable path | 物理资产、人类数字孪生、结构健康和可穿戴系统研究入口。 |
| `plm-dt-contest` | 研究与学术 | frontier_sensor | IFIP WG 5.1 / PLM Digital Twin Contest | [入口](https://www.plm-conference.org/call-for-dtcontest-2026/) | discovery candidate | static_html, needs adapter/validation | 从竞赛和短视频中发现真实数字孪生实现，需核对项目材料。 |
| `siemens-dt` | 平台与厂商 | broad_coverage | Siemens Digital Twin technology | [入口](https://www.siemens.com/en-gb/company/digital-twin/) | validated candidate | static_html, stable path | 工业产品、生产、性能孪生和生命周期实践，厂商主张需交叉核验。 |
| `nvidia-dt` | 平台与厂商 | broad_coverage | NVIDIA Omniverse Digital Twins overview | [入口](https://docs.omniverse.nvidia.com/digital-twins/latest/overview.html) | validated candidate | static_html, stable path | 物理准确性、实时数据、AI 和工业/数据中心数字孪生实现参照。 |
| `nvidia-omniverse-docs` | 平台与厂商 | broad_coverage | NVIDIA Omniverse developer documentation | [入口](https://docs.nvidia.com/omniverse/index.html) | validated candidate | static_html, stable path | OpenUSD、仿真、数据聚合、工厂孪生工作流和参考架构。 |
| `bentley-itwin` | 平台与厂商 | broad_coverage | Bentley iTwin platform | [入口](https://www.bentley.com/software/itwin/) | validated candidate | static_html, stable path | 基础设施工程、BIM、IoT、现实捕捉和资产运维孪生。 |
| `ptc-thingworx` | 平台与厂商 | broad_coverage | PTC ThingWorx Industrial IoT platform | [入口](https://www.ptc.com/en/products/thingworx/) | validated candidate | static_html, stable path | 工业连接、分析、应用和资产优化实现参照。 |
| `ptc-docs` | 平台与厂商 | broad_coverage | PTC ThingWorx documentation resources | [入口](https://www.ptc.com/en/support/help/thingworx_doc_resources) | discovery candidate | static_html, needs adapter/validation | 版本、发布说明、连接服务和开发文档入口。 |
| `autodesk-tandem` | 平台与厂商 | broad_coverage | Autodesk Tandem digital twin platform | [入口](https://intandem.autodesk.com/) | validated candidate | static_html, stable path | BIM、设施运营、资产数据、传感器和客户案例。 |
| `autodesk-tandem-api` | 平台与厂商 | broad_coverage | Autodesk Tandem APIs and platform | [入口](https://intandem.autodesk.com/tandem-as-a-platform/) | validated candidate | static_html, stable path | REST API、BMS/CMMS 集成和第三方应用扩展入口。 |
| `ansys-twin-builder` | 平台与厂商 | broad_coverage | Ansys Twin Builder | [入口](https://www.ansys.com/en-gb/products/digital-twin/ansys-twin-builder) | validated candidate | static_html, stable path | 混合模型、仿真、验证、部署和预测维护实现参照。 |
| `dassault-virtual-twin` | 平台与厂商 | broad_coverage | Dassault Systèmes Virtual Twin Experiences | [入口](https://www.3ds.com/virtual-twin) | validated candidate | static_html, stable path | 科学模型、全生命周期、虚拟孪生和行业客户主张。 |
| `sap-iot` | 平台与厂商 | broad_coverage | SAP Internet of Things | [入口](https://help.sap.com/docs/SAP_IoT) | validated candidate | static_html, stable path | 真实对象建模、设备连接、IoT 服务与 SAP 业务应用衔接。 |
| `sap-dt-news` | 平台与厂商 | frontier_sensor | SAP News digital twin tag | [入口](https://news.sap.com/tags/digital-twin/) | validated + historical replay | static_html, stable path | 平台新闻、组织数字孪生和客户案例发现。 |
| `aveva-dt` | 平台与厂商 | broad_coverage | AVEVA industrial digital twin | [入口](https://www.aveva.com/en/solutions/digital-transformation/digital-twin/) | validated candidate | static_html, stable path | ET/OT/IT、工程数据、实时数据、模型、分析和工业案例。 |
| `aveva-presentations` | 平台与厂商 | frontier_sensor | AVEVA 2026 presentations and webinars | [入口](https://www.aveva.com/en/perspectives/presentations/2026/) | discovery candidate | static_html, needs adapter/validation | 从会议演讲和案例演示发现实施证据，厂商主张需核验。 |
| `tencent-energy-twin` | 平台与厂商 | broad_coverage | 腾讯智慧能源数字孪生产品文档 | [入口](https://cloud.tencent.com/document/product/1686/95686) | validated + historical replay | static_html, stable path | 能源数字孪生的数据底座、3D、模型和多端协同能力。 |
| `tencent-raydata` | 平台与厂商 | broad_coverage | 腾讯云 RayData Web 数字孪生可视化产品 | [入口](https://cloud.tencent.com/product/web?Is=home) | validated candidate | static_html, stable path | 可视化编排、数据接入、权限和行业方案；不等同于完整数字孪生。 |
| `huawei-astrocanvas` | 平台与厂商 | broad_coverage | Huawei Cloud Astro Canvas | [入口](https://www.huaweicloud.com/intl/en-us/product/appcube/astrocanvas.html) | discovery candidate | static_html, needs adapter/validation | 城市数字孪生可视化、低代码和数据连接实现参照。 |
| `baidu-dugis` | 平台与厂商 | broad_coverage | 百度智能云数字孪生地图 DuGIS | [入口](https://cloud.baidu.com/product/dugisdt.html?from=ppn50829sdvbsjv) | discovery candidate | static_html, needs adapter/validation | GIS、IoT、大数据和城市/园区孪生实现参照。 |
| `esri-arcgis-urban` | 平台与厂商 | broad_coverage | Esri ArcGIS Urban | [入口](https://www.esri.com/en-us/arcgis/products/arcgis-urban/overview) | discovery candidate | static_html, needs adapter/validation | 城市规划、3D 场景和地理空间决策参照。 |
| `unity-industry` | 平台与厂商 | broad_coverage | Unity Industry solutions | [入口](https://unity.com/solutions/industry) | discovery candidate | static_html, needs adapter/validation | 实时 3D、仿真和工业可视化实现参照，需区分可视化与孪生闭环。 |
| `fiware-dt` | 开源与数据空间 | expert_interpreter | FIWARE for Digital Twins | [入口](https://www.fiware.org/wp-content/uploads/FF_PositionPaper_FIWARE4DigitalTwins.pdf) | validated candidate | static_html, stable path | 上下文信息、数据连接器、历史数据和开放组件组合。 |
| `eclipse-digital-twin` | 开源与数据空间 | expert_interpreter | Eclipse Digital Twin Top-Level Project | [入口](https://projects.eclipse.org/projects/dt) | validated candidate | static_html, stable path | Eclipse 数字孪生项目总览、许可证和参考实现生态。 |
| `eclipse-basyx` | 开源与数据空间 | expert_interpreter | Eclipse BaSyx | [入口](https://eclipse.dev/basyx/) | validated candidate | static_html, stable path | AAS、OPC UA、MQTT、注册表、子模型和工业中间件实现。 |
| `eclipse-tractusx` | 开源与数据空间 | expert_interpreter | Eclipse Tractus-X | [入口](https://projects.eclipse.org/projects/automotive.tractusx) | validated + historical replay | static_html, stable path | Catena-X/Manufacturing-X 数据空间参考实现和版本动态。 |
| `openusd` | 开源与数据空间 | expert_interpreter | OpenUSD | [入口](https://openusd.org/) | validated candidate | static_html, stable path | 高性能 3D 场景组合、模式和跨工具协作基础。 |
| `cesium-open` | 开源与数据空间 | broad_coverage | Cesium Open Ecosystem | [入口](https://cesium.com/why-cesium/open-ecosystem/) | validated candidate | static_html, stable path | 地理空间 3D、CesiumJS 和数字地球可视化生态。 |
| `ifcopenshell` | 开源与数据空间 | community | IfcOpenShell | [入口](https://ifcopenshell.org/) | discovery candidate | static_html, needs adapter/validation | IFC 解析、几何和建筑数据自动化工具，需关注版本与许可证。 |
| `bonsai-bim` | 开源与数据空间 | community | Bonsai BIM | [入口](https://bonsaibim.org/) | discovery candidate | static_html, needs adapter/validation | Blender 上的开源 BIM/IFC 工作流，作为建筑数字孪生数据入口参照。 |
| `openmodelica` | 开源与数据空间 | community | OpenModelica | [入口](https://openmodelica.org/) | discovery candidate | static_html, needs adapter/validation | 开源建模与仿真环境，适合追踪机理模型和联合仿真线索。 |
| `o3de` | 开源与数据空间 | community | Open 3D Engine | [入口](https://o3de.org/) | discovery candidate | static_html, needs adapter/validation | 开放 3D 引擎和实时场景实现参照，不自动等同于数字孪生平台。 |
| `speckle` | 开源与数据空间 | community | Speckle open data platform | [入口](https://speckle.systems/) | discovery candidate | static_html, needs adapter/validation | AEC 数据流、协作和模型互操作发现入口。 |
| `idsa-dataspaces` | 开源与数据空间 | expert_interpreter | International Data Spaces Association | [入口](https://internationaldataspaces.org/) | validated candidate | static_html, stable path | 数据空间、主权数据共享、信任与连接器生态入口。 |
| `digital-twin-insider-linkedin` | 媒体与社区 | community | Digital Twin Insider LinkedIn Newsletter | [入口](https://www.linkedin.com/newsletters/digital-twin-newsletter-6937723177603092481) | manual discovery candidate | browser, needs adapter/validation | 面向数字孪生行业的周刊和作者注意力线索；登录态/社交平台，默认人工采集。 |
| `digital-twin-insider-site` | 媒体与社区 | broad_coverage | Digital Twin Insider / Metaverse Insider | [入口](https://metaverseinsider.tech/) | discovery candidate | static_html, needs adapter/validation | 数字孪生市场新闻、融资、公司和产品线索；商业媒体，需要回到一手证据。 |
| `iiot-world` | 媒体与社区 | broad_coverage | IIoT World Industrial AI, IoT & OT Cybersecurity | [入口](https://www.iiot-world.com/) | validated + historical replay | static_html, stable path | 工业 AI、预测维护、OT 安全、智能制造和数字孪生实践线索。 |
| `iiot-world-newsletter` | 媒体与社区 | community | IIoT World weekly newsletter | [入口](https://www.iiot-world.com/subscribe/) | manual discovery candidate | browser, needs adapter/validation | 周刊、专家访谈和线上活动入口；商业媒体/Newsletter，需标注赞助内容。 |
| `iot-insider` | 媒体与社区 | broad_coverage | IoT Insider | [入口](https://www.iotinsider.com/) | discovery candidate | static_html, needs adapter/validation | IoT、工业、智能城市和播客内容，适合发现设备连接与落地线索。 |
| `digital-twin-newswire` | 媒体与社区 | broad_coverage | The Digital Twin world modelling newswire | [入口](https://the-digital-twin.com/en/news) | discovery candidate | static_html, needs adapter/validation | 数字孪生建模、预测、能源、农业、资产和政策新闻线索。 |
| `autodesk-digital-thread` | 媒体与社区 | community | Autodesk The Digital Thread podcast | [入口](https://intandem.autodesk.com/podcast-listing/) | manual discovery candidate | browser, needs adapter/validation | 数字线程、建筑与设施运营访谈/播客，厂商主导，需交叉核验。 |
| `ieee-digital-reality` | 媒体与社区 | expert_interpreter | IEEE Digital Reality webinars and podcasts | [入口](https://digitalreality.ieee.org/webinars/) | validated candidate | static_html, stable path | 数字现实、AR/VR/MR 与数字孪生的公开讲座和播客入口。 |
| `idta-newsletter` | 媒体与社区 | expert_interpreter | IDTA news and newsletter | [入口](https://industrialdigitaltwin.org/en/) | validated + historical replay | static_html, stable path | AAS、协会治理、研究中心、培训与活动动态。 |
| `itu-webinars` | 媒体与社区 | expert_interpreter | ITU digital twin webinar archive | [入口](https://www.itu.int/en/ITU-T/webinars/Documents/Outcome%20Document%20%282021%29.pdf) | validated candidate | static_html, stable path | 城市数字孪生标准与行业实践的公开会议材料。 |
| `eigen-webinars` | 媒体与社区 | broad_coverage | Eigen digitalisation and digital twin webinars | [入口](https://eigen.co/resources/webinars/) | discovery candidate | static_html, needs adapter/validation | 数字化、知识图谱、验证与数字孪生客户演示，厂商内容需核验。 |
| `smart-cities-world` | 媒体与社区 | broad_coverage | Smart Cities World | [入口](https://www.smartcitiesworld.net/) | discovery candidate | static_html, needs adapter/validation | 智慧城市、基础设施和城市技术新闻，数字孪生信息需回溯项目原始来源。 |
| `cities-today` | 媒体与社区 | broad_coverage | Cities Today | [入口](https://www.cities-today.com/) | discovery candidate | static_html, needs adapter/validation | 城市治理、交通、基础设施和数字化案例发现入口。 |
| `engineering-com-dt` | 媒体与社区 | broad_coverage | Engineering.com digital twin topic | [入口](https://www.engineering.com/category/digital-twin/) | discovery candidate | static_html, needs adapter/validation | 工程软件、制造、BIM 和数字孪生解释/新闻入口。 |
| `bimplus` | 媒体与社区 | broad_coverage | BIMplus | [入口](https://www.bimplus.co.uk/) | discovery candidate | static_html, needs adapter/validation | BIM、建筑数据、基础设施和数字孪生交付线索。 |
| `gisuser` | 媒体与社区 | broad_coverage | GISuser | [入口](https://gisuser.com/) | discovery candidate | static_html, needs adapter/validation | GIS、测绘、空间数据和城市数字孪生新闻线索。 |
| `geospatial-world` | 媒体与社区 | broad_coverage | Geospatial World | [入口](https://www.geospatialworld.net/) | discovery candidate | static_html, needs adapter/validation | 地理空间、遥感、基础设施和数字孪生产业动态。 |
| `automation-world` | 媒体与社区 | broad_coverage | Automation World | [入口](https://www.automationworld.com/) | discovery candidate | static_html, needs adapter/validation | 自动化、制造、工业 IoT 和数字孪生应用新闻。 |
| `control-engineering` | 媒体与社区 | broad_coverage | Control Engineering | [入口](https://www.controleng.com/) | discovery candidate | static_html, needs adapter/validation | 控制系统、工业网络、仿真和设备运维线索。 |
| `industryweek` | 媒体与社区 | broad_coverage | IndustryWeek technology and IIoT | [入口](https://www.industryweek.com/technology-and-iiot) | discovery candidate | static_html, needs adapter/validation | 制造业管理、工业技术和投资/运营案例发现入口。 |

## 接入顺序

第一批接入标准与政策、研究检索、项目采购和高价值平台文档；第二批接入开源项目、会议/播客、行业媒体和 Newsletter；第三批再接入需要浏览器登录、社交平台或人工订阅的来源。任何来源进入日报主组合前，都要同时具备：明确角色、至少一个信息要素映射、可重复采集路径、历史观察以及证据 URL。

本矩阵不是“越多越好”的链接仓库，而是给私人情报所提供一个足够宽的候选雷达。最终日报应由历史回放、信源组合和覆盖审计决定，而不是按来源数量直接堆叠。
