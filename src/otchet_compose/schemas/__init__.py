"""Packaged JSON Schemas for otchet-compose configs."""

from __future__ import annotations

import json
from importlib import resources

from jsonschema import Draft202012Validator


def load_schema(version: int = 1) -> dict:
    """Load a bundled config schema by major config version."""
    schema_file = resources.files(__package__).joinpath(f"v{version}.json")
    if not schema_file.is_file():
        raise ValueError(f"Unsupported schema version: {version}")
    return json.loads(schema_file.read_text(encoding="utf-8"))


def validate_instance(instance: object, version: int = 1) -> None:
    """Validate a raw config against the bundled schema."""
    errors = sorted(Draft202012Validator(load_schema(version)).iter_errors(instance), key=lambda error: list(error.path))
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        raise ValueError(f"JSON Schema validation failed at {location}: {error.message}")
