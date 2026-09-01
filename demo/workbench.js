(function () {
  "use strict";

  const ARTIFACT_ORDER = [
    "domain-profile.json",
    "source-map.json",
    "acquisition-plan.json",
    "source-activation.json",
    "knowledge-graph.json",
    "knowledge-graph.md",
    "bootstrap-report.json",
    "bootstrap-report.md",
    "daily-brief.json",
    "daily-brief.md",
    "content-inventory.json",
    "content-inventory.md",
    "content/",
    "run-manifest.json",
  ];

  const REQUIRED_RUN_JSON = [
    "run-manifest.json",
    "domain-profile.json",
    "source-map.json",
    "acquisition-plan.json",
    "source-activation.json",
    "knowledge-graph.json",
    "bootstrap-report.json",
    "daily-brief.json",
    "content-inventory.json",
  ];

  const ROOT_RUN_ARTIFACTS = new Set(ARTIFACT_ORDER.filter((path) => !path.endsWith("/")));

  const METHOD_LABELS = {
    api: "API",
    atom: "Atom",
    browser: "浏览器",
    json: "JSON",
    manual: "人工",
    opml: "OPML",
    rss: "RSS",
    sitemap: "Sitemap",
    static_html: "静态页面",
    unknown: "未配置",
  };

  const STATUS_LABELS = {
    blocked: "阻断",
    captured: "已抓取",
    complete: "已完成",
    empty: "无新内容",
    failed: "失败",
    observed: "已观察",
    partial: "部分完成",
    pending: "待处理",
    ready: "待运行",
    succeeded: "成功",
  };

  const ROLE_LABELS = {
    academic: "学术研究",
    official_primary: "官方一手",
    platform_provider: "平台与厂商",
    professional_media: "专业媒体",
    standards_body: "标准组织",
    research: "研究机构",
    community: "专业社区",
    public_procurement: "公共采购",
  };

  const state = {
    run: null,
    files: [],
    runRoot: "",
    mode: "demo",
    objectUrls: [],
    activeView: "overview",
    graphInventoryMode: "nodes",
    graphQuery: "",
    sourceFilter: "all",
    contentFilter: "all",
    sourceQuery: "",
    contentQuery: "",
    lastFocus: null,
  };

  const dom = {
    runDomain: document.getElementById("run-domain"),
    runBadge: document.getElementById("run-badge"),
    importInput: document.getElementById("run-import"),
    importLabel: document.querySelector(".import-button span"),
    importHint: document.getElementById("import-hint"),
    overviewLede: document.getElementById("overview-lede"),
    heroGraphCount: document.getElementById("hero-graph-count"),
    heroEvidenceCount: document.getElementById("hero-evidence-count"),
    metricSources: document.getElementById("metric-sources"),
    metricContent: document.getElementById("metric-content"),
    metricContentNote: document.getElementById("metric-content-note"),
    metricEvidence: document.getElementById("metric-evidence"),
    metricStories: document.getElementById("metric-stories"),
    runSummary: document.getElementById("run-summary"),
    pipeline: document.getElementById("run-pipeline"),
    runGuideForm: document.getElementById("run-guide-form"),
    controlDomainInput: document.getElementById("control-domain-input"),
    controlRunState: document.getElementById("control-run-state"),
    controlRunDomain: document.getElementById("control-run-domain"),
    controlRunId: document.getElementById("control-run-id"),
    controlRunMeta: document.getElementById("control-run-meta"),
    controlStageSummary: document.getElementById("control-stage-summary"),
    controlStageList: document.getElementById("control-stage-list"),
    controlActionList: document.getElementById("control-action-list"),
    controlLogGrid: document.getElementById("control-log-grid"),
    storyPreview: document.getElementById("story-preview-list"),
    coverageValue: document.getElementById("coverage-value"),
    coverageBar: document.getElementById("coverage-bar-fill"),
    coverageList: document.getElementById("coverage-list"),
    artifactList: document.getElementById("artifact-list"),
    graphSvg: document.getElementById("graph-svg"),
    graphStageNote: document.getElementById("graph-stage-note"),
    graphStats: document.getElementById("graph-stats"),
    graphNodeList: document.getElementById("graph-node-list"),
    graphInventorySummary: document.getElementById("graph-inventory-summary"),
    graphSearch: document.getElementById("graph-search"),
    graphInventoryBody: document.getElementById("graph-inventory-body"),
    graphInventoryEmpty: document.getElementById("graph-inventory-empty"),
    sourceSearch: document.getElementById("source-search"),
    sourceTable: document.getElementById("source-table-body"),
    sourceEmpty: document.getElementById("source-empty"),
    contentSearch: document.getElementById("content-search"),
    contentList: document.getElementById("content-list"),
    contentEmpty: document.getElementById("content-empty"),
    dailyHeading: document.getElementById("daily-brief-heading"),
    dailyWindow: document.getElementById("daily-window"),
    briefList: document.getElementById("brief-list"),
    evidenceList: document.getElementById("evidence-list"),
    drawer: document.getElementById("content-drawer"),
    drawerBackdrop: document.getElementById("drawer-backdrop"),
    drawerKicker: document.getElementById("drawer-kicker"),
    drawerTitle: document.getElementById("drawer-title"),
    drawerMeta: document.getElementById("drawer-meta"),
    drawerLinks: document.getElementById("drawer-links"),
    drawerBody: document.getElementById("drawer-body"),
    drawerClose: document.getElementById("drawer-close"),
    toast: document.getElementById("toast"),
  };

  function makeElement(tagName, className, text) {
    const node = document.createElement(tagName);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function number(value) {
    return Number(value || 0).toLocaleString("zh-CN");
  }

  function percent(value) {
    return `${Math.round(Number(value || 0) * 100)}%`;
  }

  function date(value) {
    if (!value) return "未提供日期";
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) return String(value);
    return new Intl.DateTimeFormat("zh-CN", {
      dateStyle: "medium",
      timeZone: "Asia/Shanghai",
    }).format(parsed);
  }

  function dateTime(value) {
    if (!value) return "未记录";
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) return String(value);
    return new Intl.DateTimeFormat("zh-CN", {
      dateStyle: "medium",
      timeStyle: "short",
      timeZone: "Asia/Shanghai",
    }).format(parsed);
  }

  function methodLabel(value) {
    return METHOD_LABELS[value] || value || "未配置";
  }

  function roleLabel(value) {
    return ROLE_LABELS[value] || value || "未标注角色";
  }

  function statusLabel(value) {
    return STATUS_LABELS[value] || value || "未记录";
  }

  function normalizePath(value) {
    return String(value || "")
      .replaceAll("\\", "/")
      .replace(/^\.\//, "")
      .replace(/^\/+/, "");
  }

  function hasUnsafePath(value) {
    return normalizePath(value).split("/").some((segment) => segment === "." || segment === "..");
  }

  function selectedFilePath(file) {
    return normalizePath(file?.webkitRelativePath || file?.name);
  }

  function runRootForFiles(files) {
    const firstPath = selectedFilePath(files[0]);
    if (!firstPath || hasUnsafePath(firstPath)) return "";
    const separator = firstPath.indexOf("/");
    return separator > 0 ? firstPath.slice(0, separator) : "";
  }

  function relativeRunPath(path, root = state.runRoot) {
    const normalized = normalizePath(path);
    if (!normalized || hasUnsafePath(normalized) || !root) return "";
    const prefix = `${root}/`;
    return normalized.startsWith(prefix) ? normalized.slice(prefix.length) : "";
  }

  function fileRelativePath(file) {
    return relativeRunPath(selectedFilePath(file));
  }

  function basename(value) {
    const path = normalizePath(value);
    return path.slice(path.lastIndexOf("/") + 1);
  }

  function formatCountPair(current, total) {
    return `${number(current)} / ${number(total)}`;
  }

  function createBadge(status, label) {
    const badge = makeElement("span", `status-badge is-${status}`, label || statusLabel(status));
    badge.setAttribute("data-status", status || "unknown");
    return badge;
  }

  function createLink(label, href) {
    const link = makeElement("a", "drawer-link", label);
    link.href = href;
    link.target = "_blank";
    link.rel = "noreferrer noopener";
    return link;
  }

  function safeExternalUrl(href) {
    try {
      const parsed = new URL(String(href || ""));
      return ["http:", "https:"].includes(parsed.protocol) ? parsed.href : "";
    } catch {
      return "";
    }
  }

  function createExternalLink(label, href) {
    const safeHref = safeExternalUrl(href);
    return safeHref ? createLink(label, safeHref) : null;
  }

  function createAction(label, className, handler) {
    const button = makeElement("button", className, label);
    button.type = "button";
    button.addEventListener("click", handler);
    return button;
  }

  function sourceList() {
    return Array.isArray(state.run?.sourceMap?.sources) ? state.run.sourceMap.sources : [];
  }

  function sourceMap() {
    return new Map(sourceList().map((source) => [source.id, source]));
  }

  function statusMap() {
    const statuses = Array.isArray(state.run?.activation?.source_statuses)
      ? state.run.activation.source_statuses
      : [];
    return new Map(statuses.map((item) => [item.source_id, item]));
  }

  function acquisitionMap() {
    const runs = Array.isArray(state.run?.activation?.runs) ? state.run.activation.runs : [];
    return new Map(runs.map((item) => [item.source_id, item]));
  }

  function evidenceList() {
    return Array.isArray(state.run?.activation?.evidence) ? state.run.activation.evidence : [];
  }

  function contentList() {
    return Array.isArray(state.run?.contentInventory?.items) ? state.run.contentInventory.items : [];
  }

  function storyList() {
    return Array.isArray(state.run?.report?.brief?.stories) ? state.run.report.brief.stories : [];
  }

  function signalMap() {
    const signals = Array.isArray(state.run?.activation?.signals) ? state.run.activation.signals : [];
    return new Map(signals.map((item) => [item.id, item]));
  }

  function contentById(id) {
    return contentList().find((item) => item.id === id) || null;
  }

  function contentByRef(reference) {
    const target = normalizePath(reference);
    return contentList().find((item) => normalizePath(item.relative_path) === target) || null;
  }

  function contentForEvidence(evidence) {
    if (!evidence) return null;
    if (evidence.content_ref) return contentByRef(evidence.content_ref);
    return contentList().find((item) => item.evidence_id === evidence.id) || null;
  }

  function elementLabels() {
    const elements = Array.isArray(state.run?.profile?.elements) ? state.run.profile.elements : [];
    return new Map(
      elements.map((item) => [item.id, item.label || item.name || item.title || item.id]),
    );
  }

  function findFile(relativePath) {
    const target = normalizePath(relativePath);
    if (!target || hasUnsafePath(target)) return null;
    return (
      state.files.find((file) => {
        return fileRelativePath(file) === target;
      }) || null
    );
  }

  function showToast(message) {
    dom.toast.textContent = message;
    dom.toast.hidden = false;
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(() => {
      dom.toast.hidden = true;
    }, 4200);
  }

  function setRunHeader() {
    const manifest = state.run.manifest;
    dom.runDomain.textContent = `${state.mode === "demo" ? "演示运行" : "已导入运行"} · ${manifest.domain}`;
    dom.runBadge.textContent = state.mode === "demo" ? "演示数据" : "已导入";
    dom.runBadge.classList.toggle("is-live", state.mode !== "demo");
    dom.importLabel.textContent = state.mode === "demo" ? "导入运行目录" : "重新导入运行目录";
    if (state.mode === "demo") {
      dom.importHint.textContent = "当前为演示运行。点击右上角“导入运行目录”，即可查看你实际运行生成的全部文件。";
      dom.overviewLede.textContent = "这里不是一张日报截图，而是一次运行留下的完整链路：领域底图、信源网络、真实内容、证据映射与最后的日报。";
    } else {
      const folder = state.files[0]?.webkitRelativePath?.split("/")[0] || "运行目录";
      dom.importHint.textContent = `已载入“${folder}”，工作台现在展示的是这次运行目录里的真实产物。`;
      dom.overviewLede.textContent = "这是一次可回看的真实运行：从领域底图到信源激活、全文归档、证据映射与日报，所有层都来自你导入的运行目录。";
    }
  }

  function renderMetrics() {
    const manifest = state.run.manifest;
    const graph = state.run.graph;
    const activation = state.run.activation;
    dom.heroGraphCount.textContent = number(Array.isArray(graph.nodes) ? graph.nodes.length : 0);
    dom.heroEvidenceCount.textContent = number(Array.isArray(activation.evidence) ? activation.evidence.length : 0);
    dom.metricSources.textContent = number(manifest.source_count);
    dom.metricContent.textContent = number(manifest.captured_content_count);
    dom.metricContentNote.textContent = `${number(manifest.content_count)} 条结果已登记，${number(manifest.captured_content_count)} 条形成全文`;
    dom.metricEvidence.textContent = number(manifest.evidence_count);
    dom.metricStories.textContent = number(manifest.story_count);
  }

  function renderPipeline() {
    clear(dom.pipeline);
    const manifest = state.run.manifest;
    const activation = state.run.activation;
    const graph = state.run.graph;
    const stages = [
      ["01", "领域底图", `${number(manifest.source_count)} 个来源候选`],
      ["02", "采集计划", `${number(manifest.ready_source_count)} 个可运行入口`],
      ["03", "内容归档", `${number(manifest.captured_content_count)} 条规范化全文`],
      ["04", "证据激活", `${number(activation.evidence.length)} 条可回链证据`],
      ["05", "判断交付", `${number(manifest.story_count)} 条日报故事`],
    ];
    stages.forEach(([index, title, detail]) => {
      const item = makeElement("div", "process-step");
      item.append(makeElement("span", "process-index", index));
      item.append(makeElement("strong", "", title));
      item.append(makeElement("small", "", detail));
      dom.pipeline.append(item);
    });
    dom.runSummary.textContent = `${number(graph.nodes.length)} 个节点、${number(graph.edges.length)} 条有类型关系；失败与阻断也保留在同一次运行里。`;
  }

  function activateSourceFilter(filter) {
    state.sourceFilter = filter;
    document.querySelectorAll("[data-source-filter]").forEach((tab) => {
      const active = tab.dataset.sourceFilter === filter;
      tab.classList.toggle("is-active", active);
      tab.setAttribute("aria-selected", String(active));
    });
    renderSources();
  }

  function activateContentFilter(filter) {
    state.contentFilter = filter;
    document.querySelectorAll("[data-content-filter]").forEach((tab) => {
      const active = tab.dataset.contentFilter === filter;
      tab.classList.toggle("is-active", active);
      tab.setAttribute("aria-selected", String(active));
    });
    renderContent();
  }

  function renderControl() {
    const manifest = state.run.manifest;
    const activation = state.run.activation;
    const graph = state.run.graph;
    const profile = state.run.profile;
    const items = contentList();
    const captured = Number(manifest.captured_content_count || items.filter((item) => item.status === "captured").length);
    const failed = items.filter((item) => item.status === "failed").length;
    const blocked = items.filter((item) => item.status === "blocked").length;
    const pending = failed + blocked;
    const evidenceCount = Array.isArray(activation.evidence) ? activation.evidence.length : 0;
    const storyCount = storyList().length;
    const isDemo = state.mode === "demo";
    const runState = isDemo ? "empty" : pending ? "partial" : "complete";

    dom.controlRunState.className = "status-badge";
    dom.controlRunState.classList.add(`is-${runState}`);
    dom.controlRunState.textContent = isDemo ? "演示运行" : statusLabel(runState);
    dom.controlRunState.dataset.status = runState;
    dom.controlRunDomain.textContent = manifest.domain || "未命名领域";
    dom.controlRunId.textContent = `run ${manifest.run_id || "unindexed-run"}`;
    if (document.activeElement !== dom.controlDomainInput) {
      dom.controlDomainInput.value = manifest.domain || "";
    }
    clear(dom.controlRunMeta);
    [
      ["生成时间", dateTime(manifest.generated_at)],
      ["运行窗口", `${date(activation.window_start)} 至 ${date(activation.generated_at || manifest.generated_at)}`],
      ["采集入口", `${number(manifest.ready_source_count)} 个可运行`],
    ].forEach(([label, value]) => {
      const item = makeElement("div");
      item.append(makeElement("dt", "", label), makeElement("dd", "", value));
      dom.controlRunMeta.append(item);
    });

    const stages = [
      { index: "01", title: "领域底图", detail: `${number(graph.nodes?.length)} 个节点 · ${number(profile.elements?.length)} 个信息要素`, status: graph.nodes?.length ? "complete" : "pending", action: "看知识图谱", target: "graph" },
      { index: "02", title: "来源网络", detail: `${number(manifest.source_count)} 个候选 · ${number(manifest.ready_source_count)} 个可运行入口`, status: manifest.source_count ? "complete" : "pending", action: "看信源网络", target: "sources" },
      { index: "03", title: "采集与归档", detail: `${number(captured)} / ${number(manifest.content_count)} 条形成规范化全文`, status: captured ? (pending ? "partial" : "complete") : "pending", action: "看内容清单", target: "content" },
      { index: "04", title: "证据与知识域", detail: `${number(evidenceCount)} 条证据 · ${number(manifest.signal_count)} 条信号`, status: evidenceCount ? "complete" : "pending", action: "看证据链", target: "brief" },
      { index: "05", title: "日报交付", detail: `${number(storyCount)} 条故事 · 可回到证据与全文`, status: storyCount ? "complete" : "pending", action: "打开日报", target: "brief" },
    ];
    dom.controlStageSummary.textContent = `${stages.length} 个阶段 · ${isDemo ? "演示流程" : "当前运行"}`;
    clear(dom.controlStageList);
    stages.forEach((stage) => {
      const item = makeElement("article", `control-stage is-${stage.status}`);
      item.append(makeElement("span", "control-stage-marker", stage.index));
      const copy = makeElement("div", "control-stage-copy");
      copy.append(makeElement("strong", "", stage.title), makeElement("small", "", stage.detail));
      const stageStatus = createBadge(stage.status, statusLabel(stage.status));
      stageStatus.classList.add("control-stage-status");
      item.append(copy, stageStatus);
      const action = createAction(stage.action, "control-stage-action", () => {
        if (stage.target === "sources") activateSourceFilter("all");
        if (stage.target === "content") activateContentFilter("all");
        showView(stage.target, true);
      });
      action.classList.add("control-stage-action");
      item.append(action);
      dom.controlStageList.append(item);
    });

    const sourcePending = sourceList().filter((source) => ["blocked", "failed", "pending", "empty"].includes(effectiveSourceStatus(source))).length;
    clear(dom.controlActionList);
    const actions = [
      { label: `导入另一份运行目录`, handler: () => dom.importInput.click() },
      { label: `查看待处理来源与空结果 · ${number(sourcePending)} 条`, handler: () => { activateSourceFilter("blocked"); showView("sources", true); } },
      { label: `复核规范化全文 · ${number(captured)} 条`, handler: () => { activateContentFilter("captured"); showView("content", true); } },
      { label: `打开本次日报 · ${number(storyCount)} 条故事`, handler: () => showView("brief", true) },
      { label: "打开运行清单", handler: () => openArtifact("run-manifest.json") },
    ];
    actions.forEach((entry) => dom.controlActionList.append(createAction(entry.label, "control-action", entry.handler)));

    clear(dom.controlLogGrid);
    [
      ["运行模式", isDemo ? "演示数据" : "本地真实运行"],
      ["输入方式", manifest.input_mode || "未记录"],
      ["候选来源", `${number(manifest.source_count)} 个`],
      ["待处理结果", `${number(pending)} 条失败或阻断`],
      ["可回链证据", `${number(evidenceCount)} 条`],
      ["知识图谱", `${number(graph.nodes?.length)} 节点 / ${number(graph.edges?.length)} 关系`],
      ["可交付文件", `${number(manifest.artifacts?.length || ARTIFACT_ORDER.length)} 项`],
      ["最后交付", `${number(storyCount)} 条日报故事`],
    ].forEach(([label, value]) => {
      const item = makeElement("div");
      item.append(makeElement("dt", "", label), makeElement("dd", "", value));
      dom.controlLogGrid.append(item);
    });
  }

  function renderStoriesPreview() {
    clear(dom.storyPreview);
    const stories = storyList().slice(0, 3);
    if (!stories.length) {
      dom.storyPreview.append(makeElement("p", "empty-state", "本次运行还没有形成日报故事。"));
      return;
    }
    const sources = sourceMap();
    stories.forEach((story) => {
      const item = makeElement("article", "story-preview");
      const body = makeElement("div");
      const source = sources.get(story.primary_source_id);
      body.append(makeElement("h3", "", story.title));
      body.append(makeElement("p", "", `${source?.name || story.primary_source_id} · ${story.event_type}`));
      const meta = makeElement("div", "story-meta");
      meta.append(makeElement("span", "", `判断分 ${percent(story.score)}`));
      meta.append(makeElement("span", "", `${story.signal_ids.length} 条信号`));
      body.append(meta);
      item.append(body);
      dom.storyPreview.append(item);
    });
  }

  function renderCoverage() {
    const coverage = state.run.report.coverage || {};
    const total = Number(coverage.total_elements || 0);
    const covered = Number(coverage.covered_elements || 0);
    const weighted = Number(coverage.weighted_coverage || 0);
    dom.coverageValue.textContent = formatCountPair(covered, total);
    dom.coverageBar.style.transform = `scaleX(${Math.max(0, Math.min(1, weighted))})`;
    clear(dom.coverageList);
    const labels = elementLabels();
    const rows = Array.isArray(coverage.rows) ? coverage.rows : [];
    rows.slice(0, 6).forEach((row) => {
      const item = makeElement("li");
      item.append(makeElement("span", "", labels.get(row.element_id) || row.element_id));
      item.append(makeElement("strong", "", `${percent(row.coverage_ratio)} · ${row.source_ids.length} 源`));
      dom.coverageList.append(item);
    });
    if (rows.length > 6) {
      dom.coverageList.append(makeElement("li", "", `还有 ${number(rows.length - 6)} 个信息要素，详见 bootstrap-report.json。`));
    }
    if (!rows.length) dom.coverageList.append(makeElement("li", "", "本次运行没有提供覆盖审计行。"));
  }

  function artifactDescription(path) {
    if (path === "content/") return "规范化全文与原始响应的文件夹";
    if (path.includes("graph")) return "领域节点、来源节点、证据节点与 typed edges";
    if (path.includes("activation")) return "每个来源的运行状态、证据和信号";
    if (path.includes("brief")) return "面向阅读的日报故事与证据入口";
    if (path.includes("report")) return "覆盖、推荐、回测与日报的综合报告";
    if (path.includes("content")) return "所有内容结果的状态与文件索引";
    if (path.includes("source-map")) return "专家、来源、角色与领域关系";
    if (path.includes("acquisition")) return "来源获取方式和阻断原因";
    if (path.includes("profile")) return "领域边界、信息要素与情报要求";
    if (path.includes("manifest")) return "本次运行的总索引和计数";
    return "本次运行的可审计产物";
  }

  function artifactState(path) {
    if (state.mode === "demo") return "演示预览";
    if (path === "content/") return state.files.some((file) => fileRelativePath(file).startsWith("content/")) ? "已导入" : "未找到文件夹";
    return findFile(path) ? "已导入" : "未找到";
  }

  function renderArtifacts() {
    clear(dom.artifactList);
    const artifacts = Array.isArray(state.run.manifest.artifacts) && state.run.manifest.artifacts.length
      ? state.run.manifest.artifacts
      : ARTIFACT_ORDER;
    artifacts.forEach((path) => {
      const item = makeElement("article", "artifact-item");
      const type = makeElement("span", "artifact-type", path === "content/" ? "DIRECTORY" : basename(path).split(".").pop().toUpperCase());
      const copy = makeElement("div");
      copy.append(makeElement("strong", "", path));
      copy.append(makeElement("span", "", artifactDescription(path)));
      const action = createAction(state.mode === "demo" ? "查看预览" : "打开产物", "artifact-open", () => openArtifact(path));
      const meta = makeElement("div", "artifact-meta");
      meta.append(makeElement("span", "", artifactState(path)));
      item.append(type, copy, meta, action);
      dom.artifactList.append(item);
    });
  }

  function graphKindLabel(kind) {
    const labels = {
      domain: "领域",
      topic: "主题",
      element: "信息要素",
      source: "来源",
      expert: "专家",
      evidence: "证据",
      event: "事件",
      nugget: "知识片段",
    };
    return labels[kind] || kind || "节点";
  }

  function shortLabel(value, length) {
    const text = String(value || "");
    return text.length > length ? `${text.slice(0, length - 1)}…` : text;
  }

  function svgElement(tagName, attrs) {
    const node = document.createElementNS("http://www.w3.org/2000/svg", tagName);
    Object.entries(attrs).forEach(([key, value]) => node.setAttribute(key, String(value)));
    return node;
  }

  function renderGraph() {
    const graph = state.run.graph || { nodes: [], edges: [] };
    const nodes = Array.isArray(graph.nodes) ? graph.nodes : [];
    const edges = Array.isArray(graph.edges) ? graph.edges : [];
    const preferredKinds = ["domain", "topic", "element", "source", "evidence"];
    const selected = [];
    preferredKinds.forEach((kind) => {
      nodes.filter((node) => node.kind === kind).slice(0, kind === "source" ? 6 : 4).forEach((node) => selected.push(node));
    });
    if (!selected.length) nodes.slice(0, 20).forEach((node) => selected.push(node));
    const selectedIds = new Set(selected.map((node) => node.id));
    const visibleEdges = edges.filter((edge) => selectedIds.has(edge.from_node_id) && selectedIds.has(edge.to_node_id));
    const positions = new Map();
    const columns = [
      ["domain", 88],
      ["topic", 248],
      ["element", 248],
      ["source", 478],
      ["evidence", 710],
    ];
    columns.forEach(([kind, x]) => {
      const columnNodes = selected.filter((node) => node.kind === kind);
      columnNodes.forEach((node, index) => positions.set(node.id, { x, y: 86 + index * Math.max(52, 320 / Math.max(columnNodes.length, 1)) }));
    });
    selected.filter((node) => !positions.has(node.id)).forEach((node, index) => positions.set(node.id, { x: 410, y: 90 + index * 58 }));

    clear(dom.graphSvg);
    dom.graphSvg.append(
      svgElement("title", { id: "graph-svg-title" }),
      svgElement("desc", { id: "graph-svg-desc" }),
    );
    dom.graphSvg.querySelector("title").textContent = `${state.run.manifest.domain}知识图谱关系视图`;
    dom.graphSvg.querySelector("desc").textContent = "展示领域、主题、来源和证据之间的有类型关系。";
    visibleEdges.forEach((edge) => {
      const from = positions.get(edge.from_node_id);
      const to = positions.get(edge.to_node_id);
      if (!from || !to) return;
      const line = svgElement("line", {
        x1: from.x,
        y1: from.y,
        x2: to.x,
        y2: to.y,
        class: edge.relation === "supports_element" || edge.relation === "evidences_event" ? "graph-edge is-evidence" : "graph-edge",
      });
      const title = svgElement("title", {});
      title.textContent = `${edge.relation}: ${edge.detail || ""}`;
      line.append(title);
      dom.graphSvg.append(line);
    });
    selected.forEach((node) => {
      const point = positions.get(node.id);
      if (!point) return;
      const group = svgElement("g", { class: "graph-node", "data-kind": node.kind, transform: `translate(${point.x} ${point.y})` });
      const circle = svgElement("circle", { r: node.kind === "domain" ? 16 : 10 });
      const title = makeElement("title", "", `${graphKindLabel(node.kind)}：${node.label}`);
      const text = svgElement("text", {
        x: node.kind === "evidence" ? -16 : node.kind === "domain" ? 22 : 16,
        y: 4,
        "text-anchor": node.kind === "evidence" ? "end" : "start",
      });
      text.textContent = shortLabel(node.label, node.kind === "source" ? 18 : 14);
      group.append(circle, title, text);
      dom.graphSvg.append(group);
    });
    dom.graphStageNote.textContent = `视图展示 ${number(selected.length)} / ${number(nodes.length)} 个关键节点`;
    clear(dom.graphStats);
    const counts = new Map();
    nodes.forEach((node) => counts.set(node.kind, (counts.get(node.kind) || 0) + 1));
    [
      ["全部节点", nodes.length],
      ["有类型关系", edges.length],
      ["来源节点", counts.get("source") || 0],
      ["证据节点", counts.get("evidence") || 0],
    ].forEach(([label, value]) => {
      const item = makeElement("div", "graph-stat");
      item.append(makeElement("span", "", label), makeElement("strong", "", number(value)));
      dom.graphStats.append(item);
    });
    clear(dom.graphNodeList);
    selected.slice(0, 14).forEach((node) => {
      const item = makeElement("article", "graph-node-item");
      item.dataset.kind = node.kind;
      const copy = makeElement("div");
      copy.append(makeElement("strong", "", shortLabel(node.label, 80)));
      copy.append(makeElement("small", "", `${graphKindLabel(node.kind)} · ${node.id}`));
      item.append(copy);
      dom.graphNodeList.append(item);
    });
  }

  function renderGraphInventory() {
    const graph = state.run.graph || { nodes: [], edges: [] };
    const nodes = Array.isArray(graph.nodes) ? graph.nodes : [];
    const edges = Array.isArray(graph.edges) ? graph.edges : [];
    const nodeById = new Map(nodes.map((node) => [node.id, node]));
    const query = state.graphQuery.trim().toLowerCase();
    clear(dom.graphInventoryBody);

    const addCell = (row, primary, secondary, className = "") => {
      const cell = makeElement("td");
      cell.append(makeElement("strong", className, primary));
      if (secondary) cell.append(makeElement("span", "graph-inventory-secondary", secondary));
      row.append(cell);
    };

    if (state.graphInventoryMode === "nodes") {
      const filtered = nodes.filter((node) => {
        const searchable = `${node.label || ""} ${node.id || ""} ${node.kind || ""}`.toLowerCase();
        return !query || searchable.includes(query);
      });
      dom.graphInventorySummary.textContent = `显示 ${number(filtered.length)} / ${number(nodes.length)} 个节点`;
      filtered.forEach((node) => {
        const row = makeElement("tr");
        addCell(row, shortLabel(node.label, 120), node.id);
        addCell(row, graphKindLabel(node.kind), node.kind);
        addCell(row, "领域图谱对象", node.id);
        addCell(row, "节点已纳入本次运行的完整图谱");
        dom.graphInventoryBody.append(row);
      });
      dom.graphInventoryEmpty.hidden = filtered.length > 0;
      return;
    }

    const filtered = edges.filter((edge) => {
      const from = nodeById.get(edge.from_node_id);
      const to = nodeById.get(edge.to_node_id);
      const searchable = [
        edge.id,
        edge.relation,
        edge.detail,
        edge.evidence_url,
        from?.label,
        from?.id,
        to?.label,
        to?.id,
      ].join(" ").toLowerCase();
      return !query || searchable.includes(query);
    });
    dom.graphInventorySummary.textContent = `显示 ${number(filtered.length)} / ${number(edges.length)} 条关系`;
    filtered.forEach((edge) => {
      const from = nodeById.get(edge.from_node_id);
      const to = nodeById.get(edge.to_node_id);
      const row = makeElement("tr");
      addCell(row, edge.relation || "未命名关系", edge.id);
      addCell(row, "typed edge", edge.relation || "未标注");
      addCell(
        row,
        `${from?.label || edge.from_node_id} → ${to?.label || edge.to_node_id}`,
        `${edge.from_node_id} → ${edge.to_node_id}`,
      );
      addCell(row, edge.detail || "未附说明", edge.evidence_url || "未附证据 URL");
      dom.graphInventoryBody.append(row);
    });
    dom.graphInventoryEmpty.hidden = filtered.length > 0;
  }

  function effectiveSourceStatus(source) {
    const status = statusMap().get(source.id);
    const run = acquisitionMap().get(source.id);
    return status?.status || (run?.status === "succeeded" ? "observed" : run?.status) || "pending";
  }

  function renderSources() {
    clear(dom.sourceTable);
    const sources = sourceList();
    const statuses = statusMap();
    const runs = acquisitionMap();
    const query = state.sourceQuery.trim().toLowerCase();
    const filtered = sources.filter((source) => {
      const status = effectiveSourceStatus(source);
      const matchesFilter = state.sourceFilter === "all"
        || (state.sourceFilter === "observed" && ["observed", "succeeded"].includes(status))
        || (state.sourceFilter === "blocked" && ["blocked", "failed", "pending", "empty"].includes(status));
      const text = `${source.name} ${source.id} ${source.role} ${source.acquisition?.method || ""}`.toLowerCase();
      return matchesFilter && (!query || text.includes(query));
    });
    filtered.forEach((source) => {
      const status = effectiveSourceStatus(source);
      const sourceStatus = statuses.get(source.id);
      const run = runs.get(source.id);
      const row = makeElement("tr");
      const identity = makeElement("td");
      identity.append(makeElement("strong", "", source.name || source.id));
      identity.append(makeElement("span", "", source.id));
      const role = makeElement("td");
      role.append(makeElement("span", "source-role", roleLabel(source.role)));
      role.append(makeElement("span", "", `${source.topic_ids?.length || 0} 个主题 · ${source.element_ids?.length || 0} 个要素`));
      const entry = makeElement("td");
      entry.append(makeElement("span", "source-method", methodLabel(source.acquisition?.method)));
      entry.append(makeElement("span", "source-endpoint", source.acquisition?.endpoint || "未提供入口"));
      const result = makeElement("td");
      result.append(createBadge(status));
      result.append(makeElement("span", "", sourceStatus?.last_run_at ? dateTime(sourceStatus.last_run_at) : run?.error_code || "尚未形成结果"));
      const evidence = makeElement("td");
      evidence.append(makeElement("strong", "", number(sourceStatus?.evidence_count || 0)));
      const link = createExternalLink("打开入口", source.acquisition?.endpoint);
      if (link) evidence.append(link);
      row.append(identity, role, entry, result, evidence);
      dom.sourceTable.append(row);
    });
    dom.sourceEmpty.hidden = filtered.length > 0;
  }

  function renderContent() {
    clear(dom.contentList);
    const sources = sourceMap();
    const evidenceById = new Map(evidenceList().map((item) => [item.id, item]));
    const query = state.contentQuery.trim().toLowerCase();
    const filtered = contentList().filter((item) => {
      const matchesFilter = state.contentFilter === "all" || item.status === state.contentFilter;
      const source = sources.get(item.source_id);
      const evidence = item.evidence_id ? evidenceById.get(item.evidence_id) : null;
      const text = `${item.title} ${item.source_id} ${source?.name || ""} ${item.evidence_id || ""} ${item.error_code || ""}`.toLowerCase();
      return matchesFilter && (!query || text.includes(query)) && Boolean(item);
    });
    filtered.forEach((item) => {
      const source = sources.get(item.source_id);
      const evidence = item.evidence_id ? evidenceById.get(item.evidence_id) : null;
      const card = makeElement("article", `content-item is-${item.status}`);
      const copy = makeElement("div");
      copy.append(makeElement("h3", "", item.title || item.url));
      copy.append(makeElement("p", "", `${source?.name || item.source_id} · ${item.url}`));
      const meta = makeElement("div", "content-meta");
      meta.append(makeElement("span", "", item.published_at ? `发布 ${date(item.published_at)}` : "未提供发布日期"));
      meta.append(makeElement("span", "", item.character_count ? `${number(item.character_count)} 字` : item.error_code || "无全文"));
      if (evidence) meta.append(makeElement("span", "", `证据 ${evidence.id}`));
      const stateCell = makeElement("div");
      stateCell.append(createBadge(item.status));
      if (item.error_code) stateCell.append(makeElement("span", "", item.error_code));
      const action = createAction(item.relative_path ? "打开全文" : "查看记录", "content-open", () => openContent(item));
      if (!item.relative_path && item.status !== "failed" && item.status !== "blocked") action.disabled = true;
      card.append(copy, meta, stateCell, action);
      dom.contentList.append(card);
    });
    dom.contentEmpty.hidden = filtered.length > 0;
  }

  function evidenceForStory(story) {
    const evidence = evidenceList();
    const signals = signalMap();
    for (const signalId of story.signal_ids || []) {
      const signal = signals.get(signalId);
      const match = evidence.find((item) => item.id === signalId || item.url === signal?.url);
      if (match) return match;
    }
    return evidence.find((item) => item.source_id === story.primary_source_id) || null;
  }

  function renderBrief() {
    const brief = state.run.report.brief || { stories: [] };
    const sources = sourceMap();
    dom.dailyHeading.textContent = `${brief.domain || state.run.manifest.domain} · Daily Brief`;
    dom.dailyWindow.textContent = `${date(brief.window_start)} 至 ${date(brief.generated_at)}`;
    clear(dom.briefList);
    storyList().forEach((story, index) => {
      const source = sources.get(story.primary_source_id);
      const evidence = evidenceForStory(story);
      const card = makeElement("article", "brief-story");
      card.append(makeElement("h3", "", `${String(index + 1).padStart(2, "0")} · ${story.title}`));
      card.append(makeElement("p", "", `${source?.name || story.primary_source_id} · ${story.event_type} · ${story.topic_ids.length} 个主题`));
      const meta = makeElement("div", "brief-meta");
      meta.append(makeElement("span", "", `判断分 ${percent(story.score)}`));
      meta.append(makeElement("span", "", `交叉印证 ${percent(story.corroboration)}`));
      const action = createAction(evidence ? "回到证据与全文" : "查看来源入口", "evidence-open", () => {
        if (evidence) openEvidence(evidence);
        else {
          const url = safeExternalUrl(source?.acquisition?.endpoint);
          if (url) window.open(url, "_blank", "noopener,noreferrer");
        }
      });
      meta.append(action);
      card.append(meta);
      dom.briefList.append(card);
    });
    if (!storyList().length) dom.briefList.append(makeElement("p", "empty-state", "本次运行还没有日报故事。"));
    clear(dom.evidenceList);
    evidenceList().forEach((evidence) => {
      const source = sources.get(evidence.source_id);
      const item = makeElement("article", "evidence-item");
      item.append(makeElement("h3", "", evidence.title));
      item.append(makeElement("p", "", `${source?.name || evidence.source_id} · ${evidence.event_type} · ${number(evidence.content_char_count)} 字`));
      item.append(makeElement("p", "", evidence.summary || "这条证据没有附带摘要。"));
      const meta = makeElement("div", "brief-meta");
      meta.append(makeElement("span", "", `获取 ${dateTime(evidence.retrieved_at)}`));
      meta.append(createAction(evidence.content_ref ? "打开全文" : "查看证据", "evidence-open", () => openEvidence(evidence)));
      item.append(meta);
      dom.evidenceList.append(item);
    });
    if (!evidenceList().length) dom.evidenceList.append(makeElement("p", "empty-state", "本次运行没有证据记录。"));
  }

  function renderAll() {
    setRunHeader();
    renderMetrics();
    renderPipeline();
    renderControl();
    renderStoriesPreview();
    renderCoverage();
    renderArtifacts();
    renderGraph();
    renderGraphInventory();
    renderSources();
    renderContent();
    renderBrief();
  }

  function showView(view, updateUrl) {
    const validViews = ["control", "overview", "graph", "sources", "content", "brief"];
    const next = validViews.includes(view) ? view : "control";
    state.activeView = next;
    document.querySelectorAll("[data-view]").forEach((button) => {
      const active = button.dataset.view === next;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-selected", String(active));
    });
    document.querySelectorAll("[data-panel]").forEach((panel) => {
      const active = panel.dataset.panel === next;
      panel.hidden = !active;
      panel.classList.toggle("is-visible", active);
    });
    if (updateUrl) window.history.replaceState(null, "", `#${next}`);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function revokeObjectUrls() {
    state.objectUrls.forEach((url) => URL.revokeObjectURL(url));
    state.objectUrls = [];
  }

  function addFileLink(label, relativePath) {
    const file = findFile(relativePath);
    if (!file) return;
    const url = URL.createObjectURL(file);
    state.objectUrls.push(url);
    dom.drawerLinks.append(createLink(label, url));
  }

  function setDrawerBase(kicker, title, metaItems) {
    dom.drawerKicker.textContent = kicker;
    dom.drawerTitle.textContent = title;
    clear(dom.drawerMeta);
    metaItems.filter(Boolean).forEach((item) => dom.drawerMeta.append(makeElement("span", "", item)));
    clear(dom.drawerLinks);
    dom.drawerBody.textContent = "正在读取内容……";
  }

  function openDrawer() {
    state.lastFocus = document.activeElement;
    dom.drawerBackdrop.hidden = false;
    dom.drawer.classList.add("is-open");
    dom.drawer.setAttribute("aria-hidden", "false");
    document.body.classList.add("drawer-open");
    window.setTimeout(() => dom.drawerClose.focus(), 0);
  }

  function closeDrawer() {
    revokeObjectUrls();
    dom.drawer.classList.remove("is-open");
    dom.drawer.setAttribute("aria-hidden", "true");
    dom.drawerBackdrop.hidden = true;
    document.body.classList.remove("drawer-open");
    if (state.lastFocus && typeof state.lastFocus.focus === "function") state.lastFocus.focus();
  }

  function addSourceLink(source) {
    const link = createExternalLink("打开来源入口", source?.acquisition?.endpoint);
    if (link) dom.drawerLinks.append(link);
  }

  async function readArtifactText(path) {
    const file = findFile(path);
    if (file) return file.text();
    if (state.mode === "demo") return demoArtifactText(path);
    return `运行目录中没有找到 ${path}。\n\n请确认导入的是 CLI 生成的运行目录，而不是上级的验证目录。`;
  }

  function openRunGuide(domain) {
    const cleanDomain = domain.trim();
    revokeObjectUrls();
    setDrawerBase("下一次运行指南", `${cleanDomain} · 本地构建指引`, ["领域输入", cleanDomain, "工作台不执行联网任务"]);
    dom.drawerLinks.append(createLink("阅读使用者指南", "reading.html#guide"));
    dom.drawerLinks.append(createLink("打开核心引擎说明", "reading.html#engine"));
    dom.drawerBody.textContent = [
      `1. 在支持 domain-intelligence-bootstrap 的 AI 工作流中输入：${cleanDomain}`,
      "2. 让 Skill 生成并校验这个领域的 typed seed Bundle。",
      "3. 运行 dib --domain、--bundle、--fetch，指定本地输出目录。",
      "4. 回到本工作台，导入生成的运行目录。",
      "",
      "导入后，运行管理页会显示每一层的真实状态；知识图谱、信源网络、全文、证据和日报会从同一份运行产物展开。",
    ].join("\n");
    openDrawer();
  }

  function demoArtifactText(path) {
    const data = {
      "domain-profile.json": state.run.profile,
      "source-map.json": state.run.sourceMap,
      "acquisition-plan.json": state.run.plan,
      "source-activation.json": state.run.activation,
      "knowledge-graph.json": state.run.graph,
      "bootstrap-report.json": state.run.report,
      "daily-brief.json": state.run.report.brief,
      "content-inventory.json": state.run.contentInventory,
      "run-manifest.json": state.run.manifest,
    }[path];
    if (path === "content/") return "这是全文归档目录。请在“内容清单”中打开单条内容，查看规范化全文与原始响应。";
    if (path.endsWith(".md")) return markdownPreview(path);
    return JSON.stringify(data || { artifact: path, note: "演示运行没有提供该产物的独立文件。" }, null, 2);
  }

  function markdownPreview(path) {
    if (path === "knowledge-graph.md") return `# ${state.run.manifest.domain}知识图谱\n\n本演示包含 ${state.run.graph.nodes.length} 个节点与 ${state.run.graph.edges.length} 条 typed edges。完整结构请查看 knowledge-graph.json。`;
    if (path === "daily-brief.md") return storyList().map((story, index) => `${index + 1}. ${story.title}`).join("\n");
    if (path === "content-inventory.md") return contentList().map((item) => `- ${item.status} · ${item.title}`).join("\n");
    return `# ${path}\n\n这是演示运行的可读预览。导入真实运行目录后，这里会显示文件原文。`;
  }

  async function openArtifact(path) {
    revokeObjectUrls();
    setDrawerBase("运行产物", path, [artifactDescription(path), artifactState(path), state.run.manifest.run_id ? `run ${state.run.manifest.run_id}` : ""]);
    if (path !== "content/") addFileLink("下载 / 打开原文件", path);
    openDrawer();
    try {
      dom.drawerBody.textContent = await readArtifactText(path);
    } catch (error) {
      dom.drawerBody.textContent = `读取 ${path} 失败。\n\n${error instanceof Error ? error.message : String(error)}`;
    }
  }

  async function openContent(item) {
    revokeObjectUrls();
    const source = sourceMap().get(item.source_id);
    const evidence = item.evidence_id ? evidenceList().find((entry) => entry.id === item.evidence_id) : null;
    setDrawerBase("内容详情", item.title || item.url, [statusLabel(item.status), source?.name || item.source_id, item.content_hash || "无内容哈希"]);
    addSourceLink(source);
    if (item.relative_path) addFileLink("打开规范化全文", item.relative_path);
    if (item.raw_relative_path) addFileLink("打开原始响应", item.raw_relative_path);
    openDrawer();
    if (evidence) dom.drawerMeta.append(makeElement("span", "", `证据 ${evidence.id}`));
    if (!item.relative_path) {
      dom.drawerBody.textContent = `这条内容没有形成规范化全文。\n\n状态：${statusLabel(item.status)}\n原因：${item.error_code || "未记录"}\n入口：${item.url}`;
      return;
    }
    const file = findFile(item.relative_path);
    if (!file && state.mode !== "demo") {
      dom.drawerBody.textContent = `已登记全文路径，但导入目录中没有找到文件：\n${item.relative_path}\n\n请确认选择了运行目录本身，并且没有只选择其中的 JSON 文件。`;
      return;
    }
    try {
      dom.drawerBody.textContent = file ? await file.text() : demoText(item.relative_path);
    } catch (error) {
      dom.drawerBody.textContent = `读取全文失败。\n\n${error instanceof Error ? error.message : String(error)}`;
    }
  }

  async function openEvidence(evidence) {
    const item = contentForEvidence(evidence);
    if (item) {
      await openContent(item);
      dom.drawerKicker.textContent = "证据回链 · 全文入口";
      return;
    }
    revokeObjectUrls();
    const source = sourceMap().get(evidence.source_id);
    setDrawerBase("证据记录", evidence.title, [evidence.id, source?.name || evidence.source_id, evidence.content_hash]);
    addSourceLink(source);
    const link = createExternalLink("打开证据来源", evidence.url);
    if (link) dom.drawerLinks.append(link);
    openDrawer();
    dom.drawerBody.textContent = JSON.stringify(evidence, null, 2);
  }

  function demoText(path) {
    const item = contentList().find((content) => normalizePath(content.relative_path) === normalizePath(path));
    return item?.demoText || `演示运行的全文示例：\n\n${item?.title || path}\n\n这里模拟一条从来源入口归档下来的规范化内容。导入真实运行目录后，工作台会读取 content/ 下的实际 Markdown 文件。`;
  }

  function parseJson(text, path) {
    try {
      return JSON.parse(text);
    } catch (error) {
      throw new Error(`${path} 不是有效 JSON：${error instanceof Error ? error.message : String(error)}`);
    }
  }

  function isRecord(value) {
    return Boolean(value) && typeof value === "object" && !Array.isArray(value);
  }

  function validateImportedRun(parsed) {
    const errors = [];
    const objectArtifacts = [
      ["run-manifest.json", parsed["run-manifest.json"]],
      ["domain-profile.json", parsed["domain-profile.json"]],
      ["source-map.json", parsed["source-map.json"]],
      ["acquisition-plan.json", parsed["acquisition-plan.json"]],
      ["source-activation.json", parsed["source-activation.json"]],
      ["knowledge-graph.json", parsed["knowledge-graph.json"]],
      ["bootstrap-report.json", parsed["bootstrap-report.json"]],
      ["daily-brief.json", parsed["daily-brief.json"]],
      ["content-inventory.json", parsed["content-inventory.json"]],
    ];
    objectArtifacts.forEach(([name, value]) => {
      if (!isRecord(value)) errors.push(`${name} 必须是 JSON 对象`);
    });
    if (errors.length) return { ok: false, message: errors.slice(0, 5).join("；") };

    const manifest = parsed["run-manifest.json"];
    const profile = parsed["domain-profile.json"];
    const sourceMap = parsed["source-map.json"];
    const plan = parsed["acquisition-plan.json"];
    const activation = parsed["source-activation.json"];
    const graph = parsed["knowledge-graph.json"];
    const report = parsed["bootstrap-report.json"];
    const brief = parsed["daily-brief.json"];
    const contentInventory = parsed["content-inventory.json"];
    const nonEmptyString = (value) => typeof value === "string" && value.trim().length > 0;
    const checkedArray = (value, label, nonEmpty = false) => {
      if (!Array.isArray(value)) {
        errors.push(`${label} 必须是数组`);
        return [];
      }
      if (nonEmpty && value.length === 0) errors.push(`${label} 不能是空数组`);
      return value;
    };
    const validateFields = (items, label, fields) => {
      items.forEach((item, index) => {
        if (!isRecord(item)) {
          errors.push(`${label}[${index}] 必须是对象`);
          return;
        }
        fields.forEach((field) => {
          if (!nonEmptyString(item[field])) errors.push(`${label}[${index}] 缺少 ${field}`);
        });
      });
    };
    const elements = checkedArray(profile.elements, "domain-profile.elements", true);
    const requirements = checkedArray(profile.requirements, "domain-profile.requirements", true);
    const sources = checkedArray(sourceMap.sources, "source-map.sources", true);
    const experts = checkedArray(sourceMap.experts, "source-map.experts");
    const attentionEdges = checkedArray(sourceMap.edges, "source-map.edges");
    const planItems = checkedArray(plan.items, "acquisition-plan.items", true);
    const sourceStatuses = checkedArray(activation.source_statuses, "source-activation.source_statuses", true);
    const activationRuns = checkedArray(activation.runs, "source-activation.runs");
    const evidence = checkedArray(activation.evidence, "source-activation.evidence");
    const activationSignals = checkedArray(activation.signals, "source-activation.signals");
    const nodes = checkedArray(graph.nodes, "knowledge-graph.nodes", true);
    const graphEdges = checkedArray(graph.edges, "knowledge-graph.edges");
    const reportSignals = checkedArray(report.signals, "bootstrap-report.signals");
    const recommendations = checkedArray(report.attention_recommendations, "bootstrap-report.attention_recommendations");
    const stories = checkedArray(brief.stories, "daily-brief.stories");
    const contents = checkedArray(contentInventory.items, "content-inventory.items");

    validateFields(elements, "domain-profile.elements", ["id", "label", "topic_id"]);
    validateFields(requirements, "domain-profile.requirements", ["id", "question"]);
    validateFields(sources, "source-map.sources", ["id", "name", "role"]);
    validateFields(experts, "source-map.experts", ["id", "name", "community"]);
    validateFields(attentionEdges, "source-map.edges", ["from_node_id", "to_node_id", "relation"]);
    validateFields(planItems, "acquisition-plan.items", ["source_id", "method", "status", "reason"]);
    validateFields(sourceStatuses, "source-activation.source_statuses", ["source_id", "status"]);
    validateFields(activationRuns, "source-activation.runs", ["id", "source_id", "status"]);
    validateFields(evidence, "source-activation.evidence", ["id", "source_id", "title", "url"]);
    validateFields(activationSignals, "source-activation.signals", ["id", "source_id", "title", "url"]);
    validateFields(nodes, "knowledge-graph.nodes", ["id", "kind", "label"]);
    validateFields(graphEdges, "knowledge-graph.edges", ["id", "from_node_id", "to_node_id", "relation"]);
    validateFields(reportSignals, "bootstrap-report.signals", ["id", "source_id", "title", "url"]);
    validateFields(recommendations, "bootstrap-report.attention_recommendations", ["source_id"]);
    validateFields(stories, "daily-brief.stories", ["id", "title", "primary_source_id", "event_type"]);
    validateFields(contents, "content-inventory.items", ["id", "source_id", "title", "url", "status"]);

    if (!nonEmptyString(manifest.run_id)) errors.push("run-manifest.run_id 未提供");
    if (!nonEmptyString(manifest.domain)) errors.push("run-manifest.domain 未提供");
    if (!nonEmptyString(manifest.input_mode)) errors.push("run-manifest.input_mode 未提供");
    [
      ["domain-profile.json", profile.domain],
      ["knowledge-graph.json", graph.domain],
      ["bootstrap-report.json", report.domain],
      ["daily-brief.json", brief.domain],
    ].forEach(([name, domain]) => {
      if (!nonEmptyString(domain)) errors.push(`${name} 未提供 domain`);
      else if (domain !== manifest.domain) errors.push(`${name} 的 domain 与 run-manifest 不一致`);
    });

    if (!Array.isArray(manifest.artifacts) || !REQUIRED_RUN_JSON.every((name) => manifest.artifacts.includes(name))) {
      errors.push("run-manifest.artifacts 未列出完整的根目录 JSON 产物");
    }
    const checkCount = (field, actual, label) => {
      const value = manifest[field];
      if (!Number.isInteger(value) || value < 0) errors.push(`run-manifest.${field} 不是有效计数`);
      else if (value !== actual) errors.push(`run-manifest.${field} 与${label}不一致`);
    };
    checkCount("source_count", sources.length, "信源数量");
    checkCount("ready_source_count", planItems.filter((item) => item?.status === "ready").length, "可运行信源数量");
    checkCount("blocked_source_count", planItems.filter((item) => item?.status === "blocked").length, "阻断信源数量");
    checkCount("evidence_count", evidence.length, "证据数量");
    checkCount("content_count", contents.length, "内容记录数量");
    checkCount("captured_content_count", contents.filter((item) => item?.status === "captured").length, "全文数量");
    checkCount("signal_count", activationSignals.length, "信号数量");
    checkCount("story_count", stories.length, "日报故事数量");
    if (Number.isInteger(manifest.ready_source_count) && Number.isInteger(manifest.blocked_source_count)
      && manifest.ready_source_count + manifest.blocked_source_count !== sources.length) {
      errors.push("可运行信源与阻断信源数量之和不等于信源总数");
    }

    const sourceIds = new Set();
    sources.forEach((source, index) => {
      if (!isRecord(source) || !nonEmptyString(source.id)) errors.push(`source-map.sources[${index}] 缺少 id`);
      else if (sourceIds.has(source.id)) errors.push(`source-map.sources 存在重复 id：${source.id}`);
      else sourceIds.add(source.id);
    });
    const nodeIds = new Set();
    nodes.forEach((node, index) => {
      if (!isRecord(node) || !nonEmptyString(node.id)) errors.push(`knowledge-graph.nodes[${index}] 缺少 id`);
      else if (nodeIds.has(node.id)) errors.push(`knowledge-graph.nodes 存在重复 id：${node.id}`);
      else nodeIds.add(node.id);
    });
    graphEdges.forEach((edge, index) => {
      if (!isRecord(edge) || !nonEmptyString(edge.from_node_id) || !nonEmptyString(edge.to_node_id)) {
        errors.push(`knowledge-graph.edges[${index}] 缺少端点`);
      } else if (!nodeIds.has(edge.from_node_id) || !nodeIds.has(edge.to_node_id)) {
        errors.push(`knowledge-graph.edges[${index}] 引用了不存在的节点`);
      }
    });

    const coverage = report.coverage;
    if (!isRecord(coverage) || !Array.isArray(coverage.rows)) {
      errors.push("bootstrap-report.coverage 未提供有效覆盖审计");
    } else if (!Number.isInteger(coverage.total_elements) || !Number.isInteger(coverage.covered_elements)
      || typeof coverage.weighted_coverage !== "number" || coverage.total_elements !== elements.length
      || coverage.rows.length !== coverage.total_elements) {
      errors.push("bootstrap-report.coverage 缺少有效计数");
    }

    const validContentStatuses = new Set(["captured", "failed", "blocked"]);
    contents.forEach((item, index) => {
      if (!isRecord(item)) {
        errors.push(`content-inventory.items[${index}] 必须是对象`);
        return;
      }
      if (!validContentStatuses.has(item.status)) errors.push(`content-inventory.items[${index}] 状态无效`);
      if (item.status === "captured") {
        const textPath = normalizePath(item.relative_path);
        const rawPath = normalizePath(item.raw_relative_path);
        if (!textPath.startsWith("content/") || hasUnsafePath(textPath)) errors.push(`content-inventory.items[${index}] 全文路径无效`);
        if (item.raw_relative_path && (!rawPath.startsWith("content/") || hasUnsafePath(rawPath))) errors.push(`content-inventory.items[${index}] 原始响应路径无效`);
        if (!nonEmptyString(item.content_hash) || !Number.isInteger(item.character_count) || item.character_count <= 0) {
          errors.push(`content-inventory.items[${index}] 已抓取内容缺少哈希或字符数`);
        }
      }
    });

    return errors.length
      ? { ok: false, message: errors.slice(0, 6).join("；") }
      : { ok: true, message: "" };
  }

  async function importRun(files) {
    const selected = Array.from(files || []);
    if (!selected.length) return;
    try {
      if (dom.drawer.classList.contains("is-open")) closeDrawer();
      const runRoot = runRootForFiles(selected);
      if (!runRoot) {
        showToast("请通过“导入运行目录”选择运行目录本身，不要只选择单个文件。");
        return;
      }
      const jsonFiles = new Map();
      const duplicateArtifacts = new Set();
      const invalidPaths = [];
      selected.forEach((file) => {
        const path = selectedFilePath(file);
        const relative = relativeRunPath(path, runRoot);
        if (!relative) {
          invalidPaths.push(path || file.name || "未知文件");
          return;
        }
        if (ROOT_RUN_ARTIFACTS.has(relative) && relative.endsWith(".json")) {
          if (jsonFiles.has(relative)) duplicateArtifacts.add(relative);
          else jsonFiles.set(relative, file);
        }
      });
      if (invalidPaths.length) {
        showToast(`运行目录包含无法确认归属的路径，未导入：${invalidPaths.slice(0, 2).join("、")}。`);
        return;
      }
      if (duplicateArtifacts.size) {
        showToast(`运行目录存在重复根产物，未导入：${Array.from(duplicateArtifacts).join("、")}。`);
        return;
      }
      const missingArtifacts = REQUIRED_RUN_JSON.filter((name) => !jsonFiles.has(name));
      if (missingArtifacts.length) {
        showToast(`运行目录不完整，未导入真实运行：还缺少 ${missingArtifacts.join("、")}。`);
        return;
      }
      const parsed = {};
      for (const [name, file] of jsonFiles.entries()) parsed[name] = parseJson(await file.text(), name);
      const validation = validateImportedRun(parsed);
      if (!validation.ok) {
        showToast(`运行目录校验未通过，未导入真实运行：${validation.message}`);
        return;
      }
      state.files = selected;
      state.runRoot = runRoot;
      state.mode = "imported";
      state.graphInventoryMode = "nodes";
      state.graphQuery = "";
      state.run = normalizeRun({
        manifest: parsed["run-manifest.json"],
        profile: parsed["domain-profile.json"],
        sourceMap: parsed["source-map.json"],
        plan: parsed["acquisition-plan.json"],
        activation: parsed["source-activation.json"],
        graph: parsed["knowledge-graph.json"],
        report: parsed["bootstrap-report.json"],
        brief: parsed["daily-brief.json"],
        contentInventory: parsed["content-inventory.json"],
      });
      renderAll();
      showToast(`已导入 ${runRoot}：${number(state.run.contentInventory.items.length)} 条内容记录，${number(state.run.activation.evidence.length)} 条证据。`);
    } catch (error) {
      showToast(`运行目录读取失败，未导入真实运行：${error instanceof Error ? error.message : String(error)}`);
    } finally {
      dom.importInput.value = "";
    }
  }

  function normalizeRun(input) {
    const report = input.report || {};
    const activation = input.activation || report.activation || {};
    const graph = input.graph || report.knowledge_graph || { generated_at: null, domain: "", nodes: [], edges: [] };
    const sourceMapData = input.sourceMap || { experts: [], sources: [], edges: [] };
    const contentInventory = input.contentInventory || { generated_at: null, items: [] };
    const brief = input.brief || report.brief || { generated_at: null, window_start: null, domain: input.manifest?.domain || graph.domain || "", stories: [] };
    const manifest = input.manifest || {
      run_id: "unindexed-run",
      domain: input.profile?.domain || graph.domain || "未命名领域",
      generated_at: report.generated_at || new Date().toISOString(),
      input_mode: "imported_artifacts",
      source_count: sourceMapData.sources?.length || 0,
      ready_source_count: 0,
      blocked_source_count: sourceMapData.sources?.length || 0,
      evidence_count: activation.evidence?.length || 0,
      content_count: contentInventory.items?.length || 0,
      captured_content_count: contentInventory.items?.filter((item) => item.status === "captured").length || 0,
      signal_count: activation.signals?.length || 0,
      story_count: brief.stories?.length || 0,
      artifacts: ARTIFACT_ORDER,
    };
    return {
      manifest: { ...manifest, artifacts: manifest.artifacts || ARTIFACT_ORDER },
      profile: input.profile || { domain: manifest.domain, elements: [], requirements: [] },
      sourceMap: sourceMapData,
      plan: input.plan || { items: [] },
      activation: { ...activation, source_statuses: activation.source_statuses || [], runs: activation.runs || [], evidence: activation.evidence || [], signals: activation.signals || [] },
      graph: { ...graph, nodes: graph.nodes || [], edges: graph.edges || [] },
      report: { ...report, coverage: report.coverage || { total_elements: 0, covered_elements: 0, weighted_coverage: 0, rows: [] }, brief },
      contentInventory: { ...contentInventory, items: contentInventory.items || [] },
    };
  }

  function buildDemoRun() {
    const generatedAt = "2026-08-31T08:00:00Z";
    const sources = [
      { id: "demo-standards", name: "国家标准公开系统：数字孪生标准索引", role: "official_primary", topic_ids: ["standards", "architecture"], element_ids: ["definition", "architecture"], acquisition: { method: "static_html", endpoint: "https://openstd.samr.gov.cn/", stable: true } },
      { id: "demo-ogc", name: "OGC Digital Twins & Standards", role: "standards_body", topic_ids: ["interoperability", "architecture"], element_ids: ["architecture", "interop"], acquisition: { method: "static_html", endpoint: "https://www.ogc.org/", stable: true } },
      { id: "demo-university", name: "数字孪生校园案例库", role: "research", topic_ids: ["verticals", "business"], element_ids: ["vertical", "business"], acquisition: { method: "static_html", endpoint: "https://www.ncsti.gov.cn/", stable: true } },
      { id: "demo-nist", name: "NIST Digital Twin Framework", role: "official_primary", topic_ids: ["definition", "trust"], element_ids: ["definition", "trust"], acquisition: { method: "static_html", endpoint: "https://www.nist.gov/", stable: true } },
      { id: "demo-azure", name: "Azure Digital Twins Documentation", role: "platform_provider", topic_ids: ["platform", "architecture"], element_ids: ["ecosystem", "lifecycle"], acquisition: { method: "static_html", endpoint: "https://learn.microsoft.com/azure/digital-twins/", stable: true } },
      { id: "demo-feed", name: "领域专业 Newsletter", role: "professional_media", topic_ids: ["industry"], element_ids: ["business"], acquisition: { method: "rss", endpoint: "https://example.com/digital-twin.xml", stable: false } },
    ];
    const evidence = [
      { id: "demo-evidence-standard", source_id: "demo-standards", title: "数字孪生相关标准进入更新周期", url: "https://openstd.samr.gov.cn/", summary: "标准索引出现新的数字孪生条目，提示定义、架构与互操作要求正在继续细化。", published_at: generatedAt, available_at: generatedAt, retrieved_at: generatedAt, content_hash: "sha256:demo-standard", topic_ids: ["standards", "architecture"], element_ids: ["definition", "architecture"], event_type: "standard_update", importance: 0.9, originality: 1, confirmed: true, content_ref: "content/demo-standard.md", content_type: "text/markdown", content_char_count: 426 },
      { id: "demo-evidence-case", source_id: "demo-university", title: "数字孪生校园案例披露建设与验收信息", url: "https://www.ncsti.gov.cn/", summary: "案例同时提供建设范围、验收节点和后续运营线索，适合作为实际交付证据继续追踪。", published_at: generatedAt, available_at: generatedAt, retrieved_at: generatedAt, content_hash: "sha256:demo-case", topic_ids: ["verticals", "business"], element_ids: ["vertical", "business"], event_type: "validated_case", importance: 0.85, originality: 1, confirmed: true, content_ref: "content/demo-case.md", content_type: "text/markdown", content_char_count: 518 },
      { id: "demo-evidence-ogc", source_id: "demo-ogc", title: "OGC 将数字孪生放入可互操作地理数据构件讨论", url: "https://www.ogc.org/", summary: "技术论文把数字孪生与数据空间、标准构件和 AI-ready 数据连接起来。", published_at: generatedAt, available_at: generatedAt, retrieved_at: generatedAt, content_hash: "sha256:demo-ogc", topic_ids: ["interoperability", "architecture"], element_ids: ["interop", "architecture"], event_type: "architecture_release", importance: 0.82, originality: 1, confirmed: true, content_ref: "content/demo-ogc.md", content_type: "text/markdown", content_char_count: 612 },
    ];
    const content = [
      { id: "content-demo-standard", source_id: "demo-standards", evidence_id: "demo-evidence-standard", title: "数字孪生相关标准进入更新周期", url: "https://openstd.samr.gov.cn/", published_at: generatedAt, captured_at: generatedAt, content_type: "text/markdown", relative_path: "content/demo-standard.md", raw_relative_path: "content/demo-standard.html", content_hash: "sha256:demo-standard", character_count: 426, status: "captured", error_code: null },
      { id: "content-demo-case", source_id: "demo-university", evidence_id: "demo-evidence-case", title: "数字孪生校园案例披露建设与验收信息", url: "https://www.ncsti.gov.cn/", published_at: generatedAt, captured_at: generatedAt, content_type: "text/markdown", relative_path: "content/demo-case.md", raw_relative_path: "content/demo-case.html", content_hash: "sha256:demo-case", character_count: 518, status: "captured", error_code: null },
      { id: "content-demo-ogc", source_id: "demo-ogc", evidence_id: "demo-evidence-ogc", title: "OGC 将数字孪生放入可互操作地理数据构件讨论", url: "https://www.ogc.org/", published_at: generatedAt, captured_at: generatedAt, content_type: "text/markdown", relative_path: "content/demo-ogc.md", raw_relative_path: "content/demo-ogc.html", content_hash: "sha256:demo-ogc", character_count: 612, status: "captured", error_code: null },
      { id: "content-demo-nist", source_id: "demo-nist", evidence_id: null, title: "NIST Digital Twin Framework", url: "https://www.nist.gov/", published_at: null, captured_at: generatedAt, content_type: "text/markdown", relative_path: "content/demo-nist.md", raw_relative_path: "content/demo-nist.html", content_hash: "sha256:demo-nist", character_count: 308, status: "captured", error_code: null },
      { id: "content-demo-feed", source_id: "demo-feed", evidence_id: null, title: "领域专业 Newsletter", url: "https://example.com/digital-twin.xml", published_at: null, captured_at: generatedAt, content_type: "application/rss+xml", relative_path: null, raw_relative_path: null, content_hash: null, character_count: 0, status: "failed", error_code: "FEED_UNAVAILABLE" },
      { id: "content-demo-browser", source_id: "demo-azure", evidence_id: null, title: "Azure Digital Twins Documentation", url: "https://learn.microsoft.com/azure/digital-twins/", published_at: null, captured_at: generatedAt, content_type: "text/html", relative_path: null, raw_relative_path: null, content_hash: null, character_count: 0, status: "blocked", error_code: "NO_DIRECT_ADAPTER" },
    ];
    const nodes = [
      { id: "domain:数字孪生", kind: "domain", label: "数字孪生" },
      { id: "topic:architecture", kind: "topic", label: "参考架构" },
      { id: "topic:interoperability", kind: "topic", label: "互操作" },
      { id: "topic:verticals", kind: "topic", label: "垂直案例" },
      { id: "element:definition", kind: "element", label: "边界与定义" },
      { id: "element:business", kind: "element", label: "商业价值与交付" },
      { id: "source:demo-standards", kind: "source", label: "国家标准公开系统" },
      { id: "source:demo-ogc", kind: "source", label: "OGC" },
      { id: "source:demo-university", kind: "source", label: "校园案例库" },
      { id: "source:demo-nist", kind: "source", label: "NIST" },
      { id: "evidence:demo-evidence-standard", kind: "evidence", label: "标准更新" },
      { id: "evidence:demo-evidence-case", kind: "evidence", label: "校园案例" },
      { id: "evidence:demo-evidence-ogc", kind: "evidence", label: "OGC 论文" },
    ];
    const edges = [
      ["domain:数字孪生", "topic:architecture", "contains"], ["domain:数字孪生", "topic:interoperability", "contains"], ["domain:数字孪生", "topic:verticals", "contains"],
      ["topic:architecture", "element:definition", "covers_element"], ["topic:architecture", "element:business", "covers_element"], ["topic:interoperability", "element:definition", "covers_element"],
      ["topic:architecture", "source:demo-standards", "covers_topic"], ["topic:architecture", "source:demo-ogc", "covers_topic"], ["topic:verticals", "source:demo-university", "covers_topic"], ["topic:architecture", "source:demo-nist", "covers_topic"],
      ["source:demo-standards", "evidence:demo-evidence-standard", "publishes"], ["source:demo-university", "evidence:demo-evidence-case", "publishes"], ["source:demo-ogc", "evidence:demo-evidence-ogc", "publishes"],
    ].map(([from, to, relation], index) => ({ id: `edge-demo-${String(index + 1).padStart(3, "0")}`, from_node_id: from, to_node_id: to, relation, confidence: 1, observed_at: generatedAt, evidence_url: null }));
    const report = {
      generated_at: generatedAt,
      domain: "数字孪生",
      knowledge_graph: { generated_at: generatedAt, domain: "数字孪生", nodes, edges },
      activation: { generated_at: generatedAt, window_start: "2026-08-01T08:00:00Z", source_statuses: sources.map((source) => ({ source_id: source.id, status: source.id === "demo-feed" ? "failed" : source.id === "demo-azure" ? "blocked" : "observed", last_run_at: generatedAt, evidence_count: evidence.filter((item) => item.source_id === source.id).length })), runs: [], evidence, signals: evidence.map((item) => ({ id: item.id, source_id: item.source_id, title: item.title, url: item.url, published_at: item.published_at, available_at: item.available_at, topic_ids: item.topic_ids, event_type: item.event_type, importance: item.importance, summary: item.summary, originality: 1, confirmed: true, event_id: null })), knowledge_deltas: [] },
      signals: [], attention_recommendations: [], replay: {}, evaluations: [], portfolio: {},
      coverage: { total_elements: 4, covered_elements: 4, weighted_coverage: 1, rows: ["definition", "architecture", "business", "vertical"].map((id) => ({ element_id: id, coverage_ratio: 1, source_ids: sources.filter((source) => source.element_ids.includes(id)).map((source) => source.id), gap_reasons: [] })) },
      brief: { generated_at: generatedAt, window_start: "2026-08-01T08:00:00Z", domain: "数字孪生", stories: [
        { id: "story-demo-standard", title: "国家标准公开系统出现数字孪生标准更新信号", primary_source_id: "demo-standards", source_ids: ["demo-standards"], signal_ids: ["demo-evidence-standard"], topic_ids: ["standards", "architecture"], event_type: "standard_update", score: 0.86, corroboration: 0.33, first_party: true, evidence_urls: ["https://openstd.samr.gov.cn/"] },
        { id: "story-demo-ogc", title: "OGC 将数字孪生放入可互操作地理数据构件讨论", primary_source_id: "demo-ogc", source_ids: ["demo-ogc"], signal_ids: ["demo-evidence-ogc"], topic_ids: ["interoperability", "architecture"], event_type: "architecture_release", score: 0.74, corroboration: 0.33, first_party: true, evidence_urls: ["https://www.ogc.org/"] },
        { id: "story-demo-case", title: "数字孪生校园案例披露建设与验收信息", primary_source_id: "demo-university", source_ids: ["demo-university"], signal_ids: ["demo-evidence-case"], topic_ids: ["verticals", "business"], event_type: "validated_case", score: 0.71, corroboration: 0.33, first_party: true, evidence_urls: ["https://www.ncsti.gov.cn/"] },
      ] },
    };
    const activation = report.activation;
    return normalizeRun({
      manifest: { run_id: "demo-digital-twin", domain: "数字孪生", generated_at: generatedAt, input_mode: "honest_demo_data", source_count: 6, ready_source_count: 5, blocked_source_count: 1, evidence_count: 3, content_count: 6, captured_content_count: 4, signal_count: 3, story_count: 3, artifacts: ARTIFACT_ORDER },
      profile: { domain: "数字孪生", domain_aliases: ["Digital Twin"], mode: "domain_foundation", domain_intent: "从零建立数字孪生领域的知识域与可持续情报体系", elements: [{ id: "definition", label: "边界与定义" }, { id: "architecture", label: "参考架构" }, { id: "business", label: "商业价值与交付" }, { id: "vertical", label: "垂直行业案例" }] },
      sourceMap: { experts: [], sources, edges: sources.map((source) => ({ from: "demo-attention", to: source.id, relation: "attention" })) },
      plan: { generated_at: generatedAt, source_count: 6, items: sources.map((source) => ({ source_id: source.id, method: source.acquisition.method, endpoint: source.acquisition.endpoint, status: source.id === "demo-azure" ? "blocked" : "ready", reason: source.id === "demo-azure" ? "需要外部适配器" : "已有直接入口" })) },
      activation,
      graph: { generated_at: generatedAt, domain: "数字孪生", nodes, edges },
      report,
      contentInventory: { generated_at: generatedAt, items: content },
    });
  }

  function bindEvents() {
    document.querySelectorAll("[data-view]").forEach((button) => {
      button.addEventListener("click", () => showView(button.dataset.view, true));
    });
    document.querySelectorAll("[data-view-target]").forEach((button) => {
      button.addEventListener("click", () => showView(button.dataset.viewTarget, true));
    });
    dom.runGuideForm.addEventListener("submit", (event) => {
      event.preventDefault();
      const domain = dom.controlDomainInput.value.trim();
      if (!domain) {
        showToast("请先输入一个领域名称或关键词。");
        dom.controlDomainInput.focus();
        return;
      }
      openRunGuide(domain);
    });
    document.querySelectorAll("[data-source-filter]").forEach((button) => {
      button.addEventListener("click", () => {
        state.sourceFilter = button.dataset.sourceFilter;
        document.querySelectorAll("[data-source-filter]").forEach((tab) => {
          const active = tab === button;
          tab.classList.toggle("is-active", active);
          tab.setAttribute("aria-selected", String(active));
        });
        renderSources();
      });
    });
    document.querySelectorAll("[data-content-filter]").forEach((button) => {
      button.addEventListener("click", () => {
        state.contentFilter = button.dataset.contentFilter;
        document.querySelectorAll("[data-content-filter]").forEach((tab) => {
          const active = tab === button;
          tab.classList.toggle("is-active", active);
          tab.setAttribute("aria-selected", String(active));
        });
        renderContent();
      });
    });
    document.querySelectorAll("[data-graph-inventory]").forEach((button) => {
      button.addEventListener("click", () => {
        state.graphInventoryMode = button.dataset.graphInventory;
        document.querySelectorAll("[data-graph-inventory]").forEach((tab) => {
          const active = tab === button;
          tab.classList.toggle("is-active", active);
          tab.setAttribute("aria-selected", String(active));
        });
        renderGraphInventory();
      });
    });
    dom.sourceSearch.addEventListener("input", (event) => {
      state.sourceQuery = event.target.value;
      renderSources();
    });
    dom.contentSearch.addEventListener("input", (event) => {
      state.contentQuery = event.target.value;
      renderContent();
    });
    dom.graphSearch.addEventListener("input", (event) => {
      state.graphQuery = event.target.value;
      renderGraphInventory();
    });
    dom.importInput.addEventListener("change", (event) => importRun(event.target.files));
    dom.drawerClose.addEventListener("click", closeDrawer);
    dom.drawerBackdrop.addEventListener("click", closeDrawer);
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && dom.drawer.classList.contains("is-open")) closeDrawer();
    });
    window.addEventListener("hashchange", () => showView(window.location.hash.slice(1), false));
  }

  state.run = buildDemoRun();
  bindEvents();
  renderAll();
  showView(window.location.hash.slice(1) || "control", false);
})();
