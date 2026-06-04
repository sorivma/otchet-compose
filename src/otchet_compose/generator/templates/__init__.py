"""Bundled title page templates directory.

All ``.docx`` files in this directory are shipped with the tool and are
available by their stem name (e.g. ``mirea.docx`` → template name ``mirea``).

Users can override any bundled template — or add new ones — by placing a
``.docx`` file with the same name in ``~/.otchet-compose/templates/``.
"""

from pathlib import Path

BUNDLED_TEMPLATES_DIR: Path = Path(__file__).parent
