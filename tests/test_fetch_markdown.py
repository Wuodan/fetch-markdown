from __future__ import annotations

from pathlib import Path

import pytest

from fetch_markdown import FetchMarkdownError, fetch_markdown

HF_URL = "https://huggingface.co/unsloth/GLM-4.6-GGUF"


def test_fetch_markdown_huggingface(tmp_path: Path) -> None:
    output_path = tmp_path / "huggingface.md"
    try:
        markdown = fetch_markdown(HF_URL, output_path=output_path)
    except FetchMarkdownError as exc:  # pragma: no cover - depends on network
        pytest.skip(f"Unable to contact Hugging Face: {exc}")

    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8")
    assert markdown
    print(f"Markdown saved to {output_path}")
    assert "glm" in markdown.lower()
