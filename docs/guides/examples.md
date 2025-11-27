# Worked Examples

This guide walks through complete Toulmini analyses with full JSON output.

## Example 1: Would Immortality Be a Curse?

A philosophical question that demonstrates Toulmini's handling of speculative arguments.

### Query

> "Would immortality be a curse?"

### Phase 1: Data & Claim

**Tool call**: `initiate_toulmin_sequence(query="Would immortality be a curse?")`

**Output**:
```json
{
  "data": {
    "facts": [
      "Terror Management Theory research shows mortality awareness increases prosocial behavior and meaning-making",
      "Hedonic treadmill phenomenon suggests humans adapt to positive changes and return to baseline happiness",
      "Literary analysis of immortal beings consistently portrays existential ennui and loss of purpose"
    ],
    "citations": [
      {"source": "Greenberg et al.", "reference": "Terror Management Theory (1986)"},
      {"source": "Brickman & Campbell", "reference": "Hedonic Relativism (1971)"},
      {"source": "Literary analysis", "reference": "Tolkien's Elves, Anne Rice's vampires"}
    ],
    "evidence_type": "documentary"
  },
  "claim": {
    "statement": "Immortality constitutes a psychological curse because it eliminates the temporal scarcity that gives human life meaning and purpose",
    "scope": "general"
  }
}
```

### Phase 2: Warrant & Backing

**Tool call**: `inject_logic_bridge(query, data_json, claim_json)`

**Output**:
```json
{
  "warrant": {
    "principle": "If psychological well-being depends on temporal scarcity and mortality awareness to generate meaning, then the removal of mortality eliminates the foundational conditions for sustained psychological flourishing",
    "logic_type": "deductive",
    "strength": "strong"
  },
  "backing": {
    "authority": "Existentialist philosophy (Heidegger's Being-toward-death concept) and Terror Management Theory empirical research program",
    "citations": [
      {"source": "Heidegger", "reference": "Being and Time (1927)"},
      {"source": "Becker", "reference": "The Denial of Death (1973)"},
      {"source": "TMT Research", "reference": "400+ empirical studies"}
    ],
    "strength": "strong"
  }
}
```

**Result**: Strength is "strong" — chain continues.

### Phase 3: Rebuttal & Qualifier

**Tool call**: `stress_test_argument(query, data, claim, warrant, backing)`

**Output**:
```json
{
  "rebuttal": {
    "exceptions": [
      "Meaning can arise from sources entirely unrelated to death awareness (flow states, creative mastery, deep relationships)",
      "Category error: mortal psychology cannot reliably predict immortal psychology",
      "Hedonic adaptation could work bidirectionally, allowing immortals to find new sources of meaning"
    ],
    "counterexamples": [
      "Buddhist present-moment awareness traditions derive meaning without death contemplation",
      "Intrinsically meaningful activities (mathematics, art, music) don't require mortality for significance",
      "Literary evidence consists of fiction written by mortals, not empirical data on actual immortals"
    ],
    "strength": "strong"
  },
  "qualifier": {
    "degree": "possibly",
    "confidence_pct": 45,
    "rationale": "The argument presents a coherent case from Terror Management Theory and existentialist philosophy, but strong rebuttals expose fundamental limitations in extrapolating mortal psychology to unprecedented conditions"
  }
}
```

### Phase 4: Verdict

**Tool call**: `render_verdict(query, data, claim, warrant, backing, rebuttal, qualifier)`

**Output**:
```json
{
  "verdict": {
    "status": "remanded",
    "reasoning": "The argument chain presents internally consistent reasoning grounded in established psychological and philosophical frameworks. However, the strong rebuttals expose a fundamental epistemological limitation: all evidence derives from mortal psychology extrapolated to a condition no human has experienced. The category error objection and existence of alternative meaning frameworks create sufficient reasonable doubt.",
    "final_statement": "The claim that immortality constitutes a curse remains philosophically contested; insufficient empirical grounding exists to render a definitive judgment. The question is remanded for future evidence—should immortality become achievable."
  }
}
```

### Summary

| Component | Value |
|-----------|-------|
| Claim | Immortality is a psychological curse |
| Warrant Strength | Strong |
| Backing Strength | Strong |
| Rebuttal Strength | Strong |
| Confidence | 45% (Possibly) |
| **Verdict** | **REMANDED** |

---

## Example 2: Is Remote Work More Productive?

A practical question with more empirical grounding.

### Query

> "Is remote work more productive than office work?"

### Phase 1: Data & Claim

```json
{
  "data": {
    "facts": [
      "Stanford study found 13% productivity increase for call center workers working from home",
      "Microsoft research showed 10% increase in meetings and collaboration time for remote workers",
      "Gallup data indicates 54% of remote workers report working longer hours"
    ],
    "citations": [
      {"source": "Bloom et al.", "reference": "Stanford WFH Study (2015)"},
      {"source": "Microsoft", "reference": "Work Trend Index (2021)"},
      {"source": "Gallup", "reference": "State of the Global Workplace (2022)"}
    ],
    "evidence_type": "empirical"
  },
  "claim": {
    "statement": "Remote work increases measurable output for knowledge workers in roles with clearly defined tasks",
    "scope": "limited"
  }
}
```

### Phase 2: Warrant & Backing

```json
{
  "warrant": {
    "principle": "If workers have fewer interruptions and more autonomy over their work environment, and their tasks have clear deliverables, then output per hour increases",
    "logic_type": "inductive",
    "strength": "strong"
  },
  "backing": {
    "authority": "Peer-reviewed economics research and large-scale corporate studies",
    "citations": [
      {"source": "Bloom et al.", "reference": "Quarterly Journal of Economics (2015)"},
      {"source": "Barrero, Bloom, Davis", "reference": "NBER Working Paper (2021)"}
    ],
    "strength": "strong"
  }
}
```

### Phase 3: Rebuttal & Qualifier

```json
{
  "rebuttal": {
    "exceptions": [
      "Collaboration-heavy roles (design, strategy) may suffer from reduced spontaneous interaction",
      "Junior employees lose mentorship and tacit knowledge transfer opportunities",
      "Long-term innovation metrics may differ from short-term productivity measures"
    ],
    "counterexamples": [
      "Yahoo and IBM reversed remote work policies citing collaboration concerns",
      "Studies show remote workers report higher burnout rates despite productivity gains"
    ],
    "strength": "strong"
  },
  "qualifier": {
    "degree": "probably",
    "confidence_pct": 65,
    "rationale": "Strong empirical evidence supports productivity gains for certain role types, but significant exceptions exist for collaborative work and long-term organizational health"
  }
}
```

### Phase 4: Verdict

```json
{
  "verdict": {
    "status": "sustained",
    "reasoning": "The claim, properly scoped to 'knowledge workers with clearly defined tasks,' is supported by robust empirical evidence from peer-reviewed research. The rebuttals identify important limitations but do not invalidate the core claim—they refine its scope. The 65% confidence reflects acknowledged uncertainty around long-term effects while sustaining the immediate productivity claim.",
    "final_statement": "Remote work increases measurable output for knowledge workers with clearly defined tasks. This verdict does not extend to collaboration-heavy roles, junior employees requiring mentorship, or long-term innovation metrics."
  }
}
```

### Summary

| Component | Value |
|-----------|-------|
| Claim | Remote work increases output (scoped) |
| Warrant Strength | Strong |
| Backing Strength | Strong |
| Rebuttal Strength | Strong |
| Confidence | 65% (Probably) |
| **Verdict** | **SUSTAINED** (with scope limitations) |

---

## Full JSON Traces

Complete JSON output files for the immortality example are available in the `/examples/` directory:

- `phase1_data_claim.json`
- `phase2_warrant_backing.json`
- `phase3_rebuttal_qualifier.json`
- `phase4_verdict.json`
