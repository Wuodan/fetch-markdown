"""Utilities for rewriting hyperlink targets."""

from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup

ATTRIBUTES_TO_REWRITE: tuple[str, ...] = ("href", "src")


def rewrite_relative_links(html: str, *, base_url: str | None) -> str:
    """Return ``html`` with relative href/src values rewritten to absolute URLs."""
    if not base_url:
        return html

    soup = BeautifulSoup(html, "html.parser")
    for attr in ATTRIBUTES_TO_REWRITE:
        _rewrite_attribute(soup, attr, base_url)
    return str(soup)


def _rewrite_attribute(soup: BeautifulSoup, attribute: str, base_url: str) -> None:
    """Update each attribute occurrence to an absolute URL."""
    for element in soup.find_all(attrs={attribute: True}):
        value = element.get(attribute)
        if not isinstance(value, str) or not value:
            continue
        element[attribute] = urljoin(base_url, value)
