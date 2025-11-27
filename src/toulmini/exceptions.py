"""Custom exception hierarchy for Toulmini validation errors."""

from __future__ import annotations
from typing import Any, Dict, List, Optional


class ToulminiError(Exception):
    """Base exception for all Toulmini errors with structured messages for LLM guidance."""

    def __init__(
        self,
        message: str,
        suggestion: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.suggestion = suggestion
        self.context = context or {}
        super().__init__(self.format_message())

    def format_message(self) -> str:
        """Format error message for LLM consumption."""
        parts = [f"ERROR: {self.message}"]
        if self.suggestion:
            parts.append(f"SUGGESTION: {self.suggestion}")
        return " | ".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON output."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "suggestion": self.suggestion,
            "context": self.context,
        }


class WeakBackingError(ToulminiError):
    """Hard rejection when backing strength is 'weak'. Stops the argument chain."""

    def __init__(
        self,
        backing_authority: str,
        suggestion: Optional[str] = None
    ):
        super().__init__(
            message=f"Backing is too weak to support the warrant: '{backing_authority}'",
            suggestion=suggestion or "Provide stronger statutory, scientific, or expert backing with citations",
            context={"backing_authority": backing_authority, "rejected": True}
        )


class DependencyError(ToulminiError):
    """Missing required prior phases in the Toulmin chain."""

    def __init__(
        self,
        tool_name: str,
        missing_dependencies: List[str],
        suggestion: Optional[str] = None
    ):
        self.tool_name = tool_name
        self.missing_dependencies = missing_dependencies
        super().__init__(
            message=f"Cannot execute '{tool_name}': missing {', '.join(missing_dependencies)}",
            suggestion=suggestion or f"Complete prior phases before calling {tool_name}",
            context={"tool": tool_name, "missing": missing_dependencies}
        )


class OutputFormatError(ToulminiError):
    """LLM output doesn't match expected JSON schema."""

    def __init__(
        self,
        expected_format: str,
        received_preview: str,
        suggestion: Optional[str] = None
    ):
        self.expected_format = expected_format
        self.received_preview = received_preview[:200]
        super().__init__(
            message=f"Expected {expected_format} format, received invalid output",
            suggestion=suggestion or f"Output must be valid {expected_format}. No preamble or explanation.",
            context={"expected": expected_format, "received_preview": self.received_preview}
        )


class ChainValidationError(ToulminiError):
    """Error in chain-level validation (sequential dependencies)."""

    def __init__(
        self,
        phase: str,
        message: str,
        suggestion: Optional[str] = None
    ):
        self.phase = phase
        super().__init__(
            message=message,
            suggestion=suggestion,
            context={"phase": phase}
        )
