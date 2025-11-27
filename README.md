# Toulmini

Local MCP server implementing Toulmin's 7-step argumentation model.

## Installation

```bash
pip install -e .
```

## Usage

Run the MCP server:
```bash
python -m toulmini.server
```

Or via entry point:
```bash
toulmini
```

## MCP Client Configuration

Add to your MCP client config:
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

## Tools

1. **initiate_toulmin_sequence** - Start analysis with DATA + CLAIM
2. **inject_logic_bridge** - Generate WARRANT + BACKING
3. **stress_test_argument** - Generate REBUTTAL + QUALIFIER
4. **render_verdict** - Synthesize final VERDICT
