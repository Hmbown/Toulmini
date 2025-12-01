"""
Toulmini MCP Server.

A Logic Harness for arguments. Bad logic = crash.
Implements Stephen Toulmin's argumentation model across 4 sequential phases.
"""

import logging
import sys

from mcp.server.fastmcp import FastMCP

from .prompts import (
    prompt_phase_one,
    prompt_phase_two,
    prompt_phase_three,
    prompt_phase_four,
    prompt_format_report,
    prompt_consult_experts,
)

# === LOGGING (stderr only - never stdout for STDIO servers) ===
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("toulmini")

# === SERVER ===

MCP_INSTRUCTIONS = """
Toulmini is a Logic Harness for rigorous argument analysis using the Toulmin model.

## AUTOMATIC WORKFLOW (Recommended)

**IMPORTANT**: When a user asks you to analyze an argument or question,
DO NOT stop after each phase. Continue automatically through ALL phases
unless the user explicitly asks for step-by-step control.

When the user says things like:
- "Analyze this argument: [claim]"
- "Is [statement] true?"
- "Evaluate: [proposition]"
- "Use Toulmin to analyze: [query]"

You should automatically:
1. Call `initiate_toulmin_sequence` → Execute the returned prompt → Extract data_json and claim_json
2. Call `inject_logic_bridge` → Execute the returned prompt → Extract warrant_json and backing_json
3. Call `stress_test_argument` → Execute the returned prompt → Extract rebuttal_json and qualifier_json
4. Call `render_verdict` → Execute the returned prompt → Extract verdict_json
5. Call `format_analysis_report` → Execute the returned prompt → Present the formatted report to user

Each tool returns a PROMPT. You must EXECUTE that prompt to get JSON output,
then pass the extracted components to the next phase.

## THE COUNCIL (Optional but Powerful)

### When to Convene the Council

Use `consult_field_experts` BEFORE Phase 2 or Phase 3 when:
- **Ethical Dilemmas**: Query involves moral reasoning or contested values
  - Example perspectives: ['Utilitarian Ethicist', 'Deontologist', 'Virtue Ethicist']
- **Scientific Claims**: Query requires domain expertise or empirical validation
  - Example perspectives: ['Empiricist', 'Domain Expert', 'Skeptical Scientist']
- **Complex Policy**: Query spans multiple disciplines or stakeholder viewpoints
  - Example perspectives: ['Economist', 'Sociologist', 'Policy Analyst']
- **Legal Questions**: Query involves rights, precedent, or interpretation
  - Example perspectives: ['Constitutional Scholar', 'Legal Realist', 'Civil Rights Advocate']

### How to Integrate Council Output

**Council → Phase 2 (Backing):**
Use the `argument_for` from Council perspectives to enrich your Backing authority.

**Council → Phase 3 (Rebuttals):**
Use the `argument_against` from Council perspectives to identify stronger Rebuttals.

**Integration Pattern:**
1. Convene Council with 2-3 relevant perspectives
2. Execute the returned prompt to get `council_opinions`
3. In Phase 2: Reference Council backing in your authority statement
4. In Phase 3: Use Council critiques as rebuttal exceptions

### Council Best Practices

**DO:**
- Choose perspectives that genuinely differ in methodology or values
- Use specific expert roles, not generic labels (❌ "Expert" → ✓ "Neuroscientist")
- Integrate Council insights into your reasoning, don't just copy them

**DON'T:**
- Use the Council for simple factual queries with clear answers
- Choose redundant perspectives that would give identical arguments
- Skip integration—if you convene the Council, USE the output

## CIRCUIT BREAKERS

The analysis chain will terminate early if:
- Warrant strength is "weak" or "irrelevant"
- Backing strength is "weak" or "irrelevant"

If terminated, explain why and present partial results.

## MANUAL STEP-BY-STEP (Only if requested)

If the user explicitly asks for manual control (e.g., "walk me through each step"
or "let me see each phase"), then pause after each phase for user confirmation.

## QUICK REFERENCE

| Phase | Tool | Extracts | Notes |
|-------|------|----------|-------|
| Helper | consult_field_experts | council_opinions | Use for complex/contested queries |
| 1 | initiate_toulmin_sequence | data, claim | Foundation phase |
| 2 | inject_logic_bridge | warrant, backing | Integrate Council backing here |
| 3 | stress_test_argument | rebuttal, qualifier | Integrate Council rebuttals here |
| 4 | render_verdict | verdict | Final judgment |
| 5 | format_analysis_report | formatted report | Optional: Human-readable output |
"""

mcp = FastMCP("toulmini", instructions=MCP_INSTRUCTIONS)


@mcp.tool()
def consult_field_experts(query: str, perspectives: list[str]) -> str:
    """
    HELPER: Convene a 'Council of Experts' to generate raw arguments.

    Use this OPTIONALLY before Phase 2 (to find Backing) or Phase 3 (to find Rebuttals)
    when the topic requires specialized domain knowledge or diverse ethical viewpoints.

    Args:
        query: The proposition to analyze.
        perspectives: A list of personas or fields to simulate.
            Example: ["Utilitarian Ethicist", "Corporate Lawyer", "Environmental Scientist"]

    Returns:
        A prompt. Execute it to get JSON with arguments for and against from each perspective.
    """
    logger.info(f"Council convened: {perspectives} on '{query[:30]}...'")
    if not perspectives:
        return '{"error": "NO_PERSPECTIVES_PROVIDED"}'
    return prompt_consult_experts(query, perspectives)


@mcp.tool()
def initiate_toulmin_sequence(query: str) -> str:
    """
    PHASE 1: Begin Toulmin analysis - Extract DATA and construct CLAIM.

    This is the FIRST tool in a 4-phase sequence. Call tools in order:
    1. initiate_toulmin_sequence → 2. inject_logic_bridge → 3. stress_test_argument → 4. render_verdict

    The returned prompt forces JSON-only output. Execute the prompt and save the result.

    Args:
        query: The proposition to analyze (e.g., "Is remote work more productive?")

    Returns:
        A prompt. Execute it to get JSON like:
        {"data": {"facts": [...], "citations": [...], "evidence_type": "..."}, "claim": {"statement": "...", "scope": "..."}}

    Example flow:
        1. Call this tool with query="Should AI be regulated?"
        2. Execute the returned prompt
        3. Save the data_json and claim_json from the response
        4. Pass them to inject_logic_bridge
    """
    logger.info(f"Phase 1 initiated: {query[:50]}...")
    if len(query.strip()) < 5:
        return '{"error": "QUERY_TOO_SHORT"}'
    return prompt_phase_one(query.strip())


@mcp.tool()
def inject_logic_bridge(query: str, data_json: str, claim_json: str) -> str:
    """
    PHASE 2: Construct the logical bridge - Generate WARRANT and BACKING.

    This is the SECOND tool. Requires output from Phase 1.
    WARNING: If strength is 'weak' or 'irrelevant', the argument chain terminates.

    Args:
        query: Original query string
        data_json: The "data" object from Phase 1 as a JSON string
            Example: '{"facts": ["Study X shows..."], "citations": [{"source": "...", "reference": "..."}], "evidence_type": "empirical"}'
        claim_json: The "claim" object from Phase 1 as a JSON string
            Example: '{"statement": "Remote work increases productivity", "scope": "general"}'

    Returns:
        A prompt. Execute it to get JSON like:
        {"warrant": {"principle": "If X then Y", "logic_type": "deductive|inductive|abductive", "strength": "..."}, "backing": {"authority": "...", "citations": [...], "strength": "..."}}

    Strength levels: "absolute" | "strong" | "weak" | "irrelevant"
    - "weak" or "irrelevant" = ARGUMENT TERMINATES
    """
    logger.info("Phase 2 initiated: Constructing logical bridge")
    if not data_json or not claim_json:
        logger.warning("Phase 2 rejected: Missing Phase 1 output")
        return '{"error": "MISSING_PHASE_1_OUTPUT"}'
    return prompt_phase_two(query, data_json, claim_json)


@mcp.tool()
def stress_test_argument(
    query: str, data_json: str, claim_json: str, warrant_json: str, backing_json: str
) -> str:
    """
    PHASE 3: Adversarial stress test - Find REBUTTALS and assign QUALIFIER.

    This is the THIRD tool. Requires output from Phases 1 and 2.
    The LLM must actively try to DESTROY the argument. Find every weakness.

    Args:
        query: Original query string
        data_json: The "data" object from Phase 1 as JSON string
        claim_json: The "claim" object from Phase 1 as JSON string
        warrant_json: The "warrant" object from Phase 2 as JSON string
            Example: '{"principle": "If X then Y", "logic_type": "deductive", "strength": "strong"}'
        backing_json: The "backing" object from Phase 2 as JSON string
            Example: '{"authority": "Peer-reviewed studies...", "citations": [...], "strength": "strong"}'

    Returns:
        A prompt. Execute it to get JSON like:
        {"rebuttal": {"exceptions": [...], "counterexamples": [...], "strength": "..."}, "qualifier": {"degree": "...", "confidence_pct": 0-100, "rationale": "..."}}

    Qualifier degrees: "certainly" | "presumably" | "probably" | "possibly" | "apparently"
    If rebuttal.strength == "absolute", the ARGUMENT IS DESTROYED.
    """
    logger.info("Phase 3 initiated: Adversarial stress test")
    missing = []
    if not data_json:
        missing.append("data")
    if not claim_json:
        missing.append("claim")
    if not warrant_json:
        missing.append("warrant")
    if not backing_json:
        missing.append("backing")

    if missing:
        logger.warning(f"Phase 3 rejected: Missing components {missing}")
        return f'{{"error": "MISSING_COMPONENTS", "missing": {missing}}}'

    # CIRCUIT BREAKER: Validate Warrant and Backing strength
    if error_response := _validate_logic_bridge(warrant_json, backing_json):
        return error_response

    return prompt_phase_three(query, data_json, claim_json, warrant_json, backing_json)


def _validate_logic_bridge(warrant_json: str, backing_json: str) -> str | None:
    """Helper to validate Warrant and Backing strength. Returns error JSON if failed."""
    try:
        # We need to parse the JSON strings into dicts first, but Pydantic's model_validate_json handles strings directly?
        # The input is a JSON string representing the object.
        # Let's import the models inside the function to avoid circular imports if any,
        # though top-level import is better. I'll add top-level imports in a separate edit.
        from .models.components import Warrant, Backing

        warrant = Warrant.model_validate_json(warrant_json)
        warrant.logic_check()

        backing = Backing.model_validate_json(backing_json)
        backing.logic_check()

    except ValueError as e:
        logger.error(f"CIRCUIT BREAKER TRIGGERED: {str(e)}")
        return f'{{"error": "TERMINATION_SIGNAL", "reason": "{str(e)}"}}'
    except Exception as e:
        logger.error(f"Validation error: {e}")
        return f'{{"error": "VALIDATION_ERROR", "reason": "{str(e)}"}}'

    return None


@mcp.tool()
def render_verdict(
    query: str,
    data_json: str,
    claim_json: str,
    warrant_json: str,
    backing_json: str,
    rebuttal_json: str,
    qualifier_json: str,
) -> str:
    """
    PHASE 4: Final verdict - Render judgment on the complete argument chain.

    This is the FOURTH and FINAL tool. Requires all 6 components from Phases 1-3.
    This is a court. There are no appeals.

    Args:
        query: Original query string
        data_json: The "data" object from Phase 1 as JSON string
        claim_json: The "claim" object from Phase 1 as JSON string
        warrant_json: The "warrant" object from Phase 2 as JSON string
        backing_json: The "backing" object from Phase 2 as JSON string
        rebuttal_json: The "rebuttal" object from Phase 3 as JSON string
            Example: '{"exceptions": [...], "counterexamples": [...], "strength": "strong"}'
        qualifier_json: The "qualifier" object from Phase 3 as JSON string
            Example: '{"degree": "probably", "confidence_pct": 65, "rationale": "..."}'

    Returns:
        A prompt. Execute it to get JSON like:
        {"verdict": {"status": "sustained|overruled|remanded", "reasoning": "...", "final_statement": "..."}}

    Verdict status:
        - "sustained": Argument holds. Claim validated.
        - "overruled": Argument fails. Claim rejected.
        - "remanded": Insufficient evidence. Requires further investigation.

    Consistency rules enforced:
        - If rebuttal.strength == "absolute" → verdict MUST be "overruled"
        - If qualifier.confidence_pct < 30 → verdict SHOULD be "overruled" or "remanded"
    """
    logger.info("Phase 4 initiated: Rendering final verdict")
    required = [
        data_json,
        claim_json,
        warrant_json,
        backing_json,
        rebuttal_json,
        qualifier_json,
    ]
    if not all(required):
        logger.warning("Phase 4 rejected: Incomplete argument chain")
        return '{"error": "INCOMPLETE_CHAIN"}'

    # CIRCUIT BREAKER: Validate Warrant and Backing strength again (safety net)
    if error_response := _validate_logic_bridge(warrant_json, backing_json):
        return error_response

    return prompt_phase_four(
        query,
        data_json,
        claim_json,
        warrant_json,
        backing_json,
        rebuttal_json,
        qualifier_json,
    )


@mcp.tool()
def format_analysis_report(
    query: str,
    data_json: str,
    claim_json: str,
    warrant_json: str,
    backing_json: str,
    rebuttal_json: str,
    qualifier_json: str,
    verdict_json: str,
) -> str:
    """
    PHASE 5 (Optional): Format the complete analysis as a readable markdown report.

    This is an OPTIONAL tool to call after render_verdict (Phase 4).
    It transforms all the JSON outputs into a nicely formatted, human-readable report.

    Args:
        query: Original query string
        data_json: The "data" object from Phase 1 as JSON string
        claim_json: The "claim" object from Phase 1 as JSON string
        warrant_json: The "warrant" object from Phase 2 as JSON string
        backing_json: The "backing" object from Phase 2 as JSON string
        rebuttal_json: The "rebuttal" object from Phase 3 as JSON string
        qualifier_json: The "qualifier" object from Phase 3 as JSON string
        verdict_json: The "verdict" object from Phase 4 as JSON string

    Returns:
        A prompt that will generate a well-formatted markdown report summarizing
        the entire Toulmin analysis with proper headings, sections, and styling.

    Example:
        Call this tool with all the accumulated JSON from Phases 1-4 to get a final report.
    """
    logger.info("Phase 5 initiated: Formatting analysis report")
    required = [
        data_json,
        claim_json,
        warrant_json,
        backing_json,
        rebuttal_json,
        qualifier_json,
        verdict_json,
    ]
    if not all(required):
        logger.warning("Phase 5 rejected: Incomplete argument chain")
        return '{"error": "INCOMPLETE_CHAIN"}'

    return prompt_format_report(
        query,
        data_json,
        claim_json,
        warrant_json,
        backing_json,
        rebuttal_json,
        qualifier_json,
        verdict_json,
    )


@mcp.resource("toulmin://model")
def toulmin_model_resource() -> str:
    """
    Returns a detailed explanation of the Toulmin Argumentation Model.
    Useful for LLMs to "read" to understand the definitions of Data, Claim, Warrant, etc.
    """
    return """
# The Toulmin Argumentation Model

Stephen Toulmin's model (1958) breaks arguments into six functional components.
It moves beyond the syllogism (Premise -> Conclusion) to model how practical arguments actually work.

## 1. DATA (Grounds)
The raw facts or evidence used to support the claim.
- **Nature**: Empirical, statistical, testimonial, or documentary.
- **Requirement**: Must be verifiable and cited.
- **Example**: "It is raining outside" (Visual observation).

## 2. CLAIM
The assertion or conclusion that is being argued for.
- **Nature**: The destination of the argument.
- **Requirement**: Must be falsifiable.
- **Example**: "I should take an umbrella."

## 3. WARRANT
The logical bridge that connects Data to Claim.
- **Nature**: A general principle, rule, or license.
- **Structure**: "Since [Warrant], therefore [Claim]."
- **Example**: "Since getting wet is undesirable..." (Implicit principle).

## 4. BACKING
The authority or support for the Warrant.
- **Nature**: Why should we believe the Warrant?
- **Requirement**: Statutory, scientific, or expert authority.
- **Example**: "Hygiene standards dictate staying dry prevents illness."

## 5. REBUTTAL
Conditions where the Warrant does not hold.
- **Nature**: Exceptions, counter-examples, or "black swans".
- **Requirement**: Must be specific conditions, not just "it might be wrong".
- **Example**: "Unless I am going swimming anyway."

## 6. QUALIFIER
The degree of certainty attached to the Claim.
- **Nature**: Modality (presumably, possibly, certainly).
- **Requirement**: Must reflect the strength of Rebuttals.
- **Example**: "Probably."

## The Verdict
In Toulmini, the final output is a Verdict:
- **SUSTAINED**: The argument holds up to scrutiny.
- **OVERRULED**: The argument fails (logic weak, rebuttals strong).
- **REMANDED**: Insufficient data to decide.
"""


@mcp.prompt("toulmin-help")
def toulmin_help_prompt() -> str:
    """
    Returns a prompt that explains how to use the Toulmini tools.
    """
    return """
You are a helpful assistant explaining how to use the Toulmini Logic Harness.

Toulmini is NOT a chatbot. It is a strict, 4-phase logic engine.
To analyze an argument, you must use the tools in this exact order:

(Optional) **consult_field_experts(query, perspectives)**
   - Convene a "Council" to generate diverse viewpoints/backing.
   - Use this if the topic is complex or requires domain expertise.

1. **initiate_toulmin_sequence(query)**
   - Extracts DATA and constructs the CLAIM.
   - *Output*: JSON with data and claim.

2. **inject_logic_bridge(query, data, claim)**
   - Constructs the WARRANT and BACKING.
   - *Output*: JSON with warrant and backing.
   - *Note*: If logic is weak, it crashes here.

3. **stress_test_argument(query, data, claim, warrant, backing)**
   - Finds REBUTTALS and assigns a QUALIFIER.
   - *Output*: JSON with rebuttal and qualifier.

4. **render_verdict(...)**
   - Passes final judgment (SUSTAINED, OVERRULED, REMANDED).
   - *Output*: JSON with verdict.

5. **format_analysis_report(...)** (Optional)
   - Creates a nice Markdown report.

**Tip**: Always pass the JSON output from the previous step into the next step.
"""


def main():
    """Run the Toulmini MCP server."""
    logger.info("Toulmini Logic Harness starting...")
    logger.info(
        "5 tools available: initiate_toulmin_sequence → inject_logic_bridge → "
        "stress_test_argument → render_verdict → format_analysis_report (optional)"
    )
    logger.info("Resources: toulmin://model")
    logger.info("Prompts: toulmin-help")
    mcp.run()


if __name__ == "__main__":
    main()
