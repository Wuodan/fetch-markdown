"""HTML conversion helpers for fetch-markdown."""

from __future__ import annotations

from typing import Any, Optional

import markdownify
import readabilipy.simple_json

from fetch_markdown.models import (
    Html2MarkdownContentTypeError,
    Html2MarkdownToMarkdownError,
)

HTML_TAG_THRESHOLD = 100


def to_markdown(
        html: str,
        content_type: Optional[Any] = None,
) -> str:
    """Convert raw HTML into Markdown."""

    content_type_value = str(content_type or "")
    is_content_type_html = (
            not content_type_value or "text/html" in content_type_value.lower()
    )
    if not is_content_type_html:
        raise Html2MarkdownContentTypeError(
            f"Received non-html content type {content_type}. Here is the raw content:\n{html}"
        )

    is_page_html = "<html" in html[:HTML_TAG_THRESHOLD].lower()
    if not is_page_html:
        raise Html2MarkdownToMarkdownError(
            "Not a valid HTML document. "
            f"Here are the first {HTML_TAG_THRESHOLD} characters:\n"
            f"{html[:HTML_TAG_THRESHOLD]}"
        )

    return _extract_content_from_html(html)


def _extract_content_from_html(html: str) -> str:
    """Run Readability + markdownify to simplify an HTML document."""
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
