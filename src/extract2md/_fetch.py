"""Core logic adapted directly from the MCP fetch server."""

from __future__ import annotations

import asyncio
from urllib.parse import urlparse, urlunparse

from extract2md.models import Html2MarkdownFetchError
from protego import Protego

DEFAULT_USER_AGENT = (
    "extract2md/0.1 (+https://github.com/Wuodan/extract2md)"
)


def _get_robots_txt_url(url: str) -> str:
    """Return the robots.txt URL for the host extracted from ``url``."""
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, "/robots.txt", "", "", ""))


async def _check_may_fetch_url(
        url: str,
        user_agent: str,
        proxy_url: str | None = None,
) -> None:
    """Validate robots.txt rules for the provided URL."""
    from httpx import AsyncClient, HTTPError

    robot_txt_url = _get_robots_txt_url(url)

    async with AsyncClient(proxy=proxy_url) as client:
        try:
            response = await client.get(
                robot_txt_url,
                follow_redirects=True,
                headers={"User-Agent": user_agent},
            )
        except HTTPError as exc:  # pragma: no cover - depends on network
            raise Html2MarkdownFetchError(
                f"Failed to fetch robots.txt {robot_txt_url}: {exc}"
            ) from exc
        if response.status_code in (401, 403):
            raise Html2MarkdownFetchError(
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
        raise Html2MarkdownFetchError(
            "robots.txt disallows fetching this page for the configured user-agent"
        )


async def _fetch_url(
        url: str,
        user_agent: str,
        *,
        proxy_url: str | None = None,
        timeout: float = 30.0,
) -> tuple[str, str]:
    """Perform the HTTP GET request and return response body and content-type."""
    from httpx import AsyncClient, HTTPError

    async with AsyncClient(proxy=proxy_url) as client:
        try:
            response = await client.get(
                url,
                follow_redirects=True,
                headers={"User-Agent": user_agent},
                timeout=timeout,
            )
        except HTTPError as exc:  # pragma: no cover - depends on network
            raise Html2MarkdownFetchError(f"Failed to fetch {url}: {exc!r}") from exc
        if response.status_code >= 400:
            raise Html2MarkdownFetchError(
                f"Failed to fetch {url} - status code {response.status_code}",
            )

        content = response.text

    content_type = response.headers.get("content-type", "")

    return content, content_type


async def _fetch_async(
        url: str,
        *,
        user_agent: str,
        ignore_robots_txt: bool,
        proxy_url: str | None,
        timeout: float,
) -> tuple[str, str]:
    """Wrapper that optionally enforces robots.txt validation before fetching."""
    if not ignore_robots_txt:
        await _check_may_fetch_url(url, user_agent, proxy_url=proxy_url)

    return await _fetch_url(
        url,
        user_agent,
        proxy_url=proxy_url,
        timeout=timeout,
    )


def fetch_url(
        url: str,
        *,
        user_agent: str | None = None,
        ignore_robots_txt: bool = False,
        proxy_url: str | None = None,
        timeout: float = 30.0,
) -> tuple[str, str]:
    """Fetch the given URL and return the content and content-type.

    Args:
        url: Webpage to fetch.
        user_agent: Custom User-Agent header, defaults to a project specific one.
        ignore_robots_txt: Skip robots.txt validation when True.
        proxy_url: HTTP proxy URL if requests must be proxied.
        timeout: Timeout for individual HTTP requests.

    Returns:
        content and content-type of the fetched page.
    """
    if not url:
        raise ValueError("A non-empty URL is required")

    resolved_user_agent = user_agent or DEFAULT_USER_AGENT
    content, content_type = asyncio.run(
        _fetch_async(
            url,
            user_agent=resolved_user_agent,
            ignore_robots_txt=ignore_robots_txt,
            proxy_url=proxy_url,
            timeout=timeout,
        )
    )

    return content, content_type
