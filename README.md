<div align="center">

# Toulmini

**Logic Harness for Large Language Models**

[![PyPI version](https://img.shields.io/pypi/v/toulmini?color=blue&logo=pypi&logoColor=white)](https://pypi.org/project/toulmini/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)
[![Tests](https://github.com/Hmbown/Toulmini/actions/workflows/test.yml/badge.svg)](https://github.com/Hmbown/Toulmini/actions)

[Website](https://toulmini-web.pages.dev/) • [Documentation](https://github.com/Hmbown/Toulmini/tree/main/docs) • [Examples](https://github.com/Hmbown/Toulmini/tree/main/examples) • [PyPI](https://pypi.org/project/toulmini/)

</div>

---

## What is Toulmini?

Toulmini enforces rigorous argumentation through [Stephen Toulmin's model](https://en.wikipedia.org/wiki/Toulmin_method). It's an MCP server that forces LLMs into structured reasoning—no external API keys required.

**The problem:** LLMs hedge, skip logical steps, and avoid self-critique.

**The solution:** Toulmini enforces falsifiable claims, sequential phases, and mandatory adversarial testing. Weak logic triggers circuit breakers that terminate the analysis.

```
Query → Data/Claim → Warrant/Backing → Rebuttal/Qualifier → Verdict
         Phase 1        Phase 2            Phase 3          Phase 4
```

---

## Quickstart

```bash
pip install toulmini
```

### Configure your MCP client

<details>
<summary><strong>Claude Code</strong></summary>

```bash
claude mcp add toulmini -- python -m toulmini.server
```
</details>

<details>
<summary><strong>Claude Desktop</strong></summary>

Add to your config file:
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

Config locations:
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux:** `~/.config/Claude/claude_desktop_config.json`
</details>

<details>
<summary><strong>CLI helper</strong></summary>

```bash
toulmini-cli --verify          # Health check
toulmini-cli --config          # Show current config
toulmini-cli --install -       # Print MCP snippet
```
</details>

### Use it

```
"Analyze this argument: Should we allow human genetic engineering?"
```

Toulmini executes all phases automatically and returns a verdict.

---

## How It Works

### The 5 Tools

| Tool | Phase | Purpose |
|------|-------|---------|
| `initiate_toulmin_sequence` | 1 | Extract evidence, construct claim |
| `inject_logic_bridge` | 2 | Build warrant + backing (circuit breaker) |
| `stress_test_argument` | 3 | Adversarial attack on your own argument |
| `render_verdict` | 4 | Final judgment: sustained / overruled / remanded |
| `format_analysis_report` | 5 | Optional markdown report |

### Circuit Breakers

If the warrant or backing is weak, the chain **terminates immediately**—no weak arguments reach the verdict phase.

### The Council (Optional)

Convene expert perspectives before Phase 2 or 3:

```python
consult_field_experts(
    query="Should we allow genetic engineering?",
    perspectives=["Bioethicist", "Medical Geneticist", "Disability Rights Advocate"]
)
```

---

## Toulmin's Model

| Component | Purpose |
|-----------|---------|
| **Data** | Evidence and facts (cited) |
| **Claim** | Falsifiable assertion based on the data |
| **Warrant** | Logical principle connecting data → claim |
| **Backing** | Authority supporting the warrant |
| **Rebuttal** | Conditions where the warrant fails |
| **Qualifier** | Confidence level (certainly / probably / possibly) |
| **Verdict** | Final judgment with rationale |

---

## Limitations

**Citation reliability:** Without web search, citations come from LLM training data and may be outdated or hallucinated. Treat them as leads to investigate, not verified sources.

**Failure modes:**
- Weak warrant/backing → chain terminates at Phase 2
- Absolute rebuttal → verdict must be "overruled"
- Confidence < 30% → verdict should be "overruled" or "remanded"

---

## Development

```bash
git clone https://github.com/Hmbown/Toulmini.git
cd Toulmini
pip install -e ".[dev]"
pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## Links

- [Documentation](https://github.com/Hmbown/Toulmini/tree/main/docs)
- [Examples](https://github.com/Hmbown/Toulmini/tree/main/examples)
- [Hegelion](https://github.com/Hmbown/Hegelion) — Dialectical reasoning (sister project)

---

<div align="center">

**MIT License** • [Report Issues](https://github.com/Hmbown/Toulmini/issues)

</div>
