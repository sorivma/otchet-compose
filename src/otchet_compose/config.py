from pathlib import Path
import yaml

from .generator.blocks import REGISTRY


SUPPORTED_VERSION = 1


def load_config(config_path: Path) -> dict:
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

    return {
        "output": str(output_path),
        "reserve_title_page": reserve_title_page,
        "toc": toc,
    }


def _validate_content(content: object, base_dir: Path) -> list[dict]:
    if not isinstance(content, list) or not content:
        raise ValueError("content обязателен и должен быть непустым списком")

    return [_validate_block(block, index, base_dir) for index, block in enumerate(content, start=1)]


def _validate_block(block: object, index: int, base_dir: Path) -> dict:
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
    path = Path(raw_path)
    if path.is_absolute():
        return path.resolve()
    return (base_dir / path).resolve()
