"""Command-line entry point for otchet-compose.

Exposes the ``gen`` subcommand that loads a YAML config and delegates
document generation to :func:`~otchet_compose.generator.generate_document`.
"""

import argparse
import sys
from pathlib import Path

import yaml

from .cli_output import error_payload, print_json, success_payload
from .config import load_config
from .generator import generate_document
from .generator.blocks import REGISTRY
from .generator.title_page import describe_templates
from .init import create_config, init_command
from .manifest import write_manifest
from .schemas import load_schema


class MachineArgumentParser(argparse.ArgumentParser):
    """Argument parser that preserves the JSON contract for syntax errors."""

    def error(self, message: str) -> None:
        if "--json" in sys.argv[1:]:
            command = next((arg for arg in sys.argv[1:] if not arg.startswith("-")), "cli")
            print_json(error_payload(command, "invalid_arguments", message), error=True)
            self.exit(2)
        super().error(message)


def gen_command(args) -> int:
    """Execute the ``gen`` subcommand.

    Loads the YAML config at *args.config* (defaults to
    ``otchet-compose.yml`` in the current directory) and calls
    :func:`~otchet_compose.generator.generate_document`.

    Returns 0 on success, 1 if an exception is caught by :func:`main`.
    """
    config_path = Path(args.config or "otchet-compose.yml").resolve()
    config = load_config(config_path)
    config_warnings = _config_warnings(config)
    planned_output = Path(config["document"]["output"])
    _check_output(planned_output, args.output_root, args.force)
    if args.manifest:
        _check_output(Path(args.manifest), args.output_root, args.force)
    if args.dry_run:
        if args.json:
            print_json(
                success_payload(
                    "gen",
                    outputs=[planned_output],
                    data={"config": str(config_path), "dry_run": True},
                    warnings=config_warnings,
                )
            )
        else:
            print(f"Dry run successful. Planned output: {planned_output}")
            for warning in config_warnings:
                print(f"Предупреждение: {warning['message']}", file=sys.stderr)
        return 0

    warnings: list[str] | None = [warning["message"] for warning in config_warnings] if args.json else None
    if not args.json:
        for warning in config_warnings:
            print(f"Предупреждение: {warning['message']}", file=sys.stderr)
    output = generate_document(config, quiet=args.json, warnings=warnings)
    manifest = None
    if args.manifest:
        manifest_inputs = [config_path]
        manifest_inputs.extend(
            block["path"]
            for block in config["content"]
            if block["type"] == "figure" and block.get("path") and Path(block["path"]).is_file()
        )
        manifest = write_manifest(args.manifest, command="otchet-compose gen", inputs=manifest_inputs, outputs=[output])
    if args.json:
        print_json(
            success_payload(
                "gen",
                outputs=[output, *([manifest] if manifest else [])],
                data={"config": str(config_path), "manifest": str(manifest) if manifest else None},
                warnings=[
                    {
                        "code": "missing_figure" if message.startswith("Figure image is missing:") else "generation_warning",
                        "message": message,
                    }
                    for message in warnings or []
                ],
            )
        )
    return 0


def validate_command(args) -> int:
    """Validate and normalize a config without generating a document."""
    config_path = Path(args.config or "otchet-compose.yml").resolve()
    config = load_config(config_path)
    warnings = _config_warnings(config)
    output = config["document"]["output"]
    if args.json:
        print_json(
            success_payload(
                "validate",
                data={
                    "config": str(config_path),
                    "document_output": output,
                    "block_count": len(config["content"]),
                },
                warnings=warnings,
            )
        )
    else:
        print(f"Конфигурация корректна: {config_path}")
        print(f"Выходной файл: {output}")
        print(f"Блоков содержимого: {len(config['content'])}")
        for warning in warnings:
            print(f"Предупреждение: {warning['message']}", file=sys.stderr)
    return 0


def schema_command(args) -> int:
    """Print the bundled JSON Schema for a config version."""
    schema = load_schema(args.version)
    if args.json:
        print_json(success_payload("schema", data={"schema": schema, "version": args.version}))
    else:
        print_json(schema)
    return 0


def inspect_command(args) -> int:
    """Describe installed capabilities for agents and integrations."""
    data = {
        "config_version": 1,
        "block_types": sorted(REGISTRY),
        "templates": describe_templates(),
    }
    if args.json:
        print_json(success_payload("inspect", data=data))
    else:
        print(f"Config version: {data['config_version']}")
        print(f"Block types: {', '.join(data['block_types'])}")
        print(f"Templates: {', '.join(template['name'] for template in data['templates'])}")
    return 0


def init_dispatch_command(args) -> int:
    """Run interactive init or create a config from explicit arguments."""
    if not args.non_interactive:
        return init_command(args)
    params = {}
    for item in args.param:
        if "=" not in item:
            raise ValueError(f"--param must use KEY=VALUE format: {item}")
        key, value = item.split("=", 1)
        if not key:
            raise ValueError(f"--param key must not be empty: {item}")
        params[key] = value
    path = Path(args.config or "otchet-compose.yml").resolve()
    _check_output(path, args.output_root, args.force)
    output = create_config(
        path,
        document_output=args.document_output,
        toc=args.toc,
        template=args.template,
        params=params,
        reserve_title_page=args.reserve_title_page,
        force=args.force,
    )
    if args.json:
        print_json(success_payload("init", outputs=[output], data={"config": str(output), "non_interactive": True}))
    else:
        print(f"Конфигурация сохранена: {output}")
    return 0


def _add_config_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-f",
        "--config",
        default=None,
        help="Путь к YAML-конфигурации (по умолчанию: otchet-compose.yml)",
    )


def _add_json_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="Вывести стабильный JSON-ответ")


def _add_write_safety_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--dry-run", action="store_true", help="Проверить генерацию без записи файла")
    parser.add_argument("--force", action="store_true", help="Разрешить перезапись существующего файла")
    parser.add_argument("--output-root", help="Запретить запись за пределами указанной директории")
    parser.add_argument("--manifest", help="Записать SHA-256 manifest после успешной генерации")


def _check_output(output: Path, output_root: str | None, force: bool) -> None:
    output = output.resolve()
    if output_root:
        root = Path(output_root).resolve()
        if not output.is_relative_to(root):
            raise ValueError(f"Output path is outside --output-root: {output}")
    if output.exists() and not force:
        raise FileExistsError(f"Output already exists; use --force to overwrite: {output}")


def _config_warnings(config: dict) -> list[dict[str, str]]:
    warnings = []
    for block in config["content"]:
        if block["type"] == "figure" and block.get("path") and not Path(block["path"]).is_file():
            warnings.append({"code": "missing_figure", "message": f"Figure image is missing: {block['path']}"})
    return warnings


def build_parser() -> argparse.ArgumentParser:
    """Build and return the root argument parser with all subcommands."""
    parser = MachineArgumentParser(
        prog="otchet-compose",
        description="Генератор отчётов по лабораторным работам в формате DOCX",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen_parser = subparsers.add_parser("gen", help="Сгенерировать отчёт")
    _add_config_argument(gen_parser)
    _add_json_argument(gen_parser)
    _add_write_safety_arguments(gen_parser)
    gen_parser.set_defaults(func=gen_command)

    validate_parser = subparsers.add_parser("validate", help="Проверить YAML-конфигурацию")
    _add_config_argument(validate_parser)
    _add_json_argument(validate_parser)
    validate_parser.set_defaults(func=validate_command)

    schema_parser = subparsers.add_parser("schema", help="Вывести JSON Schema конфигурации")
    schema_parser.add_argument("--version", type=int, default=1, help="Версия схемы")
    _add_json_argument(schema_parser)
    schema_parser.set_defaults(func=schema_command)

    inspect_parser = subparsers.add_parser("inspect", help="Показать возможности установленного пакета")
    _add_json_argument(inspect_parser)
    inspect_parser.set_defaults(func=inspect_command)

    init_parser = subparsers.add_parser("init", help="Создать стартовую конфигурацию")
    init_parser.add_argument("--non-interactive", action="store_true", help="Создать конфигурацию без вопросов")
    _add_config_argument(init_parser)
    init_parser.add_argument("--document-output", default="./build/report.docx")
    init_parser.add_argument("--template")
    init_parser.add_argument("--param", action="append", default=[], help="Параметр шаблона KEY=VALUE")
    init_parser.add_argument("--reserve-title-page", action="store_true")
    init_parser.add_argument("--toc", action=argparse.BooleanOptionalAction, default=True)
    init_parser.add_argument("--force", action="store_true")
    init_parser.add_argument("--output-root")
    _add_json_argument(init_parser)
    init_parser.set_defaults(func=init_dispatch_command)

    return parser


def main() -> int:
    """Parse CLI arguments and dispatch to the appropriate subcommand.

    Returns the integer exit code (0 = success, 1 = error).
    """
    parser = build_parser()
    args = parser.parse_args()

    try:
        return args.func(args)
    except (FileNotFoundError, FileExistsError, ValueError, yaml.YAMLError) as exc:
        if getattr(args, "json", False):
            print_json(error_payload(args.command, "invalid_input", str(exc)), error=True)
        else:
            print(f"Ошибка: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        if getattr(args, "json", False):
            print_json(error_payload(args.command, "internal_error", str(exc)), error=True)
        else:
            print(f"Ошибка: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
