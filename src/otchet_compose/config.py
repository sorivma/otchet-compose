from pathlib import Path
import yaml


SUPPORTED_VERSION = 1
SUPPORTED_BLOCK_TYPES = {"heading", "paragraph", "figure"}
SUPPORTED_HEADING_LEVELS = {1, 2, 3}


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

    normalized_blocks = []

    for index, block in enumerate(content, start=1):
        normalized_blocks.append(_validate_block(block, index, base_dir))

    return normalized_blocks


def _validate_block(block: object, index: int, base_dir: Path) -> dict:
    if not isinstance(block, dict):
        raise ValueError(f"Блок content[{index}] должен быть объектом")

    block_type = block.get("type")
    if block_type not in SUPPORTED_BLOCK_TYPES:
        raise ValueError(
            f"Блок content[{index}] имеет неподдерживаемый type: {block_type!r}. "
            f"Допустимо: {', '.join(sorted(SUPPORTED_BLOCK_TYPES))}"
        )

    if block_type == "heading":
        return _validate_heading(block, index)

    if block_type == "paragraph":
        return _validate_paragraph(block, index)

    if block_type == "figure":
        return _validate_figure(block, index, base_dir)

    raise ValueError(f"Неизвестный тип блока в content[{index}]: {block_type!r}")


def _validate_heading(block: dict, index: int) -> dict:
    text = block.get("text")
    level = block.get("level")
    structural = block.get("structural")

    if not isinstance(text, str) or not text.strip():
        raise ValueError(
            f"content[{index}]: heading.text обязателен и должен быть строкой"
        )

    if level not in SUPPORTED_HEADING_LEVELS:
        raise ValueError(
            f"content[{index}]: heading.level должен быть одним из "
            f"{sorted(SUPPORTED_HEADING_LEVELS)}"
        )

    if not isinstance(structural, bool):
        raise ValueError(
            f"content[{index}]: heading.structural должен быть true/false"
        )

    return {
        "type": "heading",
        "text": text.strip(),
        "level": level,
        "structural": structural,
    }


def _validate_paragraph(block: dict, index: int) -> dict:
    text = block.get("text")

    if not isinstance(text, str) or not text.strip():
        raise ValueError(
            f"content[{index}]: paragraph.text обязателен и должен быть строкой"
        )

    return {
        "type": "paragraph",
        "text": text.strip(),
    }


def _validate_figure(block: dict, index: int, base_dir: Path) -> dict:
    caption = block.get("caption")
    path = block.get("path")

    if not isinstance(caption, str) or not caption.strip():
        raise ValueError(
            f"content[{index}]: figure.caption обязателен и должен быть строкой"
        )

    normalized_path = None
    if path is not None:
        if not isinstance(path, str) or not path.strip():
            raise ValueError(
                f"content[{index}]: figure.path должен быть непустой строкой, если указан"
            )
        normalized_path = str(_resolve_path(base_dir, path))

    return {
        "type": "figure",
        "caption": caption.strip(),
        "path": normalized_path,
    }


def _resolve_path(base_dir: Path, raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path.resolve()
    return (base_dir / path).resolve()