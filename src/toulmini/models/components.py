"""The 7 Toulmin argumentation components."""

from __future__ import annotations
from typing import Annotated, List
from pydantic import BaseModel, Field, field_validator, model_validator
from typing_extensions import Self

from .base import (
    Citation,
    QualifierValue,
    VerdictOutcome,
    BackingStrength,
    LogicType,
    EvidenceType,
    RebuttalSeverity,
)
from ..exceptions import WeakBackingError


class Data(BaseModel):
    """
    DATA (Grounds): Raw facts or evidence supporting a claim.
    Must be cited and verifiable.
    """

    facts: Annotated[
        List[str],
        Field(min_length=1, description="List of factual statements")
    ]
    citations: Annotated[
        List[Citation],
        Field(min_length=1, description="Sources for the facts")
    ]
    evidence_type: EvidenceType = Field(
        ..., description="Type of evidence provided"
    )

    @field_validator("facts", mode="after")
    @classmethod
    def validate_facts_not_empty(cls, v: List[str]) -> List[str]:
        """Ensure each fact is substantive."""
        validated = []
        for i, fact in enumerate(v):
            fact = fact.strip()
            if len(fact) < 10:
                raise ValueError(f"Fact {i+1} is too short (minimum 10 characters)")
            validated.append(fact)
        return validated


class Claim(BaseModel):
    """
    CLAIM: An assertion or conclusion based on the Data.
    Must be derivable from the provided evidence.
    """

    statement: Annotated[
        str,
        Field(min_length=20, max_length=500, description="The claim statement")
    ]
    scope: Annotated[
        str,
        Field(description="Scope: universal, general, specific, or singular")
    ]

    @field_validator("statement", mode="after")
    @classmethod
    def validate_statement_is_assertive(cls, v: str) -> str:
        """Ensure claim is a proper assertion, not a question."""
        v = v.strip()
        if v.endswith("?"):
            raise ValueError("Claim cannot be a question - must be an assertion")
        return v

    @field_validator("scope", mode="after")
    @classmethod
    def validate_scope(cls, v: str) -> str:
        """Validate scope is one of allowed values."""
        allowed = {"universal", "general", "specific", "singular"}
        if v.lower() not in allowed:
            raise ValueError(f"Invalid scope '{v}'. Use: {', '.join(allowed)}")
        return v.lower()


class Warrant(BaseModel):
    """
    WARRANT: The logical principle or rule connecting Data to Claim.
    Answers: 'How does the data support the claim?'
    """

    principle: Annotated[
        str,
        Field(min_length=30, max_length=800, description="The logical principle")
    ]
    logic_type: LogicType = Field(
        ..., description="Type of logical reasoning"
    )

    @field_validator("principle", mode="after")
    @classmethod
    def validate_principle_is_general(cls, v: str) -> str:
        """Ensure warrant expresses a general principle."""
        v = v.strip()
        general_indicators = [
            "if", "when", "whenever", "generally", "typically",
            "because", "since", "as a rule", "it follows"
        ]
        has_general = any(ind in v.lower() for ind in general_indicators)
        if not has_general and len(v) < 100:
            raise ValueError(
                "Warrant should express a general principle. "
                "Use constructions like 'If X, then Y' or 'When X, generally Y'"
            )
        return v


class Backing(BaseModel):
    """
    BACKING: Support for the Warrant itself.
    Statutory, legal, scientific, or authoritative justification.

    NOTE: If strength is 'weak', this will raise WeakBackingError.
    """

    authority: Annotated[
        str,
        Field(min_length=20, max_length=1000, description="The authoritative support")
    ]
    citations: Annotated[
        List[Citation],
        Field(min_length=1, description="Citations supporting the backing")
    ]
    strength: BackingStrength = Field(
        ..., description="Strength of the backing: strong, moderate, or weak"
    )

    @model_validator(mode="after")
    def reject_weak_backing(self) -> Self:
        """HARD REJECTION: Raise error if backing is weak."""
        if self.strength == "weak":
            raise WeakBackingError(
                backing_authority=self.authority[:100],
                suggestion="The argument chain requires stronger backing. "
                           "Provide statutory, scientific, or expert authority with solid citations."
            )
        return self


class Rebuttal(BaseModel):
    """
    REBUTTAL: Conditions under which the Warrant does not apply.
    Edge cases, exceptions, 'black swans.'
    """

    edge_cases: Annotated[
        List[str],
        Field(min_length=1, description="Specific edge cases where warrant fails")
    ]
    counterexamples: Annotated[
        List[str],
        Field(default=[], description="Potential counterexamples")
    ]
    limitations: Annotated[
        str,
        Field(min_length=20, description="Known boundaries of the argument")
    ]
    severity: RebuttalSeverity = Field(
        ..., description="Severity of the rebuttals"
    )

    @field_validator("edge_cases", mode="after")
    @classmethod
    def validate_edge_cases_are_conditional(cls, v: List[str]) -> List[str]:
        """Ensure edge cases express conditional statements."""
        validated = []
        conditional_words = ["if", "when", "unless", "except", "in case", "should", "were", "would"]
        for i, case in enumerate(v):
            case = case.strip()
            if len(case) < 15:
                raise ValueError(f"Edge case {i+1} is too brief (minimum 15 characters)")
            if not any(word in case.lower() for word in conditional_words):
                raise ValueError(
                    f"Edge case {i+1} should be conditional. "
                    "Use 'If X, then the warrant fails' format"
                )
            validated.append(case)
        return validated


class Qualifier(BaseModel):
    """
    QUALIFIER: Degree of force or certainty of the claim.
    Modifies the claim based on the strength of support and rebuttals.
    """

    degree: QualifierValue = Field(
        ..., description="Degree of certainty"
    )
    rationale: Annotated[
        str,
        Field(min_length=30, max_length=500, description="Why this qualifier was chosen")
    ]
    confidence_pct: Annotated[
        int,
        Field(ge=0, le=100, description="Confidence percentage 0-100")
    ]

    @field_validator("rationale", mode="after")
    @classmethod
    def validate_rationale_explains_choice(cls, v: str) -> str:
        """Ensure rationale explains the qualifier choice."""
        v = v.strip()
        explanation_words = ["because", "since", "given", "considering", "due to", "based on"]
        if not any(word in v.lower() for word in explanation_words):
            raise ValueError(
                "Rationale should explain why this qualifier was chosen. "
                "Use 'Because X, the claim is qualified as Y'"
            )
        return v


class Verdict(BaseModel):
    """
    VERDICT: Final synthesis determining if the Claim stands.
    Integrates all six prior components.
    """

    outcome: VerdictOutcome = Field(
        ..., description="Final verdict: STANDS, FALLS, or QUALIFIED"
    )
    reasoning: Annotated[
        str,
        Field(min_length=100, max_length=2000, description="Comprehensive reasoning")
    ]
    final_statement: Annotated[
        str,
        Field(min_length=20, max_length=300, description="One-sentence summary")
    ]

    @field_validator("reasoning", mode="after")
    @classmethod
    def validate_reasoning_is_comprehensive(cls, v: str) -> str:
        """Ensure reasoning addresses multiple components."""
        v = v.strip()
        components = ["data", "claim", "warrant", "backing", "rebuttal", "qualifier"]
        mentioned = sum(1 for comp in components if comp in v.lower())
        if mentioned < 3:
            raise ValueError(
                "Verdict reasoning should reference most Toulmin components. "
                f"Address: {', '.join(components)}"
            )
        return v
