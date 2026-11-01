# Changelog

## 0.18.0 — Chunk-id collisions fixed (2026-11-01)

- Long-document merge disambiguates reused synthetic ids (first-wins remap),
  so merged books always validate; the committed 245-entity book model is
  repaired without touching any names, evidence, or relations.
- A demo-integrity test now pins every committed analysis and artifact
  (schema, Anki shape, SVG parse, OBJ cuboid math, REPORT coverage) —
  it caught this bug before release.

## 0.17.0 — Big-model honesty (2026-11-01)

- Pathway lists cap at 12 with totals (a 245-entity book yields 562 routes;
  the worksheet shows the best, not all of them).
- Podcast quality scores the trimmed episode scope, not the whole book;
  scripts record covered_ids/trimmed_from.
- Full book artifacts committed (TSV, questions, podcast, diagram) with
  re-scored REPORT (83.3).

## 0.16.0 — Editor's pass on real output (2026-11-01)

- Summaries use arrow-form relations with hub caps (no more doubled verbs or
  17-link bullets); person/place join the entity categories; podcast scripts
  trim to top-degree entities so episodes stay in the study window.
- Video frames retry once with an explicit grounding demand; merged models
  keep real boxes instead of nulling them.

## 0.15.0 — Whole books become models (2026-11-01)

- Chunked long-text analysis: books split at paragraph boundaries, every
  chunk analyzed, entities merged by normalized name, relationships remapped
  and deduped. Proven live on a 209k-char Turkish book in one auto-create.
- Paragraph-aware `chunk_text` in sources; `merge_analyses` in schema with
  longest-description-wins and evidence concatenation.

## 0.14.0 — Live-model verification (2026-11-01)

- First production Muse runs on real materials: hand analyses vs live Spark
  analyses score 93.8-100 on the same quality battery; live video auto-create
  (4 frames, 36 entities) is honest about boxless frames with a text-only
  warning and partial-grounding notes.
- SAM adapter scans raw responses for localizable output before falling back,
  and records the empty-output finding; flashcard decks dedupe exact repeats.
- `demo/real_analyses/`: three hand-authored analyses, three live Muse
  analyses, every artifact, and the comparison REPORT.

## 0.13.0 — Eyes on the material (2026-11-01)

- Frame quality gate: blank transition cards dropped, near-duplicates removed,
  low-detail frames (paper texture, grain) kept but flagged — calibrated
  against real Kurzgesagt-style footage (texture 38 vs content 580-2800).
  Video auto-create analyzes only frames worth analyzing.
- Real-library hardening: EPUB manifests with href-first attributes,
  JFIF/WebP/GIF/BMP end to end, full-length ingestion text, AES PDFs via
  `cryptography` (201/204 files import; only scanned-image PDFs refuse).

## 0.12.0 — Automatic video + quality analysis (2026-11-01)

- Automatic study-video creation: Pillow storyboard (title, entity spotlights,
  recap) encoded to real H.264 MP4 via the bundled imageio-ffmpeg binary —
  no system tools, no key, fully offline after install.
- `atlas/quality.py`: 0–100 analyzers with named checks for videos, flashcards,
  infographics, podcasts, and 3D models; `POST /api/quality`, in-app scores,
  CLI `quality`/`video`. Real trials: fixture deck/podcast/diagram/OBJ score
  100; stub videos and broken geometry score low with named issues.
- Real-materials hardening (204 mixed files: 201 import): EPUB manifest parsing
  no longer assumes attribute order; JFIF/WebP/GIF/BMP ingest end to end;
  ingestion keeps full text (trimming only at the Muse boundary); AES-encrypted
  PDFs read via `cryptography`; fixed an inline-import scoping crash that broke
  every route after the quality endpoints landed.

## 0.11.0 — Proven on 81 real medical PDFs (2026-11-01)

- Trialled against a real 81-file, 77 MB medical library: 78 import with fast
  Turkish-safe text extraction, 3 scanned-image PDFs refused with page counts.
- Scanned-PDF errors now name the page count and the OCR way out.
- `atlas.cli batch <folder>`: offline import report for whole folders.
- PDF pages render to figures (`POST /api/pdf/render`, UI button) with optional
  PyMuPDF; honest install hint without it. `/api/import` reports page counts.

## 0.10.0 — Every format is learning material (2026-11-01)

- Study diagram posters (SVG + Pillow PNG) redrawn from boxes and arrows.
- 3D layer tours: ordered stops with observation cues and camera hints.
- Podcast scripts: two-host walkthrough with evidence, pathway segment, recap,
  quiz teasers, and speaking-time estimate (markdown + JSON, TTS-ready).
- Question banks: every generatable question with answers + evidence, JSON or
  markdown worksheet; CLI `materials` covers all four.

## 0.9.0 — AI-testable, AI-seeable, AI-usable (2026-11-01)

- `python -m atlas.selftest`: one offline command proves every layer works and
  prints a JSON report (exit 0/1) — for AI agents and CI.
- `GET /api/state`: one call sees a whole model (digest, iso, deck size,
  stats, artifact URLs); `GET /api/models?format=text` reads all models as
  plain text.
- `python -m atlas.cli agent`: watches an AI drive the full loop offline.

## 0.8.0 — One-click everything (2026-11-01)

- Double-click launchers (`start.bat`/`install.bat` join the ps1/sh scripts).
- On-figure quizzes: a structure highlights on the canvas, labels hide so names
  can't leak, answers grade inline with a running score.
- Auto study pack: offline extractive brief (overview, evidence bullets,
  pathway chains, stats) with Muse-polished prose when a key is set; CLI
  `summary` for agents.
- Iso layer slider peels the 3D stack category by category.

## 0.7.0 — 3D models + flashcards (2026-11-01)

- 3D from any 2D model: offline isometric stacked canvas view (3D toggle) and
  Wavefront OBJ export (one named cuboid per located entity, text-only entities
  listed, never faked into geometry) — printable tactile study models.
- Flashcards from the same model: highlight/description/relation cards, in-app
  review with flip + self-graded score, Anki TSV export, CLI `deck`/`obj`.

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
