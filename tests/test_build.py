"""Integration tests for generator/build.py — generate_document."""

from pathlib import Path

import pytest

from otchet_compose.generator.build import generate_document


def _base_config(tmp_path: Path, **overrides) -> dict:
    cfg = {
        "version": 1,
        "document": {
            "output": str(tmp_path / "out.docx"),
            "reserve_title_page": False,
            "toc": False,
            "title_page": None,
        },
        "content": [
            {"type": "paragraph", "text": "Hello"},
        ],
    }
    cfg["document"].update(overrides)
    return cfg


class TestGenerateDocument:
    def test_creates_output_file(self, tmp_path):
        cfg = _base_config(tmp_path)
        generate_document(cfg)
        assert (tmp_path / "out.docx").exists()

    def test_creates_parent_directories(self, tmp_path):
        out = tmp_path / "nested" / "deep" / "report.docx"
        cfg = _base_config(tmp_path, output=str(out))
        generate_document(cfg)
        assert out.exists()

    def test_with_toc(self, tmp_path):
        cfg = _base_config(tmp_path, toc=True)
        generate_document(cfg)
        assert (tmp_path / "out.docx").exists()

    def test_with_reserve_title_page(self, tmp_path):
        cfg = _base_config(tmp_path, reserve_title_page=True)
        generate_document(cfg)
        assert (tmp_path / "out.docx").exists()

    def test_with_title_page_template(self, tmp_path):
        cfg = _base_config(tmp_path, title_page={
            "template": "mock",
            "params": {
                "institute": "И", "department": "К", "discipline": "Д",
                "work_type": "О", "work_number": "1", "work_title": "Т",
                "student": "С", "group": "Г", "teacher": "П", "year": "2025",
            },
        })
        generate_document(cfg)
        assert (tmp_path / "out.docx").exists()

    def test_with_all_block_types(self, tmp_path):
        cfg = _base_config(tmp_path)
        cfg["content"] = [
            {"type": "heading", "text": "Цель", "level": 1, "structural": True},
            {"type": "paragraph", "text": "Some text"},
            {"type": "figure", "caption": "Fig", "path": None},
            {"type": "list", "style": "bullet", "items": ["A", "B"]},
            {"type": "table", "caption": "Tbl", "headers": ["X"], "rows": [["1"]]},
        ]
        generate_document(cfg)
        assert (tmp_path / "out.docx").exists()

    def test_prints_output_path(self, tmp_path, capsys):
        cfg = _base_config(tmp_path)
        generate_document(cfg)
        assert "out.docx" in capsys.readouterr().out
