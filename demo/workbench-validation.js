(function (root) {
  "use strict";

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

  function normalizePath(value) {
    return String(value || "")
      .replaceAll("\\", "/")
      .replace(/^\.\//, "")
      .replace(/^\/+/, "");
  }

  function hasUnsafePath(value) {
    return normalizePath(value).split("/").some((segment) => segment === "." || segment === "..");
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
    const validateArrayFields = (items, label, fields) => {
      items.forEach((item, index) => {
        if (!isRecord(item)) return;
        fields.forEach((field) => {
          if (!Array.isArray(item[field])) errors.push(`${label}[${index}] 的 ${field} 必须是数组`);
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
    validateArrayFields(stories, "daily-brief.stories", ["source_ids", "signal_ids", "topic_ids"]);

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
    checkCount("signal_count", reportSignals.length, "日报信号数量");
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
    const coverageRows = isRecord(coverage) && Array.isArray(coverage.rows) ? coverage.rows : [];
    validateFields(coverageRows, "bootstrap-report.coverage.rows", ["element_id"]);
    validateArrayFields(coverageRows, "bootstrap-report.coverage.rows", ["source_ids"]);

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
        if (!rawPath.startsWith("content/") || hasUnsafePath(rawPath)) errors.push(`content-inventory.items[${index}] 原始响应路径无效`);
        if (!nonEmptyString(item.content_hash) || !Number.isInteger(item.character_count) || item.character_count <= 0) {
          errors.push(`content-inventory.items[${index}] 已抓取内容缺少哈希或字符数`);
        }
      }
    });

    return errors.length
      ? { ok: false, message: errors.slice(0, 6).join("；") }
      : { ok: true, message: "" };
  }

  const api = { REQUIRED_RUN_JSON, normalizePath, hasUnsafePath, isRecord, validateImportedRun };
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.PrivateIntelligenceWorkbenchValidation = api;
})(typeof globalThis === "object" ? globalThis : this);
