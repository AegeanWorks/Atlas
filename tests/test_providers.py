from atlas.config import AtlasConfig
from atlas.muse_provider import MuseProvider
from atlas.sam_provider import SamProvider
from atlas.schema import BoundingBox


def _muse_transport(payload):
    assert payload["model"].startswith("muse-spark")
    assert payload["response_format"]["type"] == "json_schema"
    content = [c for c in payload["messages"][1]["content"] if c["type"] == "image_url"]
    assert content and content[0]["image_url"]["url"].startswith("data:image/")
    return {"choices": [{"message": {"content":
        '{"entities": [{"id": "striatum", "name": "Striatum", '
        '"category": "anatomical-structure", "box": [10, 10, 50, 50], '
        '"confidence": 0.9}], "relationships": []}'}}]}


def _sam_transport(payload):
    assert payload["model"] == "sam-3.1"
    kinds = [c["type"] for c in payload["input"][0]["content"]]
    assert "input_text" in kinds and "input_image" in kinds
    return {"mask_ref": "", "box": [10, 10, 50, 50]}


def test_muse_provider_mock(tmp_path):
    img = tmp_path / "f.png"
    img.write_bytes(__import__("base64").b64decode(
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="))
    cfg = AtlasConfig(api_key="test", data_dir=str(tmp_path))
    analysis = MuseProvider(cfg, transport=_muse_transport).analyze_figure(str(img))
    assert analysis.entities[0].id == "striatum"


def test_sam_bbox_fallback(tmp_path):
    img = tmp_path / "f.png"
    img.write_bytes(b"fakepng")
    cfg = AtlasConfig(api_key="test", data_dir=str(tmp_path))
    seg = SamProvider(cfg, transport=_sam_transport).segment(
        str(img), "striatum", "striatum",
        BoundingBox(0, 0, 0.5, 0.5))
    assert seg.kind == "bbox-fallback"  # no mask decoded -> honest fallback, never fake mask
    assert seg.bbox is not None
