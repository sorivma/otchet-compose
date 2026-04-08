"""Paragraph block handler.

Validates ``type: paragraph`` blocks and renders them as ``GOST Body
Text`` paragraphs with a 1.25 cm first-line indent.
"""

from pathlib import Path

from ..content import add_body_paragraph
from ._base import RenderContext


class ParagraphHandler:
    """Handler for ``type: paragraph`` blocks."""
    def validate(self, block: dict, index: int, base_dir: Path) -> dict:
        text = block.get("text")

        if not isinstance(text, str) or not text.strip():
            raise ValueError(
                f"content[{index}]: paragraph.text обязателен и должен быть строкой"
            )

        return {
            "type": "paragraph",
            "text": text.strip(),
        }

    def render(self, doc, block: dict, ctx: RenderContext) -> None:
        add_body_paragraph(doc, block["text"])
        ctx.current_page_has_content = True
