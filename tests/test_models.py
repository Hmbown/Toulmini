import pytest
from pydantic import ValidationError
from toulmini.models.components import (
    Claim, Warrant, Backing, Rebuttal, Verdict, Data, Citation, Qualifier
)
from toulmini.models.chain import ToulminChain

# --- Helper Objects ---
valid_citation = Citation(source="Source A", reference="Page 1")
valid_data = Data(
    facts=["Fact 1"],
    citations=[valid_citation],
    evidence_type="empirical"
)
valid_claim = Claim(
    statement="This is a valid statement that is long enough.",
    scope="general"
)
valid_warrant = Warrant(
    principle="If X then Y principle logic that is long enough.",
    logic_type="deductive",
    strength="strong"
)
valid_backing = Backing(
    authority="Authority Name Long Enough",
    citations=[valid_citation],
    strength="strong"
)
valid_rebuttal = Rebuttal(
    exceptions=["Exception 1"],
    strength="weak"
)
valid_qualifier = Qualifier(
    degree="probably",
    confidence_pct=80,
    rationale="Rationale is long enough for validity."
)
valid_verdict = Verdict(
    status="sustained",
    reasoning="Reasoning is very long and detailed and supports the sustained verdict successfully without contradiction.",
    final_statement="Final statement."
)

# --- Component Tests ---

def test_claim_validation():
    # Valid claim
    claim = Claim(statement="This is a valid statement.", scope="general")
    assert claim.scope == "general"

    # Invalid: ends with question mark
    with pytest.raises(ValidationError) as excinfo:
        Claim(statement="Is this a question?", scope="general")
    assert "Claims are assertions, not questions" in str(excinfo.value)

    # Invalid: too short
    with pytest.raises(ValidationError):
        Claim(statement="Short", scope="general")

def test_warrant_logic_check():
    # Valid warrant
    warrant = Warrant(
        principle="If X then Y principle logic that is long enough.",
        logic_type="deductive",
        strength="strong"
    )
    warrant.logic_check()  # Should not raise

    # Invalid: weak strength
    weak_warrant = Warrant(
        principle="If X then Y principle logic that is long enough.",
        logic_type="deductive",
        strength="weak"
    )
    with pytest.raises(ValueError, match="WARRANT REJECTED"):
        weak_warrant.logic_check()

def test_backing_logic_check():
    # Valid backing
    backing = Backing(
        authority="Authority Name Long Enough",
        citations=[valid_citation],
        strength="strong"
    )
    backing.logic_check() # Should not raise

    # Invalid: weak strength
    weak_backing = Backing(
        authority="Authority Name Long Enough",
        citations=[valid_citation],
        strength="weak"
    )
    with pytest.raises(ValueError, match="BACKING REJECTED"):
        weak_backing.logic_check()

def test_rebuttal_logic_check():
    # Valid rebuttal (weak attack means argument stands)
    rebuttal = Rebuttal(
        exceptions=["Exception 1"],
        strength="weak"
    )
    rebuttal.logic_check()

    # Invalid: absolute strength (destroys argument)
    fatal_rebuttal = Rebuttal(
        exceptions=["Exception 1"],
        strength="absolute"
    )
    with pytest.raises(ValueError, match="REBUTTAL FATAL"):
        fatal_rebuttal.logic_check()

def test_verdict_consistency():
    # Valid sustained
    v1 = Verdict(
        status="sustained",
        reasoning="This reasoning supports the claim and explains why it succeeds perfectly well.",
        final_statement="Final statement."
    )

    # Valid overruled
    v2 = Verdict(
        status="overruled",
        reasoning="This reasoning explains why the claim fails and is rejected completely.",
        final_statement="Final statement."
    )

    # Inconsistent: sustained but fails
    with pytest.raises(ValidationError, match="VERDICT INCONSISTENT"):
        Verdict(
            status="sustained",
            reasoning="This reasoning explains why the claim fails miserably.",
            final_statement="Final statement."
        )

    # Inconsistent: overruled but succeeds
    with pytest.raises(ValidationError, match="VERDICT INCONSISTENT"):
        Verdict(
            status="overruled",
            reasoning="This reasoning explains why the claim succeeds perfectly.",
            final_statement="Final statement."
        )

# --- Chain Tests ---

def test_chain_completeness():
    chain = ToulminChain(
        query="Test Query",
        data=valid_data,
        claim=valid_claim,
        warrant=valid_warrant,
        backing=valid_backing,
        rebuttal=valid_rebuttal,
        qualifier=valid_qualifier,
        verdict=valid_verdict
    )
    assert chain.is_complete
    assert chain.phase == 4
    chain.run_logic_checks()

def test_chain_dependencies():
    # Missing Data for Claim
    with pytest.raises(ValidationError, match="Claim requires Data"):
        ToulminChain(
            query="Test",
            claim=valid_claim
        )

    # Missing Claim for Warrant
    with pytest.raises(ValidationError, match="Warrant requires Claim"):
        ToulminChain(
            query="Test",
            data=valid_data,
            # no claim
            warrant=valid_warrant
        )

    # Missing Warrant for Backing
    with pytest.raises(ValidationError, match="Backing requires Warrant"):
        ToulminChain(
            query="Test",
            data=valid_data,
            claim=valid_claim,
            # no warrant
            backing=valid_backing
        )

def test_chain_run_logic_checks():
    # Chain with weak warrant
    weak_warrant = Warrant(
        principle="If X then Y principle logic that is long enough.",
        logic_type="deductive",
        strength="weak"
    )

    chain = ToulminChain(
        query="Test",
        data=valid_data,
        claim=valid_claim,
        warrant=weak_warrant
    )

    # Validation passes (Pydantic doesn't call logic_check automatically on fields unless validator calls it)
    # But run_logic_checks should fail
    with pytest.raises(ValueError, match="WARRANT REJECTED"):
        chain.run_logic_checks()
