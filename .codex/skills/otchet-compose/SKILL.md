---
name: otchet-compose
description: Validate and generate DOCX reports from otchet-compose YAML using the repository CLI.
---

# Otchet Compose

1. Discover capabilities with `otchet-compose inspect --json`.
2. Read the exact contract with `otchet-compose schema --json`.
3. Validate with `otchet-compose validate -f <config> --json`.
4. Preview with `otchet-compose gen -f <config> --dry-run --output-root <root> --json`.
5. Generate with an explicit output root. Add `--force` only for intentional replacement.
6. Add `--manifest <path>` when exact input/output hashes are required.

Use `otchet-compose init --non-interactive ... --json` to create starter configs.
