"""Command-line entry point for otchet-compose.

Exposes the ``gen`` subcommand that loads a YAML config and delegates
document generation to :func:`~otchet_compose.generator.generate_document`.
"""

import argparse
from pathlib import Path

from .config import load_config
from .generator import generate_document
from .init import init_command


def gen_command(args) -> int:
    """Execute the ``gen`` subcommand.

    Loads the YAML config at *args.config* (defaults to
    ``otchet-compose.yml`` in the current directory) and calls
    :func:`~otchet_compose.generator.generate_document`.

    Returns 0 on success, 1 if an exception is caught by :func:`main`.
    """
    config_path = Path(args.config or "otchet-compose.yml").resolve()
    config = load_config(config_path)
    generate_document(config)
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build and return the root argument parser with all subcommands."""
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

    init_parser = subparsers.add_parser("init", help="Создать стартовую конфигурацию")
    init_parser.set_defaults(func=init_command)

    return parser


def main() -> int:
    """Parse CLI arguments and dispatch to the appropriate subcommand.

    Returns the integer exit code (0 = success, 1 = error).
    """
    parser = build_parser()
    args = parser.parse_args()

    try:
        return args.func(args)
    except Exception as e:
        print(f"Ошибка: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())