from __future__ import annotations

from pathlib import Path

from fetch_markdown import cli


def test_cli_prints_stdout(monkeypatch, capsys):
    def fake_fetch(url, **kwargs):  # noqa: ANN001
        assert url == "https://example.com"
        return "hello"

    monkeypatch.setattr(cli, "fetch_markdown", fake_fetch)

    exit_code = cli.main(["https://example.com"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "hello" in captured.out


def test_cli_writes_file(monkeypatch, tmp_path: Path, capsys):
    def fake_fetch(url, output_path=None, **kwargs):  # noqa: ANN001
        if output_path:
            Path(output_path).write_text("written")
        return "written"

    monkeypatch.setattr(cli, "fetch_markdown", fake_fetch)

    output_path = tmp_path / "out.md"
    exit_code = cli.main([
        "https://example.com",
        "--output",
        str(output_path),
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert output_path.read_text() == "written"
    assert "Markdown written" in captured.err
