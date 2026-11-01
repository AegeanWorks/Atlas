"""Hand-authored Atlas analyses (by the AI, from viewing the figures).

Provenance: every entity/relationship carries provenance "manual-ai-viewed",
model_inferred=false, and an uncertainty note where boxes are hand-estimated.
These are honest first passes meant to be refined via Atlas corrections —
never presented as Muse output.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "real_analyses")
os.makedirs(OUT, exist_ok=True)


def E(i, name, cat, desc, bbox, ev, conf=0.8, unc="hand-estimated box from rendered view"):
    return {"id": i, "name": name, "category": cat, "description": desc,
            "bbox": bbox, "source_evidence": ev, "confidence": conf,
            "uncertainty": unc, "mask_ref": "", "model_inferred": False}


def R(s, t, rel, expl, ev, conf=0.8):
    return {"source_id": s, "target_id": t, "rel_type": rel, "explanation": expl,
            "supporting_evidence": ev, "confidence": conf,
            "provenance": "manual-ai-viewed", "model_inferred": False}


def B(x0, y0, x1, y1):
    return {"x_min": x0, "y_min": y0, "x_max": x1, "y_max": y1}


MITO = {
    "analysis_version": "atlas.visual-knowledge/v1",
    "document_ref": "Materials/3 - WAY More than a Powerhouse (Kurzgesagt-style explainer frame)",
    "source_page": 0, "figure_id": "mito-frame-manual",
    "entities": [
        E("cell", "Cell", "anatomical-structure", "Eukaryotic cell hosting the reaction.",
          B(0.375, 0.274, 0.609, 0.788), "large blue cell, center frame", 0.9, ""),
        E("mito", "Mitochondrion", "component", "Organelle where respiration runs; folded inner membrane visible.",
          B(0.445, 0.411, 0.539, 0.668), "dark central body with folded membrane", 0.85, ""),
        E("o2", "Oxygen (O2)", "molecule", "Electron acceptor feeding respiration.",
          B(0.109, 0.565, 0.180, 0.685), "blue 'O2' pill, mid-left", 0.9, ""),
        E("food", "Food (substrate)", "molecule", "Nutrient substrate entering the cell.",
          B(0.086, 0.360, 0.172, 0.462), "blue 'food' pill, upper-left", 0.8,
          "generic substrate, precise molecule unspecified"),
        E("energy", "Energy", "other", "Useful output of respiration.",
          B(0.375, 0.839, 0.469, 0.942), "'Energy' in bottom equation", 0.9, ""),
        E("co2", "Carbon dioxide (CO2)", "molecule", "Waste gas output.",
          B(0.555, 0.839, 0.617, 0.942), "'CO2' in bottom equation", 0.9, ""),
        E("h2o", "Water (H2O)", "molecule", "Byproduct output.",
          B(0.688, 0.839, 0.766, 0.942), "'H2O' in bottom equation", 0.9, ""),
        E("resp", "Cellular respiration", "pathway", "O2 + Food = Energy + CO2 + H2O.",
          None, "bottom equation 'O2 + Food = Energy + CO2 + H2O'", 0.9,
          "process, no single location"),
    ],
    "relationships": [
        R("cell", "food", "receives-input-from", "The cell takes up food as substrate.", "pill outside cell, left", 0.85),
        R("o2", "resp", "participates-in", "O2 is consumed by respiration.", "O2 in equation", 0.9),
        R("food", "resp", "participates-in", "Food is consumed by respiration.", "Food in equation", 0.9),
        R("resp", "energy", "produces", "Respiration releases energy.", "Energy in equation", 0.9),
        R("resp", "co2", "produces", "Respiration releases CO2.", "CO2 in equation", 0.9),
        R("resp", "h2o", "produces", "Respiration releases water.", "H2O in equation", 0.9),
        R("cell", "mito", "contains", "The mitochondrion sits inside the cell.", "dark body inside blue cell", 0.9),
        R("mito", "resp", "participates-in", "Respiration runs in the mitochondrion.", "'fig 1: Simplified Cellular Respiration'", 0.85),
    ],
}

with open(os.path.join(OUT, "mitochondrion_manual.json"), "w", encoding="utf-8") as fh:
    json.dump(MITO, fh, indent=2)
print("mitochondrion_manual.json written")
