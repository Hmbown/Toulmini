# Toulmini

A local MCP server that enforces rigorous argumentation through Stephen Toulmin's model. Forces LLMs into structured, sequential reasoning across 7 discrete steps.

## What is Toulmin's Model?

Stephen Toulmin's argumentation model breaks reasoning into six interconnected components (plus a final verdict):

```
DATA (Grounds) ──────► CLAIM
        │                 ▲
        │                 │
        ▼                 │
    WARRANT ◄──────── BACKING
        │
        ▼
    REBUTTAL ──────► QUALIFIER ──────► VERDICT
```

| Component | Purpose | Example |
|-----------|---------|---------|
| **DATA** | Raw facts/evidence (must be cited) | "Studies show remote workers are 13% more productive" |
| **CLAIM** | Assertion based *only* on the data | "Remote work increases productivity" |
| **WARRANT** | Logical principle connecting data to claim | "If controlled studies show X, then X is likely true" |
| **BACKING** | Authority supporting the warrant | "Meta-analyses in organizational psychology..." |
| **REBUTTAL** | Conditions where the warrant fails | "Unless the worker lacks a dedicated workspace..." |
| **QUALIFIER** | Degree of certainty | "Presumably" / "Probably" / "Certainly" |
| **VERDICT** | Final synthesis | "QUALIFIED: Claim holds for knowledge workers with proper setup" |

## Why This Exists

LLMs tend to hedge, compromise, or give "balanced" answers without confronting genuine contradictions. Toulmini forces separation:

- **No hedging in claims** - qualifiers come later
- **No skipping steps** - can't render verdict without rebuttal
- **Hard rejection of weak backing** - stops the chain if support is speculative
- **Adversarial stress testing** - must find "black swan" edge cases

## Installation

```bash
git clone https://github.com/Hmbown/Toulmini.git
cd Toulmini
pip install -e .
```

## Usage

### Run the MCP Server

```bash
# Via module
python -m toulmini.server

# Via entry point
toulmini
```

### MCP Client Configuration

**Claude Desktop / Cursor / VS Code:**

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

## The 4 Tools

### 1. `initiate_toulmin_sequence`

Starts the analysis. Returns a prompt that forces the LLM to output **DATA** and **CLAIM** only.

```
Input:  query (str) - "Is this copyright infringement?"
Output: Structured prompt → JSON with data + claim
```

### 2. `inject_logic_bridge`

Takes DATA and CLAIM, returns a prompt for **WARRANT** and **BACKING**.

```
Input:  data_json, claim_json, query
Output: Structured prompt → JSON with warrant + backing

⚠️ HARD REJECTION: If backing.strength == "weak", the chain terminates.
```

### 3. `stress_test_argument`

Takes the chain so far, forces adversarial analysis for **REBUTTAL** and **QUALIFIER**.

```
Input:  data_json, claim_json, warrant_json, backing_json, query
Output: Structured prompt → JSON with rebuttal + qualifier

Must find "black swan" scenarios where the warrant fails.
```

### 4. `render_verdict`

Takes the complete 6-part chain, synthesizes the final **VERDICT**.

```
Input:  All 6 component JSONs + query
Output: Structured prompt → JSON with verdict (STANDS / FALLS / QUALIFIED)
```

## Example Flow

```
User: "Is AI-generated art copyright infringement?"

1. initiate_toulmin_sequence("Is AI-generated art copyright infringement?")
   → LLM outputs DATA (cases, laws) + CLAIM (assertion)

2. inject_logic_bridge(data, claim, query)
   → LLM outputs WARRANT (legal principle) + BACKING (case law)
   → If backing is "weak" → REJECTED, chain stops

3. stress_test_argument(data, claim, warrant, backing, query)
   → LLM outputs REBUTTAL (edge cases) + QUALIFIER (certainty level)

4. render_verdict(all_components, query)
   → LLM outputs VERDICT: "QUALIFIED - depends on training data consent"
```

## Architectural Constraints

- **API-less, local-only** - no external calls except to your configured LLM
- **Pydantic validation** - strict schema enforcement on all components
- **Sequential dependencies** - enforced at both tool and model level
- **No "yapping"** - all prompts end with "RESPOND WITH ONLY THE JSON"

## Project Structure

```
toulmini/
├── pyproject.toml
├── README.md
└── src/toulmini/
    ├── __init__.py
    ├── server.py          # MCP entry point (FastMCP)
    ├── exceptions.py      # WeakBackingError, DependencyError
    ├── prompts.py         # 4 JSON-forcing prompt templates
    ├── tools.py           # Tool implementations
    └── models/
        ├── __init__.py
        ├── base.py        # Citation, Literal types
        ├── components.py  # 7 Toulmin components
        └── chain.py       # ToulminChain aggregate
```

## Key Exceptions

| Exception | When | Effect |
|-----------|------|--------|
| `WeakBackingError` | `backing.strength == "weak"` | **Terminates chain** |
| `DependencyError` | Missing required prior phases | Blocks tool execution |
| `ChainValidationError` | Invalid component sequence | Prevents invalid state |
| `OutputFormatError` | LLM output not valid JSON | Requires retry |

## Inspired By

- [Hegelion](https://github.com/Hmbown/Hegelion) - Dialectical reasoning wrapper (thesis/antithesis/synthesis)
- Stephen Toulmin's "The Uses of Argument" (1958)

## License

MIT
