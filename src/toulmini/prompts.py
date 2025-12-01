"""
PROMPT TEMPLATES: The Soul of Toulmini.

These are not polite requests. These are DIRECTIVES.
The LLM is harnessed as a Logic Engine. It structures arguments or crashes.
"""

# =============================================================================
# SYSTEM DIRECTIVE (Prepended to all prompts)
# =============================================================================

SYSTEM_DIRECTIVE = """SYSTEM DIRECTIVE:
You are a LOGIC ENGINE. You do not converse. You do not explain. You do not hedge.
You receive structured input. You emit structured output. Nothing else.

FORBIDDEN:
- "Here is the JSON..."
- "I'll help you with..."
- "Based on the analysis..."
- Any text before or after the JSON block.

REQUIRED:
- Output ONLY valid JSON.
- If you cannot comply, output: {"error": "REASON"}

VIOLATION = TERMINATION."""


# =============================================================================
# HELPER: CONSULT EXPERTS (The Council)
# =============================================================================


def prompt_consult_experts(query: str, perspectives: list[str]) -> str:
    """
    HELPER: Convene a council of experts to generate raw arguments.

    Common perspective examples:
    - Ethics: 'Utilitarian Ethicist', 'Deontologist', 'Virtue Ethicist'
    - Science: 'Empirical Scientist', 'Skeptical Researcher', 'Domain Expert'
    - Law: 'Constitutional Scholar', 'Legal Realist', 'Civil Libertarian'
    - Policy: 'Economist', 'Sociologist', 'Public Health Expert'

    Integration guidance:
    - Use 'argument_for' to enrich Backing in Phase 2
    - Use 'argument_against' to seed Rebuttals in Phase 3
    """
    perspectives_str = ", ".join(perspectives)
    return f"""{SYSTEM_DIRECTIVE}

═══════════════════════════════════════════════════════════════════════════════
HELPER: CONSULT THE COUNCIL OF EXPERTS
═══════════════════════════════════════════════════════════════════════════════

QUERY: {query}

REQUIRED PERSPECTIVES (The Council):
{perspectives_str}

YOUR TASK:
You must simulate the viewpoints of these specific experts/personas.
For EACH perspective, provide:
1. A supporting argument (BACKING potential for Phase 2)
2. A dissenting argument (REBUTTAL potential for Phase 3)

This is NOT the final verdict. It is raw material generation for the Toulmin process.

INTEGRATION GUIDANCE:
- argument_for: Will be used to strengthen Warrant Backing in Phase 2
- argument_against: Will be used to identify Rebuttals in Phase 3
- key_citation: Provide authoritative sources for this perspective's view

OUTPUT SCHEMA:
{{
  "council_opinions": [
    {{
      "perspective": "string (e.g., 'Utilitarian Ethicist')",
      "argument_for": "string (strongest point in favor)",
      "argument_against": "string (strongest point against)",
      "key_citation": "string (a likely source/authority for this view)"
    }}
  ]
}}

EMIT JSON. NOTHING ELSE."""


# =============================================================================
# PHASE 1: DATA + CLAIM
# =============================================================================


def prompt_phase_one(query: str) -> str:
    """PHASE 1: Extract DATA and construct CLAIM. No hedging."""
    return f"""{SYSTEM_DIRECTIVE}

═══════════════════════════════════════════════════════════════════════════════
PHASE 1: DATA EXTRACTION + CLAIM CONSTRUCTION
═══════════════════════════════════════════════════════════════════════════════

QUERY: {query}

YOUR TASK:
You are forbidden from answering the query. You must ONLY:
1. Extract verifiable DATA (facts with citations)
2. Construct a falsifiable CLAIM based solely on that data

RULES:
- DATA must contain at least one fact.
- Each fact requires a citation (source + reference).
- CLAIM must be an assertion, NOT a question.
- CLAIM must NOT contain hedging words (might, could, perhaps, possibly).
- If you cannot find credible data, output: {{"error": "INSUFFICIENT_DATA"}}

OUTPUT SCHEMA:
{{
  "data": {{
    "facts": ["string"],
    "citations": [{{"source": "string", "reference": "string", "url": "string|null"}}],
    "evidence_type": "empirical|statistical|testimonial|documentary|expert"
  }},
  "claim": {{
    "statement": "string (min 10 chars, no hedging)",
    "scope": "universal|general|specific|singular"
  }}
}}

CITATION URL RULE:
- Include "url" ONLY if you know the exact URL with certainty.
- If unsure, set "url": null. NEVER hallucinate URLs.
- Prefer DOIs for academic papers (e.g., "https://doi.org/10.1234/...").

EMIT JSON. NOTHING ELSE."""


# =============================================================================
# PHASE 2: WARRANT + BACKING
# =============================================================================


def prompt_phase_two(query: str, data_json: str, claim_json: str) -> str:
    """PHASE 2: Construct logical bridge. Weak logic = crash."""
    return f"""{SYSTEM_DIRECTIVE}

═══════════════════════════════════════════════════════════════════════════════
PHASE 2: LOGICAL BRIDGE CONSTRUCTION
═══════════════════════════════════════════════════════════════════════════════

QUERY: {query}

INPUT DATA:
{data_json}

INPUT CLAIM:
{claim_json}

YOUR TASK:
You are a Logic Engine. You are forbidden from answering the question.
You must ONLY construct the logical bridge between DATA and CLAIM.

1. WARRANT: The general principle that connects data to claim.
   Format: "If X, then Y" or "When X, generally Y"
   CRITICAL: Must be a general rule, NOT a restatement of the Data.

2. BACKING: The authority that validates the warrant.
   Must be statutory, scientific, or expert authority with citations.
   Distinction: Warrant is the logic; Backing is the support for that logic.

STRENGTH ASSESSMENT (CRITICAL):
You MUST assess the strength of both WARRANT and BACKING:
- "absolute": Logically airtight. No reasonable counter.
- "strong": Solid reasoning. Minor exceptions possible.
- "weak": Speculative. Assumptions not validated. **THIS WILL CRASH THE ARGUMENT.**
- "irrelevant": Does not connect Data to Claim. **THIS WILL CRASH THE ARGUMENT.**

If the Data does not logically compel the Claim, you MUST mark strength as "weak".
Do not be charitable. Be ruthless.

OUTPUT SCHEMA:
{{
  "warrant": {{
    "principle": "string (min 20 chars)",
    "logic_type": "deductive|inductive|abductive",
    "strength": "absolute|strong|weak|irrelevant"
  }},
  "backing": {{
    "authority": "string (min 10 chars)",
    "citations": [{{"source": "string", "reference": "string", "url": "string|null"}}],
    "strength": "absolute|strong|weak|irrelevant"
  }}
}}

CITATION URL RULE:
- Include "url" ONLY if you know the exact URL with certainty.
- If unsure, set "url": null. NEVER hallucinate URLs.

EMIT JSON. NOTHING ELSE."""


# =============================================================================
# PHASE 3: REBUTTAL + QUALIFIER
# =============================================================================


def prompt_phase_three(
    query: str, data_json: str, claim_json: str, warrant_json: str, backing_json: str
) -> str:
    """PHASE 3: Attack the argument. Find the black swans."""
    return f"""{SYSTEM_DIRECTIVE}

═══════════════════════════════════════════════════════════════════════════════
PHASE 3: ADVERSARIAL STRESS TEST
═══════════════════════════════════════════════════════════════════════════════

QUERY: {query}

ARGUMENT CHAIN:
DATA: {data_json}
CLAIM: {claim_json}
WARRANT: {warrant_json}
BACKING: {backing_json}

YOUR TASK:
You are an adversary. Your job is to DESTROY this argument.
Find every weakness. Every edge case. Every "black swan."

1. REBUTTAL: Conditions where the warrant FAILS.
   - List specific exceptions (minimum 1).
   - Find counterexamples if they exist.
   - Be adversarial. Do not protect the argument.

2. QUALIFIER: Given the rebuttals, how certain is the claim?
   - Be honest. If rebuttals are devastating, confidence should be low.

STRENGTH ASSESSMENT FOR REBUTTAL:
- "absolute": The rebuttal completely destroys the argument. **CLAIM CANNOT STAND.**
- "strong": Significant weakness found. Claim is damaged.
- "weak": Minor edge cases only. Claim mostly holds.
- "irrelevant": No meaningful rebuttal found. (Be suspicious of this.)

OUTPUT SCHEMA:
{{
  "rebuttal": {{
    "exceptions": ["string (each min 10 chars)"],
    "counterexamples": ["string"],
    "strength": "absolute|strong|weak|irrelevant"
  }},
  "qualifier": {{
    "degree": "certainly|presumably|probably|possibly|apparently",
    "confidence_pct": 0-100,
    "rationale": "string (min 10 chars)"
  }}
}}

EMIT JSON. NOTHING ELSE."""


# =============================================================================
# PHASE 4: VERDICT
# =============================================================================


def prompt_phase_four(
    query: str,
    data_json: str,
    claim_json: str,
    warrant_json: str,
    backing_json: str,
    rebuttal_json: str,
    qualifier_json: str,
) -> str:
    """PHASE 4: Render judgment. No appeals."""
    return f"""{SYSTEM_DIRECTIVE}

═══════════════════════════════════════════════════════════════════════════════
PHASE 4: VERDICT
═══════════════════════════════════════════════════════════════════════════════

QUERY: {query}

COMPLETE ARGUMENT CHAIN:
1. DATA: {data_json}
2. CLAIM: {claim_json}
3. WARRANT: {warrant_json}
4. BACKING: {backing_json}
5. REBUTTAL: {rebuttal_json}
6. QUALIFIER: {qualifier_json}

YOUR TASK:
Render final judgment. This is a court. There are no appeals.

STATUS OPTIONS:
- "sustained": The argument holds. Claim is validated.
- "overruled": The argument fails. Claim is rejected.
- "remanded": Insufficient evidence. Requires further investigation.

CONSISTENCY REQUIREMENTS:
- If rebuttal.strength == "absolute", verdict MUST be "overruled".
- If qualifier.confidence_pct < 30, verdict SHOULD be "overruled" or "remanded".
- If warrant.strength or backing.strength was "weak", you should not have reached this phase.

OUTPUT SCHEMA:
{{
  "verdict": {{
    "status": "sustained|overruled|remanded",
    "reasoning": "string (min 50 chars, must reference the chain)",
    "final_statement": "string (min 10 chars)"
  }}
}}

EMIT JSON. NOTHING ELSE."""


# =============================================================================
# PHASE 5: FORMAT REPORT (Optional)
# =============================================================================


def prompt_format_report(
    query: str,
    data_json: str,
    claim_json: str,
    warrant_json: str,
    backing_json: str,
    rebuttal_json: str,
    qualifier_json: str,
    verdict_json: str,
) -> str:
    """PHASE 5 (Optional): Format the complete analysis as a readable report."""
    return f"""You are a report formatter. Transform this Toulmin argument analysis into a clean, readable markdown report.

═══════════════════════════════════════════════════════════════════════════════
TOULMIN ANALYSIS REPORT
═══════════════════════════════════════════════════════════════════════════════

QUERY: {query}

RAW ANALYSIS DATA:
- DATA: {data_json}
- CLAIM: {claim_json}
- WARRANT: {warrant_json}
- BACKING: {backing_json}
- REBUTTAL: {rebuttal_json}
- QUALIFIER: {qualifier_json}
- VERDICT: {verdict_json}

YOUR TASK:
Generate a well-formatted markdown report with the following structure:

# Toulmin Analysis: [Short version of query]

## Verdict: [SUSTAINED/OVERRULED/REMANDED] [appropriate emoji]

> [One-sentence final statement from verdict]

---

## The Claim
[The claim statement, formatted nicely]

**Scope**: [scope] | **Confidence**: [X]%

---

## Evidence (Data)
[List each fact as a bullet point]

### Sources
[For each citation, format as:]
- **[Source]**: [Reference] [If URL exists, add as markdown link]

---

## Logical Bridge

### Warrant
> [The warrant principle in a blockquote]

**Logic Type**: [type] | **Strength**: [strength]

### Backing
[The backing authority statement]

**Sources**: [List backing citations with links if available]

---

## Stress Test

### Rebuttals Found
[List each exception as a numbered item]

### Counterexamples
[List counterexamples if any, or "None identified"]

**Rebuttal Strength**: [strength]

---

## Confidence Assessment
**Degree**: [qualifier degree] | **Confidence**: [X]%

[Qualifier rationale]

---

## Final Reasoning
[The full verdict reasoning]

---
*Analysis generated using the Toulmin argumentation model*

OUTPUT THE MARKDOWN REPORT. Nothing else."""
