"""Offline no-key path: every drop becomes a real, honestly-labelled model."""
import json

from atlas import offline as off
from atlas.app import auto_create_model, honest_error
from atlas.config import AtlasConfig
from atlas.store import AtlasStore


TEXT = ("The striatum receives input from the cortex. The striatum inhibits "
        "the globus pallidus. The cortex activates the striatum. " * 4)


def test_offline_builder_validates():
    analysis = off.build_offline_analysis(TEXT, document_ref="d", figure_id="f")
    assert not analysis.validate()
    assert analysis.entities and analysis.relationships
    assert all(e.source_evidence and e.model_inferred for e in analysis.entities)
    assert all("offline-extractive" in e.uncertainty for e in analysis.entities)


def test_auto_create_text_without_key_uses_offline(tmp_path):
    src = tmp_path / "notes.txt"
    src.write_text(TEXT, encoding="utf-8")
    store = AtlasStore(str(tmp_path / "data"))
    config = AtlasConfig(api_key="", data_dir=str(tmp_path / "data"))
    result = auto_create_model(store, config, str(src))
    assert result["model_created"] is True and result["offline"] is True
    assert "offline-extractive" in result["warning"]


def test_auto_create_image_without_key_uses_offline(tmp_path):
    from PIL import Image
    src = tmp_path / "cortex.png"
    Image.new("RGB", (80, 60), (10, 20, 30)).save(src)
    store = AtlasStore(str(tmp_path / "data2"))
    config = AtlasConfig(api_key="", data_dir=str(tmp_path / "data2"))
    result = auto_create_model(store, config, str(src), note="cortex layers")
    assert result["model_created"] is True and result["offline"] is True
    assert result["figure_url"].startswith("/figures/")


def test_keyless_live_call_still_refuses():
    from atlas.muse_provider import MuseProvider
    config = AtlasConfig(api_key="")
    try:
        MuseProvider(config).analyze_text(TEXT)
    except RuntimeError as exc:
        assert "refusing live call" in str(exc)
    else:
        raise AssertionError("keyless live call did not refuse")


def test_honest_error_names_cause_and_fix():
    body = honest_error(Exception(
        "No text on any of 3 page(s): scanned images or encryption."))
    assert "scanned-image PDF" in body["cause"] and "OCR" in body["fix"]
    keyless = honest_error(RuntimeError("MODEL_API_KEY/META_API_KEY is not set; refusing live call"))
    assert keyless["cause"] and keyless["fix"]


def test_extended_quality_covers_new_materials():
    from demo.basal_ganglia_fixture import FIXTURE_ANALYSIS
    from atlas import flashcards as fc
    from atlas import materials as mat
    from atlas import quality as qa
    from atlas import summaries as sm
    data = json.loads(json.dumps(FIXTURE_ANALYSIS))
    report = qa.quality_report(data, {
        "deck": fc.build_deck(data), "podcast": mat.podcast_script(data),
        "diagram_svg": mat.diagram_svg(data), "tour": mat.tour_3d(data),
        "questions": mat.question_bank(data), "summary": sm.extractive_summary(data),
        "include_learn": True})
    for key in ("flashcards", "podcast", "infographic", "tour",
                "questions", "summary", "learn"):
        assert key in report, key
        assert 0 <= report[key]["score"] <= 100
    assert 0 <= report["overall"] <= 100
