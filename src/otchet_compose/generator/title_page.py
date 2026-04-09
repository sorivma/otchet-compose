"""Title page renderer.

Two template sources are supported, checked in this order:

1. **User .docx templates** — ``~/.otchet-compose/templates/<name>.docx``
   Placeholders inside the DOCX text use ``{{key}}`` syntax. The file is
   loaded with python-docx, all placeholders are substituted, and then the
   body content is prepended to the output document.

2. **Built-in programmatic templates** — defined in
   :mod:`~otchet_compose.generator.templates` as Python functions.
   They render directly with python-docx so no external file is required.

The lookup is identical to ``styles.json``: user files always win over
built-ins, allowing a user to shadow a built-in by placing a file with
the same name in ``~/.otchet-compose/templates/``.

Placeholder substitution
------------------------
``{{key}}`` tokens are replaced by the matching value in *params*.  A token
whose key is absent in *params* is left unchanged.  Tokens that span
multiple python-docx ``Run`` objects (Word can split a word into several
runs for internal reasons) are handled by collapsing the paragraph text
into the first run before substitution.
"""

import copy
import re
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn

from .templates import BUILTIN_TEMPLATES

_USER_TEMPLATES_DIR = Path.home() / ".otchet-compose" / "templates"

_PLACEHOLDER_RE = re.compile(r"\{\{([^}]+)\}\}")


def render_title_page(doc, name: str, params: dict) -> None:
    """Render the named title page template as the first content of *doc*.

    Args:
        doc: The python-docx ``Document`` being built.
        name: Template name (without ``.docx`` extension).
        params: Mapping of placeholder keys to replacement strings.

    Raises:
        ValueError: If no template with *name* is found in either location.
    """
    user_path = _USER_TEMPLATES_DIR / f"{name}.docx"

    if user_path.exists():
        _render_docx_template(doc, user_path, params)
    elif name in BUILTIN_TEMPLATES:
        BUILTIN_TEMPLATES[name](doc, params)
    else:
        _raise_not_found(name)


def list_available_templates() -> list[str]:
    """Return sorted names of all available templates (built-ins + user files)."""
    names = set(BUILTIN_TEMPLATES.keys())
    if _USER_TEMPLATES_DIR.exists():
        names.update(p.stem for p in _USER_TEMPLATES_DIR.glob("*.docx"))
    return sorted(names)


# ---------------------------------------------------------------------------
# User .docx template rendering
# ---------------------------------------------------------------------------

def _render_docx_template(doc, template_path: Path, params: dict) -> None:
    """Load *template_path*, substitute params, and prepend its body into *doc*."""
    tmpl = Document(str(template_path))
    _substitute_all(tmpl, params)
    _prepend_body(doc, tmpl)


def _substitute_all(tmpl_doc, params: dict) -> None:
    """Replace ``{{key}}`` in every paragraph of *tmpl_doc*, including tables."""
    for para in _iter_all_paragraphs(tmpl_doc):
        _substitute_paragraph(para, params)


def _iter_all_paragraphs(doc):
    """Yield every paragraph in *doc*, including paragraphs inside table cells."""
    yield from doc.paragraphs
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                yield from cell.paragraphs


def _substitute_paragraph(para, params: dict) -> None:
    """Substitute ``{{key}}`` tokens in *para*, handling cross-run splits.

    Word sometimes splits a token like ``{{name}}`` across several ``Run``
    objects.  To handle this correctly the method collapses all run text into
    the first run (preserving its character format), performs substitution,
    then clears the remaining runs.
    """
    full_text = "".join(run.text for run in para.runs)
    if "{{" not in full_text:
        return

    substituted = _PLACEHOLDER_RE.sub(
        lambda m: params.get(m.group(1).strip(), m.group(0)),
        full_text,
    )

    if para.runs:
        para.runs[0].text = substituted
        for run in para.runs[1:]:
            run.text = ""


def _prepend_body(doc, tmpl_doc) -> None:
    """Insert all non-sectPr body elements of *tmpl_doc* at the start of *doc*.

    Note: only the XML elements are copied; relationships (images, embedded
    objects) from the template document are *not* transferred.  For purely
    text-based title pages this is sufficient.
    """
    body = doc.element.body
    children = list(body)
    insert_before = children[0] if children else None

    for elem in tmpl_doc.element.body:
        if elem.tag == qn("w:sectPr"):
            continue  # do not import the template's section/page-break settings
        cloned = copy.deepcopy(elem)
        if insert_before is not None:
            body.insert(list(body).index(insert_before), cloned)
        else:
            body.append(cloned)


# ---------------------------------------------------------------------------
# Error helpers
# ---------------------------------------------------------------------------

def _raise_not_found(name: str) -> None:
    available = list_available_templates()
    hint = ", ".join(available) if available else "нет"
    raise ValueError(
        f"Шаблон титульного листа {name!r} не найден. "
        f"Доступные шаблоны: {hint}. "
        f"Чтобы использовать собственный шаблон, поместите "
        f"<name>.docx в {_USER_TEMPLATES_DIR}."
    )
