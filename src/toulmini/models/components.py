"""The 7 Toulmin components. Strict Pydantic. Logic Compiler."""

from typing import List
from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing_extensions import Self

from .base import (
    Citation,
    StrengthLevel,
    VerdictStatus,
    QualifierForce,
    LogicType,
    EvidenceType,
)


class Data(BaseModel):
    """DATA (Grounds): Raw facts. No facts = no argument."""

    model_config = ConfigDict(extra="forbid")

    facts: List[str] = Field(..., min_length=1)
    citations: List[Citation] = Field(..., min_length=1)
    evidence_type: EvidenceType


class Claim(BaseModel):
    """CLAIM: The assertion. Must be falsifiable."""

    model_config = ConfigDict(extra="forbid")

    statement: str = Field(..., min_length=10)
    scope: str = Field(..., description="universal|general|specific|singular")

    @model_validator(mode="after")
    def no_questions(self) -> Self:
        if self.statement.strip().endswith("?"):
            raise ValueError("CLAIM REJECTED: Claims are assertions, not questions.")
        return self


class Warrant(BaseModel):
    """WARRANT: The logical bridge. If weak, the argument collapses."""

    model_config = ConfigDict(extra="forbid")

    principle: str = Field(..., min_length=20)
    logic_type: LogicType
    strength: StrengthLevel

    def logic_check(self) -> None:
        """HARD REJECTION: Weak warrants crash the argument."""
        if self.strength == "weak":
            raise ValueError(
                "WARRANT REJECTED: Strength is 'weak'. "
                "The logical bridge does not hold. Argument terminated."
            )
        if self.strength == "irrelevant":
            raise ValueError(
                "WARRANT REJECTED: Strength is 'irrelevant'. "
                "The warrant does not connect Data to Claim. Argument terminated."
            )


class Backing(BaseModel):
    """BACKING: Authority behind the Warrant. Weak backing = no foundation."""

    model_config = ConfigDict(extra="forbid")

    authority: str = Field(..., min_length=10)
    citations: List[Citation] = Field(..., min_length=1)
    strength: StrengthLevel

    def logic_check(self) -> None:
        """HARD REJECTION: Weak backing crashes the argument."""
        if self.strength == "weak":
            raise ValueError(
                "BACKING REJECTED: Strength is 'weak'. "
                "Insufficient authority to support the Warrant. Argument terminated."
            )
        if self.strength == "irrelevant":
            raise ValueError(
                "BACKING REJECTED: Strength is 'irrelevant'. "
                "The backing does not support the Warrant. Argument terminated."
            )


class Rebuttal(BaseModel):
    """REBUTTAL: The attack vector. Must find weaknesses or admit there are none."""

    model_config = ConfigDict(extra="forbid")

    exceptions: List[str] = Field(..., min_length=1)
    counterexamples: List[str] = Field(default=[])
    strength: StrengthLevel  # How devastating are the rebuttals?

    def logic_check(self) -> None:
        """Check rebuttal strength. Strong rebuttals may kill the argument."""
        if self.strength == "absolute":
            raise ValueError(
                "REBUTTAL FATAL: Strength is 'absolute'. "
                "The rebuttal completely destroys the argument. Claim cannot stand."
            )


class Qualifier(BaseModel):
    """QUALIFIER: Degree of certainty. Honest assessment required."""

    model_config = ConfigDict(extra="forbid")

    degree: QualifierForce
    confidence_pct: int = Field(..., ge=0, le=100)
    rationale: str = Field(..., min_length=10)


class Verdict(BaseModel):
    """VERDICT: The final judgment. No appeals."""

    model_config = ConfigDict(extra="forbid")

    status: VerdictStatus
    reasoning: str = Field(..., min_length=50)
    final_statement: str = Field(..., min_length=10)

    @model_validator(mode="after")
    def validate_consistency(self) -> Self:
        """Verdict must be internally consistent."""
        reasoning_lower = self.reasoning.lower()

        # If sustained, reasoning shouldn't say it fails
        if self.status == "sustained":
            if "fails" in reasoning_lower or "rejected" in reasoning_lower:
                raise ValueError(
                    "VERDICT INCONSISTENT: Status is 'sustained' but reasoning suggests failure."
                )

        # If overruled, reasoning shouldn't say it succeeds
        if self.status == "overruled":
            if "succeeds" in reasoning_lower or "sustained" in reasoning_lower:
                raise ValueError(
                    "VERDICT INCONSISTENT: Status is 'overruled' but reasoning suggests success."
                )

        return self
