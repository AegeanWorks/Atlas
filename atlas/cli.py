"""Atlas headless CLI — AI agents and scripts drive Atlas without a browser.

  python -m atlas.cli create figure.png --note "caption..."   # one drop -> one model
  python -m atlas.cli models                                  # see every model
  python -m atlas.cli show <figure-id>                        # read one model
  python -m atlas.cli learn <figure-id> spatial-recall        # practice headlessly
  python -m atlas.cli contract                                # machine contract

Live creation needs MODEL_API_KEY/META_API_KEY; reading models never does.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from atlas.app import api_contract, auto_create_model, list_models  # noqa: E402
from atlas.config import AtlasConfig  # noqa: E402
from atlas import learning as learn  # noqa: E402
from atlas.store import AtlasStore  # noqa: E402


def cmd_create(args) -> int:
    store = AtlasStore(args.data)
    config = AtlasConfig.from_env(data_dir=args.data)
    try:
        result = auto_create_model(store, config, args.file, args.note,
                                   args.figure_id, args.wonder)
    except Exception as exc:
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}))
        return 1
    if result.get("model_created"):
        a = result["analysis"]
        print(json.dumps({"ok": True, "figure_id": result["figure_id"],
                          "entities": len(a["entities"]),
                          "relationships": len(a["relationships"]),
                          "figure_url": result.get("figure_url", "")}))
    else:
        print(json.dumps({"ok": True, "model_created": False,
                          "document": result["document"]}))
    return 0


def cmd_models(args) -> int:
    print(json.dumps({"models": list_models(AtlasStore(args.data))}, indent=2))
    return 0


def cmd_show(args) -> int:
    data = AtlasStore(args.data).load_analysis(args.figure_id)
    if data is None:
        print(json.dumps({"ok": False, "error": f"unknown figure_id {args.figure_id!r}"}))
        return 1
    print(json.dumps(data, indent=2))
    return 0


def cmd_learn(args) -> int:
    data = AtlasStore(args.data).load_analysis(args.figure_id)
    if data is None:
        print(json.dumps({"ok": False, "error": f"unknown figure_id {args.figure_id!r}"}))
        return 1
    fn = {"spatial-recall": learn.spatial_recall_challenge,
          "pathway-tracing": learn.pathway_tracing_challenge,
          "visual-identification": learn.visual_identification_challenge,
          "relationship-recall": learn.relationship_recall_challenge}[args.mode]
    challenge = fn(data, args.seed)
    if args.answer is None:
        print(json.dumps(challenge, indent=2))
        return 0
    answer = args.answer
    if challenge.get("mode") == "pathway-tracing":
        answer = [a.strip() for a in answer.split(",")]
    print(json.dumps({"challenge": challenge.get("prompt"),
                      "grade": learn.grade(challenge, answer)}, indent=2))
    return 0


def cmd_deck(args) -> int:
    from atlas import flashcards as fc
    data = AtlasStore(args.data).load_analysis(args.figure_id)
    if data is None:
        print(json.dumps({"ok": False, "error": f"unknown figure_id {args.figure_id!r}"}))
        return 1
    deck = fc.build_deck(data)
    if args.anki:
        with open(args.anki, "w", encoding="utf-8") as fh:
            fh.write(fc.to_anki_tsv(deck))
        print(json.dumps({"ok": True, "cards": len(deck["cards"]), "anki": args.anki}))
    else:
        print(json.dumps(deck, indent=2))
    return 0


def cmd_obj(args) -> int:
    from atlas import models3d as m3d
    data = AtlasStore(args.data).load_analysis(args.figure_id)
    if data is None:
        print(json.dumps({"ok": False, "error": f"unknown figure_id {args.figure_id!r}"}))
        return 1
    try:
        text = m3d.export_obj(data)
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}))
        return 1
    out = args.out or f"{args.figure_id}.obj"
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(text)
    print(json.dumps({"ok": True, "obj": out}))
    return 0


def cmd_summary(args) -> int:
    from . import summaries as sm
    data = AtlasStore(args.data).load_analysis(args.figure_id)
    if data is None:
        print(json.dumps({"ok": False, "error": f"unknown figure_id {args.figure_id!r}"}))
        return 1
    print(json.dumps(sm.extractive_summary(data), indent=2))
    return 0


def cmd_agent(args) -> int:
    """One command proving an AI can drive Atlas: fixture model, summary,
    deck, learn round, OBJ — all offline, all printed as JSON."""
    import tempfile
    from .selftest import run
    data_dir = args.data if args.data != "data" else tempfile.mkdtemp(prefix="atlas-agent-")
    report = run(data_dir)
    print(json.dumps(report, indent=2))
    return 0 if report["failed"] == 0 else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Atlas headless CLI for AI agents")
    ap.add_argument("--data", default="data")
    sub = ap.add_subparsers(dest="command", required=True)
    c = sub.add_parser("create", help="one file -> one model")
    c.add_argument("file")
    c.add_argument("--note", default="")
    c.add_argument("--figure-id", default="")
    c.add_argument("--wonder", action="store_true")
    c.set_defaults(func=cmd_create)
    m = sub.add_parser("models", help="list every model")
    m.set_defaults(func=cmd_models)
    s = sub.add_parser("show", help="read one model")
    s.add_argument("figure_id")
    s.set_defaults(func=cmd_show)
    lrn = sub.add_parser("learn", help="challenge (and optionally grade)")
    lrn.add_argument("figure_id")
    lrn.add_argument("mode", choices=["spatial-recall", "pathway-tracing",
                                      "visual-identification", "relationship-recall"])
    lrn.add_argument("--seed", type=int, default=0)
    lrn.add_argument("--answer", default=None)
    lrn.set_defaults(func=cmd_learn)
    ct = sub.add_parser("contract", help="print the machine contract")
    ct.set_defaults(func=lambda a: (print(json.dumps(api_contract(), indent=2)), 0)[1])
    dk = sub.add_parser("deck", help="build flashcards (optionally export Anki TSV)")
    dk.add_argument("figure_id")
    dk.add_argument("--anki", default="")
    dk.set_defaults(func=cmd_deck)
    ob = sub.add_parser("obj", help="export the model as Wavefront OBJ 3D")
    ob.add_argument("figure_id")
    ob.add_argument("--out", default="")
    ob.set_defaults(func=cmd_obj)
    smry = sub.add_parser("summary", help="print the auto study brief")
    smry.add_argument("figure_id")
    smry.set_defaults(func=cmd_summary)
    ag = sub.add_parser("agent", help="prove AI autonomy: fixture model end to end")
    ag.add_argument("--figure-id", default="agent-demo")
    ag.set_defaults(func=cmd_agent)
    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
