"""Figure block handler.

Validates ``type: figure`` blocks and renders them as either an embedded
image (when ``path`` points to an existing file) or a bordered placeholder
table.  Each rendered figure increments
:attr:`~otchet_compose.generator.blocks._base.RenderContext.figure_counter`
so captions are numbered consecutively across the document.
"""

from pathlib import Path

from docx.enum.table import WD_ALIGN_VERTICAL, WD_ROW_HEIGHT_RULE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm

from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from ._base import RenderContext


class FigureHandler:
    """Handler for ``type: figure`` blocks."""

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
        """Append a figure (image or placeholder) and its numbered caption."""
        ctx.figure_counter += 1
        image_path = block.get("path")

        if image_path and Path(image_path).exists():
            paragraph = doc.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.add_run().add_picture(image_path, width=Cm(16))
        else:
            _add_placeholder(doc)

        _add_caption(doc, ctx.figure_counter, block["caption"])
        ctx.current_page_has_content = True


def _add_placeholder(doc) -> None:
    """Insert a 12 × 7 cm bordered table as a figure placeholder."""
    table = doc.add_table(rows=1, cols=1)
    table.autofit = False
    _set_table_borders(table)

    cell = table.cell(0, 0)
    cell.width = Cm(12)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    row = table.rows[0]
    row.height = Cm(7)
    row.height_rule = WD_ROW_HEIGHT_RULE.EXACTLY

    paragraph = cell.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.style = "GOST Figure Placeholder"
    paragraph.add_run("Изображение отсутствует")


def _set_table_borders(table) -> None:
    """Apply a thin black single-line border to all six sides of *table*."""
    tbl = table._tbl
    tbl_pr = tbl.tblPr
    borders = tbl_pr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for border_name in ("top", "left", "bottom", "right", "insideH", "insideV"):
        border = borders.find(qn(f"w:{border_name}"))
        if border is None:
            border = OxmlElement(f"w:{border_name}")
            borders.append(border)
        border.set(qn("w:val"), "single")
        border.set(qn("w:sz"), "8")
        border.set(qn("w:space"), "0")
        border.set(qn("w:color"), "000000")


def _add_caption(doc, figure_number: int, text: str) -> None:
    """Append a ``GOST Caption`` paragraph formatted as "Рисунок N – text"."""
    caption_text = f"Рисунок {figure_number} – {text.strip().rstrip('.')}"
    doc.add_paragraph(caption_text, style="GOST Caption")


def _resolve_path(base_dir: Path, raw_path: str) -> Path:
    """Resolve *raw_path* relative to *base_dir*; absolute paths are kept as-is."""
    path = Path(raw_path)
    if path.is_absolute():
        return path.resolve()
    return (base_dir / path).resolve()
