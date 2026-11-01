"""Hand-authored Atlas analysis 2/3: methionine cycle pathway (26.png), by the AI.

Reading the figure: a green-box cycle Methionine -> SAM -> SAH -> Homocysteine
-> Methionine, with the folate loop (THF/5-MTHF, MS) feeding remethylation on
the left, BHMT/betaine as the alternate route, transsulfuration draining
Homocysteine -> Cysteine leftward, MAT2A driving SAM synthesis, AHCY/MT around
SAH, and outputs to polyamines, methylations, purine/pyrimidine synthesis.
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


CYCLE = {
    "analysis_version": "atlas.visual-knowledge/v1",
    "document_ref": "Materials/26.png (methionine cycle pathway diagram)",
    "source_page": 0, "figure_id": "methionine-cycle-manual",
    "entities": [
        E("methionine", "Methionine", "molecule", "Essential amino acid; cycle entry and hub.",
          B(0.472, 0.136, 0.602, 0.233), "green box 'Methionine', top center", 0.9, ""),
        E("sam", "SAM", "molecule", "S-adenosylmethionine; universal methyl donor.",
          B(0.713, 0.506, 0.783, 0.623), "green box 'SAM', right", 0.9, ""),
        E("sah", "SAH", "molecule", "S-adenosylhomocysteine; SAM after methyl donation.",
          B(0.542, 0.837, 0.622, 0.934), "green box 'SAH', bottom", 0.9, ""),
        E("hcy", "Homocysteine", "molecule", "Branch point: remethylated or transsulfurated.",
          B(0.321, 0.506, 0.522, 0.603), "green box 'Homocysteine', middle-left", 0.9, ""),
        E("cysteine", "Cysteine", "molecule", "Transsulfuration end product.",
          B(0.020, 0.506, 0.141, 0.603), "green box 'Cysteine', far left", 0.9, ""),
        E("adenosine", "Adenosine", "molecule", "Released when SAH becomes homocysteine.",
          B(0.271, 0.837, 0.392, 0.934), "green box 'Adenosine', bottom-left", 0.85, ""),
        E("betaine", "Betaine", "molecule", "Methyl donor for the BHMT route.",
          B(0.371, 0.642, 0.472, 0.739), "green box 'Betaine'", 0.85, ""),
        E("dmg", "Dimethylglycine", "molecule", "Betaine after methyl donation.",
          B(0.432, 0.584, 0.622, 0.661), "green box 'Dimethylglycine'", 0.85, ""),
        E("thf", "THF", "molecule", "Tetrahydrofolate; folate loop carrier.",
          B(0.291, 0.214, 0.351, 0.292), "'THF', upper left loop", 0.85, ""),
        E("mthf", "5-MTHF", "molecule", "5-methyl-THF; feeds the MS remethylation step.",
          B(0.241, 0.331, 0.341, 0.409), "'5 MTHF', left loop", 0.85, ""),
        E("ms", "MS (methionine synthase)", "protein", "Enzyme remethylating homocysteine via folate.",
          B(0.357, 0.409, 0.412, 0.486), "blue 'MS' label on left arrow", 0.8, ""),
        E("bhmt", "BHMT", "protein", "Betaine-homocysteine methyltransferase; alternate route.",
          B(0.402, 0.506, 0.482, 0.584), "blue 'BHMT' label", 0.8, ""),
        E("mat2a", "MAT2A", "protein", "Enzyme synthesizing SAM from methionine.",
          B(0.602, 0.428, 0.693, 0.506), "blue 'MAT2A' label, right arrow", 0.8, ""),
        E("ahcy", "AHCY", "protein", "Enzyme converting SAH to homocysteine + adenosine.",
          B(0.392, 0.739, 0.472, 0.817), "blue 'AHCY' label", 0.8, ""),
        E("mt", "MT (methyltransferases)", "protein", "Enzymes moving methyl groups from SAM.",
          B(0.683, 0.720, 0.723, 0.798), "blue 'MT' label", 0.75,
          "abbreviation only; class of enzymes"),
        E("ch3", "Methyl group (CH3)", "molecule", "Transferred unit; ends in methylations.",
          B(0.723, 0.798, 0.783, 0.875), "'CH3' label above Methylations", 0.85, ""),
        E("methylations", "Methylations", "process", "Downstream methylation reactions.",
          B(0.833, 0.837, 0.964, 0.934), "dark box 'Methylations', bottom-right", 0.85, ""),
        E("polyamines", "Polyamine synthesis", "pathway", "SAM-consuming output route.",
          B(0.853, 0.428, 0.974, 0.525), "dark box 'Polyamine synthesis'", 0.85, ""),
        E("purines", "Purine synthesis", "pathway", "Folate-linked output at top right.",
          B(0.843, 0.019, 0.964, 0.156), "dark box 'Purine synthesis'", 0.85, ""),
        E("folate_cycle", "Folate cycle", "pathway", "THF/5-MTHF loop feeding remethylation.",
          B(0.201, 0.233, 0.301, 0.311), "'Folate cycle' label, upper left", 0.8,
          "label region; approximate"),
        E("salvage", "Methionine salvage cycle", "pathway", "Return route shown upper right.",
          B(0.582, 0.292, 0.763, 0.370), "'Methionine salvage cycle' label", 0.75,
          "label region; approximate"),
        E("transsulf", "Transsulfuration pathway", "pathway", "Homocysteine → Cysteine drain.",
          B(0.120, 0.537, 0.311, 0.615), "label left of Homocysteine", 0.8,
          "label overlaps diagram; approximate"),
        E("met_cycle", "Methionine cycle", "pathway", "Core Methionine→SAM→SAH→Homocysteine loop.",
          B(0.452, 0.681, 0.643, 0.759), "center label", 0.8,
          "label overlaps diagram; approximate"),
    ],
    "relationships": [
        R("methionine", "sam", "produces", "MAT2A converts methionine to SAM.", "down-right arrow via MAT2A", 0.85),
        R("mat2a", "sam", "regulates", "MAT2A drives SAM synthesis.", "blue MAT2A on the arrow", 0.8),
        R("sam", "sah", "produces", "Methyltransferases convert SAM to SAH.", "down arrow via MT", 0.85),
        R("mt", "sah", "regulates", "MT enzymes mediate SAM→SAH.", "blue MT on the arrow", 0.75),
        R("sah", "hcy", "produces", "AHCY converts SAH to homocysteine (+adenosine).", "arrow via AHCY", 0.85),
        R("sah", "adenosine", "produces", "Adenosine released alongside homocysteine.", "branch arrow to Adenosine", 0.8),
        R("hcy", "methionine", "produces", "MS remethylates homocysteine using 5-MTHF.", "left arrow via MS", 0.85),
        R("ms", "methionine", "regulates", "MS catalyzes the remethylation.", "blue MS on the arrow", 0.8),
        R("mthf", "methionine", "participates-in", "5-MTHF donates the methyl group.", "folate loop arrow into MS step", 0.8),
        R("thf", "mthf", "produces", "Folate loop interconverts THF and 5-MTHF.", "loop arrows upper left", 0.75),
        R("bhmt", "hcy", "regulates", "BHMT drives the alternate betaine-dependent remethylation.", "blue BHMT label", 0.8),
        R("betaine", "dmg", "produces", "Betaine becomes dimethylglycine after donation.", "Betaine→Dimethylglycine", 0.8),
        R("hcy", "cysteine", "produces", "Transsulfuration drains homocysteine to cysteine.", "leftward arrow", 0.85),
        R("sam", "polyamines", "participates-in", "SAM feeds polyamine synthesis.", "arrow to dark box", 0.8),
        R("ch3", "methylations", "participates-in", "Methyl groups end in methylations.", "arrow to Methylations", 0.8),
        R("sam", "methylations", "participates-in", "SAM-sourced methyl groups methylate targets.", "via MT/CH3 route", 0.75),
    ],
}

with open(os.path.join(OUT, "methionine_cycle_manual.json"), "w", encoding="utf-8") as fh:
    json.dump(CYCLE, fh, indent=2)
print("methionine_cycle_manual.json written")
