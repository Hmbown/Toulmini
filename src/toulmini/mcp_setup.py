"""Shared MCP setup helpers for Toulmini CLI and scripts."""

from __future__ import annotations

import json
import site
import sys
from pathlib import Path
from typing import Dict


USAGE_NOTE = """
Toulmini MCP setup
------------------
Use this helper to generate the MCP snippet for Cursor / Claude Desktop.

Examples:
  toulmini-setup-mcp                # print JSON snippet
  toulmini-setup-mcp --write        # write to ./mcp_config.json
  toulmini-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"  # macOS Claude Desktop

Common config paths:
  macOS Claude Desktop: ~/Library/Application Support/Claude/claude_desktop_config.json
  Cursor:               ~/.cursor/mcp_config.json
  Windsurf:             ~/.codeium/windsurf/mcp_config.json

Note: After modifying the config, quit and reopen Claude Desktop for changes to take effect.
"""


def _package_dir() -> Path:
    return Path(__file__).resolve().parent


def get_python_path() -> str:
    """Return the current Python executable path."""

    return sys.executable


def is_installed_in_site_packages() -> bool:
    """Detect whether Toulmini is installed from site-packages."""

    package_path = _package_dir()

    site_packages = []
    try:
        site_packages = site.getsitepackages()  # type: ignore[attr-defined]
    except AttributeError:
        pass

    for site_package in site_packages:
        if site_package and str(package_path).startswith(site_package):
            return True

    try:
        user_site = site.getusersitepackages()
    except AttributeError:
        user_site = None

    if user_site and str(package_path).startswith(user_site):
        return True

    return False


def get_project_root() -> Path:
    """Best-effort detection of the project root.

    For editable/source installs, this resolves to the repository root.
    For regular pip installs, this falls back to the package directory.
    """

    package_dir = _package_dir()

    candidates = [package_dir.parent.parent, package_dir.parent]
    for candidate in candidates:
        if candidate and (candidate / "pyproject.toml").exists():
            return candidate

    return package_dir


def generate_config(
    python_path: str, project_root: Path, is_installed: bool
) -> Dict[str, dict]:
    """Generate the MCP config dictionary."""

    env: Dict[str, str] = {}

    if not is_installed:
        env["PYTHONPATH"] = str(project_root)

    config = {
        "mcpServers": {
            "toulmini": {
                "command": python_path,
                "args": ["-m", "toulmini.server"],
            }
        }
    }

    if env:
        config["mcpServers"]["toulmini"]["env"] = env

    return config


def print_setup_instructions(dry_run: bool = False) -> None:
    """Print human-readable instructions and JSON snippet."""

    python_path = get_python_path()
    is_installed = is_installed_in_site_packages()
    project_root = get_project_root()

    config = generate_config(python_path, project_root, is_installed)
    snippet = config["mcpServers"]
    json_output = json.dumps(snippet, indent=2)

    if dry_run:
        return

    print("\n" + "=" * 70)
    print("TOULMINI MCP CONFIGURATION SNIPPET")
    print("=" * 70)
    print("Copy the snippet below into your 'Global MCP Settings' (Cursor)")
    print("or your MCP configuration file:")
    print("-" * 70)
    print(json_output)
    print("-" * 70)

    print("\nTools available:")
    print("  - initiate_toulmin_sequence (Phase 1: DATA + CLAIM)")
    print("  - inject_logic_bridge (Phase 2: WARRANT + BACKING)")
    print("  - stress_test_argument (Phase 3: REBUTTAL + QUALIFIER)")
    print("  - render_verdict (Phase 4: VERDICT)")
    print("  - format_analysis_report (Phase 5: Markdown report)")
    print("  - consult_field_experts (Helper: Council of Experts)")

    print("\nCommon config paths:")
    print(
        "  macOS Claude Desktop: ~/Library/Application Support/Claude/claude_desktop_config.json"
    )
    print("  Cursor:               ~/.cursor/mcp_config.json")
    print("  Windsurf:             ~/.codeium/windsurf/mcp_config.json")

    print(
        "\n⚠️  Restart Required: Quit and reopen Claude Desktop after modifying the config."
    )

    if not is_installed:
        print(f"\nℹ️  NOTE: Detected source installation at {project_root}")
        print("   Added PYTHONPATH to ensure the server runs correctly.")
    else:
        print("\nℹ️  NOTE: Detected installed package.")

    print("\nFor automated setup, run:")
    print(
        '  toulmini-setup-mcp --write "$HOME/Library/Application Support/Claude/claude_desktop_config.json"'
    )


def _write_config(target: Path, snippet: dict) -> None:
    """Write MCP config to a given file."""

    target = target.expanduser().resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        try:
            existing = json.loads(target.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            print(
                f"⚠️  Warning: Existing config at {target} is invalid. Creating new file."
            )
            existing = {}

        merged = existing.get("mcpServers", {})
        merged.update(snippet)

        payload = {
            "mcpServers": merged,
            **{k: v for k, v in existing.items() if k != "mcpServers"},
        }
    else:
        payload = {"mcpServers": snippet}

    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"✅ Wrote MCP config to {target}")
    print("\n⚠️  Remember to restart Claude Desktop for changes to take effect!")


__all__ = [
    "USAGE_NOTE",
    "get_python_path",
    "is_installed_in_site_packages",
    "get_project_root",
    "generate_config",
    "print_setup_instructions",
    "_write_config",
]
