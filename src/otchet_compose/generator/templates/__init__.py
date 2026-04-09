"""Built-in programmatic title page templates.

Each entry in ``BUILTIN_TEMPLATES`` is a callable with signature::

    fn(doc: Document, params: dict) -> None

It renders a title page directly into *doc* using python-docx primitives,
so no external file is needed and no styles from a foreign DOCX are imported.

To add a new built-in template:
1. Create ``<name>.py`` in this package and implement the render function.
2. Add one entry to ``BUILTIN_TEMPLATES`` below.
"""

from .mirea import render as _mirea

BUILTIN_TEMPLATES: dict = {
    "mirea": _mirea,
}
