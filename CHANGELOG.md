# Changelog

All notable changes to Toulmini will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-11-27

### Added

- **Core MCP Server** with 4 sequential Toulmin tools:
  - `initiate_toulmin_sequence` - Phase 1: Extract DATA and construct CLAIM
  - `inject_logic_bridge` - Phase 2: Generate WARRANT and BACKING
  - `stress_test_argument` - Phase 3: Find REBUTTALS and assign QUALIFIER
  - `render_verdict` - Phase 4: Render final judgment
- **Pydantic Models** for all 7 Toulmin components with strict validation
- **Circuit Breakers** that terminate argument chains on weak logic
- **JSON-forcing Prompts** that prevent conversational hedging
- **Comprehensive Test Suite** covering happy paths and failure modes
- **CI/CD Pipeline** with pytest, ruff, mypy, and automated PyPI publishing
- **MCP Client Configurations** for Claude Code, Claude Desktop, Cursor, and Windsurf
- **Examples Directory** with complete JSON traces for "Would immortality be a curse?"

### Technical

- Python 3.10+ support
- Dependencies: `mcp[cli]>=1.0.0`, `pydantic>=2.0.0`
- Stderr-only logging (STDIO-safe for MCP servers)
- Full type hint coverage

[1.0.0]: https://github.com/Hmbown/Toulmini/releases/tag/v1.0.0
