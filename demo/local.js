(function () {
  "use strict";

  const state = { jobId: "", polling: false };
  const dom = {
    health: document.getElementById("health-badge"),
    domainForm: document.getElementById("domain-form"),
    domain: document.getElementById("domain-input"),
    start: document.getElementById("start-button"),
    settingsForm: document.getElementById("settings-form"),
    endpoint: document.getElementById("endpoint-input"),
    model: document.getElementById("model-input"),
    apiKey: document.getElementById("api-key-input"),
    settingsStatus: document.getElementById("settings-status"),
    setupMessage: document.getElementById("setup-message"),
    progress: document.getElementById("progress-section"),
    progressPercent: document.getElementById("progress-percent"),
    progressBar: document.getElementById("progress-bar"),
    progressMessage: document.getElementById("progress-message"),
    progressSteps: document.getElementById("progress-steps"),
    result: document.getElementById("run-result"),
    runsCount: document.getElementById("runs-count"),
    runsList: document.getElementById("runs-list"),
  };

  function setHealth(ready, label) {
    dom.health.className = `health-badge ${ready ? "is-ready" : "is-offline"}`;
    dom.health.textContent = label;
  }

  function setSetupMessage(message) {
    dom.setupMessage.textContent = message;
    dom.setupMessage.hidden = !message;
  }

  async function request(path, options) {
    const response = await fetch(path, options);
    let payload = {};
    try { payload = await response.json(); } catch {}
    if (!response.ok) {
      const error = new Error(payload.message || `请求失败（${response.status}）`);
      error.status = response.status;
      error.payload = payload;
      throw error;
    }
    return payload;
  }

  function jsonOptions(payload) {
    return { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) };
  }

  async function refreshHealth() {
    try {
      const payload = await request("/api/health");
      setHealth(payload.provider_configured ? true : false, payload.provider_configured ? "本地服务已就绪" : "等待连接 AI");
    } catch {
      setHealth(false, "本地服务未启动");
    }
  }

  function phaseRank(phase) {
    return { queued: 0, seed: 1, map: 2, capture: 3, archive: 4, complete: 5 }[phase] || 0;
  }

  function renderProgress(job) {
    const percent = Math.max(0, Math.min(100, Number(job.percent || 0)));
    dom.progress.hidden = false;
    dom.progressPercent.textContent = `${percent}%`;
    dom.progressBar.style.width = `${percent}%`;
    dom.progressMessage.textContent = job.message || "正在处理……";
    const current = phaseRank(job.phase);
    dom.progressSteps.querySelectorAll("[data-phase]").forEach((step) => {
      const rank = phaseRank(step.dataset.phase);
      step.classList.toggle("is-active", rank === current && job.status !== "complete");
      step.classList.toggle("is-complete", rank < current || job.status === "complete");
    });
  }

  function renderResult(job) {
    dom.result.hidden = false;
    dom.result.className = `run-result ${job.status === "failed" ? "is-error" : ""}`;
    while (dom.result.firstChild) dom.result.removeChild(dom.result.firstChild);
    const text = document.createElement("span");
    text.textContent = job.status === "failed" ? `这次建立没有完成：${job.error || "暂时没有更多错误信息"}` : `“${job.domain}”已经建立。完整产物、知识图谱、全文清单和日报都在这次运行的工作台里。`;
    dom.result.append(text);
    if (job.status === "complete") {
      const link = document.createElement("a");
      link.href = `/demo/workbench.html?run=${encodeURIComponent(job.id)}#overview`;
      link.textContent = "打开这次领域工作台 ↗";
      dom.result.append(link);
    }
  }

  async function pollJob(jobId) {
    if (state.polling) return;
    state.polling = true;
    try {
      for (;;) {
        const job = await request(`/api/runs/${encodeURIComponent(jobId)}`);
        renderProgress(job);
        if (job.status === "complete" || job.status === "failed") {
          renderResult(job);
          dom.start.disabled = false;
          await loadRuns();
          break;
        }
        await new Promise((resolve) => window.setTimeout(resolve, 1200));
      }
    } catch (error) {
      renderResult({ status: "failed", error: error.message, domain: dom.domain.value });
      dom.start.disabled = false;
    } finally {
      state.polling = false;
    }
  }

  async function saveSettings(event) {
    event.preventDefault();
    dom.settingsStatus.textContent = "正在保存……";
    dom.settingsStatus.classList.remove("is-saved");
    try {
      await request("/api/settings", jsonOptions({ endpoint: dom.endpoint.value.trim(), model: dom.model.value.trim(), api_key: dom.apiKey.value }));
      dom.settingsStatus.textContent = "已保存到当前本地运行进程。可以开始建立领域。";
      dom.settingsStatus.classList.add("is-saved");
      setSetupMessage("");
      await refreshHealth();
    } catch (error) {
      dom.settingsStatus.textContent = error.message;
      dom.settingsStatus.classList.remove("is-saved");
    }
  }

  async function startBuild(event) {
    event.preventDefault();
    const domain = dom.domain.value.trim();
    if (!domain) return;
    setSetupMessage("");
    dom.start.disabled = true;
    dom.result.hidden = true;
    try {
      const payload = await request("/api/runs", jsonOptions({ domain }));
      state.jobId = payload.id;
      renderProgress({ id: payload.id, domain, status: "queued", phase: "queued", percent: 0, message: payload.message });
      await pollJob(payload.id);
    } catch (error) {
      dom.start.disabled = false;
      if (error.status === 409 || error.payload?.status === "needs_setup") {
        setSetupMessage("还差一步：先在右侧填写 AI 接口地址和模型名称，再保存连接设置。保存后，回到这里再次点击“开始建立我的领域”。");
        dom.endpoint.focus();
      } else {
        setSetupMessage(error.message);
      }
    }
  }

  function runStatus(job) {
    if (job.status === "complete") return "已建立";
    if (job.status === "failed") return "未完成";
    if (job.status === "running") return "建立中";
    return "排队中";
  }

  async function loadRuns() {
    try {
      const payload = await request("/api/runs");
      const runs = Array.isArray(payload.runs) ? payload.runs : [];
      dom.runsCount.textContent = `${runs.length} 个领域`;
      while (dom.runsList.firstChild) dom.runsList.removeChild(dom.runsList.firstChild);
      if (!runs.length) {
        const empty = document.createElement("p");
        empty.className = "empty-state";
        empty.textContent = "还没有本地运行记录。输入一个领域，就从这里开始。";
        dom.runsList.append(empty);
        return;
      }
      runs.forEach((job) => {
        const card = document.createElement("article");
        card.className = "run-card";
        const title = document.createElement("h3");
        title.textContent = job.domain || "未命名领域";
        const detail = document.createElement("p");
        detail.textContent = job.message || "本地运行记录";
        const footer = document.createElement("div");
        footer.className = "run-card-footer";
        const status = document.createElement("span");
        status.className = `run-status ${job.status === "failed" ? "is-failed" : ""}`;
        status.textContent = runStatus(job);
        footer.append(status);
        if (job.status === "complete") {
          const link = document.createElement("a");
          link.href = `/demo/workbench.html?run=${encodeURIComponent(job.id)}#overview`;
          link.textContent = "打开工作台 ↗";
          footer.append(link);
        }
        card.append(title, detail, footer);
        dom.runsList.append(card);
      });
    } catch {
      dom.runsCount.textContent = "暂不可读取";
    }
  }

  dom.settingsForm.addEventListener("submit", saveSettings);
  dom.domainForm.addEventListener("submit", startBuild);
  refreshHealth();
  loadRuns();
})();
