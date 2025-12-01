"""Tests for MCP setup script."""

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import from scripts directory
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from setup_mcp import (
    generate_config,
    get_project_root,
    get_python_path,
    is_installed_in_site_packages,
    print_setup_instructions,
    _write_config,
)


# === Fixtures ===


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary config file path."""
    return tmp_path / "test_config.json"


@pytest.fixture
def sample_existing_config():
    """Sample existing MCP config for merge testing."""
    return {
        "mcpServers": {
            "existing-server": {
                "command": "python",
                "args": ["-m", "existing.server"],
            }
        },
        "otherSetting": "preserved",
    }


# === Basic Functionality Tests ===


def test_get_python_path():
    """Test that get_python_path returns current Python executable."""
    python_path = get_python_path()

    assert python_path == sys.executable
    assert Path(python_path).exists()
    assert Path(python_path).is_file()


def test_get_project_root():
    """Test that get_project_root returns correct path."""
    project_root = get_project_root()

    assert isinstance(project_root, Path)
    assert project_root.exists()
    assert project_root.is_dir()
    # Should contain pyproject.toml
    assert (project_root / "pyproject.toml").exists()


def test_is_installed_in_site_packages():
    """Test site-packages detection."""
    result = is_installed_in_site_packages()

    # Should be a boolean
    assert isinstance(result, bool)

    # In development (running from source), should be False
    # In CI or installed package, should be True
    # We can't assert a specific value as it depends on test environment


# === Config Generation Tests ===


def test_generate_config_installed_package():
    """Test config generation for installed package (no PYTHONPATH needed)."""
    python_path = "/usr/bin/python3"
    project_root = Path("/dummy/project/root")
    is_installed = True

    config = generate_config(python_path, project_root, is_installed)

    assert "mcpServers" in config
    assert "toulmini" in config["mcpServers"]

    toulmini_config = config["mcpServers"]["toulmini"]
    assert toulmini_config["command"] == python_path
    assert toulmini_config["args"] == ["-m", "toulmini.server"]

    # Should NOT have env for installed packages
    assert "env" not in toulmini_config


def test_generate_config_source_installation():
    """Test config generation for source installation (PYTHONPATH needed)."""
    python_path = "/usr/bin/python3"
    project_root = Path("/home/user/toulmini")
    is_installed = False

    config = generate_config(python_path, project_root, is_installed)

    assert "mcpServers" in config
    assert "toulmini" in config["mcpServers"]

    toulmini_config = config["mcpServers"]["toulmini"]
    assert toulmini_config["command"] == python_path
    assert toulmini_config["args"] == ["-m", "toulmini.server"]

    # Should have env with PYTHONPATH for source installations
    assert "env" in toulmini_config
    assert "PYTHONPATH" in toulmini_config["env"]
    assert toulmini_config["env"]["PYTHONPATH"] == str(project_root)


def test_generate_config_different_python_paths():
    """Test config generation with various Python paths."""
    test_paths = [
        "/usr/bin/python3",
        "/opt/homebrew/bin/python3.11",
        "C:\\Python311\\python.exe",
        "/home/user/.pyenv/versions/3.11.0/bin/python",
    ]

    for python_path in test_paths:
        config = generate_config(python_path, Path("/dummy"), True)
        assert config["mcpServers"]["toulmini"]["command"] == python_path


# === File Writing Tests ===


def test_write_config_new_file(temp_config_file):
    """Test writing config to a new file."""
    snippet = {
        "toulmini": {
            "command": "python",
            "args": ["-m", "toulmini.server"],
        }
    }

    _write_config(temp_config_file, snippet)

    # File should exist
    assert temp_config_file.exists()

    # Should contain valid JSON
    with open(temp_config_file, "r") as f:
        data = json.load(f)

    assert "mcpServers" in data
    assert data["mcpServers"] == snippet


def test_write_config_merge_with_existing(temp_config_file, sample_existing_config):
    """Test merging config with existing file."""
    # Write existing config first
    temp_config_file.write_text(json.dumps(sample_existing_config))

    # New snippet to add
    snippet = {
        "toulmini": {
            "command": "python",
            "args": ["-m", "toulmini.server"],
        }
    }

    _write_config(temp_config_file, snippet)

    # Read merged result
    with open(temp_config_file, "r") as f:
        data = json.load(f)

    # Should have both servers
    assert "mcpServers" in data
    assert "existing-server" in data["mcpServers"]
    assert "toulmini" in data["mcpServers"]

    # Should preserve other settings
    assert "otherSetting" in data
    assert data["otherSetting"] == "preserved"


def test_write_config_overwrite_existing_server(temp_config_file):
    """Test that writing the same server overwrites it."""
    # Initial config
    initial = {
        "mcpServers": {
            "toulmini": {
                "command": "old_python",
                "args": ["-m", "old.server"],
            }
        }
    }
    temp_config_file.write_text(json.dumps(initial))

    # New snippet (updated)
    snippet = {
        "toulmini": {
            "command": "new_python",
            "args": ["-m", "toulmini.server"],
        }
    }

    _write_config(temp_config_file, snippet)

    # Read result
    with open(temp_config_file, "r") as f:
        data = json.load(f)

    # Should have updated command
    assert data["mcpServers"]["toulmini"]["command"] == "new_python"
    assert data["mcpServers"]["toulmini"]["args"] == ["-m", "toulmini.server"]


def test_write_config_creates_parent_directories(tmp_path):
    """Test that parent directories are created if they don't exist."""
    nested_path = tmp_path / "deeply" / "nested" / "path" / "config.json"

    snippet = {"toulmini": {"command": "python", "args": ["-m", "toulmini.server"]}}

    _write_config(nested_path, snippet)

    # File should exist
    assert nested_path.exists()

    # Parent directories should exist
    assert nested_path.parent.exists()


def test_write_config_expands_tilde(tmp_path):
    """Test that ~ is expanded in file paths."""
    # Create a mock path with ~
    with patch("pathlib.Path.expanduser") as mock_expand:
        # Make expanduser return a path in tmp_path
        expanded_path = tmp_path / "config.json"
        mock_expand.return_value = expanded_path

        snippet = {"toulmini": {"command": "python", "args": ["-m", "toulmini.server"]}}

        # Call with ~ path
        _write_config(Path("~/config.json"), snippet)

        # expanduser should have been called
        mock_expand.assert_called()


def test_write_config_handles_corrupted_json(temp_config_file, capsys):
    """Test that corrupted existing JSON is handled gracefully."""
    # Write invalid JSON
    temp_config_file.write_text("{ invalid json }")

    snippet = {"toulmini": {"command": "python", "args": ["-m", "toulmini.server"]}}

    # Should not raise, should create new file
    _write_config(temp_config_file, snippet)

    # Should have warning in output
    captured = capsys.readouterr()
    assert "invalid" in captured.out.lower() or "warning" in captured.out.lower()

    # File should now contain valid JSON
    with open(temp_config_file, "r") as f:
        data = json.load(f)

    assert "mcpServers" in data
    assert "toulmini" in data["mcpServers"]


def test_write_config_preserves_formatting():
    """Test that written JSON is properly formatted (indented)."""
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        temp_path = Path(f.name)

    try:
        snippet = {"toulmini": {"command": "python", "args": ["-m", "toulmini.server"]}}

        _write_config(temp_path, snippet)

        # Read raw content
        content = temp_path.read_text()

        # Should be indented (contain newlines and spaces)
        assert "\n" in content
        assert "  " in content  # 2-space indent
    finally:
        temp_path.unlink()


# === Print Instructions Tests ===


def test_print_setup_instructions_dry_run():
    """Test print_setup_instructions with dry_run."""
    # Should not raise
    print_setup_instructions(dry_run=True)


def test_print_setup_instructions_output(capsys):
    """Test that print_setup_instructions produces expected output."""
    print_setup_instructions(dry_run=False)

    captured = capsys.readouterr()
    output = captured.out

    # Should contain key sections
    assert "TOULMINI MCP CONFIGURATION SNIPPET" in output
    assert "toulmini" in output  # Server name in snippet
    assert "command" in output
    assert "Tools available:" in output
    assert "initiate_toulmin_sequence" in output
    assert "Common config paths:" in output


# === Integration Tests ===


def test_full_config_generation_workflow():
    """Test complete workflow from detection to config generation."""
    python_path = get_python_path()
    is_installed = is_installed_in_site_packages()
    project_root = get_project_root()

    config = generate_config(python_path, project_root, is_installed)

    # Should have valid structure
    assert "mcpServers" in config
    assert "toulmini" in config["mcpServers"]
    assert "command" in config["mcpServers"]["toulmini"]
    assert "args" in config["mcpServers"]["toulmini"]

    # Command should be current Python
    assert config["mcpServers"]["toulmini"]["command"] == python_path

    # Args should point to toulmini.server
    assert config["mcpServers"]["toulmini"]["args"] == ["-m", "toulmini.server"]


def test_config_snippet_is_json_serializable():
    """Test that generated config can be JSON serialized."""
    python_path = get_python_path()
    project_root = get_project_root()

    config = generate_config(python_path, project_root, False)
    snippet = config["mcpServers"]

    # Should be serializable without error
    json_str = json.dumps(snippet, indent=2)
    assert isinstance(json_str, str)
    assert len(json_str) > 0

    # Should be deserializable
    parsed = json.loads(json_str)
    assert parsed == snippet


# === Edge Cases ===


def test_generate_config_empty_project_root():
    """Test config generation with empty project root."""
    config = generate_config("python", Path(""), False)

    # Should still generate valid config
    assert "mcpServers" in config
    # PYTHONPATH for Path("") becomes "." (current directory)
    assert config["mcpServers"]["toulmini"]["env"]["PYTHONPATH"] == "."


def test_write_config_with_unicode_paths(tmp_path):
    """Test writing config with unicode characters in path."""
    unicode_dir = tmp_path / "カタカナ" / "中文"
    unicode_file = unicode_dir / "config.json"

    snippet = {"toulmini": {"command": "python", "args": ["-m", "toulmini.server"]}}

    _write_config(unicode_file, snippet)

    # Should handle unicode paths correctly
    assert unicode_file.exists()

    with open(unicode_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "mcpServers" in data
