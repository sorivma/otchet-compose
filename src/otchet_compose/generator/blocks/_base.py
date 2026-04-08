from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class RenderContext:
    figure_counter: int = 0
    current_page_has_content: bool = False


class BlockHandler(Protocol):
    def validate(self, block: dict, index: int, base_dir: Path) -> dict: ...
    def render(self, doc, block: dict, ctx: RenderContext) -> None: ...
