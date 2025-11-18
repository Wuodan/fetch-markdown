"""High-level helpers exposed to library users."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from extract2md._fetch import DEFAULT_USER_AGENT as _DEFAULT_USER_AGENT
from extract2md._fetch import fetch_url
from extract2md._html import to_markdown
from extract2md._links import rewrite_relative_links

DEFAULT_USER_AGENT = _DEFAULT_USER_AGENT


def html_to_markdown(
        html: str,
        content_type: Any | None = None,
        *,
        base_url: str | None = None,
        rewrite_relative_urls: bool = True,
) -> str:
    """Convert HTML into Markdown."""

    processed_html = (
        rewrite_relative_links(html, base_url=base_url)
        if rewrite_relative_urls
        else html
    )
    return to_markdown(processed_html, content_type)


def file_to_markdown(
        path: Path | str,
        *,
        encoding: str | None = "utf-8",
        base_url: str | None = None,
        rewrite_relative_urls: bool = True,
) -> str:
    """Convert a local HTML file into Markdown."""

    file_path = Path(path)
    html = file_path.read_text(encoding=encoding)
    resolved_base_url = base_url or file_path.resolve().as_uri()
    return html_to_markdown(
        html,
        base_url=resolved_base_url,
        rewrite_relative_urls=rewrite_relative_urls,
    )


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
        base_url: str | None = None,
        rewrite_relative_urls: bool = True,
) -> str:
    """Fetch the given URL and return the simplified Markdown content."""

    content, content_type = fetch(
        url,
        user_agent=user_agent,
        ignore_robots_txt=ignore_robots_txt,
        proxy_url=proxy_url,
        timeout=timeout,
    )
    return html_to_markdown(
        content,
        content_type,
        base_url=base_url or url,
        rewrite_relative_urls=rewrite_relative_urls,
    )


__all__ = [
    "DEFAULT_USER_AGENT",
    "file_to_markdown",
    "fetch",
    "fetch_to_markdown",
    "html_to_markdown",
]
