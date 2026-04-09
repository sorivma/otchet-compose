"""Heading block handler.

Validates ``type: heading`` blocks and renders them using the appropriate
GOST heading style.  Structural headings (``structural: true``) are
uppercased automatically and receive a page break when preceding content
exists on the current page.
"""

from pathlib import Path

from ._base import RenderContext

_SUPPORTED_LEVELS = {1, 2, 3}


class HeadingHandler:
    """Handler for ``type: heading`` blocks."""

    def validate(self, block: dict, index: int, base_dir: Path) -> dict:
        text = block.get("text")
        level = block.get("level")
        structural = block.get("structural")

        if not isinstance(text, str) or not text.strip():
            raise ValueError(
                f"content[{index}]: heading.text обязателен и должен быть строкой"
            )
        if level not in _SUPPORTED_LEVELS:
            raise ValueError(
                f"content[{index}]: heading.level должен быть одним из "
                f"{sorted(_SUPPORTED_LEVELS)}"
            )
        if not isinstance(structural, bool):
            raise ValueError(
                f"content[{index}]: heading.structural должен быть true/false"
            )

        return {
            "type": "heading",
            "text": text.strip(),
            "level": level,
            "structural": structural,
        }

    def render(self, doc, block: dict, ctx: RenderContext) -> None:
        """Append a heading paragraph, inserting a page break for structural headings."""
        text = block["text"]
        level = block["level"]
        structural = block["structural"]

        if structural:
            if ctx.current_page_has_content:
                doc.add_page_break()
            style_name = "GOST Heading 1" if level == 1 else "GOST Heading 2"
            doc.add_paragraph(text.upper(), style=style_name)
        else:
            style_name = {1: "GOST Heading 1", 2: "GOST Heading 2", 3: "GOST Heading 3"}[level]
            doc.add_paragraph(text, style=style_name)

        ctx.current_page_has_content = True
