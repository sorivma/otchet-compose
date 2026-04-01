import argparse
from pathlib import Path

from .config import load_config
from .generator import generate_document


def gen_command(args) -> int:
    config_path = Path(args.config or "otchet-compose.yml").resolve()
    config = load_config(config_path)
    generate_document(config)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="otchet-compose",
        description="Генератор отчётов по лабораторным работам в формате DOCX",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen_parser = subparsers.add_parser("gen", help="Сгенерировать отчёт")
    gen_parser.add_argument(
        "-f",
        "--config",
        default=None,
        help="Путь к YAML-конфигурации (по умолчанию: otchet-compose.yml)",
    )
    gen_parser.set_defaults(func=gen_command)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        return args.func(args)
    except Exception as e:
        print(f"Ошибка: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())