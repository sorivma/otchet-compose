"""Tests for the command-line machine contract."""

from __future__ import annotations

import json
import sys

import pytest

from otchet_compose.cli import main
from otchet_compose.config import load_config
from tests.conftest import write_config


MINIMAL_YAML = """
version: 1
document:
  output: "./build/report.docx"
  reserve_title_page: false
  toc: false
content:
  - type: paragraph
    text: "Hello"
"""


def _run(monkeypatch, *args: str) -> int:
    monkeypatch.setattr(sys, "argv", ["otchet-compose", *args])
    return main()


def test_argument_error_preserves_json_contract(monkeypatch, capsys):
    with pytest.raises(SystemExit) as exc:
        _run(monkeypatch, "gen", "--unknown", "--json")

    assert exc.value.code == 2
    payload = json.loads(capsys.readouterr().err)
    assert payload["errors"][0]["code"] == "invalid_arguments"


def test_validate_json_success(tmp_path, monkeypatch, capsys):
    config = write_config(tmp_path, MINIMAL_YAML)

    assert _run(monkeypatch, "validate", "-f", str(config), "--json") == 0

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert captured.err == ""
    assert payload["status"] == "success"
    assert payload["command"] == "validate"
    assert payload["outputs"] == []
    assert payload["errors"] == []
    assert payload["data"]["block_count"] == 1


def test_validate_json_error_goes_to_stderr(tmp_path, monkeypatch, capsys):
    missing = tmp_path / "missing.yml"

    assert _run(monkeypatch, "validate", "-f", str(missing), "--json") == 2

    captured = capsys.readouterr()
    payload = json.loads(captured.err)
    assert captured.out == ""
    assert payload["status"] == "error"
    assert payload["errors"][0]["code"] == "invalid_input"


def test_plain_error_goes_to_stderr(tmp_path, monkeypatch, capsys):
    assert _run(monkeypatch, "validate", "-f", str(tmp_path / "missing.yml")) == 2

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Ошибка:" in captured.err


def test_gen_json_has_single_machine_readable_response(tmp_path, monkeypatch, capsys):
    config = write_config(tmp_path, MINIMAL_YAML)

    assert _run(monkeypatch, "gen", "-f", str(config), "--json") == 0

    captured = capsys.readouterr()
    payload = json.loads(captured.out)
    assert captured.err == ""
    assert payload["status"] == "success"
    assert payload["command"] == "gen"
    assert payload["outputs"] == [str((tmp_path / "build" / "report.docx").resolve())]


def test_gen_dry_run_does_not_write_output(tmp_path, monkeypatch, capsys):
    config = write_config(tmp_path, MINIMAL_YAML)

    assert _run(monkeypatch, "gen", "-f", str(config), "--dry-run", "--json") == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["data"]["dry_run"] is True
    assert not (tmp_path / "build" / "report.docx").exists()


def test_gen_refuses_overwrite_without_force(tmp_path, monkeypatch, capsys):
    config = write_config(tmp_path, MINIMAL_YAML)
    output = tmp_path / "build" / "report.docx"
    output.parent.mkdir()
    output.write_text("existing", encoding="utf-8")

    assert _run(monkeypatch, "gen", "-f", str(config), "--json") == 2
    assert "use --force" in json.loads(capsys.readouterr().err)["errors"][0]["message"]


def test_gen_rejects_output_outside_root(tmp_path, monkeypatch, capsys):
    config = write_config(tmp_path, MINIMAL_YAML)

    assert _run(
        monkeypatch,
        "gen",
        "-f",
        str(config),
        "--output-root",
        str(tmp_path / "allowed"),
        "--json",
    ) == 2
    assert "outside --output-root" in json.loads(capsys.readouterr().err)["errors"][0]["message"]


def test_gen_writes_sha256_manifest(tmp_path, monkeypatch, capsys):
    config = write_config(tmp_path, MINIMAL_YAML)
    manifest = tmp_path / "build" / "manifest.json"

    assert _run(
        monkeypatch,
        "gen",
        "-f",
        str(config),
        "--manifest",
        str(manifest),
        "--json",
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    manifest_payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["data"]["manifest"] == str(manifest.resolve())
    assert manifest_payload["command"] == "otchet-compose gen"
    assert len(manifest_payload["inputs"][0]["sha256"]) == 64
    assert len(manifest_payload["outputs"][0]["sha256"]) == 64


def test_gen_manifest_must_stay_inside_output_root(tmp_path, monkeypatch, capsys):
    config = write_config(tmp_path, MINIMAL_YAML)

    assert _run(
        monkeypatch,
        "gen",
        "-f",
        str(config),
        "--manifest",
        str(tmp_path / "outside.json"),
        "--output-root",
        str(tmp_path / "build"),
        "--json",
    ) == 2
    assert "outside --output-root" in json.loads(capsys.readouterr().err)["errors"][0]["message"]


def test_schema_json_exposes_versioned_schema(monkeypatch, capsys):
    assert _run(monkeypatch, "schema", "--json") == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "success"
    assert payload["data"]["version"] == 1
    assert payload["data"]["schema"]["properties"]["version"]["const"] == 1


def test_inspect_json_describes_blocks_and_templates(monkeypatch, capsys):
    assert _run(monkeypatch, "inspect", "--json") == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["data"]["block_types"] == ["figure", "heading", "list", "paragraph", "table"]
    assert {template["name"] for template in payload["data"]["templates"]} >= {"mock", "rut"}


def test_init_non_interactive_creates_valid_config(tmp_path, monkeypatch, capsys):
    config = tmp_path / "created.yml"

    assert _run(
        monkeypatch,
        "init",
        "--non-interactive",
        "-f",
        str(config),
        "--template",
        "rut",
        "--param",
        "student=Иванов",
        "--output-root",
        str(tmp_path),
        "--json",
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["data"]["non_interactive"] is True
    assert load_config(config)["document"]["title_page"]["params"]["student"] == "Иванов"


def test_validate_warns_about_missing_figure(tmp_path, monkeypatch, capsys):
    config = write_config(
        tmp_path,
        MINIMAL_YAML.replace(
            '  - type: paragraph\n    text: "Hello"',
            '  - type: figure\n    caption: "Missing"\n    path: "missing.png"',
        ),
    )

    assert _run(monkeypatch, "validate", "-f", str(config), "--json") == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["warnings"][0]["code"] == "missing_figure"
