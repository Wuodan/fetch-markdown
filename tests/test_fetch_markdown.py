"""Live network test exercising the full fetch→markdown pipeline."""

from __future__ import annotations

import pytest

from extract2md import Html2MarkdownError, fetch_to_markdown

Example_URL = "https://www.iana.org/help/example-domains"


def test_fetch_to_markdown(tmp_path) -> None:
    """Fetch real content from iana.org and persist the resulting Markdown."""
    try:
        markdown = fetch_to_markdown(Example_URL)
    except Html2MarkdownError as exc:  # pragma: no cover - depends on network
        # Networking hiccups shouldn't fail the suite; treat them as skipped.
        pytest.skip(f"Unable to contact iana.org: {exc}")

    output_path = tmp_path / "example-domains.md"
    output_path.write_text(markdown, encoding="utf-8")
    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8")
    assert markdown
    print(f"Markdown saved to {output_path}")
    assert "example domains" in markdown.lower()
