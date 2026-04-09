"""GOST-style paragraph style loader.

Style definitions are loaded from ``styles.json`` using a two-location
lookup:

1. ``~/.otchet-compose/styles.json`` — user override (checked first).
2. The ``styles.json`` bundled alongside this module — default fallback.

This means the tool works out of the box with no setup, but a user can
drop their own ``styles.json`` into ``~/.otchet-compose/`` to fully
customise fonts, spacing, and Word UI priorities without touching the
package source.

The JSON format uses string measurements (``"1.25cm"``, ``"18pt"``) and
string enum keys (``"justify"``, ``"one_point_five"``); see the bundled
``styles.json`` for a complete annotated example.
"""

import json
from pathlib import Path

from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.shared import Cm, Pt

from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from .fields import OxmlHelper

_BUNDLED_STYLES_JSON = Path(__file__).parent / "styles.json"
_USER_STYLES_JSON = Path.home() / ".otchet-compose" / "styles.json"

_ALIGNMENT = {
    "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
    "left": WD_ALIGN_PARAGRAPH.LEFT,
    "right": WD_ALIGN_PARAGRAPH.RIGHT,
}

_LINE_SPACING_RULE = {
    "single": WD_LINE_SPACING.SINGLE,
    "one_point_five": WD_LINE_SPACING.ONE_POINT_FIVE,
}


def _parse_measurement(value: str):
    """Convert a string measurement like ``"1.25cm"`` or ``"18pt"`` to a python-docx unit."""
    if value.endswith("cm"):
        return Cm(float(value[:-2]))
    if value.endswith("pt"):
        return Pt(float(value[:-2]))
    raise ValueError(f"Unrecognised measurement: {value!r} (expected e.g. '1.25cm' or '18pt')")


def _resolve_spec(raw: dict) -> dict:
    """Resolve string-encoded values in a raw style spec to python-docx objects."""
    spec = {k: v for k, v in raw.items() if k != "para"}
    para = dict(raw["para"])
    para["alignment"] = _ALIGNMENT[para["alignment"]]
    para["line_spacing_rule"] = _LINE_SPACING_RULE[para["line_spacing_rule"]]
    para["first_line_indent"] = _parse_measurement(para["first_line_indent"])
    para["space_before"] = _parse_measurement(para["space_before"])
    para["space_after"] = _parse_measurement(para["space_after"])
    if "left_indent" in para:
        para["left_indent"] = _parse_measurement(para["left_indent"])
    if "right_indent" in para:
        para["right_indent"] = _parse_measurement(para["right_indent"])
    spec["para"] = para
    return spec


def _locate_styles_json() -> Path:
    """Return the styles JSON path to use.

    Prefers ``~/.otchet-compose/styles.json`` when it exists so users can
    override the bundled defaults without modifying the package.
    """
    if _USER_STYLES_JSON.exists():
        return _USER_STYLES_JSON
    return _BUNDLED_STYLES_JSON


def _load_style_specs() -> list[dict]:
    """Read the active ``styles.json`` and return a list of resolved style spec dicts."""
    with _locate_styles_json().open("r", encoding="utf-8") as f:
        return [_resolve_spec(s) for s in json.load(f)]


def _set_outline_level(style, level: int) -> None:
    """Set the ``w:outlineLvl`` XML attribute on *style*'s paragraph properties.

    Required for Word's built-in TOC to recognise custom styles as headings.
    *level* follows the OOXML convention: 0 = Heading 1, 1 = Heading 2, etc.
    """
    p_pr = style.element.get_or_add_pPr()
    outline = p_pr.find(qn("w:outlineLvl"))
    if outline is None:
        outline = OxmlElement("w:outlineLvl")
        p_pr.append(outline)
    outline.set(qn("w:val"), str(level))


def _get_or_create_style(doc, name: str, base: str):
    """Return the named style, creating it if it doesn't exist, and set its base style."""
    styles = doc.styles
    try:
        style = styles[name]
    except KeyError:
        style = styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
    style.base_style = styles[base]
    return style


def _expose_in_word_ui(style, priority: int) -> None:
    """Make *style* visible in Word's style gallery at the given *priority*."""
    style.hidden = False
    style.unhide_when_used = True
    style.quick_style = True
    style.locked = False
    style.priority = priority


def _apply_spec(doc, spec: dict) -> None:
    """Apply a single resolved style spec dict to *doc*."""
    name = spec["name"]
    style = (
        doc.styles["Normal"]
        if name == "Normal"
        else _get_or_create_style(doc, name, spec["base"])
    )

    if "priority" in spec:
        _expose_in_word_ui(style, spec["priority"])

    font_spec = spec["font"]
    OxmlHelper.set_font(
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
    pf.left_indent = para.get("left_indent", Cm(0))
    pf.right_indent = para.get("right_indent", Cm(0))
    pf.space_before = para["space_before"]
    pf.space_after = para["space_after"]
    pf.line_spacing = para["line_spacing"]
    pf.line_spacing_rule = para["line_spacing_rule"]
    if "keep_with_next" in para:
        pf.keep_with_next = para["keep_with_next"]

    if "outline_level" in spec:
        _set_outline_level(style, spec["outline_level"])


def setup_styles(doc) -> None:
    """Load ``styles.json`` and apply every style spec to *doc*."""
    for spec in _load_style_specs():
        _apply_spec(doc, spec)
