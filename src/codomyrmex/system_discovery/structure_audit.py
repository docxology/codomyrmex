"""Read-only structure audit for top-level Codomyrmex modules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from codomyrmex.system_discovery.module_catalog import (
    ModuleCatalog,
    ModuleCatalogEntry,
    build_module_catalog,
)

if TYPE_CHECKING:
    from pathlib import Path

IssueSeverity = Literal["error", "warning"]

RETIRED_GHOST_ARCHITECTURE = "ghost" + "_architecture"
DEFAULT_RETIRED_MODULE_NAMES = frozenset({RETIRED_GHOST_ARCHITECTURE})


@dataclass(frozen=True)
class StructureIssue:
    """One structural issue found in the source module layout."""

    severity: IssueSeverity
    code: str
    module: str
    message: str
    relative_path: str

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable representation."""
        return {
            "severity": self.severity,
            "code": self.code,
            "module": self.module,
            "message": self.message,
            "relative_path": self.relative_path,
        }


@dataclass(frozen=True)
class ModuleStructureAudit:
    """Structure audit result for ``src/codomyrmex``."""

    catalog: ModuleCatalog
    issues: tuple[StructureIssue, ...]

    @property
    def errors(self) -> tuple[StructureIssue, ...]:
        """Issues that should fail structure gates."""
        return tuple(issue for issue in self.issues if issue.severity == "error")

    @property
    def warnings(self) -> tuple[StructureIssue, ...]:
        """Issues that should be reviewed but do not fail the gate."""
        return tuple(issue for issue in self.issues if issue.severity == "warning")

    @property
    def passed(self) -> bool:
        """Whether the structure audit has no errors."""
        return not self.errors

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable audit summary."""
        return {
            "passed": self.passed,
            "runtime_module_count": self.catalog.runtime_module_count,
            "support_surface_count": self.catalog.support_surface_count,
            "docs_module_count": self.catalog.docs_module_count,
            "orphaned_docs_module_count": len(
                self.catalog.docs_modules_without_source_entries
            ),
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "issues": [issue.to_dict() for issue in self.issues],
        }

    def to_markdown(self) -> str:
        """Return a concise Markdown report."""
        lines = [
            "# Codomyrmex Source Structure Audit",
            "",
            f"- Runtime modules: {self.catalog.runtime_module_count}",
            f"- Support surfaces: {self.catalog.support_surface_count}",
            f"- Docs module directories: {self.catalog.docs_module_count}",
            "- Orphaned docs module directories: "
            f"{len(self.catalog.docs_modules_without_source_entries)}",
            f"- Errors: {len(self.errors)}",
            f"- Warnings: {len(self.warnings)}",
            f"- Status: {'PASS' if self.passed else 'FAIL'}",
        ]
        if self.issues:
            lines.extend(
                [
                    "",
                    "| Severity | Code | Module | Path | Message |",
                    "|---|---|---|---|---|",
                ]
            )
            for issue in self.issues:
                lines.append(
                    "| "
                    f"{issue.severity} | {issue.code} | {issue.module} | "
                    f"{issue.relative_path} | {issue.message} |"
                )
        return "\n".join(lines) + "\n"


def _issue(
    entry: ModuleCatalogEntry,
    code: str,
    message: str,
    *,
    severity: IssueSeverity = "error",
) -> StructureIssue:
    return StructureIssue(
        severity=severity,
        code=code,
        module=entry.name,
        message=message,
        relative_path=entry.relative_path,
    )


def _entry_issues(entry: ModuleCatalogEntry) -> list[StructureIssue]:
    issues: list[StructureIssue] = []
    if entry.kind == "support_surface":
        if not entry.has_agents:
            issues.append(
                _issue(
                    entry,
                    "support-agents-missing",
                    "Support surface is missing AGENTS.md.",
                    severity="warning",
                )
            )
        if not entry.has_readme:
            issues.append(
                _issue(
                    entry,
                    "support-readme-missing",
                    "Support surface is missing README.md.",
                    severity="warning",
                )
            )
        return issues

    if not entry.has_init:
        issues.append(
            _issue(entry, "init-missing", "Runtime module lacks __init__.py.")
        )
    if not entry.has_readme:
        issues.append(
            _issue(entry, "readme-missing", "Runtime module lacks README.md.")
        )
    if not entry.has_agents:
        issues.append(
            _issue(entry, "agents-missing", "Runtime module lacks AGENTS.md.")
        )
    if not entry.has_spec:
        issues.append(_issue(entry, "spec-missing", "Runtime module lacks SPEC.md."))
    if not entry.has_pai:
        issues.append(_issue(entry, "pai-missing", "Runtime module lacks PAI.md."))
    if not entry.has_api_spec:
        issues.append(
            _issue(
                entry, "api-spec-missing", "Runtime module lacks API_SPECIFICATION.md."
            )
        )
    if entry.has_mcp_tools and not entry.has_mcp_spec:
        issues.append(
            _issue(
                entry,
                "mcp-spec-missing",
                "Runtime module exposes mcp_tools.py without MCP_TOOL_SPECIFICATION.md.",
            )
        )
    if not entry.has_py_typed:
        issues.append(
            _issue(
                entry,
                "py-typed-missing",
                "Runtime module lacks py.typed marker.",
            )
        )
    if not entry.has_tests:
        issues.append(_issue(entry, "tests-missing", "Runtime module lacks tests."))
    if not entry.docs_module_exists:
        issues.append(
            _issue(
                entry,
                "docs-module-missing",
                "Runtime module lacks docs/modules/<name> counterpart.",
            )
        )
    return issues


def audit_module_structure(
    repo_root: str | Path | None = None,
    *,
    retired_module_names: set[str] | frozenset[str] = DEFAULT_RETIRED_MODULE_NAMES,
) -> ModuleStructureAudit:
    """Audit the top-level source module structure without writing files."""
    catalog = build_module_catalog(repo_root)
    issues: list[StructureIssue] = []
    for module_name in catalog.docs_modules_without_source_entries:
        issues.append(
            StructureIssue(
                severity="error",
                code="docs-module-orphaned",
                module=module_name,
                message="docs/modules entry lacks a top-level src/codomyrmex counterpart.",
                relative_path=f"docs/modules/{module_name}",
            )
        )
    for entry in catalog.entries:
        if entry.name in retired_module_names:
            issues.append(
                _issue(
                    entry,
                    "retired-module-present",
                    "Retired module name is still present in src/codomyrmex.",
                )
            )
        issues.extend(_entry_issues(entry))
    return ModuleStructureAudit(catalog=catalog, issues=tuple(issues))


__all__ = [
    "DEFAULT_RETIRED_MODULE_NAMES",
    "RETIRED_GHOST_ARCHITECTURE",
    "IssueSeverity",
    "ModuleStructureAudit",
    "StructureIssue",
    "audit_module_structure",
]
