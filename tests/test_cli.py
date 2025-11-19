"""CLI-focused regression tests."""

from __future__ import annotations

import io
from pathlib import Path

from extract2md import cli
from extract2md.converters import DEFAULT_CONVERTER


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
            converter=None,
    ):
        assert html == "<html>hello</html>"
        assert content_type == "text/html"
        assert base_url == "https://example.com"
        assert rewrite_relative_urls is True
        assert converter == DEFAULT_CONVERTER
        return "hello"

    monkeypatch.setattr(cli, "fetch", fake_fetch)
    monkeypatch.setattr(cli, "html_to_markdown", fake_html_to_markdown)

    exit_code = cli.main(["https://example.com"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "hello" in captured.out


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
            converter=None,
    ):
        assert html == "<html>file</html>"
        assert content_type is None
        assert base_url == expected_base
        assert rewrite_relative_urls is True
        assert converter == DEFAULT_CONVERTER
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
        return "converted-stdin"

    monkeypatch.setattr(cli, "html_to_markdown", fake_html_to_markdown)

    exit_code = cli.main(["-"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "converted-stdin" in captured.out


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
            converter=None,
    ):
        assert rewrite_relative_urls is False
        assert converter == DEFAULT_CONVERTER
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
            converter=None,
    ):
        assert base_url == "https://override.test"
        assert rewrite_relative_urls is True
        assert converter == DEFAULT_CONVERTER
        return "converted"

    monkeypatch.setattr(cli, "html_to_markdown", fake_html_to_markdown)

    exit_code = cli.main(["-", "--base-url", "https://override.test"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "converted" in captured.out


def test_cli_supports_custom_converter(monkeypatch, capsys):
    """--converter should be forwarded to html_to_markdown."""

    def fake_fetch(url, **kwargs):  # noqa: ANN001
        return "<html>body</html>", "text/html"

    def fake_html_to_markdown(  # noqa: ANN001
            html,
            content_type=None,
            *,
            base_url=None,
            rewrite_relative_urls=None,
            converter=None,
    ):
        assert converter == "trafilatura"
        return "body"

    monkeypatch.setattr(cli, "fetch", fake_fetch)
    monkeypatch.setattr(cli, "html_to_markdown", fake_html_to_markdown)

    exit_code = cli.main(["https://example.com", "--converter", "trafilatura"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "body" in captured.out
