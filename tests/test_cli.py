"""CLI-focused regression tests."""

from __future__ import annotations

import io
from pathlib import Path

from fetch_markdown import cli


def test_cli_prints_stdout(monkeypatch, capsys):
    """CLI should print converted Markdown to stdout by default."""

    def fake_fetch(url, **kwargs):  # noqa: ANN001
        assert url == "https://example.com"
        return "<html>hello</html>", "text/html"

    def fake_html_to_markdown(html, content_type=None):  # noqa: ANN001
        assert html == "<html>hello</html>"
        assert content_type == "text/html"
        return "hello"

    monkeypatch.setattr(cli, "fetch", fake_fetch)
    monkeypatch.setattr(cli, "html_to_markdown", fake_html_to_markdown)

    exit_code = cli.main(["https://example.com"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "hello" in captured.out


def test_cli_writes_file(monkeypatch, tmp_path: Path, capsys):
    """CLI should write Markdown to the provided --output path."""

    def fake_fetch(url, **kwargs):  # noqa: ANN001
        return "<html>file</html>", "text/html"

    def fake_html_to_markdown(html, content_type=None):  # noqa: ANN001
        assert content_type == "text/html"
        return "written"

    monkeypatch.setattr(cli, "fetch", fake_fetch)
    monkeypatch.setattr(cli, "html_to_markdown", fake_html_to_markdown)

    output_path = tmp_path / "out.md"
    exit_code = cli.main([
        "https://example.com",
        "--output",
        str(output_path),
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert output_path.read_text(encoding="utf-8") == "written"
    assert "Markdown written" in captured.err


def test_cli_reads_file_source(monkeypatch, tmp_path: Path, capsys):
    """CLI should read HTML from disk and pass it through the converter."""
    html_file = tmp_path / "page.html"
    html_file.write_text("<html>file</html>", encoding="utf-8")

    def fake_html_to_markdown(html, content_type=None):  # noqa: ANN001
        assert html == "<html>file</html>"
        assert content_type is None
        return "converted"

    monkeypatch.setattr(cli, "html_to_markdown", fake_html_to_markdown)

    exit_code = cli.main([str(html_file)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "converted" in captured.out


def test_cli_reads_stdin_source(monkeypatch, capsys):
    """CLI should pipe stdin when '-' is used as the source."""
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO("<html>stdin</html>"))

    def fake_html_to_markdown(*args, **kwargs):  # noqa: ANN001
        raise AssertionError("html_to_markdown should not run when --raw is set")

    monkeypatch.setattr(cli, "html_to_markdown", fake_html_to_markdown)

    exit_code = cli.main(["-", "--raw"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "<html>stdin</html>" in captured.out


def test_cli_writes_file_from_path_source(monkeypatch, tmp_path: Path, capsys):
    """CLI should transform a local file and persist output when requested."""
    html_file = tmp_path / "page.html"
    html_file.write_text("<html>file</html>", encoding="utf-8")

    def fake_html_to_markdown(html, content_type=None):  # noqa: ANN001
        return html.upper()

    monkeypatch.setattr(cli, "html_to_markdown", fake_html_to_markdown)

    output_path = tmp_path / "out.md"
    exit_code = cli.main([
        str(html_file),
        "--output",
        str(output_path),
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert output_path.read_text(encoding="utf-8") == "<HTML>FILE</HTML>"
    assert "Markdown written" in captured.err
