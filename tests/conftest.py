"""Shared pytest fixtures."""

import textwrap
from pathlib import Path

import pytest


@pytest.fixture()
def base_dir(tmp_path: Path) -> Path:
    """Return a temporary directory to use as config base_dir."""
    return tmp_path


def write_config(tmp_path: Path, content: str) -> Path:
    """Write *content* to a YAML file in *tmp_path* and return the path."""
    path = tmp_path / "otchet-compose.yml"
    path.write_text(textwrap.dedent(content), encoding="utf-8")
    return path
