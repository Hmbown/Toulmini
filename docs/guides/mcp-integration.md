# MCP Integration Guide

This guide explains how to use Toulmini as an MCP (Model Context Protocol) server with your AI assistant.

## What is MCP?

MCP (Model Context Protocol) is a standard for connecting AI assistants to external tools and data sources. Toulmini implements an MCP server that exposes 4 tools for structured argumentation.

## The 4 Tools

### Tool 1: `initiate_toulmin_sequence`

**Purpose**: Start the analysis. Extract DATA and construct CLAIM.

**Input**:
```json
{
  "query": "Would immortality be a curse?"
}
```

**Returns**: A prompt that the LLM executes to produce:
```json
{
  "data": {
    "facts": ["..."],
    "citations": [{"source": "...", "reference": "..."}],
    "evidence_type": "empirical"
  },
  "claim": {
    "statement": "...",
    "scope": "general"
  }
}
```

### Tool 2: `inject_logic_bridge`

**Purpose**: Build the logical bridge. Generate WARRANT and BACKING.

**Input**:
```json
{
  "query": "Would immortality be a curse?",
  "data_json": "{...}",
  "claim_json": "{...}"
}
```

**Returns**: A prompt that produces:
```json
{
  "warrant": {
    "principle": "If X then Y",
    "logic_type": "deductive",
    "strength": "strong"
  },
  "backing": {
    "authority": "...",
    "citations": [...],
    "strength": "strong"
  }
}
```

**Warning**: If strength is "weak" or "irrelevant", the argument chain terminates.

### Tool 3: `stress_test_argument`

**Purpose**: Adversarial attack. Find REBUTTALS and assign QUALIFIER.

**Input**:
```json
{
  "query": "...",
  "data_json": "{...}",
  "claim_json": "{...}",
  "warrant_json": "{...}",
  "backing_json": "{...}"
}
```

**Returns**: A prompt that produces:
```json
{
  "rebuttal": {
    "exceptions": ["..."],
    "counterexamples": ["..."],
    "strength": "strong"
  },
  "qualifier": {
    "degree": "possibly",
    "confidence_pct": 45,
    "rationale": "..."
  }
}
```

### Tool 4: `render_verdict`

**Purpose**: Final judgment on the complete argument chain.

**Input**:
```json
{
  "query": "...",
  "data_json": "{...}",
  "claim_json": "{...}",
  "warrant_json": "{...}",
  "backing_json": "{...}",
  "rebuttal_json": "{...}",
  "qualifier_json": "{...}"
}
```

**Returns**: A prompt that produces:
```json
{
  "verdict": {
    "status": "remanded",
    "reasoning": "...",
    "final_statement": "..."
  }
}
```

## Execution Flow

```
Query: "Is remote work more productive?"

1. User/Agent calls initiate_toulmin_sequence(query)
2. Tool returns Phase 1 prompt
3. LLM generates DATA + CLAIM JSON
4. User/Agent calls inject_logic_bridge(query, data, claim)
5. Tool returns Phase 2 prompt
6. LLM generates WARRANT + BACKING JSON
   └─► If strength == "weak": STOP
7. User/Agent calls stress_test_argument(...)
8. Tool returns Phase 3 prompt
9. LLM generates REBUTTAL + QUALIFIER JSON
10. User/Agent calls render_verdict(...)
11. Tool returns Phase 4 prompt
12. LLM generates VERDICT JSON
```

## Usage Tips

### Let the LLM Drive

Most MCP-aware assistants (Claude, Cursor, etc.) will automatically:
1. Recognize that a Toulmin analysis is needed
2. Call tools in sequence
3. Pass outputs between phases

You can simply say:

> "Use Toulmini to analyze: Should we adopt a 4-day work week?"

### Manual Control

For more control, explicitly request each phase:

> "Use initiate_toulmin_sequence to analyze: Is social media harmful to democracy?"

Then review the output before proceeding:

> "Now call inject_logic_bridge with those results"

### Handling Termination

If Phase 2 terminates due to weak warrant/backing, the assistant should inform you:

> "The argument chain terminated because the backing was rated 'weak'. The evidence was insufficient to support the logical bridge."

This is expected behavior—Toulmini rejects poorly-supported arguments.

## Debugging

### Check Tool Registration

In Claude Code:
```bash
claude mcp list
```

Or type `/mcp` in a session to see Toulmini's status.

### View Server Logs

Toulmini logs to stderr. To see debug output:

```bash
python -m toulmini.server 2>&1 | tee toulmini.log
```

### Test Manually

```bash
python verify_toulmini.py
```

This script verifies all 4 tools are registered correctly.
