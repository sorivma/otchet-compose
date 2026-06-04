"""Tests for the bundled JSON Schema."""

from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

from otchet_compose.schemas import load_schema


def test_schema_is_valid():
    Draft202012Validator.check_schema(load_schema())


def test_examples_conform_to_schema():
    validator = Draft202012Validator(load_schema())
    paths = [Path("examples/otchet-compose.yml"), Path("doc/otchet-compose.llm.ref.yml")]

    for path in paths:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert list(validator.iter_errors(raw)) == [], path
