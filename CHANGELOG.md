# Changelog

## 0.6.1 — Text-model honesty pass (2026-11-01)

- Text models clear the figure canvas instead of showing a broken image or a
  stale figure; status says graph + learning are ready with no overlay.
- `/api/import` and `/api/upload` extract text through the universal ingester,
  so EPUB/TXT/MD report real text stats (was: backend "unavailable"); import
  also accepts URLs with guidance toward auto-create.

## 0.6.0 — Everything becomes learning material (2026-11-01)

- Universal ingestion (`atlas/sources.py`, stdlib only): article links, YouTube
  public captions, EPUB books (spine order), video via system ffmpeg (frames
  merged into one namespaced model), plus PDF/TXT/MD/DOCX/PPTX/transcripts.
- Text knowledge path (`MuseProvider.analyze_text`): same validated schema with
  quoted evidence instead of boxes; entity `box` now optional end to end.
- `auto-create` dispatches any source; new `/frames/` serving; link box in the UI.

## 0.5.0 — One-click, drop-to-model, AI-drivable (2026-11-01)

- One-click install/start (`install.ps1|.sh`, `start.ps1|.sh`: venv + deps + browser).
- Drop zone: `POST /api/upload` (multipart) + `POST /api/auto-create` turn one
  dropped image into a saved model with zero further clicks.
- AI visibility: `GET /api/models` lists every model; `GET /api/contract`
  serves the versioned machine contract (`docs/AI_CONTRACT.md`).
- Headless CLI (`python -m atlas.cli`): create/models/show/learn/contract so AI
  agents create and teach autonomously.

## 0.4.0 — Segmentation loop + exploration polish (2026-11-01)

- "Segment selected (SAM)" button: SAM 3.1 masks attach to entities via
  `/api/analysis/attach-mask`; served back over `/masks/` (basename-guarded)
  and overlaid on the original figure.
- Category filter shared by canvas, entity list, and knowledge graph.
- Drag-to-pan on the figure viewport (entity clicks still select).

## 0.3.0 — Atlas, fully on its own (2026-11-01)

- Removed the NeuralDeck live-checkout path entirely (`NEURALDECK_PATH`,
  sibling probing, `neuraldeck_adapter.py`): the in-project text backend
  (`atlas/text_backend.py` + `atlas/doc_text.py`) is the only backend.
- Renamed the project to Atlas (was NeuralDeck-Atlas): README, workspace
  brand, docs, and version strings.

## 0.2.0 — Standalone by default (2026-11-01)

- Vendored NeuralDeck document-text functions in-project (`atlas/doc_text.py`:
  PDF/DOCX/PPTX/TXT/VTT/SRT/JSON): Atlas installs and runs with no sibling
  project. Live checkout only via explicit `NEURALDECK_PATH` opt-in.
- Fixed no-key guard bypass: `transport is self._http_post` on bound methods is
  always False, so missing-key analyze/segment calls hit the network; replaced
  with an explicit `_live_transport` flag (+ missing SAM guard added).
- Fixed NeuralDeck PDF page count (was `text.count("\x0c")+1`, always 1).

## 0.1.1 — Review hardening (2026-11-01)

- Fixed spatial-recall options to carry entity ids (grading was unwinnable from the UI).
- Fixed figure display/API path split: `/api/figure/select` now returns `figure_url` for the canvas while keeping the server path for analysis.
- Lazy AtlasStore init (no `data/` side effect on import); query-safe POST routing; PDF import returns a figure hint.
- SAM sends the correct image MIME; Muse/SAM refuse >45 MB images with a clear message (50 MB API limit).
- PDF figure selection rejected with actionable guidance instead of an obscure PIL error.
- Bundled basal-ganglia SVG schematic; demo runner refreshes the static sample JSON so UI and fixture never drift; pathway hint no longer leaks the answer.

## 0.1.0 — P0 vertical slice (2026-11-01)

- Standalone Atlas app (stdlib server + zero-dep workspace UI), own config/data/tests/docs/versioning.
- Isolated NeuralDeck adapter (reuse document extraction when present, local fallback; zero writes into NeuralDeck).
- Muse Spark/Wonder provider with structured JSON schema + 0–1000 grounding validation; SAM 3.1 provider with honest bbox fallback.
- Manual figure selection with provenance; shared-model canvas + knowledge graph; 4 visual learning modes; atomic persistence with separate corrections + cache.
- Basal-ganglia fixture + honest fixture/live demo runner; offline-safe test suite.
