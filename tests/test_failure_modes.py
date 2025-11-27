import pytest
import json
from toulmini.server import stress_test_argument

def test_weak_warrant_termination():
    """Test that a weak warrant triggers the TERMINATION_SIGNAL."""
    query = "The moon is made of cheese because it is yellow."
    data_json = '{"facts": ["The moon is yellow."], "citations": [{"source": "Visual Observation", "reference": "Night Sky"}], "evidence_type": "empirical"}'
    claim_json = '{"statement": "The moon is made of cheese.", "scope": "specific"}'
    
    # Deliberately weak warrant
    warrant_json = '{"principle": "Things that are yellow are made of cheese.", "logic_type": "inductive", "strength": "weak"}'
    backing_json = '{"authority": "None", "citations": [{"source": "None", "reference": "None"}], "strength": "weak"}'

    result = stress_test_argument(query, data_json, claim_json, warrant_json, backing_json)
    
    assert "TERMINATION_SIGNAL" in result
    assert "WARRANT REJECTED" in result

def test_irrelevant_backing_termination():
    """Test that irrelevant backing triggers the TERMINATION_SIGNAL."""
    query = "Should we eat more fruit?"
    data_json = '{"facts": ["Fruit contains vitamins."], "citations": [{"source": "FDA", "reference": "Nutrition Guide"}], "evidence_type": "scientific"}'
    claim_json = '{"statement": "We should eat more fruit.", "scope": "general"}'
    
    # Strong warrant, but irrelevant backing
    warrant_json = '{"principle": "Vitamins are essential for health.", "logic_type": "deductive", "strength": "strong"}'
    backing_json = '{"authority": "My neighbor Bob", "citations": [{"source": "Conversation", "reference": "Yesterday"}], "strength": "irrelevant"}'

    result = stress_test_argument(query, data_json, claim_json, warrant_json, backing_json)
    
    assert "TERMINATION_SIGNAL" in result
    assert "BACKING REJECTED" in result

def test_missing_phase1_output_in_phase2():
    """Test that missing Phase 1 output in Phase 2 returns an error."""
    from toulmini.server import inject_logic_bridge
    query = "Some query"
    # Missing data_json and claim_json
    result = inject_logic_bridge(query, "", "")
    assert "MISSING_PHASE_1_OUTPUT" in result

def test_missing_components_in_phase3():
    """Test that missing components in Phase 3 returns an error."""
    from toulmini.server import stress_test_argument
    query = "Some query"
    # Missing warrant and backing
    result = stress_test_argument(query, "{}", "{}", "", "")
    assert "MISSING_COMPONENTS" in result
    assert "warrant" in result
    assert "backing" in result

def test_incomplete_chain_in_phase4():
    """Test that incomplete chain in Phase 4 returns an error."""
    from toulmini.server import render_verdict
    query = "Some query"
    # Missing rebuttal and qualifier
    result = render_verdict(query, "{}", "{}", "{}", "{}", "", "")
    assert "INCOMPLETE_CHAIN" in result
