import json
from toulmini.server import (
    initiate_toulmin_sequence,
    inject_logic_bridge,
    stress_test_argument,
    render_verdict
)

def test_full_toulmin_cycle_happy_path():
    """
    Test the complete Toulmin argumentation cycle with valid inputs.
    Phase 1 -> Phase 2 -> Phase 3 -> Phase 4
    """
    query = "Should AI be regulated?"
    
    # --- Phase 1: Data & Claim ---
    # Simulate LLM output for Phase 1
    # In a real unit test, we might mock the LLM, but here the tools return PROMPTS.
    # Wait, the tools return PROMPTS, they don't execute the LLM.
    # The server.py tools return strings (prompts).
    # So we just verify the tools return strings and don't crash.
    
    prompt_1 = initiate_toulmin_sequence(query)
    assert isinstance(prompt_1, str)
    assert "PHASE 1" in prompt_1
    assert "DATA EXTRACTION" in prompt_1
    
    # Mock the JSON output that the LLM *would* produce from Prompt 1
    data_json = json.dumps({
        "facts": ["AI models can generate harmful content."],
        "citations": [{"source": "AI Safety Institute", "reference": "2024 Report"}],
        "evidence_type": "empirical"
    })
    claim_json = json.dumps({
        "statement": "AI requires regulatory oversight.",
        "scope": "general"
    })
    
    # --- Phase 2: Warrant & Backing ---
    prompt_2 = inject_logic_bridge(query, data_json, claim_json)
    assert isinstance(prompt_2, str)
    assert "PHASE 2" in prompt_2
    assert "LOGICAL BRIDGE" in prompt_2
    
    # Mock JSON output for Phase 2
    warrant_json = json.dumps({
        "principle": "Technologies that pose public risks require oversight.",
        "logic_type": "deductive",
        "strength": "strong"
    })
    backing_json = json.dumps({
        "authority": "Precautionary Principle",
        "citations": [{"source": "Legal Philosophy", "reference": "Standard Text"}],
        "strength": "strong"
    })
    
    # --- Phase 3: Rebuttal & Qualifier ---
    prompt_3 = stress_test_argument(query, data_json, claim_json, warrant_json, backing_json)
    assert isinstance(prompt_3, str)
    assert "PHASE 3" in prompt_3
    assert "ADVERSARIAL STRESS TEST" in prompt_3
    
    # Mock JSON output for Phase 3
    rebuttal_json = json.dumps({
        "exceptions": ["Open source development might be stifled."],
        "counterexamples": [],
        "strength": "weak"
    })
    qualifier_json = json.dumps({
        "degree": "probably",
        "confidence_pct": 85,
        "rationale": "Strong consensus despite innovation risks."
    })
    
    # --- Phase 4: Verdict ---
    prompt_4 = render_verdict(query, data_json, claim_json, warrant_json, backing_json, rebuttal_json, qualifier_json)
    assert isinstance(prompt_4, str)
    assert "PHASE 4" in prompt_4
    assert "VERDICT" in prompt_4
    
    # We don't need to mock Phase 4 output as it's the end of the chain for the tools.
