from __future__ import annotations


class Html2MarkdownError(RuntimeError):
    """Base class for errors in this package."""


class Html2MarkdownContentTypeError(Html2MarkdownError):
    """Raised when HTML cannot be converted to Markdown."""


class Html2MarkdownToMarkdownError(Html2MarkdownError):
    """Raised when HTML cannot be converted to Markdown."""


class Html2MarkdownFetchError(Html2MarkdownError):
    """Raised when a URL cannot be fetched."""
