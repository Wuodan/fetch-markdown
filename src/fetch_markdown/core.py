"""Core logic adapted directly from the MCP fetch server."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse, urlunparse

import markdownify
import readabilipy.simple_json
from protego import Protego

DEFAULT_USER_AGENT = (
    "fetch-markdown/0.1 (+https://github.com/Wuodan/fetch-markdown)"
)


class FetchMarkdownError(RuntimeError):
    """Raised when a page cannot be fetched or processed."""


def extract_content_from_html(html: str) -> str:
    ret = readabilipy.simple_json.simple_json_from_html_string(
        html, use_readability=True
    )
    if not ret["content"]:
        return "<error>Page failed to be simplified from HTML</error>"
    content = markdownify.markdownify(
        ret["content"],
        heading_style=markdownify.ATX,
    )
    return content


def get_robots_txt_url(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, "/robots.txt", "", "", ""))


async def _check_may_fetch_url(
    url: str,
    user_agent: str,
    proxy_url: str | None = None,
) -> None:
    from httpx import AsyncClient, HTTPError

    robot_txt_url = get_robots_txt_url(url)

    async with AsyncClient(proxies=proxy_url) as client:
        try:
            response = await client.get(
                robot_txt_url,
                follow_redirects=True,
                headers={"User-Agent": user_agent},
            )
        except HTTPError as exc:  # pragma: no cover - depends on network
            raise FetchMarkdownError(
                f"Failed to fetch robots.txt {robot_txt_url}: {exc}"
            ) from exc
        if response.status_code in (401, 403):
            raise FetchMarkdownError(
                "robots.txt forbids autonomous fetching for this user agent",
            )
        elif 400 <= response.status_code < 500:
            return
        robot_txt = response.text
    processed_robot_txt = "\n".join(
        line for line in robot_txt.splitlines() if not line.strip().startswith("#")
    )
    robot_parser = Protego.parse(processed_robot_txt)
    if not robot_parser.can_fetch(str(url), user_agent):
        raise FetchMarkdownError(
            "robots.txt disallows fetching this page for the configured user-agent"
        )


async def _fetch_url(
    url: str,
    user_agent: str,
    *,
    force_raw: bool = False,
    proxy_url: str | None = None,
    timeout: float = 30.0,
) -> Tuple[str, str]:
    from httpx import AsyncClient, HTTPError

    async with AsyncClient(proxies=proxy_url) as client:
        try:
            response = await client.get(
                url,
                follow_redirects=True,
                headers={"User-Agent": user_agent},
                timeout=timeout,
            )
        except HTTPError as exc:  # pragma: no cover - depends on network
            raise FetchMarkdownError(f"Failed to fetch {url}: {exc!r}") from exc
        if response.status_code >= 400:
            raise FetchMarkdownError(
                f"Failed to fetch {url} - status code {response.status_code}",
            )

        page_raw = response.text

    content_type = response.headers.get("content-type", "")
    is_page_html = (
        "<html" in page_raw[:100] or "text/html" in content_type or not content_type
    )

    if is_page_html and not force_raw:
        return extract_content_from_html(page_raw), ""

    return (
        page_raw,
        f"Content type {content_type} cannot be simplified to markdown, but here is the raw content:\n",
    )


async def _fetch_markdown_async(
    url: str,
    *,
    force_raw: bool,
    user_agent: str,
    ignore_robots_txt: bool,
    proxy_url: str | None,
    timeout: float,
) -> str:
    if not ignore_robots_txt:
        await _check_may_fetch_url(url, user_agent, proxy_url=proxy_url)

    content, prefix = await _fetch_url(
        url,
        user_agent,
        force_raw=force_raw,
        proxy_url=proxy_url,
        timeout=timeout,
    )
    return prefix + content


def fetch_markdown(
    url: str,
    output_path: Optional[Path | str] = None,
    *,
    force_raw: bool = False,
    user_agent: str | None = None,
    ignore_robots_txt: bool = False,
    proxy_url: str | None = None,
    timeout: float = 30.0,
) -> str:
    """Fetch the given URL and optionally write the generated Markdown.

    Args:
        url: Webpage to fetch.
        output_path: Optional destination path for the Markdown output.
        force_raw: Skip HTML simplification and return the response body.
        user_agent: Custom User-Agent header, defaults to a project specific one.
        ignore_robots_txt: Skip robots.txt validation when True.
        proxy_url: HTTP proxy URL if requests must be proxied.
        timeout: Timeout for individual HTTP requests.

    Returns:
        Markdown (or raw text) representation of the fetched page.
    """
    if not url:
        raise ValueError("A non-empty URL is required")

    resolved_user_agent = user_agent or DEFAULT_USER_AGENT
    markdown_text = asyncio.run(
        _fetch_markdown_async(
            url,
            force_raw=force_raw,
            user_agent=resolved_user_agent,
            ignore_robots_txt=ignore_robots_txt,
            proxy_url=proxy_url,
            timeout=timeout,
        )
    )

    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(markdown_text, encoding="utf-8")

    return markdown_text
