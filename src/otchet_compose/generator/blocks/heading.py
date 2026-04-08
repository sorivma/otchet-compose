"""Heading block handler.

Validates ``type: heading`` blocks and renders them using the appropriate
GOST heading style.  Structural headings (``structural: true``) are
uppercased automatically and receive a page break when preceding content
exists on the current page.
"""

from pathlib import Path

from ..content import add_heading
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
        add_heading(
            doc,
            text=block["text"],
            level=block["level"],
            structural=block["structural"],
            page_break_before=block["structural"] and ctx.current_page_has_content,
        )
        ctx.current_page_has_content = True
