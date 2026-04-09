"""Shared types for the block handler system.

:class:`RenderContext` carries mutable rendering state (counters, flags)
that is threaded through every block render call so that the orchestrator
in :mod:`~otchet_compose.generator.build` stays stateless.

:class:`BlockHandler` is a structural :class:`~typing.Protocol` — any
class that implements ``validate`` and ``render`` with the right
signatures qualifies without explicit inheritance.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class RenderContext:
    """Mutable rendering state threaded through every block render call.

    Attributes:
        figure_counter: Incremented by each rendered figure; used for
            sequential caption numbering.
        table_counter: Incremented by each rendered table; used for
            sequential caption numbering.
        current_page_has_content: ``True`` once at least one visible element
            has been written to the current page.  Used by structural headings
            to decide whether to insert a page break before themselves.
    """

    figure_counter: int = 0
    table_counter: int = 0
    current_page_has_content: bool = False


class BlockHandler(Protocol):
    """Structural protocol for block type handlers.

    Any class that implements ``validate`` and ``render`` with the signatures
    below qualifies — no explicit inheritance required.
    """

    def validate(self, block: dict, index: int, base_dir: Path) -> dict:
        """Validate a raw block dict and return its normalised form.

        Args:
            block: Raw dict from the YAML ``content`` list.
            index: 1-based position of the block (used in error messages).
            base_dir: Directory of the config file; used to resolve relative paths.

        Returns:
            A normalised block dict ready for rendering.

        Raises:
            ValueError: If a required field is missing or has an invalid value.
        """
        ...

    def render(self, doc, block: dict, ctx: RenderContext) -> None:
        """Render a validated block dict into *doc*, updating *ctx* as needed.

        Args:
            doc: The python-docx ``Document`` being built.
            block: Normalised block dict (output of :meth:`validate`).
            ctx: Shared rendering context; handlers should update relevant
                fields (e.g. increment ``ctx.figure_counter``).
        """
        ...
