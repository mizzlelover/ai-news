const scenarioData = {
  tourism: {
    question: "是否投入新的县域文旅线路？",
    type: "市场信号",
    headline: "周边目的地开始把研学客群从团队游转向周末小团。",
    why: "这不是“市场已经验证”的结论，但说明竞品正在争夺同一客群，应优先补查客单价、复购和淡季承载能力。",
    sources: "项目运营方 · 行业解释源",
    status: "候选信号，等待数据确认",
    gap: "本地游客结构与真实转化率",
  },
  manufacturing: {
    question: "明年要不要替换一类关键设备供应商？",
    type: "供应链信号",
    headline: "两家下游工厂开始调整设备验收指标，交付周期也出现分化。",
    why: "先不要只看报价。指标变化可能影响换线成本和良率，应补查现场验证、备件周期与已有客户的连续运行记录。",
    sources: "下游采购方 · 厂商技术源",
    status: "早期信号，等待现场证据",
    gap: "同工况下的连续运行表现",
  },
  education: {
    question: "一种新的课程方法是否已经可复制？",
    type: "落地信号",
    headline: "三个学校试点开始公开课程结构，但学习结果仍然缺少横向比较。",
    why: "从“有人提出”走到“可以复制”还差一段。下一步应区分课程设计、教师培训和学生结果，不把案例数量当成效果证据。",
    sources: "学校试点 · 研究解释源",
    status: "试点阶段，结果待核",
    gap: "跨学校、跨周期的学习结果",
  },
  practitioner: {
    question: "未来三个月，什么最可能改变我的工作方式？",
    type: "变化信号",
    headline: "一个原本只在小范围讨论的规则变化，开始被客户和同行同时提及。",
    why: "单条讨论还不能成为结论，但跨角色出现意味着值得建立观察项。先确认规则原文，再看它是否会进入合同、流程或采购要求。",
    sources: "客户反馈 · 行业社区 · 原始文件",
    status: "观察项，等待权威确认",
    gap: "规则生效时间与实际执行范围",
  },
};

const tabs = [...document.querySelectorAll(".scenario-tab")];
const panel = document.querySelector("#scenario-panel");

function updateScenario(key) {
  const data = scenarioData[key];
  const activeTab = tabs.find((tab) => tab.dataset.scenario === key);
  if (!data || !activeTab || !panel) return;

  tabs.forEach((tab) => {
    const isActive = tab === activeTab;
    tab.classList.toggle("is-active", isActive);
    tab.setAttribute("aria-selected", String(isActive));
    tab.tabIndex = isActive ? 0 : -1;
  });

  panel.classList.add("is-changing");
  panel.setAttribute("aria-labelledby", activeTab.id);
  window.setTimeout(() => {
    Object.entries(data).forEach(([field, value]) => {
      const target = panel.querySelector(`[data-field="${field}"]`);
      if (target) target.textContent = value;
    });
    panel.classList.remove("is-changing");
  }, 110);
}

tabs.forEach((tab, index) => {
  tab.addEventListener("click", () => updateScenario(tab.dataset.scenario));
  tab.addEventListener("keydown", (event) => {
    const directions = { ArrowDown: 1, ArrowRight: 1, ArrowUp: -1, ArrowLeft: -1 };
    if (!(event.key in directions)) return;
    event.preventDefault();
    const nextIndex = (index + directions[event.key] + tabs.length) % tabs.length;
    const nextTab = tabs[nextIndex];
    nextTab.focus();
    updateScenario(nextTab.dataset.scenario);
  });
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
