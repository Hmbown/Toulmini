"""Prompt templates that enforce structured JSON output."""

from __future__ import annotations


# JSON Schema for Phase One output
PHASE_ONE_SCHEMA = """{
  "data": {
    "facts": ["string - factual statement 1", "string - factual statement 2"],
    "citations": [
      {"source": "string", "reference": "string", "url": "string or null"}
    ],
    "evidence_type": "empirical|statistical|testimonial|documentary|expert"
  },
  "claim": {
    "statement": "string - the assertion (20-500 chars)",
    "scope": "universal|general|specific|singular"
  }
}"""

# JSON Schema for Phase Two output
PHASE_TWO_SCHEMA = """{
  "warrant": {
    "principle": "string - the logical rule (30-800 chars)",
    "logic_type": "deductive|inductive|abductive"
  },
  "backing": {
    "authority": "string - authoritative support (20-1000 chars)",
    "citations": [{"source": "string", "reference": "string"}],
    "strength": "strong|moderate|weak"
  }
}"""

# JSON Schema for Phase Three output
PHASE_THREE_SCHEMA = """{
  "rebuttal": {
    "edge_cases": ["string - condition where warrant fails (min 15 chars each)"],
    "counterexamples": ["string - potential counterexample"],
    "limitations": "string - known boundaries (min 20 chars)",
    "severity": "fatal|significant|minor|negligible"
  },
  "qualifier": {
    "degree": "certainly|presumably|probably|possibly|apparently|unless",
    "rationale": "string - why this qualifier (30-500 chars, must explain 'because...')",
    "confidence_pct": 0-100
  }
}"""

# JSON Schema for Verdict output
VERDICT_SCHEMA = """{
  "verdict": {
    "outcome": "STANDS|FALLS|QUALIFIED",
    "reasoning": "string - comprehensive reasoning (100-2000 chars, must reference multiple components)",
    "final_statement": "string - one-sentence summary (20-300 chars)"
  }
}"""


def initiate_toulmin_prompt(query: str) -> str:
    """Generate prompt for Phase One: DATA + CLAIM."""
    return f"""## TOULMIN ARGUMENT: PHASE 1 (DATA + CLAIM)

**QUERY TO ANALYZE:** {query}

You are conducting a Toulmin argumentation analysis. This is PHASE ONE.

### YOUR TASK:
1. Identify **DATA (Grounds)** - raw facts and evidence about this query
2. Formulate a **CLAIM** - an assertion based ONLY on the data you provide

### STRICT REQUIREMENTS:
- DATA must include at least ONE verifiable fact with citation
- Each fact must be at least 10 characters
- CLAIM must be a declarative statement (NOT a question)
- CLAIM must be 20-500 characters
- CLAIM scope must be one of: universal, general, specific, singular
- NO qualifiers in the claim yet (those come in Phase 3)
- NO hedging language ("might", "could possibly", "perhaps")

### OUTPUT SCHEMA (JSON ONLY):
{PHASE_ONE_SCHEMA}

### EXAMPLE OUTPUT:
```json
{{
  "data": {{
    "facts": ["Studies show remote workers report 13% higher productivity (Stanford 2020)"],
    "citations": [{{"source": "Stanford Study", "reference": "Bloom et al. 2020", "url": null}}],
    "evidence_type": "empirical"
  }},
  "claim": {{
    "statement": "Remote work increases individual productivity compared to office work",
    "scope": "general"
  }}
}}
```

RESPOND WITH ONLY THE JSON. NO PREAMBLE. NO EXPLANATION. NO MARKDOWN FENCING."""


def inject_logic_bridge_prompt(data_json: str, claim_json: str, query: str) -> str:
    """Generate prompt for Phase Two: WARRANT + BACKING."""
    return f"""## TOULMIN ARGUMENT: PHASE 2 (WARRANT + BACKING)

**ORIGINAL QUERY:** {query}

**PRIOR DATA:**
{data_json}

**PRIOR CLAIM:**
{claim_json}

You are conducting a Toulmin argumentation analysis. This is PHASE TWO.

### YOUR TASK:
1. Formulate a **WARRANT** - the logical principle connecting the data to the claim
2. Provide **BACKING** - authoritative support for the warrant itself

### STRICT REQUIREMENTS:
- WARRANT must be a GENERAL principle (use "If X, then Y" or "When X, generally Y")
- WARRANT must be 30-800 characters
- WARRANT must explicitly bridge the specific data to the specific claim
- BACKING must cite authoritative sources (statutory, scientific, expert)
- BACKING authority must be 20-1000 characters
- BACKING must support the WARRANT, not just restate the data
- BACKING strength must be: strong, moderate, or weak

### CRITICAL WARNING:
**If backing strength is "weak", the argument chain will be REJECTED.**
Only mark as "weak" if you cannot find solid authoritative support.
This will terminate the analysis - choose "moderate" if uncertain.

### OUTPUT SCHEMA (JSON ONLY):
{PHASE_TWO_SCHEMA}

RESPOND WITH ONLY THE JSON. NO PREAMBLE. NO EXPLANATION. NO MARKDOWN FENCING."""


def stress_test_argument_prompt(
    data_json: str,
    claim_json: str,
    warrant_json: str,
    backing_json: str,
    query: str
) -> str:
    """Generate prompt for Phase Three: REBUTTAL + QUALIFIER."""
    return f"""## TOULMIN ARGUMENT: PHASE 3 (REBUTTAL + QUALIFIER) - STRESS TEST

**ORIGINAL QUERY:** {query}

**THE ARGUMENT CHAIN SO FAR:**

DATA:
{data_json}

CLAIM:
{claim_json}

WARRANT:
{warrant_json}

BACKING:
{backing_json}

You are conducting a Toulmin argumentation analysis. This is PHASE THREE: STRESS TEST.

### YOUR TASK:
1. Identify **REBUTTALS** - conditions where the warrant FAILS (black swans, edge cases)
2. Determine **QUALIFIER** - the degree of force for the claim given the rebuttals

### STRICT REQUIREMENTS:
- Find at least ONE genuine exception where the warrant doesn't hold
- Each edge case must be at least 15 characters and CONDITIONAL (use "if", "when", "unless")
- Consider "black swan" scenarios - rare but devastating counterexamples
- Be ADVERSARIAL - actively try to break the argument
- Limitations must be at least 20 characters
- Qualifier rationale must explain "because..." (30-500 chars)
- Confidence percentage must be 0-100

### SEVERITY GUIDE:
| Severity | Meaning | Suggested Qualifier |
|----------|---------|---------------------|
| fatal | Argument is fundamentally flawed | possibly, apparently |
| significant | Major weaknesses exist | probably, presumably |
| minor | Small issues only | probably, certainly |
| negligible | Trivial edge cases | certainly |

### OUTPUT SCHEMA (JSON ONLY):
{PHASE_THREE_SCHEMA}

RESPOND WITH ONLY THE JSON. NO PREAMBLE. NO EXPLANATION. NO MARKDOWN FENCING."""


def render_verdict_prompt(
    data_json: str,
    claim_json: str,
    warrant_json: str,
    backing_json: str,
    rebuttal_json: str,
    qualifier_json: str,
    query: str
) -> str:
    """Generate prompt for Final Phase: VERDICT."""
    return f"""## TOULMIN ARGUMENT: FINAL PHASE (VERDICT)

**ORIGINAL QUERY:** {query}

**COMPLETE ARGUMENT CHAIN:**

1. DATA:
{data_json}

2. CLAIM:
{claim_json}

3. WARRANT:
{warrant_json}

4. BACKING:
{backing_json}

5. REBUTTAL:
{rebuttal_json}

6. QUALIFIER:
{qualifier_json}

You are conducting a Toulmin argumentation analysis. This is the FINAL PHASE: VERDICT.

### YOUR TASK:
Render a final **VERDICT** synthesizing all six components. Does the claim stand?

### STRICT REQUIREMENTS:
- Reasoning MUST reference at least 3 of the 6 components (data, claim, warrant, backing, rebuttal, qualifier)
- Reasoning must be 100-2000 characters
- Final statement must be 20-300 characters
- Outcome MUST be consistent with qualifier and rebuttal severity:
  - If rebuttals are "fatal", outcome CANNOT be "STANDS"
  - If qualifier is "certainly", outcome is likely "STANDS"
  - Use "QUALIFIED" when claim holds only under specific conditions

### VERDICT OPTIONS:
| Outcome | Meaning |
|---------|---------|
| STANDS | Claim survives scrutiny with strong backing and manageable rebuttals |
| FALLS | Rebuttals or weak backing undermine the claim fatally |
| QUALIFIED | Claim holds under specific conditions only |

### OUTPUT SCHEMA (JSON ONLY):
{VERDICT_SCHEMA}

RESPOND WITH ONLY THE JSON. NO PREAMBLE. NO EXPLANATION. NO MARKDOWN FENCING."""
