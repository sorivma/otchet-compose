"""Block handler registry.

``REGISTRY`` maps each supported block-type string to a handler instance
that knows how to validate (config-time) and render (generation-time)
that block type.

To add a new block type:

1. Create ``<type>.py`` in this package implementing ``validate`` and
   ``render`` (see :class:`~otchet_compose.generator.blocks._base.BlockHandler`).
2. Add one entry to ``REGISTRY`` below.

No other files need to change.
"""

from ._base import BlockHandler, RenderContext
from .figure import FigureHandler
from .heading import HeadingHandler
from .list import ListHandler
from .paragraph import ParagraphHandler

REGISTRY: dict[str, BlockHandler] = {
    "heading": HeadingHandler(),
    "paragraph": ParagraphHandler(),
    "figure": FigureHandler(),
    "list": ListHandler(),
}

__all__ = ["REGISTRY", "RenderContext", "BlockHandler"]
