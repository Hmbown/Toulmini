# Toulmini Technical Specification

This document provides the complete technical specification for Toulmini's schemas, constraints, and API.

## Type Definitions

### StrengthLevel

Used by Warrant, Backing, and Rebuttal to indicate logical strength.

```typescript
type StrengthLevel = "absolute" | "strong" | "weak" | "irrelevant"
```

| Value | Meaning |
|-------|---------|
| `absolute` | Unquestionable. Cannot be challenged. |
| `strong` | Well-supported. Minor challenges possible. |
| `weak` | Poorly supported. **Triggers termination for Warrant/Backing.** |
| `irrelevant` | Does not apply. **Triggers termination for Warrant/Backing.** |

### VerdictStatus

Final judgment status.

```typescript
type VerdictStatus = "sustained" | "overruled" | "remanded"
```

| Value | Meaning |
|-------|---------|
| `sustained` | Argument holds. Claim validated. |
| `overruled` | Argument fails. Claim rejected. |
| `remanded` | Insufficient evidence. Requires further investigation. |

### QualifierForce

Degree of certainty.

```typescript
type QualifierForce = "certainly" | "presumably" | "probably" | "possibly" | "apparently"
```

| Degree | Confidence Range |
|--------|------------------|
| `certainly` | 90-100% |
| `presumably` | 70-89% |
| `probably` | 50-69% |
| `possibly` | 30-49% |
| `apparently` | 0-29% |

### LogicType

Type of logical reasoning.

```typescript
type LogicType = "deductive" | "inductive" | "abductive"
```

### EvidenceType

Category of evidence.

```typescript
type EvidenceType = "empirical" | "statistical" | "testimonial" | "documentary" | "expert"
```

---

## Component Schemas

### Citation

```json
{
  "source": "string (min 1 char)",
  "reference": "string (min 1 char)"
}
```

### Data

```json
{
  "facts": ["string", ...],          // min 1 item
  "citations": [Citation, ...],      // min 1 item
  "evidence_type": EvidenceType
}
```

### Claim

```json
{
  "statement": "string (min 10 chars)",  // MUST NOT end with "?"
  "scope": "string"                       // universal|general|specific|singular
}
```

**Validation**: Claims cannot be questions. Statements ending in `?` are rejected.

### Warrant

```json
{
  "principle": "string (min 20 chars)",
  "logic_type": LogicType,
  "strength": StrengthLevel
}
```

**Circuit Breaker**: If `strength` is `"weak"` or `"irrelevant"`, argument terminates.

### Backing

```json
{
  "authority": "string (min 10 chars)",
  "citations": [Citation, ...],           // min 1 item
  "strength": StrengthLevel
}
```

**Circuit Breaker**: If `strength` is `"weak"` or `"irrelevant"`, argument terminates.

### Rebuttal

```json
{
  "exceptions": ["string", ...],     // min 1 item
  "counterexamples": ["string", ...], // optional, can be empty
  "strength": StrengthLevel
}
```

**Note**: If `strength` is `"absolute"`, verdict MUST be `"overruled"`.

### Qualifier

```json
{
  "degree": QualifierForce,
  "confidence_pct": 0-100,            // integer
  "rationale": "string (min 10 chars)"
}
```

### Verdict

```json
{
  "status": VerdictStatus,
  "reasoning": "string (min 50 chars)",
  "final_statement": "string (min 10 chars)"
}
```

**Validation**: Reasoning must be consistent with status. Cannot say "fails" if sustained, cannot say "succeeds" if overruled.

---

## Tool API

### initiate_toulmin_sequence

**Phase 1**: Extract DATA and construct CLAIM.

```
Input:
  query: string

Output:
  Prompt string (to be executed by LLM)

LLM produces:
  {
    "data": Data,
    "claim": Claim
  }
```

### inject_logic_bridge

**Phase 2**: Generate WARRANT and BACKING.

```
Input:
  query: string
  data_json: string (JSON)
  claim_json: string (JSON)

Output:
  Prompt string (to be executed by LLM)

LLM produces:
  {
    "warrant": Warrant,
    "backing": Backing
  }
```

**Termination**: Chain stops if warrant or backing strength is weak/irrelevant.

### stress_test_argument

**Phase 3**: Find REBUTTALS and assign QUALIFIER.

```
Input:
  query: string
  data_json: string (JSON)
  claim_json: string (JSON)
  warrant_json: string (JSON)
  backing_json: string (JSON)

Output:
  Prompt string (to be executed by LLM)

LLM produces:
  {
    "rebuttal": Rebuttal,
    "qualifier": Qualifier
  }
```

### render_verdict

**Phase 4**: Render final judgment.

```
Input:
  query: string
  data_json: string (JSON)
  claim_json: string (JSON)
  warrant_json: string (JSON)
  backing_json: string (JSON)
  rebuttal_json: string (JSON)
  qualifier_json: string (JSON)

Output:
  Prompt string (to be executed by LLM)

LLM produces:
  {
    "verdict": Verdict
  }
```

---

## Consistency Rules

### Termination Conditions

| Condition | Phase | Result |
|-----------|-------|--------|
| `warrant.strength == "weak"` | 2 | Chain terminates |
| `warrant.strength == "irrelevant"` | 2 | Chain terminates |
| `backing.strength == "weak"` | 2 | Chain terminates |
| `backing.strength == "irrelevant"` | 2 | Chain terminates |

### Verdict Constraints

| Condition | Required Verdict |
|-----------|------------------|
| `rebuttal.strength == "absolute"` | `"overruled"` |
| `qualifier.confidence_pct < 30` | `"overruled"` or `"remanded"` (recommended) |

---

## Error Response Format

When inputs are invalid or missing:

```json
{
  "error": "Description of error",
  "missing": ["list", "of", "missing", "fields"]
}
```

---

## Pydantic Configuration

All models use:

```python
model_config = ConfigDict(extra="forbid")  # No extra fields allowed
```

Citation model also uses:

```python
model_config = ConfigDict(frozen=True, extra="forbid")  # Immutable
```
