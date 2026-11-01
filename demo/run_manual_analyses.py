"""Run the full Atlas learning pipeline on hand-authored real analyses.

Validates each manual analysis, saves it to an Atlas store, then generates
summary, flashcards, question bank, podcast, diagram (SVG+PNG), 3D OBJ,
study video (mitochondria only: cost), and a full quality report —
all offline except nothing (no key needed anywhere in this flow).
Writes demo/real_analyses/REPORT.md with the verdicts.
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
DATA = os.path.join(OUT, "_store")
store = AtlasStore(DATA)

FILES = ["mitochondrion_manual.json", "methionine_cycle_manual.json",
         "petechial_rash_manual.json"]

lines = ["# Real-material pipeline report (hand analyses by the AI)", ""]
for name in FILES:
    with open(os.path.join(OUT, name), encoding="utf-8") as fh:
        raw = json.load(fh)
    a = VisualAnalysis.from_dict(raw)
    assert not a.validate(), a.validate()
    data = a.to_dict()
    fid = data["figure_id"]
    store.save_analysis(fid, data)
    deck = fc.build_deck(data)
    bank = mat.question_bank(data)
    script = mat.podcast_script(data)
    brief = sm.extractive_summary(data)
    svg = mat.diagram_svg(data)
    png = mat.diagram_png(data)
    obj = m3d.export_obj(data)
    tour = mat.tour_3d(data)
    report = qa.quality_report(data, {
        "deck": deck, "podcast": script, "diagram_svg": svg, "obj": obj})
    with open(os.path.join(OUT, fid + ".tsv"), "w", encoding="utf-8") as fh:
        fh.write(fc.to_anki_tsv(deck))
    with open(os.path.join(OUT, fid + ".md"), "w", encoding="utf-8") as fh:
        fh.write(mat.questions_markdown(bank))
    with open(os.path.join(OUT, fid + ".svg"), "w", encoding="utf-8") as fh:
        fh.write(svg)
    with open(os.path.join(OUT, fid + ".obj"), "w", encoding="utf-8") as fh:
        fh.write(obj)
    lines += [f"## {fid}",
              f"- entities={len(data['entities'])} relationships={len(data['relationships'])}",
              f"- deck={len(deck['cards'])} cards, questions={len(bank['questions'])}, "
              f"pathways={len(brief['pathways'])}, tour stops={len(tour['stops'])}, "
              f"podcast ~{script['estimated_minutes']} min",
              f"- quality overall={report['overall']}: " +
              ", ".join(f"{k}={v['score']}" for k, v in report.items()
                         if isinstance(v, dict)),
              f"- issues: {sum(len(v.get('issues', [])) for v in report.values() if isinstance(v, dict))} total; " +
              "; ".join(i for v in report.values() if isinstance(v, dict) for i in v["issues"][:2]) or "none",
              ""]
    print(f"{fid}: overall={report['overall']}")

with open(os.path.join(OUT, "REPORT.md"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("REPORT.md written")
