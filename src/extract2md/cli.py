"""Command-line interface for extract2md."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from urllib.parse import urlparse

from .core import DEFAULT_USER_AGENT, fetch, html_to_markdown
from .models import Html2MarkdownError


def build_parser() -> argparse.ArgumentParser:
    """Construct and return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Fetch a web page and output cleaned Markdown",
    )
    parser.add_argument(
        "source",
        help=(
            "URL to fetch, a local HTML file, or '-' to read HTML from stdin"
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Optional path to write the generated Markdown to",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Return raw HTML when simplification is not desired",
    )
    parser.add_argument(
        "--user-agent",
        help=(
            "Custom User-Agent header. Defaults to a extract2md specific agent."
        ),
    )
    parser.add_argument(
        "--ignore-robots",
        action="store_true",
        help="Skip robots.txt validation (use with caution)",
    )
    parser.add_argument(
        "--proxy",
        help="Optional HTTP/HTTPS proxy URL",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default: 30)",
    )
    parser.add_argument(
        "--rewrite-relative-urls",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Rewrite relative href/src attributes (default: enabled)",
    )
    parser.add_argument(
        "--base-url",
        help=(
            "Optional base URL used to resolve relative links for stdin or file sources "
            "(overrides automatic detection)"
        ),
    )
    return parser


def _is_url(value: str) -> bool:
    """Return True when ``value`` looks like an HTTP(S) URL."""
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _write_output_file(content: str, output_path: Path | str) -> None:
    """Persist rendered Markdown to ``output_path``."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    """Entry point used by ``python -m extract2md`` and the console script."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        content, content_type = None, None
        base_url: str | None = args.base_url

        if args.source == "-":
            content = sys.stdin.read()

        elif _is_url(args.source):
            if base_url is None:
                base_url = args.source
            content, content_type = fetch(
                args.source,
                user_agent=args.user_agent or DEFAULT_USER_AGENT,
                ignore_robots_txt=args.ignore_robots,
                proxy_url=args.proxy,
                timeout=args.timeout,
            )

        else:
            source_path = Path(args.source)
            content = source_path.read_text(encoding="utf-8")
            if base_url is None:
                base_url = source_path.resolve().as_uri()

        if not args.raw:
            content = html_to_markdown(
                content,
                content_type,
                base_url=base_url,
                rewrite_relative_urls=args.rewrite_relative_urls,
            )

        if args.output is not None:
            _write_output_file(content, args.output)

    except (Html2MarkdownError, ValueError, OSError) as exc:
        parser.exit(1, f"error: {exc}\n")

    if args.output is None:
        print(content)
    else:
        print(f"Markdown written to {args.output.resolve()}", file=sys.stderr)

    return 0


__all__ = ["main"]
