from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.shared import Cm, Pt

from .fields import set_font, set_paragraph_outline_level


def ensure_style(doc, name: str, style_type=WD_STYLE_TYPE.PARAGRAPH, base=None):
    styles = doc.styles
    try:
        style = styles[name]
    except KeyError:
        style = styles.add_style(name, style_type)

    if base is not None:
        style.base_style = styles[base]

    return style


def expose_style_in_word_ui(style, priority: int) -> None:
    """
    Делает стиль видимым в Word в списке пользовательских стилей.
    """
    style.hidden = False
    style.unhide_when_used = True
    style.quick_style = True
    style.locked = False
    style.priority = priority


def setup_styles(doc) -> None:
    normal = doc.styles["Normal"]
    set_font(
        normal,
        name="Times New Roman",
        size=14,
        bold=False,
        italic=False,
        underline=False,
    )
    pf = normal.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.first_line_indent = Cm(1.25)
    pf.left_indent = Cm(0)
    pf.right_indent = Cm(0)
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.5
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE

    body = ensure_style(doc, "GOST Body Text", base="Normal")
    expose_style_in_word_ui(body, priority=1)
    set_font(body, name="Times New Roman", size=14, bold=False, italic=False, underline=False)
    pf = body.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.first_line_indent = Cm(1.25)
    pf.left_indent = Cm(0)
    pf.right_indent = Cm(0)
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.5
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE

    service = ensure_style(doc, "GOST Service", base="Normal")
    expose_style_in_word_ui(service, priority=90)
    set_font(service, name="Times New Roman", size=14, bold=False, italic=False, underline=False)
    pf = service.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pf.first_line_indent = Cm(0)
    pf.left_indent = Cm(0)
    pf.right_indent = Cm(0)
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.5
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE

    h1 = ensure_style(doc, "GOST Heading 1", base="Normal")
    expose_style_in_word_ui(h1, priority=2)
    set_font(h1, name="Times New Roman", size=14, bold=True, italic=False, underline=False)
    pf = h1.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf.first_line_indent = Cm(0)
    pf.left_indent = Cm(0)
    pf.right_indent = Cm(0)
    pf.space_before = Pt(0)
    pf.space_after = Pt(18)
    pf.line_spacing = 1.5
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.keep_with_next = True
    set_paragraph_outline_level(h1, 0)

    h2 = ensure_style(doc, "GOST Heading 2", base="Normal")
    expose_style_in_word_ui(h2, priority=3)
    set_font(h2, name="Times New Roman", size=14, bold=True, italic=False, underline=False)
    pf = h2.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.first_line_indent = Cm(1.25)
    pf.left_indent = Cm(0)
    pf.right_indent = Cm(0)
    pf.space_before = Pt(18)
    pf.space_after = Pt(6)
    pf.line_spacing = 1.5
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.keep_with_next = True
    set_paragraph_outline_level(h2, 1)

    h3 = ensure_style(doc, "GOST Heading 3", base="Normal")
    expose_style_in_word_ui(h3, priority=4)
    set_font(h3, name="Times New Roman", size=14, bold=True, italic=False, underline=False)
    pf = h3.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    pf.first_line_indent = Cm(1.25)
    pf.left_indent = Cm(0)
    pf.right_indent = Cm(0)
    pf.space_before = Pt(12)
    pf.space_after = Pt(6)
    pf.line_spacing = 1.5
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.keep_with_next = True
    set_paragraph_outline_level(h3, 2)

    toc_title = ensure_style(doc, "GOST TOC Title", base="Normal")
    expose_style_in_word_ui(toc_title, priority=5)
    set_font(toc_title, name="Times New Roman", size=14, bold=True, italic=False, underline=False)
    pf = toc_title.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf.first_line_indent = Cm(0)
    pf.space_before = Pt(0)
    pf.space_after = Pt(12)
    pf.line_spacing = 1.5
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE

    caption = ensure_style(doc, "GOST Caption", base="Normal")
    expose_style_in_word_ui(caption, priority=6)
    set_font(caption, name="Times New Roman", size=14, bold=False, italic=False, underline=False)
    pf = caption.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf.first_line_indent = Cm(0)
    pf.space_before = Pt(6)
    pf.space_after = Pt(6)
    pf.line_spacing = 1.0
    pf.line_spacing_rule = WD_LINE_SPACING.SINGLE

    placeholder = ensure_style(doc, "GOST Figure Placeholder", base="Normal")
    expose_style_in_word_ui(placeholder, priority=7)
    set_font(placeholder, name="Times New Roman", size=12, bold=False, italic=True, underline=False)
    pf = placeholder.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pf.first_line_indent = Cm(0)
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.0
    pf.line_spacing_rule = WD_LINE_SPACING.SINGLE