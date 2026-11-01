"""Hand-authored Atlas analysis 3/3: petechial rash diagnostic flowchart (23.jpg).

My reading: title + definition, red-flags panel, etiology and vascular-integrity
panels, a central clinical photo, then a binary tree Febrile/Toxic vs
Afebrile/nontoxic, each splitting Palpable vs Non-palpable into differential
lists, with a Work Up panel at the bottom. All entities and flows below are
what I see on the figure; boxes are hand-estimated, marked as such.
"""
import json
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "real_analyses")
os.makedirs(OUT, exist_ok=True)
UNC = "hand-estimated box from rendered view; refine via correction"


def E(i, name, cat, desc, bbox, ev, conf=0.8, unc=UNC):
    return {"id": i, "name": name, "category": cat, "description": desc,
            "bbox": bbox, "source_evidence": ev, "confidence": conf,
            "uncertainty": unc, "mask_ref": "", "model_inferred": False}


def R(s, t, rel, expl, ev, conf=0.8):
    return {"source_id": s, "target_id": t, "rel_type": rel, "explanation": expl,
            "supporting_evidence": ev, "confidence": conf,
            "provenance": "manual-ai-viewed", "model_inferred": False}


def B(x0, y0, x1, y1):
    return {"x_min": x0, "y_min": y0, "x_max": x1, "y_max": y1}


RASH = {
    "analysis_version": "atlas.visual-knowledge/v1",
    "document_ref": "Materials/23.jpg (petechial rash diagnostic flowchart)",
    "source_page": 0, "figure_id": "petechial-rash-manual",
    "entities": [
        E("rash", "Petechial rash", "anatomical-structure", "Pinpoint hemorrhagic lesions under 2 mm.",
          B(0.30, 0.02, 0.64, 0.21), "green title box with definition", 0.9, ""),
        E("photo", "Rash photograph", "other", "Clinical photo of petechiae, central reference.",
          B(0.415, 0.36, 0.585, 0.52), "central skin photo", 0.9, ""),
        E("redflags", "Red flags", "other", "Fever, toxic appearance, hypotension, mucosal lesions, severe pain, extremes of age, immunosuppression, new medication.",
          B(0.005, 0.02, 0.135, 0.335), "pink panel, upper left", 0.85, ""),
        E("etiology", "Etiology panel", "other", "Abnormal hemostasis: thrombocytopenia, platelet dysfunction, clotting factor defects.",
          B(0.735, 0.02, 1.0, 0.25), "purple panel, upper right", 0.85, ""),
        E("vascular", "Vascular integrity disruption", "process", "Trauma, infection, vasculitis, collagen disorders.",
          B(0.875, 0.02, 1.0, 0.20), "purple sub-panel, far right", 0.8, ""),
        E("febrile", "Febrile, Toxic", "other", "Feverish/toxic branch of the triage.",
          B(0.045, 0.42, 0.285, 0.53), "peach box, left", 0.9, ""),
        E("afebrile", "Afebrile, nontoxic", "other", "Non-fever branch of the triage.",
          B(0.72, 0.42, 0.99, 0.53), "pale blue box, right", 0.9, ""),
        E("palp_feb", "Palpable (febrile)", "other", "Palpable lesions under febrile/toxic.",
          B(0.005, 0.68, 0.22, 0.79), "peach box, lower left", 0.9, ""),
        E("nonpalp_feb", "Non-palpable (febrile)", "other", "Non-palpable lesions under febrile/toxic.",
          B(0.315, 0.68, 0.50, 0.79), "peach box, lower middle", 0.9, ""),
        E("palp_afeb", "Palpable (afebrile)", "other", "Palpable lesions under afebrile.",
          B(0.645, 0.68, 0.80, 0.79), "blue box, lower middle-right", 0.9, ""),
        E("nonpalp_afeb", "Non-palpable (afebrile)", "other", "Non-palpable lesions under afebrile.",
          B(0.845, 0.68, 1.0, 0.79), "blue box, lower right", 0.9, ""),
        E("ddx_feb_palp", "Febrile palpable differentials", "other", "Meningococcemia, disseminated gonococcal infection, RMSF, HSP, endocarditis.",
          B(0.005, 0.85, 0.255, 0.995), "list box, bottom left", 0.85, ""),
        E("ddx_feb_nonpalp", "Febrile non-palpable differentials", "other", "Purpura fulminans, DIC, TTP.",
          B(0.315, 0.85, 0.49, 0.995), "list box, bottom middle", 0.85, ""),
        E("ddx_afeb_palp", "Afebrile palpable differentials", "other", "Autoimmune vasculitis (lupus, RA, Sjogren, GPA, EGPA, microscopic); viral (echovirus, coxsackie, measles, parvovirus).",
          B(0.595, 0.85, 0.835, 0.995), "list box, bottom middle-right", 0.85, ""),
        E("ddx_afeb_nonpalp", "Afebrile non-palpable differentials", "other", "ITP, APLS, HIT, cholesterol embolism, amyloidosis, nutritional deficiency.",
          B(0.775, 0.85, 0.995, 0.995), "list box, bottom right", 0.85, ""),
        E("workup", "Work Up", "process", "CBC, coagulation studies, urinalysis, occult blood, hepatitis serology, protein electrophoresis, ASO titre, ANA, ANCA, RF, immunoglobulins, biopsy, ultrasound.",
          B(0.30, 0.90, 0.70, 0.995), "workup panel, bottom center", 0.8,
          "dense small type; list may be partial"),
    ],
    "relationships": [
        R("rash", "febrile", "produces", "Triage splits petechiae into febrile/toxic cases.", "blue arrow left", 0.9),
        R("rash", "afebrile", "produces", "Triage splits petechiae into afebrile cases.", "blue arrow right", 0.9),
        R("febrile", "palp_feb", "produces", "Febrile branch splits by palpability.", "blue arrows", 0.9),
        R("febrile", "nonpalp_feb", "produces", "Febrile branch splits by palpability.", "blue arrows", 0.9),
        R("afebrile", "palp_afeb", "produces", "Afebrile branch splits by palpability.", "blue arrows", 0.9),
        R("afebrile", "nonpalp_afeb", "produces", "Afebrile branch splits by palpability.", "blue arrows", 0.9),
        R("palp_feb", "ddx_feb_palp", "produces", "Palpable febrile rash suggests listed infections/vasculitis.", "arrow to list", 0.85),
        R("nonpalp_feb", "ddx_feb_nonpalp", "produces", "Non-palpable febrile rash suggests purpura fulminans/DIC/TTP.", "arrow to list", 0.85),
        R("palp_afeb", "ddx_afeb_palp", "produces", "Palpable afebrile rash suggests autoimmune/viral causes.", "arrow to list", 0.85),
        R("nonpalp_afeb", "ddx_afeb_nonpalp", "produces", "Non-palpable afebrile rash suggests platelet/coagulation causes.", "arrow to list", 0.85),
        R("redflags", "febrile", "participates-in", "Red flags push toward the febrile/toxic branch.", "adjacent panel", 0.75),
        R("etiology", "afebrile", "participates-in", "Hemostasis defects frame the afebrile differentials.", "adjacent panel", 0.7),
        R("workup", "rash", "regulates", "Workup panel governs confirmation for all branches.", "bottom panel spanning tree", 0.75),
        R("photo", "rash", "participates-in", "Photo grounds what petechiae look like.", "central photo", 0.9),
    ],
}

with open(os.path.join(OUT, "petechial_rash_manual.json"), "w", encoding="utf-8") as fh:
    json.dump(RASH, fh, indent=2)
print("petechial_rash_manual.json written")
