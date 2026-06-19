"""Read-only Codex access probes for Codomyrmex agentic surfaces.

This module gives Codex and sibling agents a single safe place to inspect the
Codomyrmex MCP, skills, trust, Hermes, and dispatch surfaces.  It deliberately
does not execute dispatches, sync upstream repositories, mutate trust state, or
call remote model APIs.
"""

from __future__ import annotations

import contextlib
import io
import os
import shutil
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

T = TypeVar("T")


def _repo_root(repo_root: str | Path | None = None) -> Path:
    if repo_root is not None:
        return Path(repo_root).expanduser().resolve()
    return Path(__file__).resolve().parents[4]


def _capture_noisy_call(func: Callable[[], T]) -> tuple[T, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        result = func()
    return result, stdout.getvalue(), stderr.getvalue()


def _summarize_captured_output(stdout: str, stderr: str) -> dict[str, Any]:
    lines = [line for line in (stdout + "\n" + stderr).splitlines() if line.strip()]
    return {
        "line_count": len(lines),
        "sample": lines[:10],
    }


def _json_safe(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _safe_surface(label: str, func: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    try:
        surface = func()
    except Exception as exc:
        return {"status": "error", "label": label, "error": str(exc)}
    surface.setdefault("status", "ready")
    surface.setdefault("label", label)
    return surface


def _count_yaml_skill_files(skills_root: Path) -> dict[str, Any]:
    upstream_dir = skills_root / "upstream"
    custom_dir = skills_root / "custom"

    def count_files(root: Path) -> tuple[int, list[str]]:
        if not root.exists():
            return 0, []
        files = sorted(
            path
            for pattern in ("skill.yaml", "*.yaml")
            for path in root.rglob(pattern)
            if path.is_file()
        )
        categories = sorted(
            {path.relative_to(root).parts[0] for path in files if path.parts}
        )
        return len(files), categories

    upstream_count, upstream_categories = count_files(upstream_dir)
    custom_count, custom_categories = count_files(custom_dir)
    return {
        "status": "ready",
        "skills_root": str(skills_root),
        "upstream_dir": str(upstream_dir),
        "custom_dir": str(custom_dir),
        "upstream_exists": upstream_dir.exists(),
        "custom_exists": custom_dir.exists(),
        "upstream_skill_files": upstream_count,
        "custom_skill_files": custom_count,
        "skill_files": upstream_count + custom_count,
        "categories": sorted(set(upstream_categories + custom_categories)),
    }


def _mcp_surface() -> dict[str, Any]:
    def load_manifest() -> dict[str, Any]:
        from codomyrmex.agents.pai.mcp_bridge import (
            PROMPT_COUNT,
            RESOURCE_COUNT,
            TOOL_COUNT,
            get_discovery_metrics,
            get_skill_manifest,
        )

        manifest = get_skill_manifest()
        metrics = get_discovery_metrics()
        return {
            "manifest": manifest,
            "metrics": metrics,
            "static_tool_count": TOOL_COUNT,
            "resource_count": RESOURCE_COUNT,
            "prompt_count": PROMPT_COUNT,
        }

    payload, stdout, stderr = _capture_noisy_call(load_manifest)
    manifest = payload["manifest"]
    tools = manifest.get("tools", [])
    resources = manifest.get("resources", [])
    prompts = manifest.get("prompts", [])
    workflows = manifest.get("workflows", [])
    tool_categories = Counter()
    for tool in tools:
        if isinstance(tool, dict):
            tool_categories[str(tool.get("category", "unknown"))] += 1
        else:
            tool_categories["unknown"] += 1

    return {
        "status": "ready",
        "mcp_server": manifest.get("mcp_server", "codomyrmex-mcp-server"),
        "tool_count": len(tools),
        "static_tool_count": payload["static_tool_count"],
        "dynamic_metrics": _json_safe(payload["metrics"]),
        "resource_count": len(resources),
        "static_resource_count": payload["resource_count"],
        "prompt_count": len(prompts),
        "static_prompt_count": payload["prompt_count"],
        "workflow_count": len(workflows),
        "tool_categories": dict(sorted(tool_categories.items())),
        "captured_output": _summarize_captured_output(stdout, stderr),
    }


def _skill_surfaces(root: Path) -> dict[str, Any]:
    skills_root = root / "src" / "codomyrmex" / "skills" / "skills"
    yaml_surface = _count_yaml_skill_files(skills_root)

    from codomyrmex.skills.discovery import DEFAULT_REGISTRY

    registered = DEFAULT_REGISTRY.list_all()
    return {
        "status": "ready",
        "yaml": yaml_surface,
        "python_discovery": {
            "status": "ready",
            "registry": "codomyrmex.skills.discovery.DEFAULT_REGISTRY",
            "registered_skill_count": len(registered),
            "registered_skills": [_json_safe(skill.to_dict()) for skill in registered],
        },
        "markdown_skill_packs": [
            {
                "path": str(path.relative_to(root)),
                "exists": path.exists(),
            }
            for path in (
                root / "SKILL.md",
                root / "src" / "codomyrmex" / "agents" / "pai" / "SKILL.md",
                root / "src" / "codomyrmex" / "orchestrator" / "fractals" / "SKILL.md",
            )
        ],
    }


def _hermes_surface() -> dict[str, Any]:
    hermes_home = Path.home() / ".hermes"
    skills_dir = hermes_home / "skills"
    skill_dirs = (
        sorted(path.name for path in skills_dir.iterdir() if path.is_dir())
        if skills_dir.exists()
        else []
    )
    return {
        "status": "ready",
        "bridge": "codomyrmex.skills.HermesSkillBridge",
        "hermes_binary": shutil.which("hermes"),
        "hermes_home": str(hermes_home),
        "skills_dir": str(skills_dir),
        "skills_dir_exists": skills_dir.exists(),
        "skill_count": len(skill_dirs),
        "skills": skill_dirs[:50],
        "truncated": len(skill_dirs) > 50,
    }


def _trust_surface() -> dict[str, Any]:
    from codomyrmex.agents.pai.trust_gateway import DESTRUCTIVE_TOOLS, TrustLevel

    return {
        "status": "ready",
        "levels": [level.value for level in TrustLevel],
        "destructive_tools": sorted(DESTRUCTIVE_TOOLS),
        "destructive_tool_count": len(DESTRUCTIVE_TOOLS),
        "contract": {
            "verify": "read-only tools become VERIFIED",
            "trust": "destructive and dynamic tools require TRUSTED state",
        },
    }


def _codex_client_surface() -> dict[str, Any]:
    return {
        "status": "ready",
        "client": "codomyrmex.agents.codex.CodexClient",
        "mcp_tools": [
            "codomyrmex.codex_execute",
            "codomyrmex.codex_access_status",
            "codomyrmex.codex_dispatch_catalog",
        ],
        "openai_api_key_present": bool(os.environ.get("OPENAI_API_KEY")),
        "codex_model": os.environ.get("CODEX_MODEL"),
        "network_call_performed": False,
    }


def get_codex_dispatch_catalog(
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Return a read-only catalog of Codomyrmex dispatch surfaces."""
    root = _repo_root(repo_root)
    entries: list[dict[str, Any]] = [
        {
            "id": "agent_orchestrator.parallel",
            "name": "AgentOrchestrator.execute_parallel",
            "classification": "side_effectful",
            "surface": "python",
            "entrypoint": "codomyrmex.agents.generic.AgentOrchestrator.execute_parallel",
            "available": (root / "src" / "codomyrmex" / "agents" / "generic").exists(),
            "notes": "Runs caller-supplied AgentInterface instances in threads.",
        },
        {
            "id": "agent_orchestrator.sequential",
            "name": "AgentOrchestrator.execute_sequential",
            "classification": "side_effectful",
            "surface": "python",
            "entrypoint": "codomyrmex.agents.generic.AgentOrchestrator.execute_sequential",
            "available": (root / "src" / "codomyrmex" / "agents" / "generic").exists(),
            "notes": "Runs caller-supplied agents in order.",
        },
        {
            "id": "message_bus",
            "name": "MessageBus publish/subscribe",
            "classification": "side_effectful",
            "surface": "python",
            "entrypoint": "codomyrmex.agents.generic.MessageBus",
            "available": (
                root / "src" / "codomyrmex" / "agents" / "generic" / "message_bus.py"
            ).exists(),
            "notes": "In-process routing; publishing invokes subscribed handlers.",
        },
        {
            "id": "pai.dispatch.execute",
            "name": "PAI dispatch execute endpoint",
            "classification": "side_effectful",
            "surface": "http",
            "entrypoint": "POST /api/dispatch/execute",
            "available": (root / "scripts" / "pai" / "SPEC.md").exists(),
            "notes": "Starts an asynchronous backend job and streams events.",
        },
        {
            "id": "pai.dispatch.jobs",
            "name": "PAI dispatch jobs endpoint",
            "classification": "read_only",
            "surface": "http",
            "entrypoint": "GET /api/dispatch/jobs",
            "available": (root / "scripts" / "pai" / "SPEC.md").exists(),
            "notes": "Lists recent dispatch manifests/status records.",
        },
        {
            "id": "improve_src.dry_run",
            "name": "Source improvement swarm dry-run",
            "classification": "dry_run",
            "surface": "cli",
            "entrypoint": (
                "uv run python scripts/agents/improve_src.py --dry-run --json"
            ),
            "available": (root / "scripts" / "agents" / "improve_src.py").exists(),
            "notes": "Builds a machine-readable task manifest without launching agents.",
        },
        {
            "id": "improve_src.jules",
            "name": "Source improvement swarm dispatch",
            "classification": "side_effectful",
            "surface": "cli",
            "entrypoint": "uv run python scripts/agents/improve_src.py",
            "available": (root / "scripts" / "agents" / "improve_src.py").exists(),
            "notes": "Launches Jules agents; keep opt-in and reviewed after dry-run.",
        },
        {
            "id": "mission_control.openclaw",
            "name": "Mission Control / OpenClaw task dispatch",
            "classification": "side_effectful",
            "surface": "service",
            "entrypoint": "src/codomyrmex/agents/mission_control/app",
            "available": (
                root / "src" / "codomyrmex" / "agents" / "mission_control" / "app"
            ).exists(),
            "notes": "Submodule-backed task orchestration surface when initialized.",
        },
    ]
    by_classification = Counter(entry["classification"] for entry in entries)
    return {
        "status": "ready",
        "repo_root": str(root),
        "dispatchers": entries,
        "summary": {
            "total": len(entries),
            "by_classification": dict(sorted(by_classification.items())),
            "available": sum(1 for entry in entries if entry["available"]),
        },
    }


def get_codex_access_status(
    repo_root: str | Path | None = None,
) -> dict[str, Any]:
    """Return one read-only status payload for Codex-visible repo capabilities."""
    root = _repo_root(repo_root)
    surfaces = {
        "pai_mcp": _safe_surface("pai_mcp", _mcp_surface),
        "skills": _safe_surface("skills", lambda: _skill_surfaces(root)),
        "hermes": _safe_surface("hermes", _hermes_surface),
        "trust_gateway": _safe_surface("trust_gateway", _trust_surface),
        "codex_client": _safe_surface("codex_client", _codex_client_surface),
    }
    surface_statuses = {
        name: data.get("status", "unknown") for name, data in surfaces.items()
    }
    overall = (
        "ready"
        if all(status == "ready" for status in surface_statuses.values())
        else "partial"
    )
    payload = {
        "status": overall,
        "repo_root": str(root),
        "surfaces": surfaces,
        "surface_statuses": surface_statuses,
        "dispatch": get_codex_dispatch_catalog(root),
        "entrypoints": {
            "cli": "uv run python scripts/agents/codex_access.py --json",
            "mcp_status_tool": "codomyrmex.codex_access_status",
            "mcp_dispatch_tool": "codomyrmex.codex_dispatch_catalog",
            "pai_mcp_server": "codomyrmex.agents.pai.mcp_bridge.create_codomyrmex_mcp_server",
        },
    }
    return _json_safe(payload)


def codex_access_is_ready(payload: dict[str, Any]) -> bool:
    """Return True when a Codex access payload is fully ready."""
    if payload.get("status") != "ready":
        return False
    surfaces = payload.get("surface_statuses", {})
    if not isinstance(surfaces, dict):
        return False
    return all(status == "ready" for status in surfaces.values())


__all__ = [
    "codex_access_is_ready",
    "get_codex_access_status",
    "get_codex_dispatch_catalog",
]
