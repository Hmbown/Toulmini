"""ToulminChain: The complete 7-step argumentation chain."""

from __future__ import annotations
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, model_validator, computed_field
from typing_extensions import Self

from .components import Data, Claim, Warrant, Backing, Rebuttal, Qualifier, Verdict
from ..exceptions import ChainValidationError


class ToulminChain(BaseModel):
    """
    Complete Toulmin argumentation chain.
    Enforces sequential dependency: each phase requires prior phases.
    """

    query: str = Field(..., min_length=10, description="Original query/topic")

    # Phase One
    data: Optional[Data] = None
    claim: Optional[Claim] = None

    # Phase Two
    warrant: Optional[Warrant] = None
    backing: Optional[Backing] = None

    # Phase Three
    rebuttal: Optional[Rebuttal] = None
    qualifier: Optional[Qualifier] = None

    # Final
    verdict: Optional[Verdict] = None

    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    @computed_field
    @property
    def current_phase(self) -> int:
        """
        Return the current phase (0-4).
        0: Not started
        1: Phase One complete (Data + Claim)
        2: Phase Two complete (Warrant + Backing)
        3: Phase Three complete (Rebuttal + Qualifier)
        4: Complete (Verdict)
        """
        if self.verdict is not None:
            return 4
        if self.qualifier is not None and self.rebuttal is not None:
            return 3
        if self.backing is not None and self.warrant is not None:
            return 2
        if self.claim is not None and self.data is not None:
            return 1
        return 0

    @computed_field
    @property
    def is_complete(self) -> bool:
        """Check if the chain is complete."""
        return self.verdict is not None

    @model_validator(mode="after")
    def validate_sequential_dependencies(self) -> Self:
        """Enforce strict sequential dependencies."""

        # Claim requires Data
        if self.claim is not None and self.data is None:
            raise ChainValidationError(
                phase="claim",
                message="Cannot have Claim without Data",
                suggestion="Complete Phase One (Data) first"
            )

        # Warrant requires Claim
        if self.warrant is not None and self.claim is None:
            raise ChainValidationError(
                phase="warrant",
                message="Cannot have Warrant without Claim",
                suggestion="Complete Phase One (Data + Claim) first"
            )

        # Backing requires Warrant
        if self.backing is not None and self.warrant is None:
            raise ChainValidationError(
                phase="backing",
                message="Cannot have Backing without Warrant",
                suggestion="Complete Phase Two (Warrant) first"
            )

        # Rebuttal requires Backing
        if self.rebuttal is not None and self.backing is None:
            raise ChainValidationError(
                phase="rebuttal",
                message="Cannot have Rebuttal without Backing",
                suggestion="Complete Phase Two (Warrant + Backing) first"
            )

        # Qualifier requires Rebuttal
        if self.qualifier is not None and self.rebuttal is None:
            raise ChainValidationError(
                phase="qualifier",
                message="Cannot have Qualifier without Rebuttal",
                suggestion="Complete Phase Three (Rebuttal) first"
            )

        # Verdict requires all prior phases
        if self.verdict is not None:
            missing = []
            if self.data is None:
                missing.append("Data")
            if self.claim is None:
                missing.append("Claim")
            if self.warrant is None:
                missing.append("Warrant")
            if self.backing is None:
                missing.append("Backing")
            if self.rebuttal is None:
                missing.append("Rebuttal")
            if self.qualifier is None:
                missing.append("Qualifier")

            if missing:
                raise ChainValidationError(
                    phase="verdict",
                    message=f"Cannot render Verdict without: {', '.join(missing)}",
                    suggestion="Complete all prior phases first"
                )

        return self

    def to_markdown_table(self) -> str:
        """Export the chain as a Markdown table."""
        rows = [
            "| Component | Value |",
            "|-----------|-------|",
        ]

        if self.data:
            facts = "; ".join(self.data.facts[:2])
            if len(facts) > 80:
                facts = facts[:77] + "..."
            rows.append(f"| **DATA** | {facts} |")

        if self.claim:
            stmt = self.claim.statement[:80]
            if len(self.claim.statement) > 80:
                stmt += "..."
            rows.append(f"| **CLAIM** | {stmt} |")

        if self.warrant:
            principle = self.warrant.principle[:80]
            if len(self.warrant.principle) > 80:
                principle += "..."
            rows.append(f"| **WARRANT** | {principle} |")

        if self.backing:
            auth = self.backing.authority[:80]
            if len(self.backing.authority) > 80:
                auth += "..."
            rows.append(f"| **BACKING** | {auth} [{self.backing.strength}] |")

        if self.rebuttal:
            cases = "; ".join(self.rebuttal.edge_cases[:2])
            if len(cases) > 80:
                cases = cases[:77] + "..."
            rows.append(f"| **REBUTTAL** | {cases} [{self.rebuttal.severity}] |")

        if self.qualifier:
            rows.append(f"| **QUALIFIER** | {self.qualifier.degree} ({self.qualifier.confidence_pct}%) |")

        if self.verdict:
            rows.append(f"| **VERDICT** | {self.verdict.outcome}: {self.verdict.final_statement} |")

        return "\n".join(rows)

    def to_json_dict(self) -> dict:
        """Export the chain as a JSON-serializable dictionary."""
        result = {"query": self.query, "current_phase": self.current_phase}

        if self.data:
            result["data"] = self.data.model_dump()
        if self.claim:
            result["claim"] = self.claim.model_dump()
        if self.warrant:
            result["warrant"] = self.warrant.model_dump()
        if self.backing:
            result["backing"] = self.backing.model_dump()
        if self.rebuttal:
            result["rebuttal"] = self.rebuttal.model_dump()
        if self.qualifier:
            result["qualifier"] = self.qualifier.model_dump()
        if self.verdict:
            result["verdict"] = self.verdict.model_dump()

        return result
