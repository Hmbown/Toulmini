# CONTINUATION PROMPT FOR AI ASSISTANT

You are helping complete the **Toulmini** MCP server - a Logic Compiler for Toulmin argumentation.

**Repository:** https://github.com/Hmbown/Toulmini

## CURRENT STATE

The core server is complete:
- 4 MCP tools (initiate_toulmin_sequence, inject_logic_bridge, stress_test_argument, render_verdict)
- Strict Pydantic models with `logic_check()` methods that crash on weak logic
- Aggressive "Logic Engine" prompts that suppress conversational filler
- FastMCP server with stdio transport

## YOUR TASK

Make this MCP server **plug-and-play** by adding comprehensive installation instructions for ALL major MCP clients. The instructions must be **current as of November 2025**.

### PLATFORMS TO DOCUMENT:

#### 1. CLAUDE CODE (Anthropic CLI)
- How to add Toulmini to `~/.claude/claude_desktop_config.json` or equivalent
- Command to register the MCP server
- Any Claude Code-specific configuration (hooks, permissions)
- Example: `claude mcp add` syntax if applicable

#### 2. CLAUDE DESKTOP (macOS/Windows app)
- Location of config file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS)
- Full JSON configuration block
- How to restart Claude Desktop to pick up changes
- Troubleshooting common issues

#### 3. GEMINI CLI (Google)
- How Gemini CLI handles MCP servers (if supported as of Nov 2025)
- Configuration file location and format
- Any Google-specific authentication or setup

#### 4. CURSOR (AI Code Editor)
- Cursor's MCP configuration location
- How to add custom MCP servers in Cursor settings
- Any Cursor-specific JSON format differences

#### 5. WINDSURF (Codeium's AI IDE)
- Windsurf's extension/plugin system for MCP
- Configuration file or UI-based setup
- Any Windsurf-specific considerations

### REQUIREMENTS FOR DOCUMENTATION:

1. **Be specific** - exact file paths, exact JSON, exact commands
2. **Be current** - November 2025 syntax (things change fast in AI tooling)
3. **Include verification** - how to test that the server is connected
4. **Include troubleshooting** - common errors and fixes
5. **Cross-platform** - macOS, Windows, Linux where applicable

### OUTPUT FORMAT:

Update the `README.md` with a new section called "## Installation & Configuration" that includes:

```markdown
## Installation & Configuration

### Prerequisites
[Python version, pip/uv, etc.]

### Install Toulmini
[pip install commands]

### Configure Your MCP Client

<details>
<summary>Claude Code</summary>
[Full instructions]
</details>

<details>
<summary>Claude Desktop</summary>
[Full instructions]
</details>

<details>
<summary>Gemini CLI</summary>
[Full instructions]
</details>

<details>
<summary>Cursor</summary>
[Full instructions]
</details>

<details>
<summary>Windsurf</summary>
[Full instructions]
</details>

### Verify Installation
[How to test]

### Troubleshooting
[Common issues]
```

### RESEARCH REQUIRED:

You will need to look up the **latest** configuration formats for each platform. MCP client configuration syntax has evolved rapidly in 2025. Do not assume old formats still work.

Key things to verify:
- Does the client use `mcpServers` or a different key?
- Does it support `command` + `args` or `url` for local servers?
- Are there new authentication or permission models?
- Has the config file location changed?

### EXAMPLE STARTING POINT (may be outdated):

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

This format worked in early 2025 but verify it's still current.

---

## CONTEXT: What Toulmini Does

Toulmini forces LLMs through Toulmin's 7-step argumentation model:

1. **DATA** → Raw facts with citations
2. **CLAIM** → Assertion based on data
3. **WARRANT** → Logical principle connecting data to claim
4. **BACKING** → Authority supporting the warrant
5. **REBUTTAL** → Conditions where warrant fails
6. **QUALIFIER** → Degree of certainty
7. **VERDICT** → Final judgment (sustained/overruled/remanded)

The server returns **prompts** that the client LLM must execute. Each tool returns a structured prompt, not a direct answer.

**Philosophy:** Bad logic = crash. Weak backing = termination. No appeals.

---

## START

Begin by researching the current (November 2025) MCP configuration formats for each platform, then update the README.md with comprehensive plug-and-play instructions.
