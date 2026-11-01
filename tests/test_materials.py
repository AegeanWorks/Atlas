"""Materials: diagrams, 3D tours, podcast scripts, question banks (0.10.0)."""
import json
import threading
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from http.server import HTTPServer

from atlas import materials as mat
from atlas.schema import VisualAnalysis
from demo.basal_ganglia_fixture import FIXTURE_ANALYSIS


def _analysis():
    return VisualAnalysis.from_dict(FIXTURE_ANALYSIS).to_dict()


def test_diagram_svg_valid_and_complete():
    svg = mat.diagram_svg(_analysis())
    root = ET.fromstring(svg)  # well-formed XML
    assert root.tag.endswith("svg")
    for name in ("Striatum", "GPe", "Thalamus", "inhibits"):
        assert name in svg


def test_diagram_png_opens():
    from PIL import Image
    import io
    img = Image.open(io.BytesIO(mat.diagram_png(_analysis())))
    assert img.size == (960, 640) and img.mode == "RGB"


def test_tour_orders_layers():
    tour = mat.tour_3d(_analysis())
    layers = [s["layer"] for s in tour["stops"]]
    assert layers == sorted(layers) and len(tour["stops"]) == 7
    assert all(s["connections"] for s in tour["stops"] if s["entity_id"] != "snr")


def test_podcast_covers_entities_and_times():
    script = mat.podcast_script(_analysis())
    text = " ".join(s["text"] for s in script["segments"])
    for name in ("Striatum", "GPe", "Thalamus", "STN"):
        assert name in text
    assert script["estimated_minutes"] > 0
    md = mat.podcast_markdown(script)
    assert md.startswith("#") and "HOST" in md


def test_question_bank_answers():
    bank = mat.question_bank(_analysis())
    kinds = {q["kind"] for q in bank["questions"]}
    assert {"identify-description", "spatial-recall", "relationship-recall"} <= kinds
    assert all(q["answer"] for q in bank["questions"])
    md = mat.questions_markdown(bank)
    assert "## Answers" in md and md.count("\n") > len(bank["questions"])


def test_material_endpoints_and_cli(tmp_path):
    from atlas import app as atlas_app
    from atlas.config import AtlasConfig
    from atlas.store import AtlasStore

    AtlasStore(str(tmp_path)).save_analysis("m1", {**_analysis(), "figure_id": "m1"})
    atlas_app.Handler.store = None
    atlas_app.Handler.config = AtlasConfig.from_env(data_dir=str(tmp_path))
    server = HTTPServer(("127.0.0.1", 0), atlas_app.Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with urllib.request.urlopen(  # noqa: S310
                f"http://127.0.0.1:{port}/api/diagram?figure_id=m1&format=svg",
                timeout=10) as r:
            assert r.status == 200 and b"<svg" in r.read()
        with urllib.request.urlopen(  # noqa: S310
                f"http://127.0.0.1:{port}/api/diagram?figure_id=m1&format=png",
                timeout=10) as r:
            assert r.read()[:8] == b"\x89PNG\r\n\x1a\n"
        with urllib.request.urlopen(  # noqa: S310
                f"http://127.0.0.1:{port}/api/tour?figure_id=m1", timeout=10) as r:
            assert len(json.load(r)["stops"]) == 7
        with urllib.request.urlopen(  # noqa: S310
                f"http://127.0.0.1:{port}/api/podcast?figure_id=m1&format=json",
                timeout=10) as r:
            assert json.load(r)["segments"]
        with urllib.request.urlopen(  # noqa: S310
                f"http://127.0.0.1:{port}/api/questions?figure_id=m1&format=md",
                timeout=10) as r:
            assert b"## Answers" in r.read()
        try:
            with urllib.request.urlopen(  # noqa: S310
                    f"http://127.0.0.1:{port}/api/diagram?figure_id=nope",
                    timeout=10):
                raise AssertionError("expected 404")
        except urllib.error.HTTPError as e:
            assert e.code == 404
    finally:
        server.shutdown()
        thread.join(timeout=5)
        atlas_app.Handler.store = None


def test_cli_materials(tmp_path, capsys):
    from atlas.cli import main
    from atlas.store import AtlasStore
    AtlasStore(str(tmp_path)).save_analysis("m1", {**_analysis(), "figure_id": "m1"})
    assert main(["--data", str(tmp_path), "materials", "m1", "tour"]) == 0
    assert "stops" in capsys.readouterr().out
    out = str(tmp_path / "m1-questions.md")
    assert main(["--data", str(tmp_path), "materials", "m1", "questions"]) == 0
    assert main(["--data", str(tmp_path), "materials", "m1", "diagram-png",
                 "--out", str(tmp_path / "m.png")]) == 0
    assert (tmp_path / "m.png").is_file()
