# Architecture — Atlas

Fully standalone application with no dependency on any other project.

```
static/index.html + app.js ──► atlas/app.py (stdlib HTTP, :8765)
        │ canvas + graph share ONE VisualAnalysis object
        ▼
┌──────────────┐  ┌───────────────┐  ┌────────────────┐  ┌─────────────┐
│ ingestion.py │─►│ muse_provider │─►│ sam_provider   │─►│ store.py    │
│ PDF/PNG/JPEG │  │ Muse Spark /  │  │ SAM 3.1 masks; │  │ analyses,   │
│ manual crop  │  │ Wonder, 0-1000│  │ bbox fallback  │  │ corrections │
│ provenance   │  │ grid, schema  │  │ never fake     │  │ cache       │
└──────┬───────┘  └───────────────┘  └────────────────┘  └─────────────┘
       │ text_backend.py + doc_text.py: in-project text extraction
       │ (PDF/DOCX/PPTX/TXT/transcripts), no external project.
       ▼
  learning.py (4 recall modes, seeded) — spatial recall, distinct from flashcards
```

## Layer responsibilities

- **Frontend**: zoom/pan canvas, toggle labels/masks, entity list, SVG knowledge
  graph, detail pane with evidence, 4 learning modes. Selecting canvas ↔ graph
  sets the same `selected` id — the two views cannot diverge.
- **Application backend** (`app.py`): import, figure select, analyze (cached),
  segment (cached), analysis load/save, corrections, learning challenges.
- **Document text** (`text_backend.py` + `doc_text.py`): extraction lives
  in-project (routines originally adapted from NeuralDeck, now Atlas-owned).
- **Meta provider layer**: `muse_provider.py` (Chat Completions + json_schema),
  `sam_provider.py` (Responses API `sam-3.1`). Replaceable `transport` callable
  in both for tests and future providers.
- **Visual processing** (`ingestion.py`): Pillow crops, normalized coords,
  SHA-256 provenance.
- **Knowledge layer** (`schema.py`): frozen dataclasses, `atlas.visual-knowledge/v1`,
  coordinate validation, `coerce_muse_payload` from 0–1000 grid.
- **Persistence** (`store.py`): atomic JSON; corrections separate from model output.

## Key decisions

- Stdlib HTTP server + zero-dependency frontend: installs in one `pip install`,
  launches with one command, testable with pytest only.
- Full-document upload is forbidden by design: providers receive the figure crop.
- Coordinates stored 0–1, exchanged with Meta 0–1000, rendered as CSS % (/10).
- Fixture data is always labelled fixture; live results require an API key.
