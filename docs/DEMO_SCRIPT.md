# Demo script — Basal ganglia (≈6 minutes, hackathon)

1. `python -m atlas.app` → open the Atlas workspace. (30s)
2. Import a PDF of a licensed basal-ganglia figure; provenance panel shows SHA + page. (30s)
3. Select the figure with a manual crop; original stays visible. (30s)
4. Analyze with Muse Spark — entities + relationships appear with confidence and
   0–1000-grounded boxes; point out striatum. (60s)
5. Select striatum → "Segment selected (SAM)" — mask overlays the original; note the honest
   `bbox-fallback` label if no mask decodes. (60s)
6. Click striatum on the canvas → graph focuses; click GPi in the graph →
   canvas highlights. Same model, no divergence. (45s)
7. Trace direct (striatum→GPi) vs indirect (striatum→GPe→STN→GPi) pathways. (45s)
8. Hide labels → spatial recall: "which structure is highlighted?" Answer live. (45s)
9. Open the detail pane: source evidence + provenance per entity; corrections are
   stored separately. (30s)

Fallback (no key / no network): `python demo/basal_ganglia_demo.py --fixture-only`
runs all 10 acceptance steps on the labelled fixture — never presented as live.
