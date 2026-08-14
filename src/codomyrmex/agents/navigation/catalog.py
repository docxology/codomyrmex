"""Read-only capability catalog for agentic navigation.

The catalog answers three operational questions without probing credentials,
starting processes, or invoking tools:

* which agent integrations are declared and where their clients live;
* which top-level Codomyrmex modules exist and what support surfaces they have;
* which MCP tools are available when an explicit tool inventory is requested.

Records are stable, JSON-safe, and sorted so an agent can use them as a
navigation index rather than relying on import order or opaque object reprs.
"""

from __future__ import annotations

import builtins
import importlib.util
import json
import math
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, cast

from codomyrmex.agents.pai.mcp.trust_metadata import is_destructive_tool

CapabilityKind = Literal["agent", "module", "tool"]
_VALID_KINDS = frozenset({"agent", "module", "tool"})


@dataclass(frozen=True)
class CapabilityRecord:
    """One navigable capability with no executable handler attached."""

    id: str
    kind: CapabilityKind
    name: str
    display_name: str
    description: str
    status: str
    source: str
    documentation: str | None = None
    trust: str = "read_only"
    tags: tuple[str, ...] = ()
    details: dict[str, Any] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-safe record for MCP and CLI consumers."""
        return {
            "id": self.id,
            "kind": self.kind,
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "status": self.status,
            "source": self.source,
            "documentation": self.documentation,
            "provenance": _json_safe(self.provenance),
            "trust": self.trust,
            "tags": _json_safe(self.tags),
            "details": _json_safe(self.details),
        }


class CapabilityCatalog:
    """Deterministic, in-memory index of capability records."""

    def __init__(
        self,
        records: tuple[CapabilityRecord, ...],
        errors: tuple[str, ...] = (),
        provenance: Mapping[str, Any] | None = None,
    ) -> None:
        self._records = tuple(sorted(records, key=_record_sort_key))
        self.errors = tuple(sorted({str(error) for error in errors}))
        self._provenance = _json_safe(dict(provenance or {}))

    def list(
        self,
        *,
        kind: CapabilityKind | None = None,
        include_unavailable: bool = False,
        limit: int = 100,
    ) -> builtins.list[CapabilityRecord]:
        """List records with stable ordering and an enforced result bound."""
        normalized_kind = _validated_kind(kind)
        _validated_bool(include_unavailable, "include_unavailable")
        bounded_limit = _bounded_limit(limit)
        records = [
            record
            for record in self._records
            if (normalized_kind is None or record.kind == normalized_kind)
            and (include_unavailable or record.status != "unavailable")
        ]
        return records[:bounded_limit]

    def find(
        self, capability_id: str, *, kind: CapabilityKind | None = None
    ) -> tuple[CapabilityRecord, ...]:
        """Return exact or bare-name matches in deterministic order.

        Bare names are convenient for humans but can be ambiguous when an
        agent and module share a name. Callers that need one record should use
        :meth:`get` and treat ``None`` as not found or ambiguous.
        """
        if not isinstance(capability_id, str):
            raise ValueError("capability_id must be a string")
        normalized = capability_id.strip()
        if not normalized:
            raise ValueError("capability_id must not be empty")
        normalized_kind = _validated_kind(kind)
        return tuple(
            record
            for record in self._records
            if (normalized_kind is None or record.kind == normalized_kind)
            and (
                record.id == normalized
                or (":" not in normalized and record.name == normalized)
            )
        )

    def get(
        self, capability_id: str, *, kind: CapabilityKind | None = None
    ) -> CapabilityRecord | None:
        """Find one exact ID or an unambiguous bare-name match."""
        matches = self.find(capability_id, kind=kind)
        return matches[0] if len(matches) == 1 else None

    def search(
        self,
        query: str,
        *,
        kind: CapabilityKind | None = None,
        include_unavailable: bool = False,
        limit: int = 20,
    ) -> builtins.list[CapabilityRecord]:
        """Search names, descriptions, sources, tags, and IDs deterministically."""
        _validated_kind(kind)
        _validated_bool(include_unavailable, "include_unavailable")
        if not isinstance(query, str):
            raise ValueError("query must be a string")
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("query must not be empty")
        # Search the complete filtered catalog. ``list`` intentionally caps
        # returned pages, but using that page cap as the search corpus makes
        # later-sorting records silently undiscoverable.
        candidates = [
            record
            for record in self._records
            if (kind is None or record.kind == kind)
            and (include_unavailable or record.status != "unavailable")
        ]
        terms = tuple(re.findall(r"[a-z0-9_:-]+", normalized_query.lower()))
        if not terms:
            raise ValueError("query must contain searchable characters")

        scored: list[tuple[int, CapabilityRecord]] = []
        for record in candidates:
            fields = {
                "id": record.id.lower(),
                "name": record.name.lower(),
                "display": record.display_name.lower(),
                "description": record.description.lower(),
                "source": record.source.lower(),
                "documentation": (record.documentation or "").lower(),
                "tags": " ".join(record.tags).lower(),
            }
            score = 0
            for term in terms:
                if fields["name"] == term or fields["id"] == term:
                    score += 12
                elif fields["name"].startswith(term):
                    score += 8
                elif any(term in value for value in fields.values()):
                    score += 3
            if score:
                scored.append((score, record))

        scored.sort(key=lambda item: (-item[0], *_record_sort_key(item[1])))
        bounded_limit = _bounded_limit(limit)
        return [record for _, record in scored[:bounded_limit]]

    def summary(self) -> dict[str, Any]:
        """Return counts and errors suitable for an operability receipt."""
        by_kind: dict[str, int] = {}
        by_status: dict[str, int] = {}
        for record in self._records:
            by_kind[record.kind] = by_kind.get(record.kind, 0) + 1
            by_status[record.status] = by_status.get(record.status, 0) + 1
        return {
            "count": len(self._records),
            "catalog_state": (
                "degraded" if self.errors else "empty" if not self._records else "ready"
            ),
            "by_kind": dict(sorted(by_kind.items())),
            "by_status": dict(sorted(by_status.items())),
            "errors": list(self.errors),
            "provenance": dict(self._provenance),
        }


def _validated_kind(value: str | None) -> CapabilityKind | None:
    """Validate a capability kind without accepting implicit coercions."""
    if value is None:
        return None
    if not isinstance(value, str) or value not in _VALID_KINDS:
        raise ValueError(f"Unsupported capability kind: {value!r}")
    return cast("CapabilityKind", value)


def _validated_bool(value: bool, name: str) -> None:
    """Reject truthy non-booleans at the Python API boundary."""
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be a boolean")


def _bounded_limit(value: int) -> int:
    """Validate and bound public result limits without implicit coercion."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("limit must be an integer")
    return max(1, min(value, 500))


def _json_safe(value: Any) -> Any:
    """Convert metadata to deterministic JSON-compatible primitives."""
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else str(value)
    if isinstance(value, Mapping):
        items = ((str(key), _json_safe(item)) for key, item in value.items())
        return dict(sorted(items))
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (set, frozenset)):
        items = [_json_safe(item) for item in value]
        return sorted(
            items,
            key=lambda item: json.dumps(item, sort_keys=True, separators=(",", ":")),
        )
    return {"unsupported_type": f"{type(value).__module__}.{type(value).__qualname__}"}


def _record_sort_key(record: CapabilityRecord) -> tuple[str, str, str]:
    """Sort by kind, stable name, and ID for collision-free output."""
    return (record.kind, record.name, record.id)


def _repository_root() -> Path:
    """Return the checkout root implied by this source file."""
    return Path(__file__).resolve().parents[4]


def _safe_repo_relative_path(path: Path, repo_root: Path) -> str | None:
    """Return a relative path without leaking paths outside the checkout."""
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except (OSError, ValueError):
        return None


def _existing_doc_path(path: Path, repo_root: Path) -> str | None:
    """Return a documentation path only when the claimed file exists."""
    try:
        if not path.is_file():
            return None
    except OSError:
        return None
    return _safe_repo_relative_path(path, repo_root)


def _module_doc_path(module_path: str) -> str | None:
    """Map a source module path to its nearest module-level README."""
    parts = module_path.split(".")
    if len(parts) < 2 or parts[0] != "codomyrmex":
        return None
    if any(not part.isidentifier() for part in parts):
        return None
    source_dir = (
        "/".join(parts[1:-1]) if parts[-1] == "mcp_tools" else "/".join(parts[1:])
    )
    return f"src/codomyrmex/{source_dir}/README.md" if source_dir else None


def _agent_records(errors: list[str]) -> list[CapabilityRecord]:
    records: list[CapabilityRecord] = []
    repo_root = _repository_root()
    try:
        # Keep importing the navigation module itself side-effect free. Agent
        # registry construction is deferred until a catalog is explicitly
        # built, and remains metadata-only.
        from codomyrmex.agents.agent_setup import AgentRegistry

        descriptors = AgentRegistry().list_agents()
    except Exception as exc:
        errors.append(f"agents: {type(exc).__name__}: {exc}")
        return records

    for descriptor in descriptors:
        client_path = None
        status = "declared"
        if descriptor.client_module and descriptor.client_class:
            client_path = f"{descriptor.client_module}.{descriptor.client_class}"
            try:
                status = (
                    "implementation_present"
                    if importlib.util.find_spec(descriptor.client_module)
                    else "unavailable"
                )
            except (ImportError, ModuleNotFoundError, ValueError) as exc:
                status = "unavailable"
                errors.append(f"agent:{descriptor.name}: {type(exc).__name__}: {exc}")
        records.append(
            CapabilityRecord(
                id=f"agent:{descriptor.name}",
                kind="agent",
                name=descriptor.name,
                display_name=descriptor.display_name,
                description=(
                    f"{descriptor.agent_type} agent using {descriptor.default_model}; "
                    "registry metadata only; construction and health are unverified"
                ),
                status=status,
                source=client_path or "agent registry",
                documentation=_existing_doc_path(
                    repo_root / "docs" / "agents" / descriptor.name / "README.md",
                    repo_root,
                ),
                provenance={
                    "discovered_by": "agent_registry",
                    "source_path": client_path or "agent registry",
                    "metadata_only": True,
                },
                trust="execution",
                tags=(descriptor.agent_type, "agent", "dispatch", "provider"),
                details={
                    "agent_type": descriptor.agent_type,
                    "config_key": descriptor.config_key,
                    "env_var": descriptor.env_var,
                    "default_model": descriptor.default_model,
                    "client_path": client_path,
                    "live_probe_performed": False,
                    "construction_verified": False,
                },
            )
        )
    return records


def _module_records(errors: list[str]) -> list[CapabilityRecord]:
    """Build module records without crossing the agent-layer boundary.

    This intentionally duplicates the small filesystem contract used by the
    system-discovery catalog.  The navigation surface is in the agents layer;
    importing system discovery here would make a read-only index violate the
    repository's foundation/core/service layering contract.
    """
    records: list[CapabilityRecord] = []
    package_root = Path(__file__).resolve().parents[2]
    repo_root = package_root.parents[1]
    docs_root = repo_root / "docs" / "modules"
    tests_root = repo_root / "tests"
    if not package_root.is_dir():
        errors.append(f"modules: package root is unavailable: {package_root}")
        return records

    try:
        module_paths = sorted(
            (
                path
                for path in package_root.iterdir()
                if path.is_dir() and path.name != "__pycache__"
            ),
            key=lambda path: path.name,
        )
    except OSError as exc:
        errors.append(f"modules: {type(exc).__name__}: {exc}")
        return records

    for path in module_paths:
        name = path.name
        test_patterns = (
            f"test_{name}.py",
            f"test_{name}_*.py",
            f"{name}/test_*.py",
            f"*/{name}/test_*.py",
        )
        has_tests = tests_root.is_dir() and any(
            any(tests_root.glob(pattern)) for pattern in test_patterns
        )
        has_init = (path / "__init__.py").is_file()
        has_readme = (path / "README.md").is_file()
        has_agents = (path / "AGENTS.md").is_file()
        has_spec = (path / "SPEC.md").is_file()
        has_pai = (path / "PAI.md").is_file()
        has_api_spec = (path / "API_SPECIFICATION.md").is_file()
        has_mcp_tools = (path / "mcp_tools.py").is_file()
        has_mcp_spec = (path / "MCP_TOOL_SPECIFICATION.md").is_file()
        has_py_typed = (path / "py.typed").is_file()
        missing_surfaces = [
            surface
            for surface, present in (
                ("README.md", has_readme),
                ("AGENTS.md", has_agents),
                ("SPEC.md", has_spec),
                ("PAI.md", has_pai),
                ("API_SPECIFICATION.md", has_api_spec),
                ("MCP_TOOL_SPECIFICATION.md", has_mcp_spec),
                ("py.typed", has_py_typed),
            )
            if not present
        ]
        records.append(
            CapabilityRecord(
                id=f"module:{name}",
                kind="module",
                name=name,
                display_name=f"codomyrmex.{name}",
                description="Top-level Codomyrmex runtime module",
                status="available" if has_init else "unavailable",
                source=_safe_repo_relative_path(path, repo_root)
                or "package filesystem",
                documentation=_existing_doc_path(
                    docs_root / name / "README.md", repo_root
                ),
                provenance={
                    "discovered_by": "filesystem",
                    "root": "src/codomyrmex",
                    "relative_path": _safe_repo_relative_path(path, repo_root),
                    "metadata_only": True,
                },
                trust="read_only",
                tags=("module", "runtime"),
                details={
                    "has_required_docs": has_readme
                    and has_agents
                    and has_spec
                    and has_pai,
                    "has_mcp_tools": has_mcp_tools,
                    "missing_surfaces": missing_surfaces,
                    "has_tests": has_tests,
                    "docs_module_exists": (docs_root / name / "README.md").is_file(),
                },
            )
        )
    return records


def _tool_records(errors: list[str]) -> list[CapabilityRecord]:
    records_by_id: dict[str, CapabilityRecord] = {}
    repo_root = _repository_root()

    def documentation_for(module_path: str) -> str | None:
        relative_path = _module_doc_path(module_path)
        if relative_path is None:
            return None
        return _existing_doc_path(repo_root / relative_path, repo_root)

    try:
        from codomyrmex.agents.pai.mcp.definitions import TOOL_DEFINITIONS

        for name, description, handler, schema in TOOL_DEFINITIONS:
            destructive = is_destructive_tool(name)
            records_by_id[f"tool:{name}"] = CapabilityRecord(
                id=f"tool:{name}",
                kind="tool",
                name=name,
                display_name=name.removeprefix("codomyrmex."),
                description=description,
                status="available",
                source=f"{handler.__module__}.{handler.__name__}",
                documentation=documentation_for(handler.__module__),
                provenance={
                    "discovered_by": "static_mcp_registry",
                    "source_path": f"{handler.__module__}.{handler.__name__}",
                    "metadata_only": True,
                },
                trust="restricted" if destructive else "read_only",
                tags=(
                    "mcp",
                    "static",
                    "tool",
                    "destructive" if destructive else "read_only",
                ),
                details={
                    "schema": schema,
                    "dynamic": False,
                    "destructive": destructive,
                },
            )
    except Exception as exc:
        errors.append(f"static tools: {type(exc).__name__}: {exc}")

    try:
        from codomyrmex.agents.pai.mcp.discovery import discover_dynamic_tools

        for name, description, handler, schema in discover_dynamic_tools():
            destructive = is_destructive_tool(name)
            records_by_id.setdefault(
                f"tool:{name}",
                CapabilityRecord(
                    id=f"tool:{name}",
                    kind="tool",
                    name=name,
                    display_name=name.removeprefix("codomyrmex."),
                    description=description,
                    status="available",
                    source=f"{handler.__module__}.{handler.__name__}",
                    documentation=documentation_for(handler.__module__),
                    provenance={
                        "discovered_by": "dynamic_mcp_discovery",
                        "source_path": f"{handler.__module__}.{handler.__name__}",
                        "metadata_only": True,
                    },
                    trust="restricted" if destructive else "read_only",
                    tags=(
                        "dynamic",
                        "mcp",
                        "tool",
                        "destructive" if destructive else "read_only",
                    ),
                    details={
                        "schema": schema,
                        "dynamic": True,
                        "destructive": destructive,
                    },
                ),
            )
    except Exception as exc:
        errors.append(f"dynamic tools: {type(exc).__name__}: {exc}")
    return list(records_by_id.values())


def build_capability_catalog(*, include_tools: bool = False) -> CapabilityCatalog:
    """Build a read-only capability catalog.

    Agent and module records are always filesystem/import metadata only. Tool
    records are included only when requested because dynamic MCP discovery may
    import optional provider modules and can be comparatively expensive.
    """
    if not isinstance(include_tools, bool):
        raise ValueError("include_tools must be a boolean")
    errors: list[str] = []
    records = _agent_records(errors) + _module_records(errors)
    if include_tools:
        records.extend(_tool_records(errors))
    sources = ["agent_registry", "package_filesystem"]
    if include_tools:
        sources.extend(["static_mcp_definitions", "dynamic_mcp_discovery"])
    return CapabilityCatalog(
        tuple(records),
        tuple(errors),
        provenance={
            "schema_version": 1,
            "mode": "metadata_only",
            "live_probes_performed": False,
            "tool_discovery_requested": include_tools,
            "sources": sources,
        },
    )


__all__ = [
    "CapabilityCatalog",
    "CapabilityKind",
    "CapabilityRecord",
    "build_capability_catalog",
]
