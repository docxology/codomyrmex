"""Structured TODO list management for the droid runner."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple
from codomyrmex.exceptions import CodomyrmexError
from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


TODO_HEADER = "[TODO]"
COMPLETED_HEADER = "[COMPLETED]"


@dataclass
class TodoItem:
    """Todoitem.

        A class for handling todoitem operations.
        """
    operation_id: str
    handler_path: str
    description: str

    @classmethod
    def parse(cls, raw: str) -> "TodoItem":
        """Parse.

            Args:        cls: Parameter for the operation.        raw: Parameter for the operation.

            Returns:        The result of the operation.
            """
        parts = [part.strip() for part in raw.split("|")]
        if len(parts) != 3:
            raise ValueError(f"Invalid TODO entry: {raw}")
        return cls(operation_id=parts[0], handler_path=parts[1], description=parts[2])

    def serialise(self) -> str:
        return f"{self.operation_id} | {self.handler_path} | {self.description}"


class TodoManager:
    """Todomanager.

    A class for handling todomanager operations.
    """
    
    def __init__(self, todo_file: str | Path):
        self.todo_path = Path(todo_file)

    def load(self) -> Tuple[List[TodoItem], List[TodoItem]]:
        """Load.

        Returns:        The result of the operation.
        """
        if not self.todo_path.exists():
            return [], []

        todo_items: List[TodoItem] = []
        completed_items: List[TodoItem] = []
        bucket = None
        skipped_lines = []

        for line_num, line in enumerate(
            self.todo_path.read_text(encoding="utf-8").splitlines(), 1
        ):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.upper() == TODO_HEADER:
                bucket = todo_items
                continue
            if stripped.upper() == COMPLETED_HEADER:
                bucket = completed_items
                continue
            if bucket is None:
                raise ValueError("TODO file missing section headers")

            try:
                bucket.append(TodoItem.parse(stripped))
            except ValueError as e:
                skipped_lines.append((line_num, stripped, str(e)))
                print(
                    f"⚠️  Warning: Skipping malformed TODO entry on line {line_num}: {e}"
                )
                continue

        if skipped_lines:
            print(
                f"ℹ️  Skipped {len(skipped_lines)} malformed TODO entries. Please fix the format."
            )

        return todo_items, completed_items

    def save(
        self, todo_items: Sequence[TodoItem], completed_items: Sequence[TodoItem]
    ) -> None:
        lines = [TODO_HEADER]
        lines.extend(item.serialise() for item in todo_items)
        lines.append("")
        lines.append(COMPLETED_HEADER)
        lines.extend(item.serialise() for item in completed_items)
        self.todo_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def rotate(
        self,
        processed: Iterable[TodoItem],
        remaining: Sequence[TodoItem],
        completed: Sequence[TodoItem],
    ) -> None:
        processed_list = list(processed)
        self.save(list(remaining), list(completed) + processed_list)


__all__ = ["TodoManager", "TodoItem", "TODO_HEADER", "COMPLETED_HEADER"]
