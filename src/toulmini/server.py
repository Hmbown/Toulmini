"""
Toulmini MCP Server.

A Logic Compiler for arguments. Bad logic = crash.
"""

from mcp.server.fastmcp import FastMCP

from .prompts import (
    prompt_phase_one,
    prompt_phase_two,
    prompt_phase_three,
    prompt_phase_four,
)

# === SERVER ===
mcp = FastMCP("toulmini")


@mcp.tool()
def initiate_toulmin_sequence(query: str) -> str:
    """
    PHASE 1: Begin Toulmin analysis.

    Returns a prompt that forces the LLM to extract DATA and construct a CLAIM.
    The LLM must execute this prompt and return JSON.

    Args:
        query: The proposition to analyze.

    Returns:
        Prompt for Phase 1 execution.
    """
    if len(query.strip()) < 5:
        return '{"error": "QUERY_TOO_SHORT"}'
    return prompt_phase_one(query.strip())


@mcp.tool()
def inject_logic_bridge(query: str, data_json: str, claim_json: str) -> str:
    """
    PHASE 2: Construct the logical bridge.

    Returns a prompt that forces the LLM to generate WARRANT and BACKING.
    WARNING: If strength is 'weak', the argument will crash when validated.

    Args:
        query: Original query.
        data_json: JSON from Phase 1 (data object).
        claim_json: JSON from Phase 1 (claim object).

    Returns:
        Prompt for Phase 2 execution.
    """
    if not data_json or not claim_json:
        return '{"error": "MISSING_PHASE_1_OUTPUT"}'
    return prompt_phase_two(query, data_json, claim_json)


@mcp.tool()
def stress_test_argument(
    query: str,
    data_json: str,
    claim_json: str,
    warrant_json: str,
    backing_json: str
) -> str:
    """
    PHASE 3: Adversarial stress test.

    Returns a prompt that forces the LLM to find REBUTTALS and assign a QUALIFIER.
    The LLM must actively try to destroy the argument.

    Args:
        query: Original query.
        data_json: JSON from Phase 1.
        claim_json: JSON from Phase 1.
        warrant_json: JSON from Phase 2.
        backing_json: JSON from Phase 2.

    Returns:
        Prompt for Phase 3 execution.
    """
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
        return f'{{"error": "MISSING_COMPONENTS", "missing": {missing}}}'

    return prompt_phase_three(query, data_json, claim_json, warrant_json, backing_json)


@mcp.tool()
def render_verdict(
    query: str,
    data_json: str,
    claim_json: str,
    warrant_json: str,
    backing_json: str,
    rebuttal_json: str,
    qualifier_json: str
) -> str:
    """
    PHASE 4: Final verdict.

    Returns a prompt that forces the LLM to render judgment.
    Status: sustained | overruled | remanded

    Args:
        query: Original query.
        data_json: JSON from Phase 1.
        claim_json: JSON from Phase 1.
        warrant_json: JSON from Phase 2.
        backing_json: JSON from Phase 2.
        rebuttal_json: JSON from Phase 3.
        qualifier_json: JSON from Phase 3.

    Returns:
        Prompt for Phase 4 execution.
    """
    required = [data_json, claim_json, warrant_json, backing_json, rebuttal_json, qualifier_json]
    if not all(required):
        return '{"error": "INCOMPLETE_CHAIN"}'

    return prompt_phase_four(
        query, data_json, claim_json, warrant_json,
        backing_json, rebuttal_json, qualifier_json
    )


def main():
    """Run the server."""
    mcp.run()


if __name__ == "__main__":
    main()
