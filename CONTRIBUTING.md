# Contributing to Toulmini

Thank you for your interest in contributing to Toulmini! This document provides guidelines and instructions for contributing.

## Development Setup

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/Hmbown/Toulmini.git
cd Toulmini

# Install in development mode
pip install -e ".[dev]"

# Or with uv
uv pip install -e ".[dev]"
```

### Running Tests

```bash
PYTHONPATH=src pytest
```

### Code Quality

We use `ruff` for linting and formatting, and `mypy` for type checking:

```bash
# Linting
ruff check src tests

# Formatting
ruff format src tests

# Type checking
mypy src
```

## Making Contributions

### Reporting Issues

- Check existing issues before creating a new one
- Use clear, descriptive titles
- Include steps to reproduce for bugs
- Include Python version and OS information

### Pull Requests

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following the code style guidelines
4. **Write tests** for new functionality
5. **Run the test suite** to ensure nothing is broken
6. **Commit** with a clear message:
   ```bash
   git commit -m "Add: brief description of change"
   ```
7. **Push** and create a Pull Request

### Commit Message Format

Use descriptive commit messages:
- `Add:` for new features
- `Fix:` for bug fixes
- `Update:` for enhancements to existing features
- `Refactor:` for code restructuring
- `Docs:` for documentation changes
- `Test:` for test additions/changes

### Code Style

- Follow PEP 8 guidelines (enforced by ruff)
- Use type hints for all function signatures
- Write docstrings for public functions and classes
- Keep functions focused and single-purpose

### Architecture Guidelines

Toulmini follows strict design principles:

1. **Sequential Dependencies**: Each phase requires prior phases to complete
2. **Strict Validation**: All components use Pydantic models with validation
3. **No External APIs**: The MCP server makes no network calls
4. **JSON-Only Output**: Prompts enforce structured JSON responses
5. **Stderr Logging**: Never pollute stdout (required for STDIO MCP)

When adding features, ensure they maintain these constraints.

## Questions?

Open an issue or start a discussion on GitHub.
