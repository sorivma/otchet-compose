from pathlib import Path

from ..content import add_figure
from ._base import RenderContext


class FigureHandler:
    def validate(self, block: dict, index: int, base_dir: Path) -> dict:
        caption = block.get("caption")
        path = block.get("path")

        if not isinstance(caption, str) or not caption.strip():
            raise ValueError(
                f"content[{index}]: figure.caption обязателен и должен быть строкой"
            )

        normalized_path = None
        if path is not None:
            if not isinstance(path, str) or not path.strip():
                raise ValueError(
                    f"content[{index}]: figure.path должен быть непустой строкой, если указан"
                )
            normalized_path = str(_resolve_path(base_dir, path))

        return {
            "type": "figure",
            "caption": caption.strip(),
            "path": normalized_path,
        }

    def render(self, doc, block: dict, ctx: RenderContext) -> None:
        ctx.figure_counter += 1
        add_figure(
            doc,
            caption=block["caption"],
            image_path=block.get("path"),
            figure_number=ctx.figure_counter,
        )
        ctx.current_page_has_content = True


def _resolve_path(base_dir: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path.resolve()
    return (base_dir / path).resolve()
