# Architecture

Toulmini is designed as a strict, opinionated reasoning framework. This document explains the technical architecture and design decisions.

## High-Level Design

```
┌─────────────────────────────────────────────────────────┐
│                     MCP Client                          │
│              (Claude, Cursor, etc.)                     │
└─────────────────────┬───────────────────────────────────┘
                      │ STDIO
                      ▼
┌─────────────────────────────────────────────────────────┐
│                 Toulmini MCP Server                     │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Tool 1: initiate_toulmin_sequence                 │ │
│  │  Tool 2: inject_logic_bridge                       │ │
│  │  Tool 3: stress_test_argument                      │ │
│  │  Tool 4: render_verdict                            │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Prompts Module (JSON-forcing templates)           │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Models (Pydantic validation)                      │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Core Design Principles

### 1. Tools Return Prompts, Not Answers

Each tool returns a **system directive** (prompt) that the LLM must follow. The tool does not perform reasoning—it structures the reasoning process.

```
User Query → Tool Call → Returns Prompt → LLM Generates JSON
```

This design allows Toulmini to work with any LLM that supports MCP, without making external API calls.

### 2. Sequential Dependencies

Phase N requires all outputs from Phases 1 through N-1:

| Phase | Requires |
|-------|----------|
| 1 | query |
| 2 | query, data, claim |
| 3 | query, data, claim, warrant, backing |
| 4 | query, data, claim, warrant, backing, rebuttal, qualifier |

This prevents skipping steps and ensures each phase builds on validated prior work.

### 3. Circuit Breakers

The argument chain terminates early if logical foundations are weak:

| Condition | Result |
|-----------|--------|
| `warrant.strength == "weak"` | Chain terminates |
| `warrant.strength == "irrelevant"` | Chain terminates |
| `backing.strength == "weak"` | Chain terminates |
| `backing.strength == "irrelevant"` | Chain terminates |

This prevents proceeding with fundamentally flawed reasoning.

### 4. JSON-Only Output

All prompts include a strict directive:

```
OUTPUT FORMAT:
Return ONLY valid JSON. No markdown. No explanation. No hedging.
```

This forces structured, parseable output and prevents conversational responses.

### 5. Stderr-Only Logging

All logging goes to stderr, never stdout. This is required for STDIO-based MCP servers to avoid polluting the communication channel.

## Module Structure

```
src/toulmini/
├── __init__.py          # Public API exports
├── server.py            # MCP server + 4 tool definitions
├── prompts.py           # Phase 1-4 prompt templates
└── models/
    ├── __init__.py      # Model exports
    ├── base.py          # Type aliases (StrengthLevel, VerdictStatus, etc.)
    ├── components.py    # 7 Toulmin component Pydantic models
    └── chain.py         # ToulminChain aggregate with validation
```

### server.py

Entry point for the MCP server. Uses FastMCP to register 4 tools:
- `initiate_toulmin_sequence`
- `inject_logic_bridge`
- `stress_test_argument`
- `render_verdict`

Each tool accepts JSON strings from previous phases and returns a structured prompt.

### prompts.py

Contains the system directive and 4 phase-specific prompt generators. Each prompt:
- Specifies exact JSON structure required
- Lists validation rules
- Defines strength levels and their meanings
- Forbids conversational output

### models/

Pydantic models for all 7 Toulmin components plus the aggregate chain:

| Model | Fields |
|-------|--------|
| `Data` | facts, citations, evidence_type |
| `Claim` | statement, scope |
| `Warrant` | principle, logic_type, strength |
| `Backing` | authority, citations, strength |
| `Rebuttal` | exceptions, counterexamples, strength |
| `Qualifier` | degree, confidence_pct, rationale |
| `Verdict` | status, reasoning, final_statement |

## Constraints Table

| Constraint | Implementation |
|------------|----------------|
| No external APIs | Server makes no network calls |
| Strict schemas | Pydantic validators on all components |
| Sequential deps | Each phase validates prior phases exist |
| JSON output | Prompts forbid non-JSON responses |
| Stderr logging | `logging.basicConfig(stream=sys.stderr)` |
| No conversation | System directive: "You do not converse" |

## Error Handling

Errors are returned as structured JSON:

```json
{
  "error": "Missing required prior phase outputs",
  "missing": ["warrant_json", "backing_json"]
}
```

The server never crashes on invalid input—it returns actionable error messages.

## Testing Strategy

Tests focus on:
1. **Happy path**: Full 4-phase cycle with valid inputs
2. **Failure modes**: Circuit breakers, missing inputs, invalid JSON
3. **Model validation**: Pydantic constraints on all components
4. **Tool registration**: All 4 tools available via MCP

See `/tests/` for the full test suite.
