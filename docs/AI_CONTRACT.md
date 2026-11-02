# AI contract — driving Atlas autonomously (atlas.api/v1)

## 5-line quickstart (no key, no browser)

```
python -m atlas.selftest            # 1. prove the app works (JSON report, exit 0/1)
python -m atlas.cli agent           # 2. watch an AI drive it end to end, offline
python -m atlas.cli models          # 3. see every model
curl /api/state?figure_id=<id>      # 4. one glance: digest, iso, deck, stats, URLs
curl "/api/models?format=text"      # 5. read all models as plain text
```

This document and `GET /api/contract` describe everything an AI agent needs to
create, read, and teach from visual models with no browser and no human.

## Setup

```
pip install -r requirements.txt
MODEL_API_KEY=... python -m atlas.app --port 8765   # or: ./start.ps1
```

Reading models never needs a key. Live creating/segmenting does; without a key,
`auto-create` builds an honest offline-extractive model (`offline: true`,
keyword frequency with quoted evidence) that drives the same endpoints.

## Autonomous loop

1. `GET /api/health` → confirm version, models (`muse-spark-1.3`, `sam-3.1`).
2. Drop a file: `POST /api/upload` (multipart, field `file`) → `staged_path`.
   Or reference a server-local path or URL directly (CLI: `python -m atlas.cli create`).
3. `POST /api/auto-create {"path": staged_path-or-url, "note": "<caption>"} →
   images/video-frames: visual entities + boxes; PDF/EPUB/TXT/link/YouTube:
   text entities with quoted evidence. Both save one model (`source_kind` tells which).
4. `GET /api/models` → see every model (ids, entity/relationship counts).
5. `GET /api/analysis?figure_id=<id>` → read the full model (grounded boxes,
   evidence, confidence). Canvas and graph render this same object.
6. `POST /api/segment {"image_path", "prompt": "<short noun>", "entity_id"}` →
   SAM 3.1 mask, then `POST /api/analysis/attach-mask` to persist it.
7. `POST /api/learn {"analysis", "mode", "seed"}` + `/api/learn/grade` →
   spatial-recall, pathway-tracing, visual-identification, relationship-recall.
   CLI: `python -m atlas.cli learn <id> spatial-recall --answer <id>`.
8. 3D + flashcards: `GET /api/model3d?figure_id=<id>&format=obj` (printable OBJ),
   `POST /api/flashcards` (deck), `GET /api/flashcards/export?figure_id=<id>`
   (Anki TSV). CLI: `deck <id> [--anki out.tsv]`, `obj <id> [--out out.obj]`.

## Rules agents must obey

- Never claim a live result without a key: keyless calls fail fast and say so.
- Never confuse boxes with masks: `kind` is `mask` only with a decoded mask.
- Coordinates are normalized 0..1 in storage, 0..1000 at the Meta boundary.
- Relationships must reference known entity ids; types come from the schema.
- Never send full documents to Meta — crops (+ optional note) only.
