"""Live-vs-manual pipeline comparison (needs MODEL_API_KEY/META_API_KEY in env).

Reads the three hand-authored analyses plus three live Muse analyses,
validates everything, runs the FULL artifact + quality pipeline on each, and
writes demo/real_analyses/REPORT.md. The key is NEVER written anywhere: it
travels only in the process environment (AtlasConfig redacts it from logs).
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atlas import flashcards as fc
from atlas import materials as mat
from atlas import models3d as m3d
from atlas import quality as qa
from atlas import summaries as sm
from atlas.schema import VisualAnalysis
from atlas.store import AtlasStore

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "real_analyses")
LIVE = r"C:\Users\Yunus-Emre\AppData\Local\Temp\atlas_live"
DATA = os.path.join(OUT, "_store")
store = AtlasStore(DATA)

PAIRS = [
    ("mitochondrion_manual.json", "mito_live.json"),
    ("methionine_cycle_manual.json", "methionine_live.json"),
    ("petechial_rash_manual.json", "rash_live.json"),
]


def run_one(raw: dict, tag: str) -> dict:
    data = VisualAnalysis.from_dict(raw).to_dict()
    store.save_analysis(data["figure_id"] + "-" + tag, data)
    deck = fc.build_deck(data)
    bank = mat.question_bank(data)
    script = mat.podcast_script(data)
    brief = sm.extractive_summary(data)
    svg = mat.diagram_svg(data)
    obj = m3d.export_obj({**data, "entities": [e for e in data["entities"]]})
    report = qa.quality_report(data, {"deck": deck, "podcast": script,
                                      "diagram_svg": svg, "obj": obj})
    return {"entities": len(data["entities"]), "relationships": len(data["relationships"]),
            "cards": len(deck["cards"]), "questions": len(bank["questions"]),
            "pathways": len(brief["pathways"]), "podcast_min": script["estimated_minutes"],
            "overall": report["overall"],
            "scores": {k: v["score"] for k, v in report.items() if isinstance(v, dict)},
            "issues": [i for v in report.values() if isinstance(v, dict) for i in v["issues"]]}


lines = ["# Manual-vs-live pipeline report", "",
         "Manual = hand analysis by the AI from viewing the figures. "
         "Live = Muse Spark 1.3 on the same figures, same day.", ""]
for manual_name, live_name in PAIRS:
    with open(os.path.join(OUT, manual_name), encoding="utf-8") as fh:
        manual_raw = json.load(fh)
    with open(os.path.join(LIVE, live_name), encoding="utf-8") as fh:
        live_raw = json.load(fh)
    m = run_one(manual_raw, "manual")
    lv = run_one(live_raw, "live")
    fid = manual_raw.get("figure_id", "?")
    lines += [f"## {fid}",
              f"- manual: E={m['entities']} R={m['relationships']} cards={m['cards']} Q={m['questions']} overall={m['overall']}",
              f"- live:   E={lv['entities']} R={lv['relationships']} cards={lv['cards']} Q={lv['questions']} overall={lv['overall']}",
              f"- live scores: {lv['scores']}",
              f"- manual issues: {m['issues'] or ['none']}",
              f"- live issues: {lv['issues'] or ['none']}", ""]
    print(f"{fid}: manual={m['overall']} live={lv['overall']}")

with open(os.path.join(OUT, "REPORT.md"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("REPORT.md written")
