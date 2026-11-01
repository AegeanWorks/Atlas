"""Flashcard decks from the validated model — recall distinct from quizzes.

Every card is generated from the SAME analysis that drives canvas/graph:
identify-by-highlight, identify-by-description, and relation cards per entity.
Decks export to Anki TSV (front/back with evidence) for spaced repetition
elsewhere, and the workspace reviews them with self-grading + running score.
"""
from __future__ import annotations


def build_deck(analysis: dict) -> dict:
    """Analysis → {"cards": [...]}. Deterministic order: stable for review."""
    entities = list(analysis.get("entities", []))
    names = {e["id"]: e.get("name", e["id"]) for e in entities}
    rels_by_target: dict[str, list] = {}
    for r in analysis.get("relationships", []):
        rels_by_target.setdefault(r["target_id"], []).append(r)
    cards = []
    for e in entities:
        eid = e["id"]
        cards.append({
            "id": f"hl-{eid}", "entity_id": eid, "kind": "identify-highlight",
            "front": {"text": "Which structure is highlighted?", "highlight_bbox": e.get("bbox")},
            "back": {"text": e.get("name", eid),
                     "detail": e.get("description", ""),
                     "evidence": e.get("source_evidence", "")},
        })
        if e.get("description"):
            cards.append({
                "id": f"desc-{eid}", "entity_id": eid, "kind": "identify-description",
                "front": {"text": e["description"], "highlight_bbox": None},
                "back": {"text": e.get("name", eid),
                         "detail": f"Category: {e.get('category', 'other')}",
                         "evidence": e.get("source_evidence", "")},
            })
        for r in rels_by_target.get(eid, []):
            cards.append({
                "id": f"rel-{r['source_id']}-{r['target_id']}", "entity_id": eid,
                "kind": "relation",
                "front": {"text": f"{names.get(r['source_id'], '?')} → ? "
                                  f"({r.get('rel_type', '?')})",
                          "highlight_bbox": None},
                "back": {"text": names.get(eid, eid),
                         "detail": r.get("explanation", ""),
                         "evidence": r.get("supporting_evidence", "")},
            })
    return {"figure_id": analysis.get("figure_id", ""), "cards": cards}


def _cell(text: str) -> str:
    return str(text or "").replace("\t", " ").replace("\r\n", "<br>").replace("\n", "<br>")


def to_anki_tsv(deck: dict) -> str:
    """Deck → Anki-importable TSV: front, back (+ detail + evidence)."""
    if not deck.get("cards"):
        raise ValueError("deck has no cards")
    rows = []
    for c in deck["cards"]:
        front = _cell(c["front"]["text"])
        back = " — ".join(part for part in
                          [_cell(c["back"]["text"]), _cell(c["back"].get("detail", "")),
                           _cell(c["back"].get("evidence", ""))] if part)
        rows.append(f"{front}\t{back}")
    return "\n".join(rows) + "\n"
