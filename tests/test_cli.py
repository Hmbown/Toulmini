"""Tests for the integrated Toulmini CLI."""

import json

from toulmini import cli


def test_cli_config_outputs_json(capsys):
    exit_code = cli.main(["--config"])
    assert exit_code == 0

    output = capsys.readouterr().out.strip()
    data = json.loads(output)
    assert "strict_mode" in data
    assert "log_level" in data


def test_cli_verify_reports_success(capsys):
    exit_code = cli.main(["--verify"])
    assert exit_code == 0

    output = capsys.readouterr().out
    assert "All verification checks passed." in output


def test_cli_install_writes_file(tmp_path):
    target = tmp_path / "mcp_config.json"
    exit_code = cli.main(["--install", str(target)])
    assert exit_code == 0

    data = json.loads(target.read_text())
    assert "mcpServers" in data
    assert "toulmini" in data["mcpServers"]
