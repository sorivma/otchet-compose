from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.shared import Cm, Pt

from .fields import set_font, set_paragraph_outline_level

_S = WD_LINE_SPACING.SINGLE
_15 = WD_LINE_SPACING.ONE_POINT_FIVE
_J = WD_ALIGN_PARAGRAPH.JUSTIFY
_C = WD_ALIGN_PARAGRAPH.CENTER
_L = WD_ALIGN_PARAGRAPH.LEFT

# Each entry drives one paragraph style. Keys:
#   name, base, priority  – style identity / Word UI visibility
#   font                  – passed to set_font()
#   para                  – paragraph format fields
#   outline_level         – optional, for TOC heading levels
_STYLE_SPECS = [
    {
        "name": "Normal",
        "font": {"size": 14, "bold": False, "italic": False, "underline": False},
        "para": {
            "alignment": _J,
            "first_line_indent": Cm(1.25),
            "space_before": Pt(0),
            "space_after": Pt(0),
            "line_spacing": 1.5,
            "line_spacing_rule": _15,
        },
    },
    {
        "name": "GOST Body Text",
        "base": "Normal",
        "priority": 1,
        "font": {"size": 14, "bold": False, "italic": False, "underline": False},
        "para": {
            "alignment": _J,
            "first_line_indent": Cm(1.25),
            "space_before": Pt(0),
            "space_after": Pt(0),
            "line_spacing": 1.5,
            "line_spacing_rule": _15,
        },
    },
    {
        "name": "GOST Service",
        "base": "Normal",
        "priority": 90,
        "font": {"size": 14, "bold": False, "italic": False, "underline": False},
        "para": {
            "alignment": _L,
            "first_line_indent": Cm(0),
            "space_before": Pt(0),
            "space_after": Pt(0),
            "line_spacing": 1.5,
            "line_spacing_rule": _15,
        },
    },
    {
        "name": "GOST Heading 1",
        "base": "Normal",
        "priority": 2,
        "font": {"size": 14, "bold": True, "italic": False, "underline": False},
        "para": {
            "alignment": _C,
            "first_line_indent": Cm(0),
            "space_before": Pt(0),
            "space_after": Pt(18),
            "line_spacing": 1.5,
            "line_spacing_rule": _15,
            "keep_with_next": True,
        },
        "outline_level": 0,
    },
    {
        "name": "GOST Heading 2",
        "base": "Normal",
        "priority": 3,
        "font": {"size": 14, "bold": True, "italic": False, "underline": False},
        "para": {
            "alignment": _J,
            "first_line_indent": Cm(1.25),
            "space_before": Pt(18),
            "space_after": Pt(6),
            "line_spacing": 1.5,
            "line_spacing_rule": _15,
            "keep_with_next": True,
        },
        "outline_level": 1,
    },
    {
        "name": "GOST Heading 3",
        "base": "Normal",
        "priority": 4,
        "font": {"size": 14, "bold": True, "italic": False, "underline": False},
        "para": {
            "alignment": _J,
            "first_line_indent": Cm(1.25),
            "space_before": Pt(12),
            "space_after": Pt(6),
            "line_spacing": 1.5,
            "line_spacing_rule": _15,
            "keep_with_next": True,
        },
        "outline_level": 2,
    },
    {
        "name": "GOST TOC Title",
        "base": "Normal",
        "priority": 5,
        "font": {"size": 14, "bold": True, "italic": False, "underline": False},
        "para": {
            "alignment": _C,
            "first_line_indent": Cm(0),
            "space_before": Pt(0),
            "space_after": Pt(12),
            "line_spacing": 1.5,
            "line_spacing_rule": _15,
        },
    },
    {
        "name": "GOST Caption",
        "base": "Normal",
        "priority": 6,
        "font": {"size": 14, "bold": False, "italic": False, "underline": False},
        "para": {
            "alignment": _C,
            "first_line_indent": Cm(0),
            "space_before": Pt(6),
            "space_after": Pt(6),
            "line_spacing": 1.0,
            "line_spacing_rule": _S,
        },
    },
    {
        "name": "GOST Figure Placeholder",
        "base": "Normal",
        "priority": 7,
        "font": {"size": 12, "bold": False, "italic": True, "underline": False},
        "para": {
            "alignment": _C,
            "first_line_indent": Cm(0),
            "space_before": Pt(0),
            "space_after": Pt(0),
            "line_spacing": 1.0,
            "line_spacing_rule": _S,
        },
    },
]


def _get_or_create_style(doc, name: str, base: str):
    styles = doc.styles
    try:
        style = styles[name]
    except KeyError:
        style = styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
    style.base_style = styles[base]
    return style


def _expose_in_word_ui(style, priority: int) -> None:
    style.hidden = False
    style.unhide_when_used = True
    style.quick_style = True
    style.locked = False
    style.priority = priority


def _apply_spec(doc, spec: dict) -> None:
    name = spec["name"]
    style = (
        doc.styles["Normal"]
        if name == "Normal"
        else _get_or_create_style(doc, name, spec["base"])
    )

    if "priority" in spec:
        _expose_in_word_ui(style, spec["priority"])

    font_spec = spec["font"]
    set_font(
        style,
        name="Times New Roman",
        size=font_spec["size"],
        bold=font_spec["bold"],
        italic=font_spec["italic"],
        underline=font_spec["underline"],
    )

    pf = style.paragraph_format
    para = spec["para"]
    pf.alignment = para["alignment"]
    pf.first_line_indent = para["first_line_indent"]
    pf.left_indent = Cm(0)
    pf.right_indent = Cm(0)
    pf.space_before = para["space_before"]
    pf.space_after = para["space_after"]
    pf.line_spacing = para["line_spacing"]
    pf.line_spacing_rule = para["line_spacing_rule"]
    if "keep_with_next" in para:
        pf.keep_with_next = para["keep_with_next"]

    if "outline_level" in spec:
        set_paragraph_outline_level(style, spec["outline_level"])


def setup_styles(doc) -> None:
    for spec in _STYLE_SPECS:
        _apply_spec(doc, spec)
