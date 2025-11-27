"""Base types for Toulmin models. Strict. Opinionated."""

from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


# === STRENGTH LEVELS ===
# Used by Backing, Rebuttal, Warrant
StrengthLevel = Literal["absolute", "strong", "weak", "irrelevant"]

# === VERDICT STATUS ===
# Legal terminology: the argument's fate
VerdictStatus = Literal["sustained", "overruled", "remanded"]

# === QUALIFIER FORCE ===
QualifierForce = Literal[
    "certainly",
    "presumably",
    "probably",
    "possibly",
    "apparently",
]

# === LOGIC TYPES ===
LogicType = Literal["deductive", "inductive", "abductive"]

# === EVIDENCE TYPES ===
EvidenceType = Literal[
    "empirical", "statistical", "testimonial", "documentary", "expert"
]


class Citation(BaseModel):
    """A citation. No citation = no credibility."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source: str = Field(..., min_length=1)
    reference: str = Field(..., min_length=1)
