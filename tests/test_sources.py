"""Universal ingestion: every source becomes learning material."""
import io
import json
import zipfile

import pytest

from atlas import sources as src
from atlas.schema import coerce_muse_payload


class _FakeResp:
    def __init__(self, data: bytes, ctype: str = "text/html"):
        self._data = data
        self.headers = {"Content-Type": ctype}

    def read(self, n: int = -1):
        return self._data if n is None or n < 0 else self._data[:n]

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_html_to_text_drops_boilerplate():
    html = ("<html><head><title>T</title></head><body><nav>menu</nav>"
            "<script>evil()</script><h1>Head</h1><p>Body text.</p></body></html>")
    text = src.html_to_text(html)
    assert "Head" in text and "Body text." in text
    assert "menu" not in text and "evil" not in text


def test_fetch_url_text_and_plain(monkeypatch):
    calls = []

    def fake_open(req, timeout=None):
        calls.append(req.full_url)
        if req.full_url.endswith(".txt"):
            return _FakeResp(b"plain words", "text/plain")
        return _FakeResp(b"<html><body><p>Article body here.</p></body></html>")
    monkeypatch.setattr(src.urllib.request, "urlopen", fake_open)
    got = src.fetch_url_text("https://example.com/a")
    assert "Article body here." in got["text"]
    assert src.fetch_url_text("https://example.com/f.txt")["text"] == "plain words"
    with pytest.raises(ValueError, match="http"):
        src.fetch_url_text("ftp://example.com/x")


def test_youtube_transcript_parses_captions(monkeypatch):
    watch = ('<html><body>{"captionTracks":[{"baseUrl":"https://t.example/cap",'
             '"languageCode":"en"}]}</body></html>')
    caps = '<transcript><text start="0">hello world</text><text start="1">second line</text></transcript>'

    def fake_open(url, timeout=None):
        target = url.full_url if hasattr(url, "full_url") else url
        return _FakeResp(caps.encode() if "t.example" in target else watch.encode())
    monkeypatch.setattr(src.urllib.request, "urlopen", fake_open)
    got = src.youtube_transcript("https://www.youtube.com/watch?v=abc123XYZ-_")
    assert "hello world" in got["text"] and "second line" in got["text"]
    with pytest.raises(ValueError, match="recognizable"):
        src.youtube_transcript("https://example.com/notube")
    assert src.youtube_video_id("https://youtu.be/abc123XYZ-_") == "abc123XYZ-_"


def _write_epub(path):
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("mimetype", "application/epub+zip")
        z.writestr("META-INF/container.xml",
                   '<container><rootfiles><rootfile full-path="OEBPS/content.opf"/>'
                   "</rootfiles></container>")
        z.writestr("OEBPS/content.opf",
                   '<package><metadata><dc:title>Test Book</dc:title></metadata>'
                   '<manifest><item id="c1" href="ch1.xhtml"/><item id="c2" href="ch2.xhtml"/>'
                   "</manifest><spine><itemref idref=\"c1\"/><itemref idref=\"c2\"/></spine></package>")
        z.writestr("OEBPS/ch1.xhtml", "<html><body><p>Chapter one words.</p></body></html>")
        z.writestr("OEBPS/ch2.xhtml", "<html><body><p>Chapter two words.</p></body></html>")


def test_epub_text_in_spine_order(tmp_path):
    path = str(tmp_path / "book.epub")
    _write_epub(path)
    got = src.epub_text(path)
    assert got["title"] == "Test Book" and got["chapters"] == 2
    assert got["text"].index("Chapter one") < got["text"].index("Chapter two")


def test_video_without_ffmpeg_is_honest(tmp_path, monkeypatch):
    monkeypatch.setattr(src.shutil, "which", lambda *a, **k: None)
    with pytest.raises(ValueError, match="ffmpeg"):
        src.video_frames(str(tmp_path / "clip.mp4"), str(tmp_path))


def test_trim_text_marks_truncation():
    assert src.trim_text("a" * 12001).endswith("[truncated: first 12000 chars of the source]")
    assert src.trim_text("short") == "short"


def test_coerce_allows_boxless_text_entities():
    a = coerce_muse_payload(
        {"entities": [{"id": "e1", "name": "N1", "category": "process",
                       "confidence": 0.8, "source_evidence": "quote"}],
         "relationships": []})
    assert a.entities[0].bbox is None


def test_analyze_text_roundtrip():
    from atlas.config import AtlasConfig
    from atlas.muse_provider import MuseProvider

    def fake_transport(payload):
        user = payload["messages"][1]["content"]
        assert "SOURCE:" in user and "some text" in user
        assert payload["response_format"]["type"] == "json_schema"
        return {"choices": [{"message": {"content":
            '{"entities": [{"id": "x", "name": "X", "category": "process", '
            '"confidence": 0.7, "source_evidence": "q"}], "relationships": []}'}}]}
    cfg = AtlasConfig(api_key="k", data_dir=".")
    analysis = MuseProvider(cfg, transport=fake_transport).analyze_text("some text")
    assert analysis.entities[0].bbox is None
    assert analysis.entities[0].source_evidence == "q"


class _FakeMuseBoth:
    def analyze_text(self, text, note="", document_ref="", figure_id=""):
        from atlas.schema import VisualAnalysis, VisualEntity
        return VisualAnalysis(document_ref=document_ref, figure_id=figure_id,
                              entities=[VisualEntity(id="t1", name="Thing",
                                                     category="component",
                                                     source_evidence=text[:20])],
                              relationships=[])

    def analyze_figure(self, *a, **k):
        from atlas.schema import VisualAnalysis, VisualEntity
        return VisualAnalysis(document_ref=k.get("document_ref", ""),
                              figure_id=k.get("figure_id", "f"),
                              entities=[VisualEntity(id="v1", name="Region",
                                                     category="component")],
                              relationships=[])


def test_auto_create_from_text_and_image(tmp_path):
    from atlas.app import auto_create_model, list_models
    from atlas.config import AtlasConfig
    from atlas.store import AtlasStore
    store = AtlasStore(str(tmp_path))
    cfg = AtlasConfig(api_key="", data_dir=str(tmp_path))
    txt = tmp_path / "n.txt"
    txt.write_text("Cortex drives striatum.", encoding="utf-8")
    r = auto_create_model(store, cfg, str(txt), muse_provider=_FakeMuseBoth())
    assert r["model_created"] and r["source_kind"] == "text"
    from PIL import Image
    img = tmp_path / "f.png"
    Image.new("RGB", (40, 30), (1, 2, 3)).save(img)
    r2 = auto_create_model(store, cfg, str(img), muse_provider=_FakeMuseBoth())
    assert r2["source_kind"] == "image" and r2["figure_url"].startswith("/figures/")
    ids = {m["figure_id"] for m in list_models(store)}
    assert {r["figure_id"], r2["figure_id"]} <= ids


def test_merge_frames_namespaces_ids():
    from atlas.app import _merge_frame_analyses
    from atlas.schema import VisualAnalysis, VisualEntity, VisualRelationship
    mk = lambda p, s, t: VisualAnalysis(
        entities=[VisualEntity(id="a", name="A", category="component"),
                  VisualEntity(id="b", name="B", category="component")],
        relationships=[VisualRelationship(source_id="a", target_id="b",
                                          rel_type="activates")])
    merged = _merge_frame_analyses([mk(0, 0, 0), mk(1, 1, 1)], "d", "vid")
    ids = {e.id for e in merged.entities}
    assert ids == {"f0-a", "f0-b", "f1-a", "f1-b"}
    assert {(r.source_id, r.target_id) for r in merged.relationships} == \
        {("f0-a", "f0-b"), ("f1-a", "f1-b")}
