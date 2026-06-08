const demoSamples = {
  spice: `2026-06-07 09:14:01 [INFO] spectre started with runset ./runsets/top_tran.scs
2026-06-07 09:14:02 [WARN] PDK corner file lp_1p8.scs loaded after tt_1p8.scs
2026-06-07 09:14:03 [WARN] Missing model parameter: vth0 in device nmos_1p8
2026-06-07 09:14:06 [ERROR] SPICE simulation failed: convergence not reached at time=4.2ns
2026-06-07 09:14:06 [ERROR] Newton iteration failed near instance XU_PLL.M1
2026-06-07 09:14:07 [INFO] last accepted timestep was 1e-15`,
  netlist: `2026-06-07 10:31:18 [INFO] ngspice reading netlist ./build/top.sp
2026-06-07 10:31:18 [INFO] include ./libs/io_cells.sp
2026-06-07 10:31:19 [ERROR] Netlist parser: undefined subckt INV_X1 at instance U42
2026-06-07 10:31:19 [ERROR] Cannot find cell NAND2_X1 referenced by top_level
2026-06-07 10:31:20 [WARN] netlist elaboration stopped before transient analysis`,
  license: `2026-06-07 11:22:11 [INFO] calibre DRC job submitted on host build-eda-02
2026-06-07 11:22:12 [ERROR] License checkout failed: feature CALIBRE_DRC not found
2026-06-07 11:22:12 [ERROR] lmgrd server returned checkout denied for user eda_demo
2026-06-07 11:22:13 [WARN] DRC run aborted before loading rule deck`
};

const demoCases = {
  simulation_convergence: {
    case_id: "case_003",
    title: "SPICE convergence failed after PDK corner switch",
    score: 2.5,
    root_cause: "Corner include order caused model inconsistency.",
    fix: "Verify model include order and rerun before tuning timestep settings."
  },
  netlist_reference: {
    case_id: "case_017",
    title: "Undefined subckt caused by missing standard-cell library include",
    score: 2.1,
    root_cause: "Netlist referenced a cell library that was not loaded.",
    fix: "Add the standard-cell library netlist include before top-level elaboration."
  },
  license_environment: {
    case_id: "case_029",
    title: "EDA job failed because license feature was unavailable",
    score: 1.1,
    root_cause: "Requested simulator feature was unavailable on the license server.",
    fix: "Confirm server reachability, feature name, checkout usage, and entitlement."
  }
};

const els = {
  logInput: document.querySelector("#logInput"),
  apiStatus: document.querySelector("#apiStatus"),
  llmStatus: document.querySelector("#llmStatus"),
  apiToggle: document.querySelector("#apiToggle"),
  llmToggle: document.querySelector("#llmToggle"),
  apiBase: document.querySelector("#apiBase"),
  analyzeBtn: document.querySelector("#analyzeBtn"),
  clearBtn: document.querySelector("#clearBtn"),
  riskLevel: document.querySelector("#riskLevel"),
  errorCount: document.querySelector("#errorCount"),
  caseCount: document.querySelector("#caseCount"),
  sourceBadge: document.querySelector("#sourceBadge"),
  summaryText: document.querySelector("#summaryText"),
  llmPanel: document.querySelector("#llmPanel"),
  categoryList: document.querySelector("#categoryList"),
  caseList: document.querySelector("#caseList"),
  recommendationList: document.querySelector("#recommendationList"),
  eventList: document.querySelector("#eventList"),
  themeBtn: document.querySelector("#themeBtn"),
  densityBtn: document.querySelector("#densityBtn")
};

let currentModel = "qwen3-max";

function init() {
  els.logInput.value = demoSamples.spice;
  bindEvents();
  detectApi();
  analyze();
}

function bindEvents() {
  document.querySelectorAll(".sample-button").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".sample-button").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      els.logInput.value = demoSamples[button.dataset.sample];
      analyze();
    });
  });

  els.clearBtn.addEventListener("click", () => {
    els.logInput.value = "";
    renderResult(staticAnalyze(""));
  });
  els.analyzeBtn.addEventListener("click", analyze);
  els.apiBase.addEventListener("change", detectApi);
  els.themeBtn.addEventListener("click", () => {
    document.documentElement.dataset.theme = document.documentElement.dataset.theme === "dark" ? "" : "dark";
  });
  els.densityBtn.addEventListener("click", () => {
    document.documentElement.dataset.density = document.documentElement.dataset.density === "compact" ? "" : "compact";
  });
  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key === "Enter") {
      analyze();
    }
  });
}

async function detectApi() {
  if (!els.apiToggle.checked) {
    setApiStatus("off", "静态模式");
    return false;
  }
  try {
    const response = await fetch(`${apiBase()}/health`, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const configResponse = await fetch(`${apiBase()}/config`, { cache: "no-store" }).catch(() => null);
    if (configResponse && configResponse.ok) {
      const config = await configResponse.json();
      currentModel = config.default_model || currentModel;
      els.llmStatus.textContent = config.llm_available ? `${currentModel} 就绪` : "LLM 未启用";
      els.llmStatus.className = `status-pill ${config.llm_available ? "status-ok" : "status-off"}`;
    }
    setApiStatus("ok", "FastAPI 在线");
    return true;
  } catch (_error) {
    setApiStatus("off", "静态兜底");
    els.llmStatus.textContent = "LLM 静默";
    els.llmStatus.className = "status-pill status-off";
    return false;
  }
}

async function analyze() {
  setBusy(true);
  const logText = els.logInput.value;
  try {
    const shouldUseApi = els.apiToggle.checked && await detectApi();
    if (shouldUseApi) {
      const response = await fetch(`${apiBase()}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ log_text: logText, use_llm: els.llmToggle.checked, model: currentModel })
      });
      if (!response.ok) throw new Error(`Analyze failed: HTTP ${response.status}`);
      const result = await response.json();
      renderResult(result, "FastAPI");
    } else {
      renderResult(staticAnalyze(logText), "Static");
    }
  } catch (error) {
    const fallback = staticAnalyze(logText);
    fallback.llm_note = `API 调用失败，已切换静态演示：${error.message}`;
    renderResult(fallback, "Static fallback");
  } finally {
    setBusy(false);
  }
}

function apiBase() {
  return els.apiBase.value.replace(/\/$/, "");
}

function setApiStatus(kind, text) {
  els.apiStatus.textContent = text;
  els.apiStatus.className = `status-pill status-${kind}`;
}

function setBusy(busy) {
  els.analyzeBtn.disabled = busy;
  els.analyzeBtn.querySelector("span").textContent = busy ? "Analyzing..." : "Analyze Log";
}

function staticAnalyze(logText) {
  const lines = logText.split(/\r?\n/);
  const events = lines
    .map((raw, index) => ({ raw, line_no: index + 1, severity: severityOf(raw), message: raw }))
    .filter((event) => ["ERROR", "FATAL", "WARNING"].includes(event.severity));

  const lower = logText.toLowerCase();
  const categories = [];
  addCategory(categories, lower, "pdk_model_missing", "PDK/model include or parameter issue", ["missing model", "model parameter", "pdk", "corner", "vth0"], events);
  addCategory(categories, lower, "simulation_convergence", "Simulation convergence failure", ["convergence", "newton", "timestep"], events);
  addCategory(categories, lower, "netlist_reference", "Netlist library/subckt reference issue", ["undefined subckt", "cannot find cell", "undefined cell"], events);
  addCategory(categories, lower, "license_environment", "License or runtime environment issue", ["license", "lmgrd", "checkout failed", "feature not found"], events);
  addCategory(categories, lower, "physical_verification", "DRC/LVS physical verification issue", ["lvs mismatch", "spacing violation", "rule deck mismatch"], events);

  categories.sort((a, b) => b.confidence - a.confidence);
  const case_matches = categories.map((category) => demoCases[category.id]).filter(Boolean).slice(0, 1);
  const recommendations = buildRecommendations(categories, case_matches, events);
  const errorCount = events.filter((event) => ["ERROR", "FATAL"].includes(event.severity)).length;
  const top = categories[0] ? categories[0].title : "No obvious EDA error pattern";
  return {
    summary: `Detected ${errorCount} error/fatal event(s) and ${events.length - errorCount} warning(s). Primary category: ${top}; ${case_matches.length ? `matched ${case_matches.length} historical case(s)` : "no strong historical case match"}.`,
    risk_level: errorCount ? "medium" : "low",
    events,
    categories,
    case_matches,
    recommendations,
    escalation: categories[0] ? "Escalate with extracted evidence lines and full raw log." : "No escalation needed for clean logs.",
    assumptions: ["Static browser analyzer is a demo fallback; FastAPI remains the authoritative path."]
  };
}

function severityOf(line) {
  if (/\b(FATAL|CRITICAL)\b/i.test(line)) return "FATAL";
  if (/\b(ERROR|ERR|FAILED|FAILURE)\b/i.test(line)) return "ERROR";
  if (/\b(WARN|WARNING)\b/i.test(line)) return "WARNING";
  return "INFO";
}

function addCategory(categories, lower, id, title, keywords, events) {
  const hits = keywords.filter((keyword) => lower.includes(keyword)).length;
  if (!hits) return;
  categories.push({
    id,
    title,
    confidence: Math.min(0.95, 0.48 + hits * 0.12),
    evidence_lines: events.map((event) => event.line_no).slice(0, 5)
  });
}

function buildRecommendations(categories, matches, events) {
  const map = {
    pdk_model_missing: "Check PDK/model include paths, selected process corner, and referenced model parameters.",
    simulation_convergence: "Review initial conditions, timestep settings, model validity, and recent netlist changes.",
    netlist_reference: "Verify subckt/cell libraries and netlist include order before rerunning elaboration.",
    license_environment: "Check license feature name, server reachability, expiry, and concurrent checkout usage.",
    physical_verification: "Confirm rule deck version, layout/netlist pair, extraction options, and layer mapping."
  };
  const recs = categories.map((category) => map[category.id]).filter(Boolean);
  if (matches.length) recs.push(`Compare against historical case ${matches[0].case_id}: ${matches[0].fix}`);
  const evidence = events.filter((event) => ["ERROR", "FATAL"].includes(event.severity)).map((event) => event.line_no);
  if (evidence.length) recs.push(`Attach evidence lines ${evidence.slice(0, 8).join(", ")} when escalating.`);
  return recs.length ? recs : ["No strong rule hit; preserve the full log and ask the tool owner to classify this new pattern."];
}

function renderResult(result, source = "Static") {
  const categories = normalizeArray(result.categories);
  const cases = normalizeArray(result.case_matches);
  const events = normalizeArray(result.events);
  const recommendations = normalizeArray(result.recommendations);
  const errorCount = events.filter((event) => ["ERROR", "FATAL"].includes(event.severity)).length;

  els.riskLevel.textContent = result.risk_level || "low";
  els.errorCount.textContent = String(errorCount);
  els.caseCount.textContent = String(cases.length);
  els.sourceBadge.textContent = source;
  els.summaryText.textContent = result.summary || "No summary available.";

  if (result.llm_note || result.llm) {
    const llmText = result.llm_note || result.llm;
    els.llmPanel.classList.remove("hidden");
    els.llmPanel.innerHTML = `
      <div class="llm-panel-head">
        <strong>大模型增强总结</strong>
        <span class="model-chip">当前模型：${escapeHtml(currentModel)}</span>
      </div>
      <div class="llm-content">${formatAssistantText(llmText)}</div>
    `;
    if (source === "FastAPI") {
      els.sourceBadge.textContent = "FastAPI + LLM";
    }
  } else {
    els.llmPanel.classList.add("hidden");
    els.llmPanel.innerHTML = "";
  }

  renderCategories(categories);
  renderCases(cases);
  renderRecommendations(recommendations);
  renderEvents(events);
}

function normalizeArray(value) {
  return Array.isArray(value) ? value : [];
}

function renderCategories(categories) {
  els.categoryList.innerHTML = categories.length ? "" : `<div class="list-item"><strong>No category</strong><span>当前日志没有命中强规则。</span></div>`;
  categories.forEach((category) => {
    const item = document.createElement("div");
    item.className = "list-item";
    item.innerHTML = `<strong>${escapeHtml(category.title || category.id)}</strong><span>confidence ${Number(category.confidence || 0).toFixed(2)} · evidence lines ${(category.evidence_lines || []).join(", ") || "n/a"}</span>`;
    els.categoryList.appendChild(item);
  });
}

function renderCases(cases) {
  els.caseList.innerHTML = cases.length ? "" : `<div class="list-item"><strong>No strong match</strong><span>没有展示弱相关案例，避免误导工程师。</span></div>`;
  cases.forEach((match) => {
    const item = document.createElement("div");
    item.className = "list-item";
    item.innerHTML = `<strong>${escapeHtml(match.case_id)} · ${escapeHtml(match.title)}</strong><p>${escapeHtml(match.root_cause || "")}</p><span>${escapeHtml(match.fix || "")}</span>`;
    els.caseList.appendChild(item);
  });
}

function renderRecommendations(recommendations) {
  els.recommendationList.innerHTML = "";
  recommendations.forEach((text) => {
    const item = document.createElement("li");
    item.textContent = text;
    els.recommendationList.appendChild(item);
  });
}

function renderEvents(events) {
  els.eventList.textContent = events
    .filter((event) => ["ERROR", "FATAL", "WARNING"].includes(event.severity))
    .map((event) => `${String(event.line_no).padStart(4, " ")} [${event.severity}] ${event.message || event.raw}`)
    .join("\n") || "No warning/error lines captured.";
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;"
  })[char]);
}

function formatAssistantText(value) {
  const escaped = escapeHtml(value);
  return escaped
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/(?:^|\n)(\d+)\.\s+/g, "<br><span class=\"llm-step\">$1.</span> ")
    .replace(/\n{2,}/g, "<br><br>")
    .replace(/\n/g, "<br>");
}

init();
