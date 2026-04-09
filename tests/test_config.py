"""Tests for config.py — load_config and its validation helpers."""

import pytest

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


class TestLoadConfig:
    def test_returns_normalised_dict(self, tmp_path):
        path = write_config(tmp_path, MINIMAL_YAML)
        cfg = load_config(path)
        assert cfg["version"] == 1
        assert "document" in cfg
        assert "content" in cfg

    def test_output_path_is_absolute(self, tmp_path):
        path = write_config(tmp_path, MINIMAL_YAML)
        cfg = load_config(path)
        from pathlib import Path
        assert Path(cfg["document"]["output"]).is_absolute()

    def test_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_config(tmp_path / "missing.yml")

    def test_wrong_version(self, tmp_path):
        path = write_config(tmp_path, MINIMAL_YAML.replace("version: 1", "version: 99"))
        with pytest.raises(ValueError, match="version"):
            load_config(path)

    def test_missing_version(self, tmp_path):
        yaml = """
            document:
              output: "./build/report.docx"
              toc: false
            content:
              - type: paragraph
                text: "Hello"
        """
        path = write_config(tmp_path, yaml)
        with pytest.raises(ValueError, match="version"):
            load_config(path)

    def test_missing_document_section(self, tmp_path):
        yaml = """
            version: 1
            content:
              - type: paragraph
                text: "Hello"
        """
        path = write_config(tmp_path, yaml)
        with pytest.raises(ValueError, match="document"):
            load_config(path)

    def test_missing_output(self, tmp_path):
        yaml = """
            version: 1
            document:
              toc: false
            content:
              - type: paragraph
                text: "Hello"
        """
        path = write_config(tmp_path, yaml)
        with pytest.raises(ValueError, match="output"):
            load_config(path)

    def test_missing_toc(self, tmp_path):
        yaml = """
            version: 1
            document:
              output: "./build/report.docx"
            content:
              - type: paragraph
                text: "Hello"
        """
        path = write_config(tmp_path, yaml)
        with pytest.raises(ValueError, match="toc"):
            load_config(path)

    def test_invalid_reserve_title_page_type(self, tmp_path):
        yaml = MINIMAL_YAML.replace("reserve_title_page: false", "reserve_title_page: yes_please")
        path = write_config(tmp_path, yaml)
        with pytest.raises(ValueError, match="reserve_title_page"):
            load_config(path)

    def test_missing_content(self, tmp_path):
        yaml = """
            version: 1
            document:
              output: "./build/report.docx"
              toc: false
        """
        path = write_config(tmp_path, yaml)
        with pytest.raises(ValueError, match="content"):
            load_config(path)

    def test_empty_content_list(self, tmp_path):
        yaml = """
            version: 1
            document:
              output: "./build/report.docx"
              toc: false
            content: []
        """
        path = write_config(tmp_path, yaml)
        with pytest.raises(ValueError, match="content"):
            load_config(path)

    def test_unknown_block_type(self, tmp_path):
        yaml = """
            version: 1
            document:
              output: "./build/report.docx"
              toc: false
            content:
              - type: unknown_block
                text: "Hello"
        """
        path = write_config(tmp_path, yaml)
        with pytest.raises(ValueError, match="unknown_block"):
            load_config(path)

    def test_non_dict_block_raises(self, tmp_path):
        yaml = """
            version: 1
            document:
              output: "./build/report.docx"
              toc: false
            content:
              - "just a string, not a dict"
        """
        path = write_config(tmp_path, yaml)
        with pytest.raises(ValueError):
            load_config(path)

    def test_defaults_reserve_title_page_to_false(self, tmp_path):
        yaml = """
            version: 1
            document:
              output: "./build/report.docx"
              toc: false
            content:
              - type: paragraph
                text: "Hello"
        """
        path = write_config(tmp_path, yaml)
        cfg = load_config(path)
        assert cfg["document"]["reserve_title_page"] is False
