"""Unit tests for the relative link rewriting utilities."""

from __future__ import annotations

from extract2md._links import rewrite_relative_links


def test_rewrite_relative_links_updates_href_and_src() -> None:
    html = '<a href="/docs">Docs</a><img src="img/logo.png" alt="logo" />'

    rewritten = rewrite_relative_links(html, base_url="https://example.com/base/")

    assert 'href="https://example.com/docs"' in rewritten
    assert 'src="https://example.com/base/img/logo.png"' in rewritten


def test_rewrite_relative_links_no_base_url_noop() -> None:
    html = '<a href="/docs">Docs</a>'

    rewritten = rewrite_relative_links(html, base_url=None)

    assert rewritten == html
