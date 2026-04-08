"""Shared OOXML helpers used across multiple generator modules.

Only two utilities genuinely cross module boundaries and live here:
- :meth:`OxmlHelper.add_field_run` — used by ``build.py`` (TOC) and ``page.py`` (footer)
- :meth:`OxmlHelper.set_font` — used by ``styles.py`` and ``page.py``

Single-consumer helpers (outline level, table borders) live in the
modules that own them.
"""

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor


class OxmlHelper:
    """Static helpers for direct OOXML element manipulation."""

    @staticmethod
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

    @staticmethod
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
