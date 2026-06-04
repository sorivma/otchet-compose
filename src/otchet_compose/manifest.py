"""Reproducible artifact manifest support."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Iterable


def file_record(path: str | Path) -> dict[str, object]:
    resolved = Path(path).resolve()
    return {
        "path": str(resolved),
        "sha256": _sha256(resolved),
        "size": resolved.stat().st_size,
    }


def write_manifest(
    manifest_path: str | Path,
    *,
    command: str,
    inputs: Iterable[str | Path],
    outputs: Iterable[str | Path],
) -> Path:
    path = Path(manifest_path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": 1,
        "command": command,
        "inputs": [file_record(item) for item in inputs],
        "outputs": [file_record(item) for item in outputs],
    }
    temp_path = _temporary_path(path)
    try:
        temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)
    return path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _temporary_path(output_path: Path) -> Path:
    handle = tempfile.NamedTemporaryFile(
        prefix=f".{output_path.stem}-",
        suffix=output_path.suffix,
        dir=output_path.parent,
        delete=False,
    )
    handle.close()
    return Path(handle.name)
