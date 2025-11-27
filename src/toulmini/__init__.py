"""Toulmini - Local MCP server implementing Toulmin's argumentation model."""

from .server import main, mcp
from .exceptions import (
    ToulminiError,
    WeakBackingError,
    DependencyError,
    OutputFormatError,
    ChainValidationError,
)
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
)

__version__ = "1.0.0"
__all__ = [
    "main",
    "mcp",
    "ToulminiError",
    "WeakBackingError",
    "DependencyError",
    "OutputFormatError",
    "ChainValidationError",
    "ToulminChain",
    "Data",
    "Claim",
    "Warrant",
    "Backing",
    "Rebuttal",
    "Qualifier",
    "Verdict",
    "Citation",
]
