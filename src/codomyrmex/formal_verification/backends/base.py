"""Abstract base class for solver backends.

Each backend wraps a specific constraint-solving engine (Z3, PySAT, etc.)
and exposes a uniform interface modeled after szeider/mcp-solver's 6-tool API.
"""

from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


class SolverStatus(enum.Enum):
    """Result status from a solve operation."""

    SAT = "sat"
    UNSAT = "unsat"
    UNKNOWN = "unknown"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class SolverResult:
    """Container for solver output."""

    status: SolverStatus
    model: dict[str, Any] | None = None
    objective_value: Any | None = None
    statistics: dict[str, Any] = field(default_factory=dict)
    error_message: str | None = None

    @property
    def is_sat(self) -> bool:
        """is Sat ."""
        return self.status == SolverStatus.SAT

    @property
    def is_unsat(self) -> bool:
        """is Unsat ."""
        return self.status == SolverStatus.UNSAT


class SolverBackend(ABC):
    """Abstract interface for constraint solver backends.

    Backends implement the mcp-solver 6-tool pattern:
    clear_model, add_item, delete_item, replace_item, get_model, solve_model.
    """

    @abstractmethod
    def clear_model(self) -> None:
        """Remove all items from the model."""

    @abstractmethod
    def add_item(self, item: str, index: int | None = None) -> int:
        """Add an item (constraint/declaration) to the model.

        Args:
            item: The constraint or declaration as a string.
            index: Optional position to insert at. Appends if None.

        Returns:
            The index where the item was inserted.
        """

    @abstractmethod
    def delete_item(self, index: int) -> str:
        """Remove and return the item at the given index."""

    @abstractmethod
    def replace_item(self, index: int, new_item: str) -> str:
        """Replace item at index with new_item, returning the old item."""

    @abstractmethod
    def get_model(self) -> list[tuple[int, str]]:
        """Return all items as (index, content) pairs."""

    @abstractmethod
    def solve_model(self, timeout_ms: int = 30000) -> SolverResult:
        """Execute the solver on the current model.

        Args:
            timeout_ms: Maximum solving time in milliseconds.

        Returns:
            SolverResult with status, model values, and statistics.
        """

    @abstractmethod
    def backend_name(self) -> str:
        """Return the human-readable name of this backend."""
