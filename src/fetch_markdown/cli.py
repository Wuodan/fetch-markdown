"""Command-line interface for fetch-markdown."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .core import DEFAULT_USER_AGENT, FetchMarkdownError, fetch_markdown


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch a web page and output cleaned Markdown",
    )
    parser.add_argument("url", help="URL to fetch")
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
            "Custom User-Agent header. Defaults to a fetch-markdown specific agent."
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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        markdown = fetch_markdown(
            args.url,
            output_path=args.output,
            force_raw=args.raw,
            user_agent=args.user_agent or DEFAULT_USER_AGENT,
            ignore_robots_txt=args.ignore_robots,
            proxy_url=args.proxy,
            timeout=args.timeout,
        )
    except (FetchMarkdownError, ValueError) as exc:
        parser.exit(1, f"error: {exc}\n")

    if args.output is None:
        print(markdown)
    else:
        print(f"Markdown written to {args.output.resolve()}", file=sys.stderr)

    return 0


__all__ = ["main", "build_parser"]
