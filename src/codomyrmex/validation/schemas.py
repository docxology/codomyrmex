"""Shared result types for cross-module interop.

Imported by validation/__init__.py and consumed by 74+ modules via:
    from codomyrmex.validation import Result, ResultStatus
"""
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ResultStatus(StrEnum):
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    SKIPPED = "skipped"


@dataclass
class Result:
    status: ResultStatus
    message: str = ""
    data: Any = field(default=None)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.status == ResultStatus.SUCCESS
