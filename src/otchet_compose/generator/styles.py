import json
from pathlib import Path

from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.shared import Cm, Pt

from .fields import set_font, set_paragraph_outline_level

_STYLES_JSON = Path(__file__).parent / "styles.json"

_ALIGNMENT = {
    "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
    "left": WD_ALIGN_PARAGRAPH.LEFT,
}

_LINE_SPACING_RULE = {
    "single": WD_LINE_SPACING.SINGLE,
    "one_point_five": WD_LINE_SPACING.ONE_POINT_FIVE,
}


def _parse_measurement(value: str):
    if value.endswith("cm"):
        return Cm(float(value[:-2]))
    if value.endswith("pt"):
        return Pt(float(value[:-2]))
    raise ValueError(f"Unrecognised measurement: {value!r} (expected e.g. '1.25cm' or '18pt')")


def _resolve_spec(raw: dict) -> dict:
    spec = {k: v for k, v in raw.items() if k != "para"}
    para = dict(raw["para"])
    para["alignment"] = _ALIGNMENT[para["alignment"]]
    para["line_spacing_rule"] = _LINE_SPACING_RULE[para["line_spacing_rule"]]
    para["first_line_indent"] = _parse_measurement(para["first_line_indent"])
    para["space_before"] = _parse_measurement(para["space_before"])
    para["space_after"] = _parse_measurement(para["space_after"])
    spec["para"] = para
    return spec


def _load_style_specs() -> list[dict]:
    with _STYLES_JSON.open("r", encoding="utf-8") as f:
        return [_resolve_spec(s) for s in json.load(f)]


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
    for spec in _load_style_specs():
        _apply_spec(doc, spec)
