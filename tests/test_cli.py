"""CLI-focused regression tests."""

from __future__ import annotations

import io
from pathlib import Path

from extract2md import cli


def test_cli_prints_stdout(monkeypatch, capsys):
    """CLI should print converted Markdown to stdout by default."""

    def fake_fetch(url, **kwargs):  # noqa: ANN001
        assert url == "https://example.com"
        return "<html>hello</html>", "text/html"

    def fake_html_to_markdown(  # noqa: ANN001
            html,
            content_type=None,
            *,
            base_url=None,
            rewrite_relative_urls=None,
    ):
        assert html == "<html>hello</html>"
        assert content_type == "text/html"
        assert base_url == "https://example.com"
        assert rewrite_relative_urls is True
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

    def fake_html_to_markdown(  # noqa: ANN001
            html,
            content_type=None,
            *,
            base_url=None,
            rewrite_relative_urls=None,
    ):
        assert content_type == "text/html"
        assert base_url == "https://example.com"
        assert rewrite_relative_urls is True
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

    expected_base = html_file.resolve().as_uri()

    def fake_html_to_markdown(  # noqa: ANN001
            html,
            content_type=None,
            *,
            base_url=None,
            rewrite_relative_urls=None,
    ):
        assert html == "<html>file</html>"
        assert content_type is None
        assert base_url == expected_base
        assert rewrite_relative_urls is True
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

    expected_base = html_file.resolve().as_uri()

    def fake_html_to_markdown(  # noqa: ANN001
            html,
            content_type=None,
            *,
            base_url=None,
            rewrite_relative_urls=None,
    ):
        assert base_url == expected_base
        assert rewrite_relative_urls is True
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


def test_cli_disable_relative_rewrite(monkeypatch, capsys):
    """Users can opt out of rewriting relative links."""

    def fake_fetch(url, **kwargs):  # noqa: ANN001
        return "<html>body</html>", "text/html"

    def fake_html_to_markdown(  # noqa: ANN001
            html,
            content_type=None,
            *,
            base_url=None,
            rewrite_relative_urls=None,
    ):
        assert rewrite_relative_urls is False
        return "body"

    monkeypatch.setattr(cli, "fetch", fake_fetch)
    monkeypatch.setattr(cli, "html_to_markdown", fake_html_to_markdown)

    exit_code = cli.main(["https://example.com", "--no-rewrite-relative-urls"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "body" in captured.out


def test_cli_base_url_override_for_stdin(monkeypatch, capsys):
    """Users may set a base URL explicitly when using stdin."""
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO("<html>stdin</html>"))

    def fake_html_to_markdown(  # noqa: ANN001
            html,
            content_type=None,
            *,
            base_url=None,
            rewrite_relative_urls=None,
    ):
        assert base_url == "https://override.test"
        assert rewrite_relative_urls is True
        return "converted"

    monkeypatch.setattr(cli, "html_to_markdown", fake_html_to_markdown)

    exit_code = cli.main(["-", "--base-url", "https://override.test"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "converted" in captured.out
