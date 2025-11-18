"""Unit tests for the public Python helpers."""

from __future__ import annotations

import pytest

from fetch_markdown import (
    Html2MarkdownContentTypeError,
    file_to_markdown,
    html_to_markdown,
)


def test_html_to_markdown_simplifies() -> None:
    """html_to_markdown should include the key HTML content in the output."""
    html = "<html><body><h1>Title</h1><p>Hello world</p></body></html>"
    markdown = html_to_markdown(html)
    assert "Title" in markdown
    assert "Hello world" in markdown


def test_file_to_markdown_reads_content(tmp_path) -> None:
    """file_to_markdown should read and convert HTML files from disk."""
    html_file = tmp_path / "page.html"
    html_file.write_text("<html><body><p>Offline</p></body></html>", encoding="utf-8")

    markdown = file_to_markdown(html_file)

    assert "Offline" in markdown


def test_html_to_markdown_rejects_non_html() -> None:
    """Non-HTML content-types must produce a clear error."""
    with pytest.raises(Html2MarkdownContentTypeError):
        html_to_markdown("just text", content_type="text/plain")
