"""
Toulmini: A Logic Compiler for Arguments.

Bad logic = crash. Weak backing = termination. No appeals.
"""

from .server import main, mcp
from .models import (
    ToulminChain,
    Data,
    Claim,
    Warrant,
    Backing,
    Rebuttal,
    Qualifier,
    Verdict,
    Citation,
    StrengthLevel,
    VerdictStatus,
)

__version__ = "2.0.0"
__all__ = [
    "main",
    "mcp",
    "ToulminChain",
    "Data",
    "Claim",
    "Warrant",
    "Backing",
    "Rebuttal",
    "Qualifier",
    "Verdict",
    "Citation",
    "StrengthLevel",
    "VerdictStatus",
]
