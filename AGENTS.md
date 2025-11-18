# Repository Guidelines

## Project Structure & Module Organization
- `src/extract2md/` holds the library and CLI entry points; `core.py` mirrors the MCP `fetch` logic, while `cli.py` exposes `extract2md` and `python -m extract2md`.
- `tests/` contains Pytest suites: `test_extract2md.py` hits the live iana.org page, and `test_cli.py` checks stdout/file behavior.
- `.github/workflows/ci.yml` defines the GH Actions pipeline; `requirements*.txt` and `pyproject.toml` declare dependencies and build metadata.

## Build, Test, and Development Commands
- Always activate the local venv: `source .venv/bin/activate` (or `.\.venv\Scripts\activate` on Windows) before running Python tooling.
- `python -m pip install -r requirements-dev.txt` – install runtime + dev deps inside `.venv`.
- `ruff check src tests` – lint for style/compliance; mirrors CI expectations.
- `pytest --cov=src --cov-report=term-missing` – run all tests and show coverage gaps.
- `python -m build` – produce sdist/wheel (CI calls hatchling with the same command).

## Coding Style & Naming Conventions
- Python 3.10+ typing, async-friendly helpers, and ATX markdown headings; stick to standard snake_case for modules, functions, and variables.
- Formatters/linters: Ruff enforces import order, unused code removal, and general PEP 8 spacing; no autoformatter is wired, so keep edits tidy manually.
- Keep comments minimal and purposeful; when copying upstream MCP code, preserve license headers.

## Testing Guidelines
- Use Pytest; name files `test_*.py` and functions `test_*`.
- Network-dependent tests should skip gracefully on failures (see `test_fetch_to_markdown` for pattern) and print artifact paths.
- Maintain coverage near current CI expectations (~85% overall) and ensure new features include unit tests or CLI regression checks.

## Commit & Pull Request Guidelines
- Commit messages follow short imperative summaries (e.g., “Add CLI file-output flag”); include context in the body when touching multiple areas.
- PRs should describe behavior changes, reference relevant issues, and note testing (e.g., “ruff + pytest --cov”). Add screenshots/output snippets if UX changes affect CLI behavior.
