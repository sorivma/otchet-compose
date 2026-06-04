# Agent Guide

## Purpose

`otchet-compose` generates DOCX reports from declarative YAML.

## Reliable Workflow

1. Discover capabilities with `otchet-compose inspect --json`.
2. Obtain the current contract with `otchet-compose schema --json`.
3. Validate with `otchet-compose validate -f <config> --json`.
4. Preview writes with `otchet-compose gen -f <config> --dry-run --output-root <root> --json`.
5. Generate with `--force` only when replacing an existing artifact is intended.
6. Use `--manifest <path>` when downstream automation must verify exact inputs and outputs.

Successful JSON is written to stdout. Errors are written to stderr. Exit code `2`
means invalid input or arguments; exit code `1` means an unexpected internal error.

## Development

```powershell
python -m pip install -e ".[dev]"
ruff check src tests
python -m pytest -q
```

Keep `src/otchet_compose/schemas/v1.json`, examples, README, and CLI behavior aligned.
