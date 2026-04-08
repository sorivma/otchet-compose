"""Low-level python-docx XML helpers.

Functions here operate directly on OOXML elements and are reused across
multiple generator modules.  They are intentionally free of any
document-structure knowledge — they only know how to manipulate the XML
primitives they receive.
"""

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor


def add_field_run(paragraph, instruction: str, placeholder: str = "", dirty: bool = False):
    """Insert a Word complex field into *paragraph*.

    Appends the standard ``begin → instrText → separate → [placeholder] → end``
    sequence of ``w:fldChar`` elements to a new run in the paragraph.

    Args:
        paragraph: The python-docx ``Paragraph`` to append to.
        instruction: The raw field instruction text (e.g. ``" PAGE "``).
        placeholder: Visible text shown before the field is updated in Word.
        dirty: When ``True`` sets ``w:dirty="true"`` so Word refreshes the
            field on next open.

    Returns:
        The new ``Run`` that contains the field XML.
    """
    """
    Вставляет complex field:
    begin -> instrText -> separate -> placeholder -> end
    """
    run = paragraph.add_run()

    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    if dirty:
        fld_begin.set(qn("w:dirty"), "true")
    run._r.append(fld_begin)

    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    run._r.append(instr)

    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    run._r.append(fld_sep)

    if placeholder:
        t = OxmlElement("w:t")
        t.text = placeholder
        run._r.append(t)

    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_end)

    return run


def set_paragraph_outline_level(style, level: int) -> None:
    """Set the ``w:outlineLvl`` XML attribute on *style*'s paragraph properties.

    This is required for Word's built-in TOC to recognise custom styles as
    headings.  *level* follows the OOXML convention: 0 = Heading 1, 1 = Heading 2, etc.
    """
    p_pr = style.element.get_or_add_pPr()
    outline = p_pr.find(qn("w:outlineLvl"))
    if outline is None:
        outline = OxmlElement("w:outlineLvl")
        p_pr.append(outline)
    outline.set(qn("w:val"), str(level))


def set_font(
    style_or_run,
    *,
    name: str = "Times New Roman",
    size: int = 14,
    bold=None,
    italic=None,
    underline=None,
    color=(0, 0, 0),
) -> None:
    """Apply font properties to a style or run, including East-Asian font slots.

    python-docx's ``font.name`` setter only fills ``w:ascii`` and ``w:hAnsi``;
    this helper also sets ``w:cs`` and ``w:eastAsia`` so Cyrillic characters
    render in Times New Roman instead of falling back to a default CJK font.

    Args:
        style_or_run: A python-docx ``_ParagraphStyle`` or ``Run`` object.
        name: Font family name.
        size: Font size in points.
        bold: ``True``/``False`` or ``None`` to leave unchanged.
        italic: ``True``/``False`` or ``None`` to leave unchanged.
        underline: ``True``/``False`` or ``None`` to leave unchanged.
        color: RGB triple ``(r, g, b)`` or ``None`` to leave unchanged.
    """
    font = style_or_run.font
    font.name = name

    r_pr = style_or_run._element.get_or_add_rPr()
    r_fonts = r_pr.rFonts
    if r_fonts is None:
        r_fonts = OxmlElement("w:rFonts")
        r_pr.append(r_fonts)

    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        r_fonts.set(qn(attr), name)

    font.size = Pt(size)

    if bold is not None:
        font.bold = bold
    if italic is not None:
        font.italic = italic
    if underline is not None:
        font.underline = underline
    if color is not None:
        font.color.rgb = RGBColor(*color)


def set_table_borders(table) -> None:
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