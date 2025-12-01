"""Toulmini MCP Setup Logic and CLI helper."""

import sys
from pathlib import Path

try:
    import toulmini  # noqa: F401
except ImportError:
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))
    import toulmini  # type: ignore  # noqa: F401

from toulmini.mcp_setup import (
    USAGE_NOTE,
    _write_config,
    generate_config,
    get_project_root,
    get_python_path,
    is_installed_in_site_packages,
    print_setup_instructions,
)


def main(argv=None):  # pragma: no cover - lightweight CLI
    """Main entry point for the setup script."""

    import argparse

    parser = argparse.ArgumentParser(
        description="Generate MCP config for Toulmini",
        epilog=USAGE_NOTE,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--write",
        nargs="?",
        const="mcp_config.json",
        metavar="PATH",
        help="Write to path (default: mcp_config.json in CWD)",
    )
    args = parser.parse_args(argv)

    python_path = get_python_path()
    is_installed = is_installed_in_site_packages()
    project_root = get_project_root()
    config = generate_config(python_path, project_root, is_installed)
    snippet = config["mcpServers"]

    if args.write:
        _write_config(Path(args.write), snippet)
    else:
        print_setup_instructions()


if __name__ == "__main__":
    main()
