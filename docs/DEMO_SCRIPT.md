# Demo script — jaw-drop cut (≈3 minutes, hackathon, fully offline-safe)

Setup (before judges arrive): `python -m atlas.app` → open workspace →
click **Try the basal-ganglia demo**. Fixture loads from `/static/`
— no key, no network. Kill Wi-Fi if you want to prove it.

## 0:00–0:20 — The hook (one sentence + one click)
> "Drop any scientific figure in — Atlas turns it into something you can
> walk through, listen to, and be tested on."

Click **✦ Reveal**. Scanline sweeps, structures pop in one-by-one with
confidence labels. Land the line:
> "That's not a slideshow — that's the validated model resolving,
> entity by entity, straight from the figure."

## 0:20–1:20 — Showpiece 1: cinematic guided tour
Press **▶ Tour**. Camera pans structure-to-structure, caption bar narrates
each stop (striatum → GPe → STN → GPi). Say nothing for two stops — let
the motion carry it. Then interrupt:
> "Every stop is the same analysis object the graph uses. Canvas and
> knowledge graph can never diverge — select either side, the other
> follows."

Click a graph node mid-tour to prove it. `‹ ›` steps, `Esc` stops.
Voice toggle on: tour speaks each stop via the browser's on-device voice.

## 1:20–2:00 — Showpiece 2: browser-voice narration
Select striatum → **🔊 Narrate**. On-device voice reads name +
description + source evidence. The point:
> "No cloud TTS, no key, no audio file — `speechSynthesis` only.
> Field classroom, airplane, censored network: it still talks."

Flip the voice in the dropdown if judges ask — all local voices listed.

## 2:00–2:40 — Showpiece 3: AI-vision reveal + quiz punch
Replay **✦ Reveal** (highest-confidence first), then without pause hit
**Quiz on figure**: labels vanish, one structure glows.
> "You — which structure is highlighted?"

Let a judge answer, click to grade live. Then **Study pack** → quality
score + diagram + podcast + MP4, all from the same model.
> "One model, every format. Nothing invented — every line traces to an
> entity, a relationship, or stated evidence."

## 2:40–3:00 — Close (offline proof)
> "Pull the network cable. Everything you just saw — tour, voice, reveal,
> quiz, study pack — runs on the fixture you already have. Live Muse/SAM
> only upgrades the analysis; it never gates the experience."

Fallback (no fixture): `python demo/basal_ganglia_demo.py --fixture-only`
rebuilds `/static/basal_ganglia_sample.json` — same 3 minutes.

Cues: Tour = `▶ Tour` · Reveal = `✦ Reveal` · Narrate = `🔊 Narrate` ·
stop anything = `Esc`. Reduced-motion users get the same stops with no
animation (`prefers-reduced-motion` honored).
