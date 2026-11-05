/* LibreSignal web UI — vanilla JS, no build step. */
(() => {
  "use strict";

  const TOTAL_MS = 70 * 60 * 1000; // ICF assessments are ~70 minutes
  const $ = (sel) => document.querySelector(sel);

  // ---------------------------------------------------------------- storage
  const store = {
    get(key, fallback) {
      try {
        const v = localStorage.getItem("libresignal:" + key);
        return v == null ? fallback : JSON.parse(v);
      } catch { return fallback; }
    },
    set(key, value) {
      try { localStorage.setItem("libresignal:" + key, JSON.stringify(value)); } catch { /* ignore */ }
    },
  };

  // ---------------------------------------------------------------- api
  async function api(path, opts = {}) {
    const res = await fetch("/api" + path, {
      headers: { "Content-Type": "application/json" },
      ...opts,
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || res.statusText);
    return data;
  }

  // ---------------------------------------------------------------- utils
  const escapeHtml = (s) => String(s).replace(/[&<>"']/g, (c) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  function renderMarkdown(md) {
    if (window.marked) return window.marked.parse(md, { gfm: true });
    return "<pre>" + escapeHtml(md) + "</pre>";
  }

  let toastTimer;
  function toast(msg) {
    const el = $("#toast");
    el.textContent = msg;
    el.classList.add("show");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => el.classList.remove("show"), 2600);
  }

  // ---------------------------------------------------------------- theme
  function applyTheme(theme) {
    if (theme) document.documentElement.dataset.theme = theme;
    else delete document.documentElement.dataset.theme;
  }
  applyTheme(store.get("theme", null));
  $("#theme-toggle").addEventListener("click", () => {
    const current = document.documentElement.dataset.theme
      || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    const next = current === "dark" ? "light" : "dark";
    store.set("theme", next);
    applyTheme(next);
  });

  // ---------------------------------------------------------------- progress
  const progress = {
    get(qid) { return store.get("progress:" + qid, { passed: [], unlocked: 1 }); },
    save(qid, p) { store.set("progress:" + qid, p); },
    unlockAll(qid) { return store.get("unlockAll:" + qid, false); },
    setUnlockAll(qid, v) { store.set("unlockAll:" + qid, v); },
  };

  // ---------------------------------------------------------------- state
  const state = {
    questions: [],
    q: null,            // current question detail
    level: 1,           // level tab being viewed
    file: "simulation", // simulation | tests | solution
    savedCode: "",
    lastRun: null,
    running: false,
  };

  // ---------------------------------------------------------------- editor
  let cm = null;
  const docs = {};
  const textarea = $("#editor");

  function initEditor() {
    if (!window.CodeMirror) return; // falls back to the plain textarea
    cm = window.CodeMirror.fromTextArea(textarea, {
      mode: "python",
      lineNumbers: true,
      indentUnit: 4,
      tabSize: 4,
      indentWithTabs: false,
      matchBrackets: true,
      autoCloseBrackets: true,
      styleActiveLine: true,
      extraKeys: {
        Tab: (ed) => ed.somethingSelected()
          ? ed.indentSelection("add")
          : ed.replaceSelection(" ".repeat(ed.getOption("indentUnit"))),
        "Shift-Tab": (ed) => ed.indentSelection("subtract"),
        "Ctrl-S": () => save(), "Cmd-S": () => save(),
        "Ctrl-Enter": () => run(state.level), "Cmd-Enter": () => run(state.level),
        "Ctrl-/": "toggleComment", "Cmd-/": "toggleComment",
      },
    });
    cm.on("change", updateDirty);
  }

  function getCode() {
    if (cm) return (docs.simulation || cm.getDoc()).getValue();
    return state.file === "simulation" ? textarea.value : state.savedCode;
  }

  function showFile(name, text) {
    state.file = name;
    document.querySelectorAll(".file-tab").forEach((b) =>
      b.classList.toggle("active", b.dataset.file === name));
    const readOnly = name !== "simulation";
    if (cm) {
      if (!docs[name]) docs[name] = window.CodeMirror.Doc(text ?? "", "python");
      cm.swapDoc(docs[name]);
      cm.setOption("readOnly", readOnly);
      cm.getWrapperElement().classList.toggle("CodeMirror-readonly", readOnly);
      cm.refresh();
    } else {
      if (name === "simulation") textarea.value = docs.simulationText ?? state.savedCode;
      else { if (state.file === "simulation") docs.simulationText = textarea.value; textarea.value = text ?? ""; }
      textarea.readOnly = readOnly;
    }
    updateDirty();
  }

  textarea.addEventListener("input", () => { docs.simulationText = textarea.value; updateDirty(); });

  function isDirty() { return state.q?.code != null && getCode() !== state.savedCode; }

  function updateDirty() {
    const el = $("#save-state");
    if (!state.q || state.q.code == null) { el.textContent = ""; return; }
    if (state.file !== "simulation") { el.textContent = "read-only"; el.className = "save-state"; return; }
    const dirty = isDirty();
    el.textContent = dirty ? "● unsaved" : "saved";
    el.className = "save-state" + (dirty ? " dirty" : "");
  }

  document.querySelectorAll(".file-tab").forEach((btn) => btn.addEventListener("click", async () => {
    const name = btn.dataset.file;
    if (name === state.file || !state.q) return;
    if (name === "simulation") return showFile("simulation");
    if (name === "solution" && !docs.solution) {
      if (!confirm("Peek at the reference solution? Try to solve it yourself first! 🙂")) return;
    }
    try {
      if (!docs[name] && !(docs[name + "Text"])) {
        const data = await api(`/questions/${state.q.id}/${name}`);
        if (!cm) docs[name + "Text"] = data.code;
        showFile(name, data.code);
      } else {
        showFile(name, docs[name + "Text"]);
      }
    } catch (e) { toast(e.message); }
  }));

  // ---------------------------------------------------------------- save / run
  async function save({ quiet = false } = {}) {
    if (!state.q || state.q.code == null) return;
    const code = getCode();
    try {
      await api(`/questions/${state.q.id}/code`, { method: "PUT", body: { code } });
      state.savedCode = code;
      updateDirty();
      if (!quiet) toast("Saved simulation.py");
    } catch (e) { toast("Save failed: " + e.message); }
  }

  async function run(level) {
    const q = state.q;
    if (!q || !q.has_tests || state.running) return;
    if (level != null && !isUnlocked(level)) return toast(`Level ${level} is locked`);
    state.running = true;
    setRunning(true, level);
    const code = getCode();
    try {
      const result = await api(`/questions/${q.id}/run`, {
        method: "POST", body: { level, code: q.code != null ? code : undefined },
      });
      if (q.code != null) { state.savedCode = code; updateDirty(); }
      if (state.q !== q) return;
      state.lastRun = { level, result };
      applyProgress(result, level);
      renderResults();
    } catch (e) {
      renderResults(e.message);
    } finally {
      state.running = false;
      setRunning(false);
    }
  }

  function setRunning(on, level) {
    $("#run-btn").disabled = on || !state.q?.has_tests;
    $("#run-all-btn").disabled = on || !state.q?.has_tests;
    if (on) {
      $("#results").classList.remove("collapsed");
      $("#results-summary").innerHTML =
        `<span class="spinner"></span> Running ${level ? "Level " + level : "all levels"}…`;
    }
  }

  $("#save-btn").addEventListener("click", () => save());
  $("#run-btn").addEventListener("click", () => run(state.level));
  $("#run-all-btn").addEventListener("click", () => run(null));
  document.addEventListener("keydown", (e) => {
    if (!state.q) return;
    const mod = e.metaKey || e.ctrlKey;
    if (mod && e.key.toLowerCase() === "s") { e.preventDefault(); save(); }
    if (mod && e.key === "Enter") { e.preventDefault(); run(state.level); }
  });
  window.addEventListener("beforeunload", (e) => { if (isDirty()) { e.preventDefault(); e.returnValue = ""; } });

  // ---------------------------------------------------------------- levels
  function isUnlocked(level) {
    if (!state.q) return false;
    if (!state.q.has_tests || progress.unlockAll(state.q.id)) return true;
    return level <= progress.get(state.q.id).unlocked;
  }

  function applyProgress(result, ranLevel) {
    if (!result.ok) return;
    const qid = state.q.id;
    const p = progress.get(qid);
    const passed = new Set(p.passed);
    const before = p.unlocked;
    for (const [lv, s] of Object.entries(result.levels)) {
      const n = Number(lv);
      if (s.total > 0 && s.passed === s.total) passed.add(n); else passed.delete(n);
    }
    // Unlock sequentially: level N+1 opens once 1..N have all passed.
    let unlocked = p.unlocked;
    const maxLevel = Math.max(...state.q.levels);
    while (unlocked < maxLevel && passed.has(unlocked)) unlocked++;
    p.passed = [...passed].sort();
    p.unlocked = Math.max(unlocked, before);
    progress.save(qid, p);

    if (ranLevel != null && passed.has(ranLevel)) {
      if (ranLevel === maxLevel) toast("🎉 All levels complete!");
      else if (p.unlocked > before) {
        toast(`✅ Level ${ranLevel} passed — Level ${ranLevel + 1} unlocked!`);
        selectLevel(ranLevel + 1);
        return;
      }
    }
    renderLevelTabs();
  }

  function selectLevel(n) {
    state.level = n;
    location.replace(`#/q/${state.q.id}/${n}`);
    renderLevelTabs();
    renderSpec();
    $("#run-btn").textContent = `Run Level ${n}`;
  }

  function renderLevelTabs() {
    const q = state.q;
    const p = progress.get(q.id);
    const tabs = $("#level-tabs");
    tabs.innerHTML = "";
    for (const n of q.levels) {
      const b = document.createElement("button");
      b.className = "level-tab";
      const locked = !isUnlocked(n);
      b.disabled = locked;
      b.classList.toggle("active", n === state.level);
      b.classList.toggle("passed", p.passed.includes(n));
      b.innerHTML = `<span class="dot"></span>Level ${n}${locked ? " 🔒" : ""}`;
      b.title = locked ? `Pass Level ${n - 1} to unlock` : `Level ${n}`;
      b.addEventListener("click", () => selectLevel(n));
      tabs.appendChild(b);
    }
    if (q.has_tests) {
      const label = document.createElement("label");
      label.className = "unlock-toggle";
      label.innerHTML = `<input type="checkbox" ${progress.unlockAll(q.id) ? "checked" : ""}> Unlock all`;
      label.querySelector("input").addEventListener("change", (e) => {
        progress.setUnlockAll(q.id, e.target.checked);
        if (!isUnlocked(state.level)) state.level = progress.get(q.id).unlocked;
        selectLevel(state.level);
      });
      tabs.appendChild(label);
    }
  }

  function renderSpec() {
    const el = $("#spec");
    const md = state.q.specs[String(state.level)];
    el.innerHTML = md ? renderMarkdown(md) : `<p class="muted">No spec for this level.</p>`;
    el.scrollTop = 0;
  }

  // ---------------------------------------------------------------- results
  function renderResults(error) {
    const body = $("#results-body");
    const summary = $("#results-summary");
    const raw = $("#raw-output");
    body.innerHTML = "";
    if (error) {
      summary.innerHTML = `<span class="summary-pill fail">Error</span>`;
      body.innerHTML = `<div class="banner err">${escapeHtml(error)}</div>`;
      return;
    }
    const run = state.lastRun;
    if (!run) { summary.textContent = "Run the tests to see results."; raw.textContent = ""; return; }
    const r = run.result;
    raw.textContent = r.output || "";
    if (!r.ok) {
      summary.innerHTML = `<span class="summary-pill fail">Error</span>`;
      body.innerHTML = `<div class="banner err">${escapeHtml(r.error)}</div>`;
      return;
    }
    const allPass = r.total > 0 && r.passed === r.total;
    const scope = run.level ? `Level ${run.level}` : "All levels";
    summary.innerHTML = `<span class="summary-pill ${allPass ? "pass" : "fail"}">${r.passed}/${r.total} passed</span>
      <span class="muted">${scope}</span>`;

    const collectErrors = r.tests.filter((t) => t.level === 0 && t.status === "error");
    if (r.total === 0 || collectErrors.length === r.total) {
      summary.innerHTML = `<span class="summary-pill fail">Import error</span><span class="muted">${scope}</span>`;
      const detail = collectErrors.map((t) => t.details).join("\n\n") || r.output;
      body.innerHTML = `<div class="banner err">Your code failed to import (syntax error?), so no tests ran.\n\n${escapeHtml(detail)}</div>`;
      return;
    }

    const byLevel = {};
    for (const t of r.tests) (byLevel[t.level] ||= []).push(t);
    for (const [lv, tests] of Object.entries(byLevel)) {
      const s = r.levels[lv];
      const group = document.createElement("div");
      group.className = "level-group";
      group.innerHTML = `<h4>Level ${lv} <span>${s.passed}/${s.total}</span></h4>`;
      for (const t of tests) {
        const d = document.createElement("details");
        d.className = "test " + t.status;
        const icon = { passed: "✓", failed: "✗", error: "!", skipped: "–" }[t.status];
        const msg = t.status === "passed" ? "" : (t.message || "").split("\n")[0];
        d.innerHTML = `<summary>
            <span class="status">${icon}</span>
            <span class="t-name" title="${escapeHtml(t.name)}">${escapeHtml(t.name)}</span>
            <span class="t-msg" title="${escapeHtml(msg)}">${escapeHtml(msg)}</span>
            <span class="t-time">${(t.time * 1000).toFixed(0)}ms</span>
          </summary>` + (t.details ? `<pre>${escapeHtml(t.details)}</pre>` : "");
        if (t.status === "passed") d.addEventListener("click", (e) => e.preventDefault());
        group.appendChild(d);
      }
      body.appendChild(group);
    }
    if (allPass && run.level) {
      const max = Math.max(...state.q.levels);
      body.insertAdjacentHTML("afterbegin", `<div class="banner">${run.level === max
        ? "🎉 Every level passed. Nice work!"
        : `Level ${run.level} passed — on to Level ${run.level + 1}.`}</div>`);
    }
    // Auto-expand the first failure for quick feedback.
    body.querySelector("details.failed, details.error")?.setAttribute("open", "");
  }

  $("#results-collapse").addEventListener("click", () => {
    $("#results").classList.toggle("collapsed");
    cm?.refresh();
  });
  $("#toggle-output").addEventListener("click", () => {
    const raw = $("#raw-output");
    raw.hidden = !raw.hidden;
    $("#results-body").hidden = !raw.hidden;
    $("#toggle-output").textContent = raw.hidden ? "Raw output" : "Test list";
  });

  // ---------------------------------------------------------------- timer
  const timer = {
    qid: null, handle: null,
    load(qid) {
      this.qid = qid;
      clearInterval(this.handle);
      this.handle = setInterval(() => this.render(), 500);
      this.render();
    },
    data() { return store.get("timer:" + this.qid, { remaining: TOTAL_MS, startedAt: null }); },
    remaining() {
      const d = this.data();
      return d.startedAt ? d.remaining - (Date.now() - d.startedAt) : d.remaining;
    },
    toggle() {
      const d = this.data();
      if (d.startedAt) store.set("timer:" + this.qid, { remaining: this.remaining(), startedAt: null });
      else store.set("timer:" + this.qid, { remaining: d.remaining, startedAt: Date.now() });
      this.render();
    },
    reset() {
      store.set("timer:" + this.qid, { remaining: TOTAL_MS, startedAt: null });
      this.render();
    },
    render() {
      if (!this.qid) return;
      const ms = this.remaining();
      const neg = ms < 0;
      const abs = Math.abs(ms);
      const m = Math.floor(abs / 60000), s = Math.floor((abs % 60000) / 1000);
      $("#timer-value").textContent = `${neg ? "-" : ""}${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
      $("#timer").classList.toggle("low", !neg && ms < 10 * 60000);
      $("#timer").classList.toggle("over", neg);
      $("#timer-toggle").textContent = this.data().startedAt ? "❚❚" : "▶";
    },
    stop() { clearInterval(this.handle); this.qid = null; },
  };
  $("#timer-toggle").addEventListener("click", () => timer.toggle());
  $("#timer-reset").addEventListener("click", () => {
    if (confirm("Reset the 70-minute timer?")) timer.reset();
  });

  // ---------------------------------------------------------------- splitter
  (() => {
    const splitter = $("#splitter");
    const spec = document.querySelector(".spec-pane");
    const saved = store.get("specWidth", null);
    if (saved) spec.style.width = saved;
    splitter.addEventListener("pointerdown", (e) => {
      splitter.setPointerCapture(e.pointerId);
      splitter.classList.add("dragging");
      const move = (ev) => {
        const pct = Math.min(70, Math.max(20, (ev.clientX / window.innerWidth) * 100));
        spec.style.width = pct + "%";
      };
      const up = () => {
        splitter.classList.remove("dragging");
        splitter.removeEventListener("pointermove", move);
        store.set("specWidth", spec.style.width);
        cm?.refresh();
      };
      splitter.addEventListener("pointermove", move);
      splitter.addEventListener("pointerup", up, { once: true });
    });
  })();

  // ---------------------------------------------------------------- views
  function renderHome() {
    timer.stop();
    state.q = null;
    $("#timer").hidden = true;
    $("#workspace").hidden = true;
    $("#home").hidden = false;
    $("#crumbs").innerHTML = "";
    document.title = "LibreSignal";
    const cards = $("#cards");
    cards.innerHTML = "";
    for (const q of state.questions) {
      const p = progress.get(q.id);
      const ready = q.has_simulation && q.has_tests;
      const el = document.createElement("button");
      el.className = "card";
      el.innerHTML = `
        <div class="card-head">
          <span class="card-icon">${q.icon}</span>
          <h3>${escapeHtml(q.title)}</h3>
          <span class="spacer"></span>
          <span class="badge ${ready ? "ready" : ""}">${ready ? "Tests ready" : "Spec only"}</span>
        </div>
        <div class="progress">${q.levels.map((n) =>
          `<span class="${p.passed.includes(n) ? "done" : ""}" title="Level ${n}"></span>`).join("")}</div>
        <div class="meta">${q.levels.length} levels · ${ready
          ? `${p.passed.length}/${q.levels.length} passed` : "read the spec, bring your own tests"}</div>`;
      el.addEventListener("click", () => { location.hash = `#/q/${q.id}`; });
      cards.appendChild(el);
    }
  }

  async function openQuestion(qid, level) {
    if (state.q?.id === qid) {
      if (level && level !== state.level && isUnlocked(level)) selectLevel(level);
      return;
    }
    if (isDirty() && !confirm("You have unsaved changes. Discard them?")) {
      location.replace(`#/q/${state.q.id}/${state.level}`);
      return;
    }
    let q;
    try { q = await api(`/questions/${encodeURIComponent(qid)}`); }
    catch (e) { toast(e.message); location.hash = "#/"; return; }

    state.q = q;
    state.savedCode = q.code ?? "";
    state.lastRun = null;
    for (const k of Object.keys(docs)) delete docs[k];

    $("#home").hidden = true;
    $("#workspace").hidden = false;
    $("#timer").hidden = !q.has_tests;
    $("#crumbs").innerHTML = `<span>/</span><b>${q.icon} ${escapeHtml(q.title)}</b>`;
    document.title = `${q.title} · LibreSignal`;

    const hasCode = q.code != null;
    $("#no-code").hidden = hasCode;
    $("#save-btn").hidden = !hasCode;
    document.querySelector('[data-file="tests"]').hidden = !q.has_tests;
    document.querySelector('[data-file="solution"]').hidden = !q.has_solution;
    document.querySelector('[data-file="simulation"]').hidden = !hasCode;
    $("#run-btn").disabled = $("#run-all-btn").disabled = !q.has_tests;

    if (cm) docs.simulation = window.CodeMirror.Doc(state.savedCode, "python");
    else docs.simulationText = state.savedCode;
    showFile("simulation");
    if (cm) cm.clearHistory();

    const p = progress.get(q.id);
    let lv = level || p.unlocked;
    if (!q.levels.includes(lv)) lv = q.levels[0] || 1;
    if (!isUnlocked(lv)) lv = p.unlocked;
    selectLevel(lv);
    renderResults();
    if (q.has_tests) timer.load(q.id);
  }

  async function route() {
    const m = location.hash.match(/^#\/q\/([\w-]+)(?:\/(\d+))?/);
    if (m) return openQuestion(m[1], m[2] ? Number(m[2]) : null);
    if (isDirty() && !confirm("You have unsaved changes. Discard them?")) {
      location.replace(`#/q/${state.q.id}/${state.level}`);
      return;
    }
    renderHome();
  }

  // ---------------------------------------------------------------- boot
  (async function boot() {
    initEditor();
    try { state.questions = await api("/questions"); }
    catch (e) { toast("Could not reach the LibreSignal server: " + e.message); }
    window.addEventListener("hashchange", route);
    route();
  })();
})();
