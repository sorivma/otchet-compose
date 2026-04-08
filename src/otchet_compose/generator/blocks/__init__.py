from ._base import BlockHandler, RenderContext
from .figure import FigureHandler
from .heading import HeadingHandler
from .paragraph import ParagraphHandler

REGISTRY: dict[str, BlockHandler] = {
    "heading": HeadingHandler(),
    "paragraph": ParagraphHandler(),
    "figure": FigureHandler(),
}

__all__ = ["REGISTRY", "RenderContext", "BlockHandler"]
