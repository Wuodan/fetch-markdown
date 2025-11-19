"""Unit tests for the public Python helpers."""

from __future__ import annotations

import pytest

from extract2md import (
    Extract2MarkdownContentTypeError,
    fetch_to_markdown,
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
    with pytest.raises(Extract2MarkdownContentTypeError):
        html_to_markdown("just text", content_type="text/plain")


def test_html_to_markdown_makes_relative_links_absolute(monkeypatch) -> None:
    """Relative URLs should be resolved when a base URL is provided."""

    def fake_rewrite(html, *, base_url):  # noqa: ANN001
        assert base_url == "https://example.com/home/"
        return '<html><body><a href="https://example.com/docs">Docs</a></body></html>'

    def fake_to_markdown(html, content_type=None, *, converter=None):  # noqa: ANN001
        assert "https://example.com/docs" in html
        return "[Docs](https://example.com/docs)"

    monkeypatch.setattr("extract2md.core.rewrite_relative_links", fake_rewrite)
    monkeypatch.setattr("extract2md.core.to_markdown", fake_to_markdown)

    markdown = html_to_markdown("<html></html>", base_url="https://example.com/home/")

    assert "[Docs](https://example.com/docs)" in markdown


def test_html_to_markdown_can_skip_relative_rewrite(monkeypatch) -> None:
    """Relative URLs remain untouched when rewriting is disabled."""

    def fake_rewrite(*args, **kwargs):  # noqa: ANN001
        raise AssertionError("rewrite_relative_links should not run")

    def fake_to_markdown(html, content_type=None, *, converter=None):  # noqa: ANN001
        assert '<a href="/docs">Docs</a>' in html
        return "[Docs](/docs)"

    monkeypatch.setattr("extract2md.core.rewrite_relative_links", fake_rewrite)
    monkeypatch.setattr("extract2md.core.to_markdown", fake_to_markdown)

    markdown = html_to_markdown(
        '<html><body><a href="/docs">Docs</a></body></html>',
        base_url="https://example.com/",
        rewrite_relative_urls=False,
    )

    assert "[Docs](/docs)" in markdown


def test_file_to_markdown_accepts_custom_base_url(monkeypatch, tmp_path) -> None:
    """Custom base_url overrides the auto-generated file URI."""
    html_file = tmp_path / "page.html"
    html_file.write_text("<html>content</html>", encoding="utf-8")

    def fake_html_to_markdown(  # noqa: ANN001
            html,
            content_type=None,
            *,
            base_url=None,
            rewrite_relative_urls=None,
            converter=None,
    ):
        assert base_url == "https://override/"
        assert rewrite_relative_urls is False
        return "converted"

    monkeypatch.setattr("extract2md.core.html_to_markdown", fake_html_to_markdown)

    markdown = file_to_markdown(
        html_file,
        base_url="https://override/",
        rewrite_relative_urls=False,
    )

    assert markdown == "converted"


def test_fetch_to_markdown_allows_custom_base_url(monkeypatch) -> None:
    """fetch_to_markdown should respect an explicit base_url value."""

    def fake_fetch(*args, **kwargs):  # noqa: ANN001
        return "<html></html>", "text/html"

    def fake_html_to_markdown(  # noqa: ANN001
            html,
            content_type=None,
            *,
            base_url=None,
            rewrite_relative_urls=None,
            converter=None,
    ):
        assert base_url == "https://override/"
        assert rewrite_relative_urls is False
        return "converted"

    monkeypatch.setattr("extract2md.core.fetch", fake_fetch)
    monkeypatch.setattr("extract2md.core.html_to_markdown", fake_html_to_markdown)

    markdown = fetch_to_markdown(
        "https://example.com/article",
        base_url="https://override/",
        rewrite_relative_urls=False,
    )

    assert markdown == "converted"


def test_fetch_to_markdown_defaults_base_url_to_source(monkeypatch) -> None:
    """When base_url is omitted, the fetched URL is used."""

    def fake_fetch(*args, **kwargs):  # noqa: ANN001
        return "<html></html>", "text/html"

    def fake_html_to_markdown(  # noqa: ANN001
            html,
            content_type=None,
            *,
            base_url=None,
            rewrite_relative_urls=None,
            converter=None,
    ):
        assert base_url == "https://example.com/article"
        return "converted"

    monkeypatch.setattr("extract2md.core.fetch", fake_fetch)
    monkeypatch.setattr("extract2md.core.html_to_markdown", fake_html_to_markdown)

    markdown = fetch_to_markdown("https://example.com/article")

    assert markdown == "converted"
