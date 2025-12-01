from toulmini.config import reset_config, set_config_value
from toulmini.server import (
    consult_field_experts,
    initiate_toulmin_sequence,
    inject_logic_bridge,
    stress_test_argument,
    render_verdict,
    format_analysis_report,
)

# --- Mocks for JSON inputs ---
# --- Mocks for JSON inputs ---
DATA_JSON = '{"facts": ["Fact 1"], "citations": [{"source": "S", "reference": "R"}], "evidence_type": "empirical"}'
CLAIM_JSON = '{"statement": "Statement", "scope": "general"}'
# Principle must be min 20 chars
WARRANT_JSON = '{"principle": "This principle is definitely longer than twenty characters.", "logic_type": "deductive", "strength": "strong"}'
# Authority must be min 10 chars
BACKING_JSON = '{"authority": "Valid Authority Name", "citations": [{"source": "Source", "reference": "Ref"}], "strength": "strong"}'
WEAK_WARRANT_JSON = '{"principle": "This warrant intentionally fails strength checks.", "logic_type": "deductive", "strength": "weak"}'
WEAK_BACKING_JSON = '{"authority": "Weak Authority", "citations": [{"source": "Source", "reference": "Ref"}], "strength": "weak"}'
REBUTTAL_JSON = '{"exceptions": [], "counterexamples": [], "strength": "weak"}'
QUALIFIER_JSON = (
    '{"degree": "probably", "confidence_pct": 80, "rationale": "Rationale"}'
)
VERDICT_JSON = '{"status": "sustained", "reasoning": "The argument holds because the evidence supports the claim with strong backing.", "final_statement": "Claim is validated."}'


def test_initiate_toulmin_sequence():
    # Valid query
    result = initiate_toulmin_sequence("Is this a valid query?")
    assert "PHASE 1: DATA EXTRACTION + CLAIM CONSTRUCTION" in result
    assert "EMIT JSON" in result

    # Short query
    result_error = initiate_toulmin_sequence("Hi")
    assert '{"error": "QUERY_TOO_SHORT"}' in result_error


def test_inject_logic_bridge():
    # Valid input
    result = inject_logic_bridge(
        query="Query", data_json=DATA_JSON, claim_json=CLAIM_JSON
    )
    assert "PHASE 2: LOGICAL BRIDGE CONSTRUCTION" in result
    assert DATA_JSON in result
    assert CLAIM_JSON in result

    # Missing input
    result_error = inject_logic_bridge(
        query="Query", data_json="", claim_json=CLAIM_JSON
    )
    assert '{"error": "MISSING_PHASE_1_OUTPUT"}' in result_error


def test_stress_test_argument():
    # Valid input
    result = stress_test_argument(
        query="Query",
        data_json=DATA_JSON,
        claim_json=CLAIM_JSON,
        warrant_json=WARRANT_JSON,
        backing_json=BACKING_JSON,
    )
    assert "PHASE 3: ADVERSARIAL STRESS TEST" in result
    assert WARRANT_JSON in result

    # Missing components
    result_error = stress_test_argument(
        query="Query",
        data_json=DATA_JSON,
        claim_json="",
        warrant_json=WARRANT_JSON,
        backing_json=BACKING_JSON,
    )
    assert '{"error": "MISSING_COMPONENTS"' in result_error
    assert "'claim'" in result_error


def test_render_verdict():
    # Valid input
    result = render_verdict(
        query="Query",
        data_json=DATA_JSON,
        claim_json=CLAIM_JSON,
        warrant_json=WARRANT_JSON,
        backing_json=BACKING_JSON,
        rebuttal_json=REBUTTAL_JSON,
        qualifier_json=QUALIFIER_JSON,
    )
    assert "PHASE 4: VERDICT" in result
    assert "COMPLETE ARGUMENT CHAIN" in result

    # Incomplete chain
    result_error = render_verdict(
        query="Query",
        data_json=DATA_JSON,
        claim_json=CLAIM_JSON,
        warrant_json="",
        backing_json=BACKING_JSON,
        rebuttal_json=REBUTTAL_JSON,
        qualifier_json=QUALIFIER_JSON,
    )
    assert '{"error": "INCOMPLETE_CHAIN"}' in result_error


def test_format_analysis_report():
    # Valid input
    result = format_analysis_report(
        query="Query",
        data_json=DATA_JSON,
        claim_json=CLAIM_JSON,
        warrant_json=WARRANT_JSON,
        backing_json=BACKING_JSON,
        rebuttal_json=REBUTTAL_JSON,
        qualifier_json=QUALIFIER_JSON,
        verdict_json=VERDICT_JSON,
    )
    assert "TOULMIN ANALYSIS REPORT" in result
    assert "# Toulmin Analysis:" in result
    assert "## Verdict:" in result

    # Incomplete chain
    result_error = format_analysis_report(
        query="Query",
        data_json=DATA_JSON,
        claim_json=CLAIM_JSON,
        warrant_json=WARRANT_JSON,
        backing_json=BACKING_JSON,
        rebuttal_json=REBUTTAL_JSON,
        qualifier_json=QUALIFIER_JSON,
        verdict_json="",
    )
    assert '{"error": "INCOMPLETE_CHAIN"}' in result_error

def test_consult_field_experts_respects_config():
    set_config_value("enable_council", False)
    try:
        response = consult_field_experts("Query", ["Expert"])
        assert response == '{"error": "COUNCIL_DISABLED"}'
    finally:
        reset_config()


def test_stress_test_rejects_weak_warrant_by_default():
    response = stress_test_argument(
        query="Query",
        data_json=DATA_JSON,
        claim_json=CLAIM_JSON,
        warrant_json=WEAK_WARRANT_JSON,
        backing_json=BACKING_JSON,
    )
    assert '"TERMINATION_SIGNAL"' in response


def test_stress_test_allows_weak_warrant_when_disabled():
    set_config_value("fail_on_weak_warrant", False)
    try:
        response = stress_test_argument(
            query="Query",
            data_json=DATA_JSON,
            claim_json=CLAIM_JSON,
            warrant_json=WEAK_WARRANT_JSON,
            backing_json=BACKING_JSON,
        )
        assert "PHASE 3: ADVERSARIAL STRESS TEST" in response
    finally:
        reset_config()


def test_stress_test_allows_weak_backing_when_disabled():
    set_config_value("fail_on_weak_backing", False)
    try:
        response = stress_test_argument(
            query="Query",
            data_json=DATA_JSON,
            claim_json=CLAIM_JSON,
            warrant_json=WARRANT_JSON,
            backing_json=WEAK_BACKING_JSON,
        )
        assert "PHASE 3: ADVERSARIAL STRESS TEST" in response
    finally:
        reset_config()


def test_stress_test_skips_checks_when_strict_mode_off():
    set_config_value("strict_mode", False)
    try:
        response = stress_test_argument(
            query="Query",
            data_json=DATA_JSON,
            claim_json=CLAIM_JSON,
            warrant_json=WEAK_WARRANT_JSON,
            backing_json=WEAK_BACKING_JSON,
        )
        assert "PHASE 3: ADVERSARIAL STRESS TEST" in response
    finally:
        reset_config()
