"""High-level helpers exposed to library users."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fetch_markdown._fetch import DEFAULT_USER_AGENT as _DEFAULT_USER_AGENT
from fetch_markdown._fetch import fetch_url
from fetch_markdown._html import to_markdown

DEFAULT_USER_AGENT = _DEFAULT_USER_AGENT


def html_to_markdown(
        html: str,
        content_type: Any | None = None,
) -> str:
    """Convert HTML into Markdown."""

    return to_markdown(html, content_type)


def file_to_markdown(
        path: Path | str,
        *,
        encoding: str | None = "utf-8",
) -> str:
    """Convert a local HTML file into Markdown."""

    html = Path(path).read_text(encoding=encoding)
    return html_to_markdown(html)


def fetch(
        url: str,
        *,
        user_agent: str | None = None,
        ignore_robots_txt: bool = False,
        proxy_url: str | None = None,
        timeout: float = 30.0,
) -> tuple[str, str]:
    """Fetch the given URL and return the content and content-type."""

    return fetch_url(
        url,
        user_agent=user_agent,
        ignore_robots_txt=ignore_robots_txt,
        proxy_url=proxy_url,
        timeout=timeout,
    )


def fetch_to_markdown(
        url: str,
        *,
        user_agent: str | None = None,
        ignore_robots_txt: bool = False,
        proxy_url: str | None = None,
        timeout: float = 30.0,
) -> str:
    """Fetch the given URL and return the simplified Markdown content."""

    content, content_type = fetch(
        url,
        user_agent=user_agent,
        ignore_robots_txt=ignore_robots_txt,
        proxy_url=proxy_url,
        timeout=timeout,
    )
    return html_to_markdown(content, content_type)


__all__ = [
    "DEFAULT_USER_AGENT",
    "file_to_markdown",
    "fetch",
    "fetch_to_markdown",
    "html_to_markdown",
]
