# extract2md

`extract2md` is all about “HTML in → Markdown out.” You can start from a live
URL, a file on disk, or an already-loaded HTML string.

It can be used from CLI or as a Python library.

## Installation

```bash
pip install extract2md
```

Prerequisites:

- Python 3.10+ runtime
- Node.js (recommended for best results; powers Readability.js content extraction)

## CLI usage

### 1. Fetch a URL and display Markdown

```bash
extract2md https://www.iana.org/help/example-domains
```

### 2. Fetch and write to a file

```bash
extract2md https://www.iana.org/help/example-domains > sample-output.md
```

### 3. Convert previously saved HTML (files or stdin)

```bash
# convert file
extract2md sample-page.html
# or from stdin
cat sample-page.html | extract2md -
```

### 4. Skip Markdown conversion and emit the HTML verbatim

```bash
extract2md --raw https://example.com
```

## Parameters

- `source`: URL, filesystem path, or `-` to read HTML from stdin.
- `--raw`: bypass HTML-to-Markdown conversion and emit the response body.
- `--user-agent STRING`: override the default identifier.
- `--ignore-robots`: skip robots.txt validation (use sparingly).
- `--proxy URL`: HTTP(S) proxy forwarded to httpx.
- `--timeout SECONDS`: request timeout (default 30 seconds).
- `--rewrite-relative-urls/--no-rewrite-relative-urls`:  
  enable or disable rewriting relative `href`/`src` attributes to absolute links (default on).
- `--base-url URL`: optional base URL for rewriting relative urls (default `source`).
- `--converter NAME`: choose the HTML conversion backend. Defaults to `trafilatura`;
  `readability` (requires Node.js) is also available.

## Environment variables

- `EXTRACT2MD_NODE_PATH`: Set the `EXTRACT2MD_NODE_PATH` environment variable to the Node.js binary (or its
  directory) if Readability.js cannot find `node` on your `PATH`.

## Python Library usage

`extract2md` can also be used as a Python library.

### 1. Fetch a URL and get Markdown

```python
from extract2md import fetch_to_markdown

markdown = fetch_to_markdown("https://www.iana.org/help/example-domains")
```

### 2. Convert a previously saved HTML file

```python
from extract2md import file_to_markdown

markdown_from_file = file_to_markdown("sample-page.html")
```

### 3. Convert an HTML string you already have

```python
from extract2md import html_to_markdown

html = "<html><body><h1>Offline HTML</h1></body></html>"
markdown_from_html = html_to_markdown(html)

# Optionally disable replacing relative links with absolute URLs
markdown_custom = html_to_markdown(
    html,
    rewrite_relative_urls=False,
)

# Or replace relative links with a custom base URL
markdown_custom = html_to_markdown(
    html,
    rewrite_relative_urls=False,
    base_url="https://example.com/docs/",
)

# Pick an alternate conversion backend (e.g., Readability)
markdown_readability = html_to_markdown(html, converter="readability")
```

### Additional public methods

Need to store markup or run your own converter? Use `fetch` and skip the Markdown
step entirely:

```python
from extract2md import fetch

raw_html, content_type = fetch("https://example.com/docs")
```

## Notes

- The CLI and library both fetch live webpages from URLs; network availability and site
  rate limits apply.
- Inspired by the [Fetch MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch).
- Thanks go to these libraries for the heavy lifting:
    - [ReadabiliPy](https://github.com/alan-turing-institute/ReadabiliPy) with
      Mozilla's [Readability.js](https://github.com/mozilla/readability) Node.js package
    - [Markdownify](https://github.com/matthewwithanm/python-markdownify)
    - [Trafilatura](https://github.com/adbar/trafilatura)
