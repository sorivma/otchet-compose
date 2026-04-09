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
  cli.py               – argparse entry point, `gen` subcommand
  config.py            – YAML loading + validation (returns plain dict)
  generator/
    __init__.py        – re-exports generate_document
    build.py           – top-level orchestrator: creates Document, calls block REGISTRY, saves file
    styles.py          – loads GOST paragraph styles from styles.json and applies them to the Document
    styles.json        – style definitions (font, spacing, indent); override via ~/.otchet-compose/styles.json
    page.py            – page size/margins (PageSetup class), footer page-number field
    fields.py          – OxmlHelper: low-level OOXML helpers (Word fields, fonts)
    blocks/
      __init__.py      – REGISTRY dict mapping block type string → handler instance
      _base.py         – RenderContext dataclass (figure_counter, table_counter, current_page_has_content)
                         BlockHandler protocol (validate + render)
      heading.py       – HeadingHandler
      paragraph.py     – ParagraphHandler
      figure.py        – FigureHandler (image or bordered placeholder table)
      list.py          – ListHandler (bullet / numeric, native Word numbering XML)
      table.py         – TableHandler (GOST-styled table with numbered caption above)

tests/
  conftest.py          – shared fixtures and write_config helper
  test_config.py       – load_config and validation tests
  blocks/
    test_heading.py
    test_paragraph.py
    test_figure.py
    test_list.py
    test_table.py
```

Data flows in one direction: `cli → config.load_config → generator.generate_document`. The config produces a validated plain dict; the generator never touches YAML.

To add a new block type: create `blocks/<type>.py` implementing `validate` and `render`, then add one entry to `REGISTRY` in `blocks/__init__.py`. Nothing else needs to change.

## Running tests

```bash
pip install -e ".[dev]"   # installs pytest
pytest tests/ -v
```

## YAML config format

Five block types are supported. The required top-level keys are `version: 1`, `document`, and `content`.

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

  - type: list
    style: bullet    # bullet (–) or numeric (1), 2), …)
    items:
      - "First item"
      - "Second item"

  - type: table
    caption: "Caption without table number"    # number is auto-assigned; caption is above table
    headers:
      - "Column A"
      - "Column B"
    rows:
      - ["cell 1", "cell 2"]
      - ["cell 3", "cell 4"]
```

`structural: true` headings are uppercased automatically and always use `GOST Heading 1` style regardless of `level`. Non-structural headings use `GOST Heading 1/2/3` matching `level`.

Figure captions are rendered below the figure as "Рисунок N – text". Table captions are rendered above the table as "Таблица N – text", right-aligned. Both counters are independent and auto-incremented.

## Reference files

- `doc/otchet-compose.llm.ref.yml` – full annotated reference YAML, useful as a prompt attachment when asking an LLM to draft a config.
- `doc/prompt.txt` – system prompt for an LLM to generate a config from raw lab-work text.
- `examples/otchet-compose.yml` – a complete working example config.
