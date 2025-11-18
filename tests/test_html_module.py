"""Tests for the low-level HTML conversion helpers."""

from __future__ import annotations

import os
from pathlib import Path

from extract2md._html import _ensure_node_path, _extract_content_from_html, to_markdown


def test_to_markdown_uses_readability_and_markdownify(monkeypatch):
    """Successful conversion should invoke both readabilipy and markdownify."""
    recorded = {}

    def fake_simple_json_from_html_string(html, use_readability):  # noqa: ANN001
        recorded["html"] = html
        recorded["use_readability"] = use_readability
        return {"content": "<p>Body</p>"}

    def fake_markdownify(value, heading_style=None):  # noqa: ANN001
        recorded["markdown_input"] = value
        recorded["heading_style"] = heading_style
        return "Body"

    monkeypatch.setattr(
        "extract2md._html.readabilipy.simple_json.simple_json_from_html_string",
        fake_simple_json_from_html_string,
    )
    monkeypatch.setattr(
        "extract2md._html.markdownify.markdownify",
        fake_markdownify,
    )

    html = "<html><body><p>Body</p></body></html>"
    result = to_markdown(html)

    assert result == "Body"
    assert recorded["html"] == html
    assert recorded["use_readability"] is True
    assert recorded["markdown_input"] == "<p>Body</p>"


def test_extract_content_handles_empty_payload(monkeypatch):
    """Empty Readability content should produce an explicit error marker."""

    def fake_simple_json_from_html_string(*args, **kwargs):  # noqa: ANN001
        return {"content": ""}

    monkeypatch.setattr(
        "extract2md._html.readabilipy.simple_json.simple_json_from_html_string",
        fake_simple_json_from_html_string,
    )

    assert (
            _extract_content_from_html("<html></html>")
            == "<error>Page failed to be simplified from HTML</error>"
    )


def test_ensure_node_path_inserts_directory(monkeypatch, tmp_path: Path):
    """EXTRACT2MD_NODE_PATH should be prepended to PATH when valid."""
    node_dir = tmp_path / "node"
    node_dir.mkdir()

    monkeypatch.setenv("EXTRACT2MD_NODE_PATH", str(node_dir))
    monkeypatch.setenv("PATH", "/usr/bin")

    _ensure_node_path()

    assert str(node_dir) == os.environ["PATH"].split(":")[0]


def test_ensure_node_path_ignores_missing_entries(monkeypatch, tmp_path: Path):
    """Non-existent paths should not be added to PATH."""
    monkeypatch.setenv("EXTRACT2MD_NODE_PATH", str(tmp_path / "missing"))
    existing_path = "/usr/bin"
    monkeypatch.setenv("PATH", existing_path)

    _ensure_node_path()

    assert os.environ["PATH"] == existing_path
