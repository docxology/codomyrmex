"""Read-only catalog of top-level Codomyrmex package surfaces.

The catalog is intentionally filesystem-based and side-effect free.  It gives
docs, scripts, and agents one stable place to ask "what exists under
src/codomyrmex?" without changing the higher-impact public
``codomyrmex.list_modules()`` contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from collections.abc import Container

ModuleKind = Literal["runtime_module", "support_surface"]

DEFAULT_SUPPORT_SURFACES = frozenset({"tests"})


@dataclass(frozen=True)
class ModuleCatalogEntry:
    """One top-level entry under ``src/codomyrmex``."""

    name: str
    relative_path: str
    kind: ModuleKind
    has_init: bool
    has_readme: bool
    has_agents: bool
    has_spec: bool
    has_pai: bool
    has_api_spec: bool
    has_mcp_tools: bool
    has_mcp_spec: bool
    has_py_typed: bool
    has_tests: bool
    docs_module_exists: bool

    @property
    def is_runtime_module(self) -> bool:
        """Whether the entry is counted as a runtime module."""
        return self.kind == "runtime_module"

    @property
    def has_required_docs(self) -> bool:
        """Whether the core module docs are present."""
        return self.has_readme and self.has_agents and self.has_spec and self.has_pai

    @property
    def has_mcp_contract_gap(self) -> bool:
        """Whether an MCP implementation is missing its tool specification."""
        return self.has_mcp_tools and not self.has_mcp_spec

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""
        return {
            "name": self.name,
            "relative_path": self.relative_path,
            "kind": self.kind,
            "has_init": self.has_init,
            "has_readme": self.has_readme,
            "has_agents": self.has_agents,
            "has_spec": self.has_spec,
            "has_pai": self.has_pai,
            "has_api_spec": self.has_api_spec,
            "has_mcp_tools": self.has_mcp_tools,
            "has_mcp_spec": self.has_mcp_spec,
            "has_py_typed": self.has_py_typed,
            "has_tests": self.has_tests,
            "docs_module_exists": self.docs_module_exists,
        }


@dataclass(frozen=True)
class ModuleCatalog:
    """Summary and entries for the top-level package catalog."""

    entries: tuple[ModuleCatalogEntry, ...]
    docs_module_names: tuple[str, ...] = ()

    @property
    def runtime_modules(self) -> tuple[ModuleCatalogEntry, ...]:
        """Entries counted as runtime modules."""
        return tuple(entry for entry in self.entries if entry.is_runtime_module)

    @property
    def support_surfaces(self) -> tuple[ModuleCatalogEntry, ...]:
        """Entries treated as support surfaces instead of runtime modules."""
        return tuple(entry for entry in self.entries if not entry.is_runtime_module)

    @property
    def runtime_module_count(self) -> int:
        """Number of runtime modules."""
        return len(self.runtime_modules)

    @property
    def support_surface_count(self) -> int:
        """Number of support surfaces."""
        return len(self.support_surfaces)

    @property
    def docs_module_count(self) -> int:
        """Number of module directories under ``docs/modules``."""
        return len(self.docs_module_names)

    @property
    def mcp_tool_modules_missing_specs(self) -> tuple[str, ...]:
        """Runtime modules with ``mcp_tools.py`` but no MCP tool spec."""
        return tuple(
            entry.name for entry in self.runtime_modules if entry.has_mcp_contract_gap
        )

    @property
    def api_spec_missing(self) -> tuple[str, ...]:
        """Runtime modules missing an API specification document."""
        return tuple(
            entry.name for entry in self.runtime_modules if not entry.has_api_spec
        )

    @property
    def docs_module_missing(self) -> tuple[str, ...]:
        """Runtime modules missing a ``docs/modules/<name>`` counterpart."""
        return tuple(
            entry.name for entry in self.runtime_modules if not entry.docs_module_exists
        )

    @property
    def py_typed_missing(self) -> tuple[str, ...]:
        """Runtime modules missing a PEP 561 marker."""
        return tuple(
            entry.name for entry in self.runtime_modules if not entry.has_py_typed
        )

    @property
    def docs_modules_without_source_entries(self) -> tuple[str, ...]:
        """``docs/modules`` directories without a top-level source counterpart."""
        entry_names = {entry.name for entry in self.entries}
        return tuple(name for name in self.docs_module_names if name not in entry_names)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable summary."""
        return {
            "runtime_module_count": self.runtime_module_count,
            "support_surface_count": self.support_surface_count,
            "docs_module_count": self.docs_module_count,
            "api_spec_missing": list(self.api_spec_missing),
            "mcp_tool_modules_missing_specs": list(self.mcp_tool_modules_missing_specs),
            "docs_module_missing": list(self.docs_module_missing),
            "docs_modules_without_source_entries": list(
                self.docs_modules_without_source_entries
            ),
            "py_typed_missing": list(self.py_typed_missing),
            "entries": [entry.to_dict() for entry in self.entries],
        }


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _has_tests_for_module(repo_root: Path, name: str) -> bool:
    test_root = repo_root / "tests"
    if not test_root.is_dir():
        return False
    patterns = (
        f"test_{name}.py",
        f"test_{name}_*.py",
        f"{name}/test_*.py",
        f"*/{name}/test_*.py",
    )
    return any(any(test_root.glob(pattern)) for pattern in patterns)


def build_module_catalog(
    repo_root: str | Path | None = None,
    *,
    support_surface_names: Container[str] = DEFAULT_SUPPORT_SURFACES,
) -> ModuleCatalog:
    """Build a read-only catalog from the repository filesystem."""
    root = Path(repo_root).resolve() if repo_root is not None else _default_repo_root()
    package_root = root / "src" / "codomyrmex"
    docs_root = root / "docs" / "modules"
    docs_module_names = (
        tuple(sorted(path.name for path in docs_root.iterdir() if path.is_dir()))
        if docs_root.is_dir()
        else ()
    )

    entries: list[ModuleCatalogEntry] = []
    for path in sorted(package_root.iterdir(), key=lambda item: item.name):
        if not path.is_dir() or path.name == "__pycache__":
            continue
        has_init = (path / "__init__.py").is_file()
        kind: ModuleKind = (
            "support_surface"
            if path.name in support_surface_names
            else "runtime_module"
        )
        entries.append(
            ModuleCatalogEntry(
                name=path.name,
                relative_path=path.relative_to(root).as_posix(),
                kind=kind,
                has_init=has_init,
                has_readme=(path / "README.md").is_file(),
                has_agents=(path / "AGENTS.md").is_file(),
                has_spec=(path / "SPEC.md").is_file(),
                has_pai=(path / "PAI.md").is_file(),
                has_api_spec=(path / "API_SPECIFICATION.md").is_file(),
                has_mcp_tools=(path / "mcp_tools.py").is_file(),
                has_mcp_spec=(path / "MCP_TOOL_SPECIFICATION.md").is_file(),
                has_py_typed=(path / "py.typed").is_file(),
                has_tests=_has_tests_for_module(root, path.name),
                docs_module_exists=(docs_root / path.name).is_dir(),
            )
        )

    # ``tests`` moved from ``tests`` to the top-level ``tests/``
    # directory; it remains a recognized support surface even though it is no
    # longer nested under ``package_root``.
    top_level_tests = root / "tests"
    if "tests" in support_surface_names and top_level_tests.is_dir():
        entries.append(
            ModuleCatalogEntry(
                name="tests",
                relative_path=top_level_tests.relative_to(root).as_posix(),
                kind="support_surface",
                has_init=(top_level_tests / "__init__.py").is_file(),
                has_readme=(top_level_tests / "README.md").is_file(),
                has_agents=(top_level_tests / "AGENTS.md").is_file(),
                has_spec=(top_level_tests / "SPEC.md").is_file(),
                has_pai=(top_level_tests / "PAI.md").is_file(),
                has_api_spec=(top_level_tests / "API_SPECIFICATION.md").is_file(),
                has_mcp_tools=(top_level_tests / "mcp_tools.py").is_file(),
                has_mcp_spec=(top_level_tests / "MCP_TOOL_SPECIFICATION.md").is_file(),
                has_py_typed=(top_level_tests / "py.typed").is_file(),
                has_tests=True,
                docs_module_exists=(docs_root / "tests").is_dir(),
            )
        )
        entries.sort(key=lambda entry: entry.name)

    return ModuleCatalog(entries=tuple(entries), docs_module_names=docs_module_names)


__all__ = [
    "DEFAULT_SUPPORT_SURFACES",
    "ModuleCatalog",
    "ModuleCatalogEntry",
    "ModuleKind",
    "build_module_catalog",
]
