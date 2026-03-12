"""Mutation status and results for Coda.io."""

from dataclasses import dataclass
from typing import Any


@dataclass
class MutationStatus:
    """Status of an asynchronous mutation."""

    completed: bool
    warning: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MutationStatus":

        return cls(
            completed=data.get("completed", False),
            warning=data.get("warning"),
        )


@dataclass
class InsertRowsResult:
    """Result of inserting rows."""

    request_id: str
    added_row_ids: list[str] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "InsertRowsResult":
        return cls(
            request_id=data.get("requestId", ""),
            added_row_ids=data.get("addedRowIds"),
        )
