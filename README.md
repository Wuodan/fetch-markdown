# fetch-markdown

`fetch-markdown` is a lightweight Python tool that reuses the content
extraction logic from Anthropic's `mcp_server_fetch` project to turn web pages
into cleaned Markdown. It can be used either as a small library or through a
command-line interface. Upstream code lives at
https://github.com/modelcontextprotocol/servers/tree/main/src/fetch.

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

## Parameters

The library function and CLI share the same core arguments/options:

- `url` (positional for CLI / first argument for library): target page.
- `output_path` / `-o/--output PATH`: optional destination file; stdout is used
  when omitted.
- `force_raw` / `--raw`: skip simplification and emit the response body verbatim.
- `user_agent` / `--user-agent STRING`: override the default identifier.
- `ignore_robots_txt` / `--ignore-robots`: skip robots.txt checks (use sparingly).
- `proxy_url` / `--proxy URL`: HTTP(S) proxy forwarded to httpx.
- `timeout` / `--timeout SECONDS`: request timeout (default 30 seconds).

## Development

- Lint with `ruff check fetch_markdown tests`.
- Run tests with `pytest --cov=fetch_markdown --cov-report=term-missing`.

The tests depend on the Hugging Face website being reachable. They will be
skipped automatically if the network call fails.
