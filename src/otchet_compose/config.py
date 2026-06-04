"""YAML configuration loader and validator.

Reads an ``otchet-compose.yml`` file, validates its structure, and returns
a normalised plain :class:`dict` that the generator can consume without
any further YAML awareness.  All relative file paths are resolved to
absolute paths relative to the config file's parent directory.
"""

from pathlib import Path
import yaml

from .generator.blocks import REGISTRY


SUPPORTED_VERSION = 1


def load_config(config_path: Path) -> dict:
    """Load and validate a YAML config file, returning a normalised dict.

    The returned dict always contains the keys ``version``, ``document``,
    and ``content``.  All file paths inside the dict are absolute strings.

    Raises:
        FileNotFoundError: if *config_path* does not exist.
        ValueError: if the YAML structure violates the schema.
    """
    config_path = config_path.resolve()

    if not config_path.exists():
        raise FileNotFoundError(f"Файл конфигурации не найден: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    if not isinstance(raw, dict):
        raise ValueError("Корень YAML-конфигурации должен быть объектом")

    base_dir = config_path.parent

    version = raw.get("version")
    if version != SUPPORTED_VERSION:
        raise ValueError(
            f"Поддерживается только version: {SUPPORTED_VERSION}, получено: {version!r}"
        )

    document = _validate_document(raw.get("document"), base_dir)
    content = _validate_content(raw.get("content"), base_dir)

    return {
        "version": version,
        "document": document,
        "content": content,
    }


def _validate_document(document: object, base_dir: Path) -> dict:
    """Validate the ``document`` section and return a normalised dict."""
    if not isinstance(document, dict):
        raise ValueError("Секция document обязательна и должна быть объектом")

    output = document.get("output")
    if not isinstance(output, str) or not output.strip():
        raise ValueError("document.output обязателен и должен быть непустой строкой")

    reserve_title_page = document.get("reserve_title_page", False)
    if not isinstance(reserve_title_page, bool):
        raise ValueError("document.reserve_title_page должен быть true/false")

    toc = document.get("toc")
    if not isinstance(toc, bool):
        raise ValueError("document.toc обязателен и должен быть true/false")

    output_path = _resolve_path(base_dir, output)

    title_page = _validate_title_page(document.get("title_page"))

    return {
        "output": str(output_path),
        "reserve_title_page": reserve_title_page,
        "toc": toc,
        "title_page": title_page,
    }


def _validate_title_page(title_page: object) -> dict | None:
    """Validate the optional ``document.title_page`` subsection."""
    if title_page is None:
        return None

    if not isinstance(title_page, dict):
        raise ValueError("document.title_page должен быть объектом")

    template = title_page.get("template")
    if not isinstance(template, str) or not template.strip():
        raise ValueError(
            "document.title_page.template обязателен и должен быть непустой строкой"
        )

    params = title_page.get("params", {})
    if not isinstance(params, dict):
        raise ValueError("document.title_page.params должен быть объектом (ключ: значение)")

    return {
        "template": template.strip(),
        "params": {str(k): str(v) for k, v in params.items()},
    }


def _validate_content(content: object, base_dir: Path) -> list[dict]:
    """Validate the ``content`` list and return a list of normalised block dicts."""
    if not isinstance(content, list) or not content:
        raise ValueError("content обязателен и должен быть непустым списком")

    return [_validate_block(block, index, base_dir) for index, block in enumerate(content, start=1)]


def _validate_block(block: object, index: int, base_dir: Path) -> dict:
    """Dispatch a single raw block to the appropriate handler's ``validate``."""
    if not isinstance(block, dict):
        raise ValueError(f"Блок content[{index}] должен быть объектом")

    block_type = block.get("type")
    if block_type not in REGISTRY:
        raise ValueError(
            f"Блок content[{index}] имеет неподдерживаемый type: {block_type!r}. "
            f"Допустимо: {', '.join(sorted(REGISTRY))}"
        )

    return REGISTRY[block_type].validate(block, index, base_dir)


def _resolve_path(base_dir: Path, raw_path: str) -> Path:
    """Resolve *raw_path* relative to *base_dir*; absolute paths are kept as-is."""
    path = Path(raw_path)
    if path.is_absolute():
        return path.resolve()
    return (base_dir / path).resolve()
