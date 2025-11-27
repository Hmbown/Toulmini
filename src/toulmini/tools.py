"""Tool implementations for the Toulmini MCP server."""

from __future__ import annotations
import json
from typing import Any, Dict

from .exceptions import DependencyError, OutputFormatError
from .prompts import (
    initiate_toulmin_prompt,
    inject_logic_bridge_prompt,
    stress_test_argument_prompt,
    render_verdict_prompt,
)


def _validate_json(json_str: str, field_name: str) -> Dict[str, Any]:
    """Validate and parse JSON string."""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        raise OutputFormatError(
            expected_format="JSON",
            received_preview=json_str[:200] if json_str else "(empty)",
            suggestion=f"The {field_name} must be valid JSON. Error: {e}"
        )


def initiate_toulmin_sequence(query: str) -> Dict[str, Any]:
    """
    Start a Toulmin analysis. Phase 1: Generate DATA and CLAIM.

    Args:
        query: The topic or question to analyze (min 10 characters)

    Returns:
        A dict containing the prompt that forces structured JSON output.
    """
    if not query or len(query.strip()) < 10:
        raise ValueError("Query must be at least 10 characters")

    prompt = initiate_toulmin_prompt(query.strip())

    return {
        "tool": "initiate_toulmin_sequence",
        "phase": 1,
        "query": query.strip(),
        "prompt": prompt,
        "expected_output": "JSON with 'data' and 'claim' objects",
        "next_tool": "inject_logic_bridge"
    }


def inject_logic_bridge(
    data_json: str,
    claim_json: str,
    query: str
) -> Dict[str, Any]:
    """
    Phase 2: Generate WARRANT and BACKING from Data and Claim.

    Args:
        data_json: JSON string of the Data from Phase 1
        claim_json: JSON string of the Claim from Phase 1
        query: Original query for context

    Returns:
        A dict containing the prompt for Warrant + Backing generation.
        WARNING: Will be REJECTED if backing strength is 'weak'.
    """
    # Validate dependencies
    missing = []
    if not data_json or data_json.strip() == "":
        missing.append("data")
    if not claim_json or claim_json.strip() == "":
        missing.append("claim")

    if missing:
        raise DependencyError(
            tool_name="inject_logic_bridge",
            missing_dependencies=missing,
            suggestion="Complete Phase 1 (initiate_toulmin_sequence) first"
        )

    # Validate JSON format
    _validate_json(data_json, "data")
    _validate_json(claim_json, "claim")

    prompt = inject_logic_bridge_prompt(data_json, claim_json, query)

    return {
        "tool": "inject_logic_bridge",
        "phase": 2,
        "query": query,
        "prompt": prompt,
        "expected_output": "JSON with 'warrant' and 'backing' objects",
        "warning": "If backing.strength is 'weak', the chain will be REJECTED",
        "next_tool": "stress_test_argument"
    }


def stress_test_argument(
    data_json: str,
    claim_json: str,
    warrant_json: str,
    backing_json: str,
    query: str
) -> Dict[str, Any]:
    """
    Phase 3: Generate REBUTTAL and QUALIFIER by stress-testing the argument.

    Args:
        data_json: JSON from Phase 1
        claim_json: JSON from Phase 1
        warrant_json: JSON from Phase 2
        backing_json: JSON from Phase 2
        query: Original query for context

    Returns:
        A dict containing the prompt for Rebuttal + Qualifier generation.
    """
    # Validate all dependencies
    missing = []
    if not data_json or data_json.strip() == "":
        missing.append("data")
    if not claim_json or claim_json.strip() == "":
        missing.append("claim")
    if not warrant_json or warrant_json.strip() == "":
        missing.append("warrant")
    if not backing_json or backing_json.strip() == "":
        missing.append("backing")

    if missing:
        raise DependencyError(
            tool_name="stress_test_argument",
            missing_dependencies=missing,
            suggestion="Complete Phase 1 and Phase 2 before stress testing"
        )

    # Validate JSON format
    _validate_json(data_json, "data")
    _validate_json(claim_json, "claim")
    _validate_json(warrant_json, "warrant")
    backing_dict = _validate_json(backing_json, "backing")

    # Check backing strength - provide early warning
    backing_strength = backing_dict.get("strength", "unknown")
    if backing_strength == "weak":
        raise DependencyError(
            tool_name="stress_test_argument",
            missing_dependencies=["strong backing"],
            suggestion="Backing strength is 'weak'. The argument chain is REJECTED. "
                       "Provide stronger authoritative support before proceeding."
        )

    prompt = stress_test_argument_prompt(
        data_json, claim_json, warrant_json, backing_json, query
    )

    return {
        "tool": "stress_test_argument",
        "phase": 3,
        "query": query,
        "prompt": prompt,
        "expected_output": "JSON with 'rebuttal' and 'qualifier' objects",
        "next_tool": "render_verdict"
    }


def render_verdict(
    data_json: str,
    claim_json: str,
    warrant_json: str,
    backing_json: str,
    rebuttal_json: str,
    qualifier_json: str,
    query: str
) -> Dict[str, Any]:
    """
    Final Phase: Render VERDICT synthesizing the complete 6-part argument.

    Args:
        data_json: JSON from Phase 1
        claim_json: JSON from Phase 1
        warrant_json: JSON from Phase 2
        backing_json: JSON from Phase 2
        rebuttal_json: JSON from Phase 3
        qualifier_json: JSON from Phase 3
        query: Original query

    Returns:
        A dict containing the prompt for final Verdict synthesis.
    """
    # Validate all 6 dependencies
    required = [
        ("data", data_json),
        ("claim", claim_json),
        ("warrant", warrant_json),
        ("backing", backing_json),
        ("rebuttal", rebuttal_json),
        ("qualifier", qualifier_json),
    ]

    missing = [name for name, val in required if not val or val.strip() == ""]

    if missing:
        raise DependencyError(
            tool_name="render_verdict",
            missing_dependencies=missing,
            suggestion="Cannot render verdict without complete 6-part chain. "
                       f"Missing: {', '.join(missing)}"
        )

    # Validate all JSON
    for name, json_str in required:
        _validate_json(json_str, name)

    prompt = render_verdict_prompt(
        data_json, claim_json, warrant_json,
        backing_json, rebuttal_json, qualifier_json, query
    )

    return {
        "tool": "render_verdict",
        "phase": 4,
        "query": query,
        "prompt": prompt,
        "expected_output": "JSON with 'verdict' object",
        "final": True
    }
