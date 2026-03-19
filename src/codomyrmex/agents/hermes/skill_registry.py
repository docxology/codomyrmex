"""Unified Hermes / PAI / MCP skill registry and project profiles.

Loads a bundled YAML registry plus optional overlays, resolves stable ``skill_ids``
to Hermes CLI ``-s`` names, merges project profile + client config + session + request
context in a fixed order.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Any

import yaml

from codomyrmex.agents.hermes.skill_names import normalize_hermes_skill_names
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

REGISTRY_ENV_VAR = "CODOMYRMEX_SKILLS_REGISTRY"
PROFILE_DIR = ".codomyrmex"
PROFILE_FILENAME = "hermes_skills_profile.yaml"
PROFILE_MAX_WALK = 12

__all__ = [
    "PROFILE_FILENAME",
    "REGISTRY_ENV_VAR",
    "SkillRecord",
    "find_project_profile_path",
    "load_skill_index",
    "merge_ordered_unique",
    "merged_hermes_skill_list_for_client",
    "parse_cli_skills_output",
    "project_profile_hermes_names",
    "resolve_skill_ids",
    "validate_registry_against_cli_lines",
]


@dataclass(frozen=True)
class SkillRecord:
    """One logical skill mapping for bridge consumers."""

    id: str
    title: str
    hermes_preload: tuple[str, ...]
    cli_only: bool = True
    pai_skill_hint: str | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)


def merge_ordered_unique(*lists: list[str] | None) -> list[str]:
    """Concatenate lists, preserving order; first occurrence of a name wins."""
    seen: set[str] = set()
    out: list[str] = []
    for lst in lists:
        if not lst:
            continue
        for s in lst:
            if s not in seen:
                seen.add(s)
                out.append(s)
    return out


def _load_yaml_file(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        logger.warning("Skill registry unreadable %s: %s", path, exc)
        return {}
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        logger.warning("Skill registry YAML invalid %s: %s", path, exc)
        return {}
    return data if isinstance(data, dict) else {}


def _parse_registry_doc(data: dict[str, Any]) -> dict[str, SkillRecord]:
    out: dict[str, SkillRecord] = {}
    raw_skills = data.get("skills")
    if not isinstance(raw_skills, list):
        return out
    for item in raw_skills:
        if not isinstance(item, dict):
            continue
        sid = str(item.get("id", "")).strip()
        if not sid:
            continue
        title = str(item.get("title", sid)).strip()
        hp = item.get("hermes_preload")
        names: list[str] = []
        if isinstance(hp, str) and hp.strip():
            names.append(hp.strip())
        elif isinstance(hp, list):
            for x in hp:
                if x is not None and str(x).strip():
                    names.append(str(x).strip())
        if not names:
            continue
        cli_only = bool(item.get("cli_only", True))
        hint = item.get("pai_skill_hint")
        pai = str(hint).strip() if hint else None
        tags_raw = item.get("tags")
        tags: list[str] = []
        if isinstance(tags_raw, list):
            tags = [str(t).strip() for t in tags_raw if str(t).strip()]
        out[sid] = SkillRecord(
            id=sid,
            title=title,
            hermes_preload=tuple(names),
            cli_only=cli_only,
            pai_skill_hint=pai,
            tags=tuple(tags),
        )
    return out


def load_skill_index() -> dict[str, SkillRecord]:
    """Load merged skill index: bundled registry + optional CODOMYRMEX_SKILLS_REGISTRY file."""
    merged: dict[str, SkillRecord] = {}

    try:
        ref = resources.files("codomyrmex.agents.hermes.data").joinpath(
            "skills_registry.yaml"
        )
        raw = yaml.safe_load(ref.read_text(encoding="utf-8"))
        if isinstance(raw, dict):
            merged.update(_parse_registry_doc(raw))
    except (FileNotFoundError, ModuleNotFoundError, TypeError, ValueError) as exc:
        logger.debug("Bundled skill registry not loaded: %s", exc)
    except (OSError, yaml.YAMLError, AttributeError) as exc:
        logger.debug("Bundled skill registry parse failed: %s", exc)

    extra = os.environ.get(REGISTRY_ENV_VAR, "").strip()
    if extra:
        path = Path(os.path.expanduser(extra))
        if path.is_file():
            merged.update(_parse_registry_doc(_load_yaml_file(path)))
        else:
            logger.warning("%s points to missing file: %s", REGISTRY_ENV_VAR, path)

    return merged


def resolve_skill_ids(
    skill_ids: list[str] | str | None,
    index: dict[str, SkillRecord] | None = None,
) -> dict[str, Any]:
    """Map registry ids to Hermes preload names and metadata."""
    idx = index if index is not None else load_skill_index()
    ids: list[str] = []
    if isinstance(skill_ids, str):
        for part in skill_ids.replace(",", " ").split():
            p = part.strip()
            if p:
                ids.append(p)
    elif isinstance(skill_ids, list):
        for x in skill_ids:
            if x is not None and str(x).strip():
                ids.append(str(x).strip())

    unknown: list[str] = []
    hermes_names: list[str] = []
    details: list[dict[str, Any]] = []

    for sid in ids:
        rec = idx.get(sid)
        if rec is None:
            unknown.append(sid)
            continue
        for n in rec.hermes_preload:
            if n not in hermes_names:
                hermes_names.append(n)
        details.append(
            {
                "id": rec.id,
                "title": rec.title,
                "hermes_preload": list(rec.hermes_preload),
                "cli_only": rec.cli_only,
                "pai_skill_hint": rec.pai_skill_hint,
                "tags": list(rec.tags),
            }
        )

    return {
        "skill_ids_requested": ids,
        "unknown_skill_ids": unknown,
        "hermes_preload": hermes_names,
        "resolved_entries": details,
    }


def find_project_profile_path(start: Path | None = None) -> Path | None:
    """Walk upward from *start* (default cwd) for ``.codomyrmex/hermes_skills_profile.yaml``."""
    cur = (start or Path.cwd()).resolve()
    for _ in range(PROFILE_MAX_WALK):
        candidate = cur / PROFILE_DIR / PROFILE_FILENAME
        if candidate.is_file():
            return candidate
        parent = cur.parent
        if parent == cur:
            break
        cur = parent
    return None


def project_profile_hermes_names(
    cwd: Path | None = None,
    index: dict[str, SkillRecord] | None = None,
) -> tuple[list[str], Path | None]:
    """Return Hermes preload names from the project profile file, if any."""
    idx = index if index is not None else load_skill_index()
    path = find_project_profile_path(Path(cwd) if cwd is not None else None)
    if path is None:
        return [], None
    doc = _load_yaml_file(path)
    names: list[str] = []

    raw_ids = doc.get("skill_ids")
    id_list: list[str] = []
    if isinstance(raw_ids, str) and raw_ids.strip():
        id_list = [raw_ids.strip()]
    elif isinstance(raw_ids, list):
        id_list = [str(x).strip() for x in raw_ids if str(x).strip()]
    if id_list:
        resolved = resolve_skill_ids(id_list, index=idx)
        names.extend(resolved.get("hermes_preload") or [])

    extra = doc.get("hermes_preload")
    if isinstance(extra, str) and extra.strip():
        names.extend(normalize_hermes_skill_names(hermes_skills=extra))
    elif isinstance(extra, list):
        names.extend(
            normalize_hermes_skill_names(
                hermes_skills=[str(x) for x in extra if str(x).strip()]
            )
        )

    return merge_ordered_unique(names), path


def _config_skill_names(
    config: dict[str, Any], index: dict[str, SkillRecord]
) -> list[str]:
    names: list[str] = []
    raw_ids = config.get("hermes_default_skill_ids")
    id_list: list[str] = []
    if isinstance(raw_ids, str) and raw_ids.strip():
        id_list = [raw_ids.strip()]
    elif isinstance(raw_ids, list):
        id_list = [str(x).strip() for x in raw_ids if str(x).strip()]
    if id_list:
        resolved = resolve_skill_ids(id_list, index=index)
        names.extend(resolved.get("hermes_preload") or [])

    hd = config.get("hermes_default_hermes_skills")
    if isinstance(hd, str) and hd.strip():
        names.extend(normalize_hermes_skill_names(hermes_skills=hd))
    elif isinstance(hd, list):
        names.extend(
            normalize_hermes_skill_names(
                hermes_skills=[str(x) for x in hd if str(x).strip()]
            )
        )
    return names


def merged_hermes_skill_list_for_client(
    *,
    cwd: Path,
    client_config: dict[str, Any],
    profile_disabled: bool,
    session_skills: list[str] | None,
    context: dict[str, Any] | None,
    index: dict[str, SkillRecord] | None = None,
) -> list[str]:
    """Merge skill layers: profile → config → session → request context (unique, stable order)."""
    idx = index if index is not None else load_skill_index()
    profile_layer: list[str] = []
    profile_path: Path | None = None
    if not profile_disabled:
        profile_layer, profile_path = project_profile_hermes_names(cwd, index=idx)
        if profile_path:
            logger.debug("Hermes skill profile loaded: %s", profile_path)

    config_layer = _config_skill_names(client_config, idx)
    session_layer = list(session_skills) if session_skills else []
    ctx_layer = normalize_hermes_skill_names(context=context) if context else []

    return merge_ordered_unique(profile_layer, config_layer, session_layer, ctx_layer)


def parse_cli_skills_output(output: str) -> set[str]:
    """Best-effort token set from ``hermes skills list`` style text output."""
    found: set[str] = set()
    for line in output.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        # strip markdown bullets / numbering
        for prefix in ("- ", "* ", "• "):
            if s.startswith(prefix):
                s = s[len(prefix) :].strip()
        for token in s.replace(",", " ").split():
            t = token.strip().strip("[]`\"'")
            if t:
                found.add(t)
                found.add(t.lower())
    return found


def validate_registry_against_cli_lines(
    cli_output: str,
    index: dict[str, SkillRecord] | None = None,
) -> dict[str, Any]:
    """Check registry ``hermes_preload`` names appear in CLI list output (substring / token heuristic)."""
    idx = index if index is not None else load_skill_index()
    tokens = parse_cli_skills_output(cli_output)
    blob = cli_output.lower()
    missing: list[dict[str, str]] = []
    for rec in idx.values():
        for hp in rec.hermes_preload:
            if hp.lower() in blob or hp.lower() in tokens or hp in tokens:
                continue
            missing.append({"skill_id": rec.id, "hermes_preload": hp})
    return {
        "status": "ok" if not missing else "mismatch",
        "registry_skill_count": len(idx),
        "missing_hermes_preload": missing,
    }
