"""Base types and shared definitions for Toulmin models."""

from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field, ConfigDict


# Qualifier values - degree of force for the argument
QualifierValue = Literal[
    "certainly",      # Absolute certainty
    "presumably",     # Strong presumption
    "probably",       # High probability
    "possibly",       # Moderate possibility
    "apparently",     # Based on appearances
    "unless",         # Conditional
]

# Verdict outcomes
VerdictOutcome = Literal["STANDS", "FALLS", "QUALIFIED"]

# Backing strength levels
BackingStrength = Literal["strong", "moderate", "weak"]

# Logic types for warrants
LogicType = Literal["deductive", "inductive", "abductive"]

# Evidence types for data
EvidenceType = Literal["empirical", "statistical", "testimonial", "documentary", "expert"]

# Rebuttal severity levels
RebuttalSeverity = Literal["fatal", "significant", "minor", "negligible"]


class Citation(BaseModel):
    """A citation for evidence or backing."""

    model_config = ConfigDict(frozen=True)

    source: str = Field(..., min_length=1, description="Source name or identifier")
    reference: str = Field(..., min_length=1, description="Specific reference or quote")
    url: Optional[str] = Field(None, description="URL if available")

    def __str__(self) -> str:
        return f"[{self.source}] {self.reference}"
