const domainData = {
  "digital-tourism": {
    name: "数字文旅产业",
    summary: "先把行业的参与者、业务链和变化来源找全，再决定你要深入哪一条线。",
    map: "政策与规则 · 技术与产品 · 项目与场景 · 市场与运营",
    people: "主管部门 · 平台企业 · 项目运营者 · 研究者",
    sources: "政策原文 · 项目/招采 · 厂商一手 · 行业解释",
    engine: "领域词典 + 人物/机构图 + 来源组合 + 每日简报",
    next: "先把领域看全，再进入具体问题和日常追踪",
  },
  robotics: {
    name: "机器人产业",
    summary: "先分清本体、核心零部件、模型、场景和交付链，再看哪些方向真的在落地。",
    map: "本体与零部件 · 模型与控制 · 场景应用 · 供应链与交付",
    people: "研发团队 · 厂商与集成商 · 下游客户 · 标准与研究机构",
    sources: "标准原文 · 产品发布 · 招投标/客户 · 工程实践",
    engine: "技术词典 + 产业链图 + 产品/项目档案 + 每日简报",
    next: "从产业链地图里选一条线，继续建立长期观察",
  },
  "low-altitude": {
    name: "低空经济",
    summary: "先建立政策、基础设施、飞行器、运营场景和监管要求之间的全景关系。",
    map: "政策与空域 · 飞行器与设施 · 运营场景 · 安全与监管",
    people: "主管部门 · 飞行器企业 · 运营方 · 空域与安全专家",
    sources: "政策/标准 · 试点项目 · 企业一手 · 运营数据",
    engine: "领域词典 + 政策图谱 + 项目与主体档案 + 每日简报",
    next: "从全景关系里找到最值得跟踪的应用方向",
  },
  education: {
    name: "职业教育",
    summary: "先看政策、学校、专业、课程、企业需求和就业结果如何连成一条教育链。",
    map: "政策与专业 · 学校与课程 · 企业需求 · 教师与学习结果",
    people: "教育主管部门 · 学校与教师 · 用人企业 · 研究者",
    sources: "政策原文 · 学校实践 · 企业招聘 · 研究解释",
    engine: "概念词典 + 学校/企业图 + 实践证据库 + 每日简报",
    next: "再从领域底图里选择一个专业方向深入",
  },
};

const domainInput = document.querySelector("#domain-input");
const domainBuild = document.querySelector("#domain-build");
const domainPanel = document.querySelector("#domain-panel");
const domainSuggestions = [...document.querySelectorAll(".domain-suggestion")];
const DOMAIN_NAME_FALLBACK_CHUNK_SIZE = 4;
const DOMAIN_NAME_TERMS = [
  "数字文旅产业",
  "机器人产业",
  "低空经济",
  "职业教育",
  "跨领域",
  "量子农业",
  "农业科技",
  "科技产业链",
  "观察实验室",
  "产业链",
  "实验室",
  "知识引擎",
  "专业领域",
  "行业社区",
].sort((left, right) => Array.from(right).length - Array.from(left).length);

function splitDomainName(value) {
  const text = String(value);
  if (typeof Intl !== "undefined" && typeof Intl.Segmenter === "function") {
    const segments = Array.from(new Intl.Segmenter("zh-CN", { granularity: "word" }).segment(text));
    const chunks = [];
    let start = 0;
    let segmentIndex = 0;
    while (start < text.length) {
      const term = DOMAIN_NAME_TERMS.find((candidate) => text.startsWith(candidate, start));
      if (term) {
        chunks.push(term);
        start += term.length;
        continue;
      }

      while (segments[segmentIndex] && segments[segmentIndex].index < start) segmentIndex += 1;
      const segment = segments[segmentIndex];
      if (!segment || segment.index !== start) break;
      chunks.push(segment.segment);
      start += segment.segment.length;
      segmentIndex += 1;
    }
    if (start === text.length) return chunks;
  }

  const characters = Array.from(text);
  const chunks = [];
  let start = 0;
  while (start < characters.length) {
    const term = DOMAIN_NAME_TERMS.find((candidate) => text.startsWith(candidate, start));
    if (term) {
      chunks.push(term);
      start += Array.from(term).length;
      continue;
    }
    chunks.push(characters.slice(start, start + DOMAIN_NAME_FALLBACK_CHUNK_SIZE).join(""));
    start += DOMAIN_NAME_FALLBACK_CHUNK_SIZE;
  }
  return chunks;
}

function renderDomainName(target, value) {
  target.replaceChildren();
  splitDomainName(value).forEach((segment) => {
    const chunk = document.createElement("span");
    chunk.className = "domain-title-chunk";
    chunk.textContent = segment;
    target.append(chunk);
  });
}

function customDomainData(name) {
  return {
    name,
    summary: "先围绕这个领域补齐边界、参与者、关键变化和可信来源，再逐步形成你的长期观察。",
    map: "政策与规则 · 核心技术与产品 · 企业与项目 · 人物与机构",
    people: "主管部门 · 头部企业 · 一线实践者 · 研究与解释者",
    sources: "官方原文 · 项目记录 · 企业一手 · 行业社区",
    engine: "领域词典 + 参与者图 + 信源组合 + 每日简报",
    next: "先把这个领域看全，再进入具体问题和日常追踪",
  };
}

function updateDomain(key) {
  if (!domainInput || !domainPanel) return;
  const inputName = domainInput.value.trim();
  const data = domainData[key] || (inputName ? customDomainData(inputName) : null);
  if (!data) return;

  domainInput.value = data.name;
  domainSuggestions.forEach((suggestion) => {
    const isActive = suggestion.dataset.domainKey === key;
    suggestion.classList.toggle("is-active", isActive);
    suggestion.setAttribute("aria-pressed", String(isActive));
  });

  domainPanel.classList.add("is-changing");
  window.setTimeout(() => {
    Object.entries(data).forEach(([field, value]) => {
      const target = domainPanel.querySelector("[data-field=\"" + field + "\"]");
      if (!target) return;
      if (field === "name") {
        renderDomainName(target, value);
        return;
      }
      target.textContent = value;
    });
    domainPanel.classList.remove("is-changing");
  }, 110);
}

const initialDomainTitle = domainPanel?.querySelector('[data-field="name"]');
if (initialDomainTitle) renderDomainName(initialDomainTitle, initialDomainTitle.textContent);

domainSuggestions.forEach((suggestion) => {
  suggestion.setAttribute("aria-pressed", String(suggestion.classList.contains("is-active")));
  suggestion.addEventListener("click", () => updateDomain(suggestion.dataset.domainKey));
});

domainBuild?.addEventListener("click", () => updateDomain());
domainInput?.addEventListener("keydown", (event) => {
  if (event.key !== "Enter") return;
  event.preventDefault();
  updateDomain();
});

const nav = document.querySelector("[data-nav]");
const updateNav = () => nav?.classList.toggle("is-scrolled", window.scrollY > 24);
updateNav();
window.addEventListener("scroll", updateNav, { passive: true });

const revealItems = [...document.querySelectorAll(".reveal")];
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (reducedMotion || !("IntersectionObserver" in window)) {
  revealItems.forEach((item) => item.classList.add("is-visible"));
} else {
  const revealObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -4%" },
  );
  revealItems.forEach((item) => revealObserver.observe(item));
}
