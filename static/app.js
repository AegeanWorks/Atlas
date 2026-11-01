/* Atlas workspace: canvas + graph share ONE analysis model. No silent divergence. */
const $ = (id) => document.getElementById(id);
let state = { figure: null, analysis: null, zoom: 1, selected: null, category: "" };

function visibleEntities() {
  if (!state.analysis) return [];
  if (!state.category) return state.analysis.entities;
  return state.analysis.entities.filter((e) => e.category === state.category);
}

async function api(path, body) {
  const r = await fetch(path, { method: body ? "POST" : "GET",
    headers: { "Content-Type": "application/json" },
    body: body ? JSON.stringify(body) : undefined });
  const data = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(data.error || r.statusText);
  return data;
}

async function refreshHealth() {
  try {
    const h = await api("/api/health");
    $("status").textContent =
      `Muse ${h.config.muse_model} · SAM ${h.config.sam_model} · Atlas standalone`;
  } catch (e) { $("status").textContent = "backend unreachable — start: python -m atlas.app"; }
}

function svgEl(tag, attrs) {
  const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
  return el;
}

function renderAll() {
  renderFilter(); renderOverlay(); renderList(); renderGraph();
  const fid = state.figureId || "workspace-figure";
  $("download-obj").href = `/api/model3d?figure_id=${encodeURIComponent(fid)}&format=obj`;
  $("anki-link").href = `/api/flashcards/export?figure_id=${encodeURIComponent(fid)}`;
}

function resetModelView() {
  state.iso = false; state.isoData = null;
  $("toggle-3d").textContent = "3D";
  deck = { cards: [], i: 0, know: 0, seen: 0 };
  showCard();
}

function toPct(b) { return { x: b.x_min * 100, y: b.y_min * 100, w: (b.x_max - b.x_min) * 100, h: (b.y_max - b.y_min) * 100 }; }

function renderOverlay() {
  const svg = $("overlay"); svg.innerHTML = "";
  if (state.iso && state.isoData) return renderIso(svg);
  const img = $("figure");
  if (!state.analysis || !img.naturalWidth) return;
  const showLabels = $("toggle-labels").checked, showBoxes = $("toggle-masks").checked;
  svg.setAttribute("viewBox", `0 0 100 100`);
  svg.style.width = img.clientWidth + "px"; svg.style.height = img.clientHeight + "px";
  for (const e of visibleEntities()) {
    if (e.mask_ref && typeof e.mask_ref === "string" && e.mask_ref.startsWith("/")) {
      // Full-crop mask overlay (mask assumed to match the analyzed crop's frame).
      const im = svgEl("image", { x: 0, y: 0, width: 100, height: 100, opacity: showBoxes ? .5 : 0 });
      im.setAttribute("href", e.mask_ref);
      svg.appendChild(im);
    }
    if (!e.bbox) continue;
    const p = toPct(e.bbox);
    const g = svgEl("g", { class: "hit" });
    if (showBoxes) {
      const r = svgEl("rect", { x: p.x, y: p.y, width: p.w, height: p.h,
        fill: e.id === state.selected ? "rgba(34,211,238,.28)" : "rgba(139,92,246,.22)",
        stroke: e.id === state.selected ? "#22d3ee" : "#8b5cf6", "stroke-width": e.id === state.selected ? .8 : .5,
        class: e.id === state.selected ? "active" : "" });
      r.addEventListener("click", () => select(e.id));
      g.appendChild(r);
    }
    if (showLabels) {
      const t = svgEl("text", { x: p.x, y: Math.max(3, p.y - 1), "font-size": 3.4, fill: "#dbe7ff" });
      t.textContent = e.name;
      t.addEventListener("click", () => select(e.id));
      g.appendChild(t);
    }
    svg.appendChild(g);
  }
}

function renderIso(svg) {
  // 2.5D stacked view: layer order = category depth, top faces face the reader.
  svg.setAttribute("viewBox", "-1 -1.1 2 2.3");
  svg.style.width = $("figure").clientWidth + "px";
  svg.style.height = $("figure").clientHeight + "px";
  for (const p of state.isoData.polygons) {
    if (state.category && p.category !== state.category) continue;
    const base = svgEl("polygon", { points: p.base.map((q) => q.join(",")).join(" "),
      fill: "rgba(139,92,246,.12)", stroke: "#3b548c", "stroke-width": .01 });
    const top = svgEl("polygon", { points: p.top.map((q) => q.join(",")).join(" "),
      fill: p.id === state.selected ? "rgba(34,211,238,.45)" : "rgba(34,211,238,.20)",
      stroke: p.id === state.selected ? "#22d3ee" : "#8b5cf6", "stroke-width": .015,
      class: "hit" });
    top.addEventListener("click", () => select(p.id));
    const c = p.top.reduce((a, q) => [a[0] + q[0] / 4, a[1] + q[1] / 4], [0, 0]);
    const t = svgEl("text", { x: c[0], y: c[1], "font-size": .07, fill: "#dbe7ff", "text-anchor": "middle" });
    t.textContent = p.name;
    t.addEventListener("click", () => select(p.id));
    svg.appendChild(base); svg.appendChild(top); svg.appendChild(t);
  }
}

$("toggle-3d").onclick = async () => {
  state.iso = !state.iso;
  $("toggle-3d").textContent = state.iso ? "2D" : "3D";
  if (state.iso && state.analysis && !state.isoData) {
    const fid = state.figureId || "workspace-figure";
    try { state.isoData = await api(`/api/model3d?figure_id=${encodeURIComponent(fid)}`); }
    catch (e) { state.isoData = null; state.iso = false; $("toggle-3d").textContent = "3D"; }
  }
  renderAll();
};

let deck = { cards: [], i: 0, know: 0, seen: 0 };
function showCard() {
  const f = $("card-front"), b = $("card-back");
  if (!deck.cards.length) { f.textContent = "Build a deck first."; b.classList.add("hidden"); return; }
  const c = deck.cards[deck.i % deck.cards.length];
  f.textContent = `[${c.kind}] ${c.front.text}`;
  b.innerHTML = "";
  b.textContent = c.back.text + (c.back.detail ? ` — ${c.back.detail}` : "");
  b.classList.add("hidden");
  $("deck-score").textContent = `card ${deck.i % deck.cards.length + 1}/${deck.cards.length} · known ${deck.know}/${deck.seen}`;
}
$("btn-deck").onclick = async () => {
  if (!state.analysis) return alert("Analyze or load a model first.");
  const d = await api("/api/flashcards", { analysis: state.analysis }).catch((e) => alert(e.message));
  if (!d) return;
  deck = { cards: d.cards, i: 0, know: 0, seen: 0 };
  showCard();
};
$("btn-flip").onclick = () => $("card-back").classList.toggle("hidden");
$("btn-know").onclick = () => { if (!deck.cards.length) return; deck.know++; deck.seen++; deck.i++; showCard(); };
$("btn-dunno").onclick = () => { if (!deck.cards.length) return; deck.seen++; deck.i++; showCard(); };

function renderFilter() {
  const sel = $("category-filter");
  const cur = state.category;
  sel.innerHTML = '<option value="">All categories</option>';
  if (!state.analysis) { state.category = ""; return; }
  for (const c of [...new Set(state.analysis.entities.map((e) => e.category))].sort()) {
    const o = document.createElement("option");
    o.value = c; o.textContent = c;
    sel.appendChild(o);
  }
  sel.value = [...sel.options].some((o) => o.value === cur) ? cur : "";
  state.category = sel.value;
}

function renderList() {
  const ul = $("entity-list"); ul.innerHTML = "";
  if (!state.analysis) return;
  for (const e of visibleEntities()) {
    const li = document.createElement("li");
    li.textContent = `${e.name} · ${e.category} · ${(e.confidence * 100).toFixed(0)}%`;
    if (e.id === state.selected) li.classList.add("active");
    li.onclick = () => select(e.id);
    ul.appendChild(li);
  }
}

function renderGraph() {
  const svg = $("graph"); svg.innerHTML = "";
  if (!state.analysis) return;
  const ents = visibleEntities();
  const ids = new Set(ents.map((e) => e.id));
  const n = Math.max(ents.length, 1);
  const pos = {};
  ents.forEach((e, i) => {
    const a = (2 * Math.PI * i) / n;
    pos[e.id] = { x: 50 + 38 * Math.cos(a), y: 50 + 38 * Math.sin(a) };
  });
  for (const r of state.analysis.relationships) {
    if (!ids.has(r.source_id) || !ids.has(r.target_id)) continue;
    const a = pos[r.source_id], b = pos[r.target_id];
    if (!a || !b) continue; // same-model invariant: skip dangling instead of inventing
    svg.appendChild(svgEl("line", { x1: a.x, y1: a.y, x2: b.x, y2: b.y }));
  }
  for (const e of ents) {
    const c = svgEl("circle", { cx: pos[e.id].x, cy: pos[e.id].y, r: e.id === state.selected ? 7 : 5,
      class: e.id === state.selected ? "active" : "" });
    c.addEventListener("click", () => select(e.id));
    const t = svgEl("text", { x: pos[e.id].x, y: pos[e.id].y + 12, "font-size": 5, fill: "#dbe7ff", "text-anchor": "middle" });
    t.textContent = e.name;
    svg.appendChild(c); svg.appendChild(t);
  }
}

function select(id) {
  if (!state.analysis) return;
  state.selected = id;
  const e = state.analysis.entities.find((x) => x.id === id);
  if (!e) return;
  const rels = state.analysis.relationships.filter((r) => r.source_id === id || r.target_id === id);
  const names = Object.fromEntries(state.analysis.entities.map((x) => [x.id, x.name]));
  $("detail").textContent =
    `${e.name} [${e.category}] conf=${e.confidence}\n${e.description}\n` +
    `evidence: ${e.source_evidence || "—"}\nuncertainty: ${e.uncertainty || "—"}\n` +
    (rels.map((r) => `· ${names[r.source_id]} --${r.rel_type}--> ${names[r.target_id]} (${r.explanation || "no note"})`).join("\n") || "· no relationships");
  renderAll();
}

$("toggle-labels").onchange = renderOverlay;
$("toggle-masks").onchange = renderOverlay;
$("category-filter").onchange = (e) => { state.category = e.target.value; renderAll(); };

// Drag-to-pan: mousedown on the image pans the viewport; overlay shapes keep clicks.
(() => {
  const vp = $("viewport");
  let sx = 0, sy = 0, sl = 0, st = 0, panning = false;
  vp.addEventListener("mousedown", (e) => {
    if (e.target.id !== "figure") return;
    panning = true; sx = e.clientX; sy = e.clientY; sl = vp.scrollLeft; st = vp.scrollTop;
  });
  window.addEventListener("mousemove", (e) => {
    if (!panning) return;
    vp.scrollLeft = sl - (e.clientX - sx);
    vp.scrollTop = st - (e.clientY - sy);
  });
  window.addEventListener("mouseup", () => { panning = false; });
})();

$("btn-segment").onclick = async () => {
  const box = $("segment-status");
  if (!state.analysis || !state.selected) { box.textContent = "Select a structure first."; return; }
  if (!state.figureFile) { box.textContent = "Segmentation needs a server-side figure (not the demo SVG). Select a figure, then analyze."; return; }
  const e = state.analysis.entities.find((x) => x.id === state.selected);
  box.textContent = `Segmenting "${e.name}" with SAM 3.1…`;
  try {
    const seg = await api("/api/segment", { image_path: state.figureFile,
      prompt: e.name, entity_id: e.id, bbox: e.bbox || undefined });
    const attached = await api("/api/analysis/attach-mask", { figure_id: state.figureId || "workspace-figure",
      entity_id: e.id, kind: seg.kind, mask_ref: seg.mask_ref || "", bbox: seg.bbox || undefined });
    state.analysis = attached.analysis;
    box.textContent = seg.kind === "mask"
      ? `Mask attached to "${e.name}".`
      : `SAM returned no decodable mask — honest bbox fallback kept for "${e.name}".`;
    renderAll();
  } catch (err) { box.textContent = `Segmentation failed: ${err.message}`; }
};
$("zoom-in").onclick = () => { state.zoom = Math.min(4, state.zoom + .25); $("figure").style.width = `${state.zoom * 100}%`; renderOverlay(); };
$("zoom-out").onclick = () => { state.zoom = Math.max(.5, state.zoom - .25); $("figure").style.width = `${state.zoom * 100}%`; renderOverlay(); };
$("reset-view").onclick = () => { state.zoom = 1; $("figure").style.width = "100%"; renderOverlay(); };

$("btn-import").onclick = async () => {
  const path = $("doc-path").value.trim();
  if (!path) return alert("Enter a server-local document/image path.");
  const r = await api("/api/import", { path }).catch((e) => alert(e.message));
  if (r) { $("provenance").textContent = JSON.stringify(r, null, 2); state.figure = r; }
};
$("btn-figure").onclick = async () => {
  const src = $("doc-path").value.trim();
  const crop = $("crop").value.split(",").map(Number);
  const r = await api("/api/figure/select", { image_path: src, crop }).catch((e) => alert(e.message));
  if (r) { setFigure(r.image_path, r.figure_url); $("provenance").textContent = JSON.stringify(r, null, 2); }
};
$("btn-analyze").onclick = async () => {
  const src = state.figureFile || $("doc-path").value.trim();
  const r = await api("/api/analyze", { image_path: src, note: $("note").value,
    figure_id: "workspace-figure" }).catch((e) => alert(e.message));
  if (r) { state.analysis = r.analysis; state.selected = null; state.figureId = "workspace-figure"; resetModelView(); renderAll(); }
};
$("btn-demo").onclick = async () => {
  const r = await fetch("/static/basal_ganglia_sample.json").then((x) => x.json()).catch(() => null);
  // Demo fixture ships with the app when present; otherwise explain the live path.
  if (!r) return alert("Demo fixture missing; run demo/basal_ganglia_demo.py --fixture-only to create it.");
  state.analysis = r;
  state.figureFile = "";
  state.figureId = "demo";
  setFigure("", r._demo_image || "/static/basal_ganglia_demo.svg");
  resetModelView();
  renderAll();
};
function setFigure(filePath, displayUrl) {
  state.figureFile = filePath;
  state.figureUrl = displayUrl;
  const img = $("figure");
  img.src = displayUrl;
  img.onload = () => { img.style.width = "100%"; renderOverlay(); };
}
// Text models (books, articles, transcripts) have no figure: clear the canvas so a
// stale image can never pose as the current model's evidence.
function showModel(auto, stagedPath) {
  state.analysis = auto.analysis;
  state.selected = null; state.figureId = auto.figure_id;
  if (auto.figure_url) {
    state.figureFile = stagedPath || "";
    setFigure(stagedPath || "", auto.figure_url);
  } else {
    state.figureFile = "";
    const img = $("figure"); img.removeAttribute("src"); img.style.width = "100%";
    $("overlay").innerHTML = "";
  }
  resetModelView();
  renderAll();
}

// One drop -> one model: upload the file, then auto-create (images fully automatic).
const dz = $("dropzone");
["dragover", "dragenter"].forEach((ev) => dz.addEventListener(ev, (e) => { e.preventDefault(); dz.classList.add("over"); }));
["dragleave", "drop"].forEach((ev) => dz.addEventListener(ev, (e) => { e.preventDefault(); dz.classList.remove("over"); }));
dz.addEventListener("drop", async (e) => {
  const file = e.dataTransfer.files && e.dataTransfer.files[0];
  if (!file) return;
  const fd = new FormData();
  fd.append("file", file, file.name);
  dz.textContent = `Uploading ${file.name}…`;
  try {
    const up = await fetch("/api/upload", { method: "POST", body: fd }).then((r) => r.json());
    if (up.error) throw new Error(up.error);
    $("provenance").textContent = JSON.stringify(up, null, 2);
    dz.textContent = "Creating model…";
    const auto = await api("/api/auto-create", { path: up.staged_path, note: $("note").value, figure_id: "workspace-figure" });
    if (!auto.model_created) { dz.textContent = "Stored. " + (auto.document.figure_hint || "Done."); return; }
    showModel(auto, up.staged_path);
    dz.textContent = auto.figure_url
      ? `Model created: ${auto.analysis.entities.length} entities, ${auto.analysis.relationships.length} relationships.`
      : `Text model created (${auto.source_kind}): graph + learning ready, no figure overlay.`;
  } catch (err) { dz.textContent = `Drop failed: ${err.message}`; }
});

$("btn-link").onclick = async () => {
  const url = $("link-input").value.trim();
  if (!url) return;
  dz.textContent = `Creating model from link…`;
  try {
    const auto = await api("/api/auto-create", { path: url, note: $("note").value, figure_id: "workspace-figure" });
    if (!auto.model_created) { dz.textContent = "Stored. " + (auto.document.figure_hint || "Done."); return; }
    showModel(auto, "");
    dz.textContent = `Model created from link: ${auto.analysis.entities.length} entities, ${auto.analysis.relationships.length} relationships (graph + learning ready).`;
  } catch (err) { dz.textContent = `Link failed: ${err.message}`; }
};

$("btn-learn").onclick = async () => {
  if (!state.analysis) return alert("Analyze a figure first.");
  const c = await api("/api/learn", { analysis: state.analysis,
    mode: $("learn-mode").value, seed: Date.now() % 100000 });
  const box = $("challenge"); box.innerHTML = "";
  const p = document.createElement("div"); p.textContent = c.prompt; box.appendChild(p);
  const answer = async (value) => {
    const g = await api("/api/learn/grade", { challenge: c, answer: value });
    const d = document.createElement("div"); d.className = "mono";
    d.textContent = g.correct ? "correct ✓" : `not quite — expected ${JSON.stringify(g.expected)}`;
    box.appendChild(d);
  };
  if (c.options) {
    for (const o of c.options) {
      const b = document.createElement("button");
      b.className = "opt"; b.textContent = typeof o === "string" ? o : o.name;
      b.onclick = () => answer(typeof o === "string" ? o : o.id);
      box.appendChild(b);
    }
  } else if (c.chain) {
    const b = document.createElement("button");
    b.className = "opt"; b.textContent = "Reveal pathway order";
    b.onclick = () => answer(c.chain);
    const hint = document.createElement("div"); hint.className = "mono";
    hint.textContent = `Trace ${c.chain.length} connected structures in order, starting at ${c.chain_names ? c.chain_names[0] : c.chain[0]}.`;
    box.appendChild(hint); box.appendChild(b);
  } else {
    const input = document.createElement("input"); input.placeholder = "rel_type, e.g. inhibits";
    const b = document.createElement("button"); b.textContent = "Check";
    b.onclick = () => answer(input.value.trim());
    box.appendChild(input); box.appendChild(b);
  }
};

window.addEventListener("resize", renderOverlay);
refreshHealth();
