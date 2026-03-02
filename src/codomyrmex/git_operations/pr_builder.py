"""PR builder for autonomous code submission.

Creates branch, commit, and PR data from code changes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class FileChange:
    """A single file change.

    Attributes:
        path: File path.
        content: New content.
        action: ``add``, ``modify``, ``delete``.
    """

    path: str
    content: str = ""
    action: str = "add"


@dataclass
class PRSpec:
    """Pull request specification.

    Attributes:
        title: PR title.
        description: PR description.
        branch: Branch name.
        base: Base branch.
        changes: File changes.
        labels: PR labels.
        test_results: Test pass/fail summary.
    """

    title: str = ""
    description: str = ""
    branch: str = ""
    base: str = "main"
    changes: list[FileChange] = field(default_factory=list)
    labels: list[str] = field(default_factory=list)
    test_results: dict[str, Any] = field(default_factory=dict)

    @property
    def file_count(self) -> int:
        return len(self.changes)

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object."""
        return {
            "title": self.title,
            "branch": self.branch,
            "base": self.base,
            "files_changed": self.file_count,
            "labels": self.labels,
            "test_results": self.test_results,
        }


class PRBuilder:
    """Build pull request specifications from code changes.

    Usage::

        builder = PRBuilder()
        pr = builder.create(
            changes=[FileChange("src/new.py", "def hello(): pass")],
            description="Add hello function",
        )
        print(pr.branch)  # e.g. "auto/add-hello-function"
    """

    def create(
        self,
        changes: list[FileChange],
        description: str = "",
        title: str = "",
        labels: list[str] | None = None,
        test_results: dict[str, Any] | None = None,
    ) -> PRSpec:
        """Create a PR spec from changes.

        Args:
            changes: File changes.
            description: PR description.
            title: PR title (auto-generated if empty).
            labels: PR labels.
            test_results: Test results summary.

        Returns:
            ``PRSpec`` ready for submission.
        """
        if not title:
            title = self._auto_title(changes)

        branch = self._branch_name(title)

        pr = PRSpec(
            title=title,
            description=description or f"Auto-generated PR: {title}",
            branch=branch,
            changes=changes,
            labels=labels or ["auto-generated"],
            test_results=test_results or {},
        )

        logger.info("PR built", extra={"title": title, "files": pr.file_count})
        return pr

    @staticmethod
    def _auto_title(changes: list[FileChange]) -> str:
        if not changes:
            return "Empty changeset"
        actions = {c.action for c in changes}
        paths = [c.path.split("/")[-1] for c in changes[:3]]
        verb = "Add" if "add" in actions else "Update"
        return f"{verb} {', '.join(paths)}"

    @staticmethod
    def _branch_name(title: str) -> str:
        slug = title.lower().replace(" ", "-")[:40]
        slug = "".join(c for c in slug if c.isalnum() or c == "-")
        return f"auto/{slug}"


__all__ = ["FileChange", "PRBuilder", "PRSpec"]
