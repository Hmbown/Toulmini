"""ToulminChain: The complete argument. Validates or crashes."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, model_validator
from typing_extensions import Self

from .components import Data, Claim, Warrant, Backing, Rebuttal, Qualifier, Verdict


class ToulminChain(BaseModel):
    """
    Complete Toulmin argument chain.

    Sequential dependency: each phase requires all prior phases.
    Logic checks: weak components crash the chain.
    """

    model_config = ConfigDict(extra="forbid")

    query: str
    data: Optional[Data] = None
    claim: Optional[Claim] = None
    warrant: Optional[Warrant] = None
    backing: Optional[Backing] = None
    rebuttal: Optional[Rebuttal] = None
    qualifier: Optional[Qualifier] = None
    verdict: Optional[Verdict] = None

    @model_validator(mode="after")
    def enforce_dependencies(self) -> Self:
        """Crash if dependencies are violated."""

        # Claim requires Data
        if self.claim and not self.data:
            raise ValueError("CHAIN ERROR: Claim requires Data.")

        # Warrant requires Claim
        if self.warrant and not self.claim:
            raise ValueError("CHAIN ERROR: Warrant requires Claim.")

        # Backing requires Warrant
        if self.backing and not self.warrant:
            raise ValueError("CHAIN ERROR: Backing requires Warrant.")

        # Rebuttal requires Backing
        if self.rebuttal and not self.backing:
            raise ValueError("CHAIN ERROR: Rebuttal requires Backing.")

        # Qualifier requires Rebuttal
        if self.qualifier and not self.rebuttal:
            raise ValueError("CHAIN ERROR: Qualifier requires Rebuttal.")

        # Verdict requires all
        if self.verdict:
            missing = []
            if not self.data:
                missing.append("Data")
            if not self.claim:
                missing.append("Claim")
            if not self.warrant:
                missing.append("Warrant")
            if not self.backing:
                missing.append("Backing")
            if not self.rebuttal:
                missing.append("Rebuttal")
            if not self.qualifier:
                missing.append("Qualifier")
            if missing:
                raise ValueError(f"CHAIN ERROR: Verdict requires {', '.join(missing)}.")

        return self

    def run_logic_checks(self) -> None:
        """
        Execute logic_check() on all components.
        Weak logic = ValueError = crash.
        """
        if self.warrant:
            self.warrant.logic_check()
        if self.backing:
            self.backing.logic_check()
        if self.rebuttal:
            self.rebuttal.logic_check()

    @property
    def phase(self) -> int:
        """Current phase (0-4)."""
        if self.verdict:
            return 4
        if self.qualifier:
            return 3
        if self.backing:
            return 2
        if self.claim:
            return 1
        return 0

    @property
    def is_complete(self) -> bool:
        """True if verdict rendered."""
        return self.verdict is not None
