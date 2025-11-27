# Configuration

After [installing Toulmini](installation.md), configure your MCP client to connect to the server.

## Claude Code (CLI)

The fastest setup:

```bash
claude mcp add toulmini --scope user -- python -m toulmini.server
```

**Verify the connection:**
```bash
claude mcp list
```

In any Claude Code session, type `/mcp` to see Toulmini's status.

### Scope Options

| Scope | Description |
|-------|-------------|
| `--scope user` | Available in all your projects |
| `--scope project` | Shared with your team via `.mcp.json` |
| *(no flag)* | Local to current project only |

## Claude Desktop

### 1. Find your config file

| Platform | Location |
|----------|----------|
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

### 2. Add Toulmini to the config

```json
{
  "mcpServers": {
    "toulmini": {
      "command": "python",
      "args": ["-m", "toulmini.server"]
    }
  }
}
```

### 3. Restart Claude Desktop

A full restart is required (not just refresh).

### 4. Verify

Ask Claude to use one of the Toulmini tools, or check the Developer Console.

## Cursor

1. Open **Cursor Settings** → **Features** → **MCP Servers**

2. Add a new server with this configuration:

```json
{
  "toulmini": {
    "command": "python",
    "args": ["-m", "toulmini.server"]
  }
}
```

3. Save and restart Cursor.

## Windsurf

1. Open **Windsurf Settings** → **MCP Configuration**

2. Add Toulmini:

```json
{
  "mcpServers": {
    "toulmini": {
      "command": "python",
      "args": ["-m", "toulmini.server"]
    }
  }
}
```

3. Restart Windsurf.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Server not found | Ensure `toulmini` is installed: `pip show toulmini` |
| Connection failed | Check Python is in your PATH |
| JSON parse error | Validate your config file syntax |
| Tools not appearing | Restart your client completely |

## Python Path Issues

If using a virtual environment, you may need to specify the full path to Python:

```json
{
  "mcpServers": {
    "toulmini": {
      "command": "/path/to/venv/bin/python",
      "args": ["-m", "toulmini.server"]
    }
  }
}
```

## Next Steps

- Learn about [Toulmin's argumentation model](../concepts/toulmin-model.md)
- See [worked examples](../guides/examples.md)
