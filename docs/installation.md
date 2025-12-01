# Installation

## 1. Install the Package (Local MCP, No API Tokens)

```bash
pip install toulmini
```

This installs both the MCP server entry point (`toulmini`) and the integrated helper
CLI (`toulmini-cli`, also available as `toulmini-setup-mcp`). No external API credentials are required—the server runs locally as an MCP endpoint your LLM client connects to.

## 2. Verify the Environment

Run the bundled checks to confirm the server, prompts, and MCP config generator are ready:

```bash
toulmini-cli --verify
```

You should see all checks marked with `✅`. If a circuit breaker is disabled
(e.g., via `.env`), the verifier will report that state.

## 3. Inspect Configuration (Optional)

```bash
toulmini-cli --config
```

This prints the effective values that `toulmini.config.get_config()` returns,
including any overrides from your `.env` file.

## 4. Install the MCP Snippet

Use the CLI to either print or write the MCP server configuration:

```bash
# Print the snippet without writing a file (great for Cursor/Windsurf)
toulmini-cli --install -

# Write the snippet to Claude Desktop (macOS example)
toulmini-cli --install "$HOME/Library/Application Support/Claude/claude_desktop_config.json"
```

When Toulmini detects a source checkout (not an installed wheel), the CLI automatically
adds `PYTHONPATH` so the MCP client can import the server.

## 5. Launch Your MCP Client

After writing the config, restart Claude Desktop / Cursor / Windsurf, then
connect to the `toulmini` server. The tools listed should match the verifier output.

## Local Development Tips

- Copy `.env.example` to `.env` and tweak flags while running tests.
- `python -m toulmini.server` still works for STDIO usage; `toulmini` in `pyproject.toml`
  points to the same entry point.
- The legacy `scripts/setup_mcp.py` file now wraps `toulmini-cli`, so CI tests remain backwards compatible.
