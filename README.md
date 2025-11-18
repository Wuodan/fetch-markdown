# fetch-markdown

`fetch-markdown` is a lightweight Python tool that reuses the content
extraction logic from Anthropic's `mcp_server_fetch` project to turn web pages
into cleaned Markdown. It can be used either as a small library or through a
command-line interface.

## Installation

```bash
pip install -r requirements-dev.txt  # includes runtime deps and pytest/ruff
```

## Library usage

```python
from pathlib import Path
from fetch_markdown import fetch_markdown

markdown = fetch_markdown("https://huggingface.co/unsloth/GLM-4.6-GGUF")
print(markdown[:200])

output_path = Path("/tmp/model-card.md")
fetch_markdown(
    "https://huggingface.co/unsloth/GLM-4.6-GGUF",
    output_path=output_path,
)
```

## CLI usage

```bash
python -m fetch_markdown https://huggingface.co/unsloth/GLM-4.6-GGUF

# or
fetch-markdown --output output.md https://huggingface.co/unsloth/GLM-4.6-GGUF
```

## Development

- Lint with `ruff check fetch_markdown tests`.
- Run tests with `pytest --cov=fetch_markdown --cov-report=term-missing`.

The tests depend on the Hugging Face website being reachable. They will be
skipped automatically if the network call fails.
