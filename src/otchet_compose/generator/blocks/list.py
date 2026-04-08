"""List block handler.

Validates ``type: list`` blocks and renders them as ``GOST List``
paragraphs with a hanging indent so the marker (bullet or number)
aligns with the first-line indent of body text and continuation lines
wrap cleanly beneath the item text.

Supported styles:

* ``bullet``  — each item is prefixed with an em-dash (``–``), the
  GOST-recommended bullet character.
* ``numeric`` — items are prefixed ``1)``, ``2)``, … in order.
"""

from pathlib import Path

from ._base import RenderContext

_BULLET_MARKER = "–"


class ListHandler:
    """Handler for ``type: list`` blocks."""

    def validate(self, block: dict, index: int, base_dir: Path) -> dict:
        """Validate a list block and return its normalised form.

        Args:
            block: Raw dict with ``style`` and ``items`` keys.
            index: 1-based position in the content list (for error messages).
            base_dir: Config file directory (unused for lists).

        Returns:
            Normalised block dict with ``type``, ``style``, and ``items``.

        Raises:
            ValueError: If ``style`` is not ``"bullet"`` or ``"numeric"``,
                or if ``items`` is missing, empty, or contains non-strings.
        """
        style = block.get("style")
        items = block.get("items")

        if style not in ("bullet", "numeric"):
            raise ValueError(
                f"content[{index}]: list.style должен быть 'bullet' или 'numeric', "
                f"получено: {style!r}"
            )

        if not isinstance(items, list) or not items:
            raise ValueError(
                f"content[{index}]: list.items обязателен и должен быть непустым списком"
            )

        for i, item in enumerate(items, start=1):
            if not isinstance(item, str) or not item.strip():
                raise ValueError(
                    f"content[{index}]: list.items[{i}] должен быть непустой строкой"
                )

        return {
            "type": "list",
            "style": style,
            "items": [item.strip() for item in items],
        }

    def render(self, doc, block: dict, ctx: RenderContext) -> None:
        """Render each list item as a ``GOST List`` paragraph.

        Bullet items are prefixed with ``–``; numeric items with ``1)``,
        ``2)``, etc.
        """
        style = block["style"]
        for i, item in enumerate(block["items"], start=1):
            marker = f"{i})" if style == "numeric" else _BULLET_MARKER
            doc.add_paragraph(f"{marker} {item}", style="GOST List")
        ctx.current_page_has_content = True
