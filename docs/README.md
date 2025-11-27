# Toulmini Documentation

Welcome to the Toulmini documentation. Toulmini is a logic harness that forces LLMs into structured, sequential reasoning through Toulmin's argumentation model.

## Quick Navigation

### Getting Started
- [Installation](getting-started/installation.md) - Install Toulmini via pip or from source
- [Configuration](getting-started/configuration.md) - Configure your MCP client

### Concepts
- [Toulmin's Model](concepts/toulmin-model.md) - Deep dive into the 7 argumentation components
- [Architecture](concepts/architecture.md) - Technical design and constraints

### Guides
- [MCP Integration](guides/mcp-integration.md) - Using Toulmini as an MCP server
- [Examples](guides/examples.md) - Worked examples with full JSON traces

### Reference
- [Technical Specification](SPEC.md) - Schemas, constraints, and API reference

## What is Toulmini?

Toulmini implements Stephen Toulmin's argumentation model as an MCP (Model Context Protocol) server. It provides 4 sequential tools that guide an LLM through rigorous logical analysis:

1. **Phase 1**: Extract DATA and construct CLAIM
2. **Phase 2**: Build logical bridge (WARRANT + BACKING)
3. **Phase 3**: Adversarial stress test (REBUTTAL + QUALIFIER)
4. **Phase 4**: Render final VERDICT

The key insight: **separating these phases into distinct tool calls forces the LLM to commit to each step before proceeding**, preventing the hedging and balanced summaries that single-prompt approaches tend toward.

## Core Principles

- **No hedging in claims** — Qualifiers come later, in their proper place
- **No skipping steps** — Can't render a verdict without completing the rebuttal
- **Hard rejection of weak backing** — The chain terminates if support is speculative
- **Adversarial stress testing** — Must actively find "black swan" scenarios

## Resources

- [GitHub Repository](https://github.com/Hmbown/Toulmini)
- [PyPI Package](https://pypi.org/project/toulmini/)
- [Website](https://toulmini.web.app)
