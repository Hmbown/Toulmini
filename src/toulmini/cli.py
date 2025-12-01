"""Integrated Toulmini CLI for installation, verification, and config inspection."""

from __future__ import annotations

import argparse
import asyncio
import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, Tuple

from .config import Config, get_config
from .mcp_setup import (
    _write_config,
    generate_config,
    get_project_root,
    get_python_path,
    is_installed_in_site_packages,
    print_setup_instructions,
)
from .server import mcp

_DEFAULT_INSTALL_TARGET = "mcp_config.json"
_EXPECTED_TOOLS = {
    "consult_field_experts",
    "initiate_toulmin_sequence",
    "inject_logic_bridge",
    "stress_test_argument",
    "render_verdict",
    "format_analysis_report",
}


def _render_config(config: Config) -> str:
    payload = asdict(config)
    payload["_initial_env"] = dict(config._initial_env)
    return json.dumps(payload, indent=2)


def _verify_environment() -> Tuple[bool, Iterable[Tuple[bool, str]]]:
    messages: list[Tuple[bool, str]] = []
    ok = True

    try:
        config = get_config()
        messages.append((True, f"Config loaded (log_level={config.log_level})"))
    except Exception as exc:  # pragma: no cover - defensive
        ok = False
        messages.append((False, f"Config error: {exc}"))

    try:
        tools = asyncio.run(mcp.list_tools())
        tool_names = {tool.name for tool in tools}
        missing = sorted(_EXPECTED_TOOLS - tool_names)
        if missing:
            ok = False
            messages.append((False, f"Server missing tools: {', '.join(missing)}"))
        else:
            messages.append((True, f"Server registered {len(tool_names)} tools"))
    except Exception as exc:  # pragma: no cover - defensive
        ok = False
        messages.append((False, f"Server error: {exc}"))

    try:
        python_path = get_python_path()
        is_installed = is_installed_in_site_packages()
        project_root = get_project_root()
        config_dict = generate_config(python_path, project_root, is_installed)
        json.dumps(config_dict)
        status = "installed" if is_installed else f"source ({project_root})"
        messages.append((True, f"MCP config ready via {status}"))
    except Exception as exc:  # pragma: no cover - defensive
        ok = False
        messages.append((False, f"MCP config error: {exc}"))

    return ok, messages


def _handle_install(target: str | None) -> None:
    python_path = get_python_path()
    is_installed = is_installed_in_site_packages()
    project_root = get_project_root()
    config = generate_config(python_path, project_root, is_installed)
    snippet = config["mcpServers"]

    if target == "-":
        print_setup_instructions(dry_run=False)
    else:
        destination = Path(target or _DEFAULT_INSTALL_TARGET)
        _write_config(destination, snippet)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Toulmini CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--config",
        action="store_true",
        help="Print the current Toulmini configuration as JSON",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run environment verification checks",
    )
    parser.add_argument(
        "--install",
        nargs="?",
        const=_DEFAULT_INSTALL_TARGET,
        metavar="PATH|-",
        help="Write MCP config to PATH (use '-' to print instructions)",
    )

    args = parser.parse_args(argv)
    ran_action = False
    exit_code = 0

    if args.config:
        ran_action = True
        print(_render_config(get_config()))

    if args.verify:
        ran_action = True
        ok, messages = _verify_environment()
        for success, message in messages:
            icon = "✅" if success else "❌"
            print(f"{icon} {message}")
        if ok:
            print("All verification checks passed.")
        else:
            print("Verification failed.")
            exit_code = 1

    if args.install is not None:
        ran_action = True
        _handle_install(args.install)

    if not ran_action:
        parser.print_help()

    return exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
