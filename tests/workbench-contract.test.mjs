import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import test from "node:test";

const workbenchSource = readFileSync(new URL("../demo/workbench.js", import.meta.url), "utf8");
const requiredRunJson = [
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

function extractFunction(source, name) {
  const start = source.indexOf(`function ${name}(`);
  if (start < 0) throw new Error(`function ${name} not found`);
  const opening = source.indexOf("{", start);
  let depth = 0;
  let quote = "";
  let escaped = false;
  for (let index = opening; index < source.length; index += 1) {
    const character = source[index];
    if (quote) {
      if (escaped) escaped = false;
      else if (character === "\\") escaped = true;
      else if (character === quote) quote = "";
      continue;
    }
    if (["'", '"', "`"].includes(character)) {
      quote = character;
      continue;
    }
    if (character === "{") depth += 1;
    if (character === "}") {
      depth -= 1;
      if (depth === 0) return source.slice(start, index + 1);
    }
  }
  throw new Error(`function ${name} is incomplete`);
}

const validateImportedRun = new Function(
  "REQUIRED_RUN_JSON",
  [
    extractFunction(workbenchSource, "normalizePath"),
    extractFunction(workbenchSource, "hasUnsafePath"),
    extractFunction(workbenchSource, "isRecord"),
    extractFunction(workbenchSource, "validateImportedRun"),
    "return validateImportedRun;",
  ].join("\n"),
)(requiredRunJson);

function validRun() {
  const source = { id: "source-1", name: "Source 1", role: "other" };
  const seedSignal = { id: "seed-1", source_id: source.id, title: "Seed", url: "https://example.org/seed" };
  const activatedSignal = { id: "activated-1", source_id: source.id, title: "Activated", url: "https://example.org/activated" };
  return {
    "run-manifest.json": {
      run_id: "run-1",
      domain: "test-domain",
      input_mode: "test",
      source_count: 1,
      ready_source_count: 1,
      blocked_source_count: 0,
      evidence_count: 0,
      content_count: 0,
      captured_content_count: 0,
      signal_count: 2,
      story_count: 0,
      artifacts: requiredRunJson,
    },
    "domain-profile.json": {
      domain: "test-domain",
      elements: [{ id: "element-1", label: "Element 1", topic_id: "topic-1" }],
      requirements: [{ id: "requirement-1", question: "What changed?" }],
    },
    "source-map.json": { sources: [source], experts: [], edges: [] },
    "acquisition-plan.json": { items: [{ source_id: source.id, method: "static_html", status: "ready", reason: "configured" }] },
    "source-activation.json": {
      source_statuses: [{ source_id: source.id, status: "observed" }],
      runs: [],
      evidence: [],
      signals: [activatedSignal],
    },
    "knowledge-graph.json": {
      domain: "test-domain",
      nodes: [
        { id: "domain:test-domain", kind: "domain", label: "test-domain" },
        { id: "element:element-1", kind: "element", label: "Element 1" },
        { id: `source:${source.id}`, kind: "source", label: source.name },
      ],
      edges: [],
    },
    "bootstrap-report.json": {
      domain: "test-domain",
      signals: [seedSignal, activatedSignal],
      attention_recommendations: [{ source_id: source.id }],
      coverage: {
        total_elements: 1,
        covered_elements: 1,
        weighted_coverage: 1,
        rows: [{ element_id: "element-1", source_ids: [] }],
      },
    },
    "daily-brief.json": { domain: "test-domain", stories: [] },
    "content-inventory.json": { items: [] },
  };
}

test("accepts retained and newly activated signals as the complete report count", () => {
  const parsed = validRun();

  assert.deepEqual(validateImportedRun(parsed), { ok: true, message: "" });
});

test("rejects a manifest count that disagrees with the complete report", () => {
  const parsed = validRun();
  parsed["run-manifest.json"].signal_count = 1;

  const result = validateImportedRun(parsed);

  assert.equal(result.ok, false);
  assert.match(result.message, /日报信号数量/);
});
