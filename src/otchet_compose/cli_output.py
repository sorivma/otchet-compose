"""Stable machine-readable output helpers for the CLI."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


def success_payload(
    command: str,
    *,
    outputs: list[str | Path] | None = None,
    data: dict[str, Any] | None = None,
    warnings: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "status": "success",
        "command": command,
        "outputs": [str(Path(output).resolve()) for output in outputs or []],
        "warnings": warnings or [],
        "errors": [],
        "data": data or {},
    }


def error_payload(command: str, code: str, message: str) -> dict[str, Any]:
    return {
        "status": "error",
        "command": command,
        "outputs": [],
        "warnings": [],
        "errors": [{"code": code, "message": message}],
        "data": {},
    }


def print_json(payload: dict[str, Any], *, error: bool = False) -> None:
    print(
        json.dumps(payload, ensure_ascii=False, sort_keys=True),
        file=sys.stderr if error else sys.stdout,
    )
