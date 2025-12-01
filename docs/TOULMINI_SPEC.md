# Toulmini Specification

## 1. Core Philosophy

Toulmini is a "Logic Harness" that enforces Stephen Toulmin's argumentation model (1958) upon Large Language Models. Unlike standard conversational agents, Toulmini requires that arguments be constructed via a rigorous, sequential process of component generation and validation.

The system operates on two fundamental principles:
1.  **Structural Completeness**: An argument is not valid unless all 7 components are present and correctly related.
2.  **Circuit Breaking**: The process must terminate immediately if any critical logical link (Warrant or Backing) is found to be weak or irrelevant.

## 2. The 7 Components

The model defines seven strict data structures.

### 2.1 Data (Grounds)
Raw facts or evidence used to support the claim. Without data, there is no argument.
*   **Schema**:
    *   `facts`: List[str] (min 1)
    *   `citations`: List[Citation]
    *   `evidence_type`: Enum (Empirical, Statistical, Testimonial, etc.)

### 2.2 Claim
The assertion or conclusion being argued.
*   **Schema**:
    *   `statement`: str (min 10 chars). Must be an assertion, not a question.
    *   `scope`: str ("universal", "general", "specific", "singular")

### 2.3 Warrant
The logical bridge connecting Data to Claim.
*   **Schema**:
    *   `principle`: str (min 20 chars). The general rule.
    *   `logic_type`: Enum (Deductive, Inductive, Abductive, Analogical)
    *   `strength`: Enum ("absolute", "strong", "weak", "irrelevant")
*   **Failure Mode**: If `strength` is "weak" or "irrelevant", the process terminates.

### 2.4 Backing
The authority supporting the Warrant.
*   **Schema**:
    *   `authority`: str (min 10 chars).
    *   `citations`: List[Citation]
    *   `strength`: Enum ("absolute", "strong", "weak", "irrelevant")
*   **Failure Mode**: If `strength` is "weak" or "irrelevant", the process terminates.

### 2.5 Rebuttal
Conditions or exceptions where the Warrant does not hold.
*   **Schema**:
    *   `exceptions`: List[str] (min 1).
    *   `counterexamples`: List[str]
    *   `strength`: Enum ("absolute", "strong", "weak", "negligible")
*   **Constraint**: If `strength` is "absolute", the Verdict must be "OVERRULED".

### 2.6 Qualifier
The degree of certainty attached to the Claim, based on the Rebuttals.
*   **Schema**:
    *   `degree`: Enum ("certainly", "presumably", "probably", "possibly", "apparently")
    *   `confidence_pct`: int (0-100)
    *   `rationale`: str

### 2.7 Verdict
The final judgment on the argument's validity.
*   **Schema**:
    *   `status`: Enum ("sustained", "overruled", "remanded")
    *   `reasoning`: str (min 50 chars)
    *   `final_statement`: str
*   **Consistency**: Status must match the reasoning provided.

## 3. Execution Flow (The 4 Phases)

The system executes in four strict phases. Each phase requires the output of the previous phases as input.

### Helper: The Council (Optional)
*   **Tool**: `consult_field_experts`
*   **Input**: Query, Perspectives (List[str])
*   **Output**: `CouncilOpinions` (JSON)
*   **Purpose**: Gather diverse, expert viewpoints to fuel Phase 2 (Backing) or Phase 3 (Rebuttals).
*   **Inspired By**: Hegelion's "Council" feature.

### Phase 1: Grounding
*   **Tool**: `initiate_toulmin_sequence`
*   **Input**: User Query
*   **Output**: `Data` + `Claim`
*   **Purpose**: Establish what is being argued and on what basis.

### Phase 2: The Logic Bridge
*   **Tool**: `inject_logic_bridge`
*   **Input**: Query, Data, Claim
*   **Output**: `Warrant` + `Backing`
*   **Purpose**: Establish the logical license to move from Data to Claim.
*   **Validation**: Checks for "weak" strength in Warrant/Backing.

### Phase 3: Stress Test
*   **Tool**: `stress_test_argument`
*   **Input**: Query, Data, Claim, Warrant, Backing
*   **Output**: `Rebuttal` + `Qualifier`
*   **Purpose**: Adversarial testing. The model must attempt to defeat its own argument.

### Phase 4: Judgment
*   **Tool**: `render_verdict`
*   **Input**: All 6 prior components
*   **Output**: `Verdict`
*   **Purpose**: Final synthesized judgment.

### Phase 5: Reporting (Optional)
*   **Tool**: `format_analysis_report`
*   **Input**: All 7 components
*   **Output**: Markdown formatted report.

## 4. Failure Modes & Circuit Breakers

Toulmini enforces logic through strict programmatic checks:

1.  **Weak Logic**: If `Warrant.strength` is "weak" or "irrelevant", Phase 2 returns a `TERMINATION_SIGNAL` error.
2.  **Weak Authority**: If `Backing.strength` is "weak" or "irrelevant", Phase 2 returns a `TERMINATION_SIGNAL` error.
3.  **Missing Dependencies**: If a tool is called without the required JSON inputs from previous phases, it returns a `MISSING_COMPONENTS` error.
4.  **Input Validation**: All inputs are validated against the Pydantic schemas defined in `src/toulmini/models/components.py`.
