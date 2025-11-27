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

## CIRCUIT BREAKERS

The analysis chain will terminate early if:
- Warrant strength is "weak" or "irrelevant"
- Backing strength is "weak" or "irrelevant"

If terminated, explain why and present partial results.

## MANUAL STEP-BY-STEP (Only if requested)

If the user explicitly asks for manual control (e.g., "walk me through each step"
or "let me see each phase"), then pause after each phase for user confirmation.

## QUICK REFERENCE

| Phase | Tool | Extracts |
|-------|------|----------|
| 1 | initiate_toulmin_sequence | data, claim |
| 2 | inject_logic_bridge | warrant, backing |
| 3 | stress_test_argument | rebuttal, qualifier |
| 4 | render_verdict | verdict |
| 5 | format_analysis_report | formatted report |
"""

mcp = FastMCP("toulmini", instructions=MCP_INSTRUCTIONS)


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


def main():
    """Run the Toulmini MCP server."""
    logger.info("Toulmini Logic Harness starting...")
    logger.info(
        "5 tools available: initiate_toulmin_sequence → inject_logic_bridge → "
        "stress_test_argument → render_verdict → format_analysis_report (optional)"
    )
    mcp.run()


if __name__ == "__main__":
    main()
