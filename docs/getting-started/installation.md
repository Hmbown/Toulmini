# Installation

## Requirements

- Python 3.10 or higher
- pip or [uv](https://docs.astral.sh/uv/)

## Install from PyPI

The simplest way to install Toulmini:

```bash
pip install toulmini
```

Or with uv:

```bash
uv pip install toulmini
```

## Install from Source

For development or to get the latest changes:

```bash
# Clone the repository
git clone https://github.com/Hmbown/Toulmini.git
cd Toulmini

# Install in development mode
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"
```

## Verify Installation

Check that Toulmini is installed correctly:

```bash
# Check the package is installed
pip show toulmini

# Run the verification script
python verify_toulmini.py
```

The verification script tests that all 4 MCP tools are registered correctly.

## Dependencies

Toulmini has minimal dependencies:

| Package | Version | Purpose |
|---------|---------|---------|
| `mcp[cli]` | >=1.0.0 | MCP server framework |
| `pydantic` | >=2.0.0 | Data validation and schemas |

### Development Dependencies

For contributing to Toulmini:

| Package | Purpose |
|---------|---------|
| `pytest` | Testing |
| `ruff` | Linting and formatting |
| `mypy` | Type checking |

## Next Steps

After installation, [configure your MCP client](configuration.md) to connect to Toulmini.
