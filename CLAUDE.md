# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

`otchet-compose` is a CLI tool that generates DOCX lab-report documents from YAML configuration files. It targets Russian academic formatting (GOST-style): A4, Times New Roman 14pt, 1.5 line spacing, 3cm left margin, automatic TOC, page numbers in footer. Figures without a `path` (or with a missing file) get a placeholder table instead of an image.

## Install and run

```bash
pip install -e .                                # install in dev mode
otchet-compose gen -f path/to/config.yml        # generate a report
otchet-compose gen                              # uses ./otchet-compose.yml by default
```

Output DOCX is written to the path specified in `document.output`; parent directories are created automatically.

## Architecture

```
src/otchet_compose/
  cli.py            – argparse entry point, `gen` subcommand
  config.py         – YAML loading + validation (returns plain dict)
  generator/
    __init__.py     – re-exports generate_document
    build.py        – top-level orchestrator: creates Document, calls helpers, saves file
    styles.py       – defines all GOST paragraph styles on the Document object
    content.py      – renders each block type (heading, paragraph, figure, TOC field)
    page.py         – page size/margins, footer page-number field
    fields.py       – low-level python-docx XML helpers (Word fields, fonts, borders)
```

Data flows in one direction: `cli → config.load_config → generator.generate_document`. The config produces a validated plain dict; the generator never touches YAML.

## YAML config format

Three block types are supported: `heading`, `paragraph`, `figure`. The required top-level keys are `version: 1`, `document`, and `content`.

```yaml
version: 1
document:
  output: "./build/report.docx"
  reserve_title_page: true   # leaves blank page 1 for a cover sheet
  toc: true                  # inserts a Word TOC field (must be updated in Word)
content:
  - type: heading
    text: "Цель работы"
    level: 1          # 1–3
    structural: true  # structural=true → ALL-CAPS + page break before (if not first)
  - type: paragraph
    text: >
      Folded scalar text goes here.
  - type: figure
    caption: "Caption without figure number"   # number is auto-assigned
    path: "./images/foo.png"                   # optional; omit for placeholder
```

`structural: true` headings are uppercased automatically and always use `GOST Heading 1` style regardless of `level`. Non-structural headings use `GOST Heading 1/2/3` matching `level`.

## Reference files

- `doc/otchet-compose.llm.ref.yml` – full annotated reference YAML, useful as a prompt attachment when asking an LLM to draft a config.
- `doc/prompt.txt` – system prompt for an LLM to generate a config from raw lab-work text.
- `examples/otchet-compose.yml` – a complete working example config.
