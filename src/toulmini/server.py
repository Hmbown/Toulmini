"""Toulmini MCP Server - Toulmin Argumentation Model."""

from __future__ import annotations
import json

from mcp.server.fastmcp import FastMCP

from .tools import (
    initiate_toulmin_sequence,
    inject_logic_bridge,
    stress_test_argument,
    render_verdict,
)
from .exceptions import ToulminiError


# Initialize FastMCP server
mcp = FastMCP("toulmini")


@mcp.tool()
def initiate_toulmin_sequence_tool(query: str) -> str:
    """
    Start a Toulmin analysis. Phase 1: Generate DATA and CLAIM.

    This tool initiates a 4-phase Toulmin argumentation sequence.
    It returns a prompt that forces the LLM to output structured JSON
    containing the foundational DATA (evidence) and CLAIM (assertion).

    Args:
        query: The topic or question to analyze (minimum 10 characters).
               Example: "Is remote work more productive than office work?"

    Returns:
        A JSON object containing:
        - tool: The tool name
        - phase: 1
        - query: The original query
        - prompt: The prompt to execute for Phase 1
        - expected_output: Description of expected JSON format
        - next_tool: The next tool to call (inject_logic_bridge)
    """
    try:
        result = initiate_toulmin_sequence(query)
        return json.dumps(result, indent=2)
    except ToulminiError as e:
        return json.dumps({"error": e.to_dict()}, indent=2)
    except Exception as e:
        return json.dumps({"error": {"message": str(e)}}, indent=2)


@mcp.tool()
def inject_logic_bridge_tool(
    data_json: str,
    claim_json: str,
    query: str
) -> str:
    """
    Phase 2: Generate WARRANT and BACKING from Data and Claim.

    This tool creates the logical bridge between evidence and conclusion.
    WARRANT: The reasoning principle (If X, then Y)
    BACKING: Authoritative support for the warrant

    WARNING: If the LLM outputs backing.strength as 'weak', the argument
    chain will be REJECTED and no further progress is possible.

    Args:
        data_json: JSON string of the Data object from Phase 1.
                   Must contain: facts, citations, evidence_type
        claim_json: JSON string of the Claim object from Phase 1.
                    Must contain: statement, scope
        query: The original query for context

    Returns:
        A JSON object containing the prompt for Warrant + Backing generation.
        If backing is weak, returns an error with rejection notice.
    """
    try:
        result = inject_logic_bridge(data_json, claim_json, query)
        return json.dumps(result, indent=2)
    except ToulminiError as e:
        return json.dumps({"error": e.to_dict()}, indent=2)
    except Exception as e:
        return json.dumps({"error": {"message": str(e)}}, indent=2)


@mcp.tool()
def stress_test_argument_tool(
    data_json: str,
    claim_json: str,
    warrant_json: str,
    backing_json: str,
    query: str
) -> str:
    """
    Phase 3: Generate REBUTTAL and QUALIFIER by stress-testing the argument.

    This tool forces adversarial analysis to find weaknesses:
    REBUTTAL: Edge cases where the warrant fails ("black swans")
    QUALIFIER: Degree of certainty (certainly, presumably, probably, etc.)

    Args:
        data_json: JSON from Phase 1 (data object)
        claim_json: JSON from Phase 1 (claim object)
        warrant_json: JSON from Phase 2 (warrant object)
        backing_json: JSON from Phase 2 (backing object)
        query: The original query for context

    Returns:
        A JSON object containing the prompt for Rebuttal + Qualifier generation.
        Rejects if backing strength was 'weak'.
    """
    try:
        result = stress_test_argument(
            data_json, claim_json, warrant_json, backing_json, query
        )
        return json.dumps(result, indent=2)
    except ToulminiError as e:
        return json.dumps({"error": e.to_dict()}, indent=2)
    except Exception as e:
        return json.dumps({"error": {"message": str(e)}}, indent=2)


@mcp.tool()
def render_verdict_tool(
    data_json: str,
    claim_json: str,
    warrant_json: str,
    backing_json: str,
    rebuttal_json: str,
    qualifier_json: str,
    query: str
) -> str:
    """
    Final Phase: Render VERDICT synthesizing the complete 6-part argument.

    This tool produces the final synthesis determining if the claim stands.
    VERDICT outcomes:
    - STANDS: Claim survives scrutiny
    - FALLS: Claim is fatally undermined
    - QUALIFIED: Claim holds only under specific conditions

    Args:
        data_json: JSON from Phase 1 (data object)
        claim_json: JSON from Phase 1 (claim object)
        warrant_json: JSON from Phase 2 (warrant object)
        backing_json: JSON from Phase 2 (backing object)
        rebuttal_json: JSON from Phase 3 (rebuttal object)
        qualifier_json: JSON from Phase 3 (qualifier object)
        query: The original query

    Returns:
        A JSON object containing the prompt for final Verdict synthesis.
        Requires all 6 prior components to be present.
    """
    try:
        result = render_verdict(
            data_json, claim_json, warrant_json,
            backing_json, rebuttal_json, qualifier_json, query
        )
        return json.dumps(result, indent=2)
    except ToulminiError as e:
        return json.dumps({"error": e.to_dict()}, indent=2)
    except Exception as e:
        return json.dumps({"error": {"message": str(e)}}, indent=2)


def main():
    """Run the Toulmini MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
