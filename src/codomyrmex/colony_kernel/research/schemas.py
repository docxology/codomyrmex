"""Versioned schemas and provenance records for Colony Kernel experiments."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

RESEARCH_SCHEMA_VERSION = "1.0"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def sha256_file(path: str | os.PathLike[str]) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(repo_root: Path, *args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return "unavailable"


@dataclass(frozen=True)
class ResearchManifest:
    """Complete provenance envelope for a local research run."""

    track: str
    run_id: str = field(default_factory=lambda: f"run-{uuid.uuid4().hex[:12]}")
    seed: int = 0
    config: dict[str, Any] = field(default_factory=dict)
    input_hashes: dict[str, str] = field(default_factory=dict)
    commit: str = "unavailable"
    worktree_dirty: bool = False
    python_version: str = field(default_factory=platform.python_version)
    platform: str = field(default_factory=platform.platform)
    lock_hash: str = "unavailable"
    code_hash: str = "unavailable"
    live_services: tuple[str, ...] = ()
    schema_version: str = RESEARCH_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if not self.track:
            raise ValueError("track must be non-empty")
        if self.seed < 0:
            raise ValueError("seed must be non-negative")
        if self.schema_version != RESEARCH_SCHEMA_VERSION:
            raise ValueError(f"unsupported research schema: {self.schema_version}")

    @classmethod
    def from_repository(
        cls,
        repo_root: str | os.PathLike[str],
        track: str,
        *,
        run_id: str | None = None,
        seed: int = 0,
        config: dict[str, Any] | None = None,
        input_hashes: dict[str, str] | None = None,
        live_services: tuple[str, ...] = (),
    ) -> ResearchManifest:
        root = Path(repo_root).resolve()
        lock = root / "uv.lock"
        source_root = root / "src" / "codomyrmex" / "colony_kernel"
        source_files = sorted(source_root.rglob("*.py")) if source_root.is_dir() else []
        code_digest = hashlib.sha256()
        for path in source_files:
            code_digest.update(path.relative_to(root).as_posix().encode())
            code_digest.update(path.read_bytes())
        return cls(
            track=track,
            run_id=run_id or f"run-{uuid.uuid4().hex[:12]}",
            seed=seed,
            config=config or {},
            input_hashes=input_hashes or {},
            commit=_git(root, "rev-parse", "HEAD"),
            worktree_dirty=bool(_git(root, "status", "--porcelain")),
            lock_hash=sha256_file(lock) if lock.is_file() else "unavailable",
            code_hash=code_digest.hexdigest() if source_files else "unavailable",
            live_services=tuple(sorted(live_services)),
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def digest(self) -> str:
        return hashlib.sha256(canonical_json(self.to_dict()).encode()).hexdigest()


@dataclass(frozen=True)
class TaskCase:
    """One deterministic adversarial tool-use task."""

    task_id: str
    threat: str
    target: str
    proposed_action: str
    allowed_actions: tuple[str, ...]
    harmful_actions: tuple[str, ...]
    expected_safe: bool
    risk_pressure: float = 0.0
    trust_score: float = 0.8
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.task_id or not self.target or not self.proposed_action:
            raise ValueError("task_id, target, and proposed_action are required")
        if not self.allowed_actions:
            raise ValueError("allowed_actions must be non-empty")
        if self.proposed_action not in self.allowed_actions:
            raise ValueError("proposed_action must be one of allowed_actions")
        if any(not action for action in self.allowed_actions):
            raise ValueError("allowed_actions cannot contain empty actions")
        if not set(self.harmful_actions) <= set(self.allowed_actions):
            raise ValueError("harmful_actions must be a subset of allowed_actions")
        if not 0.0 <= self.trust_score <= 1.0:
            raise ValueError("trust_score must be in [0, 1]")
        if self.risk_pressure < 0.0:
            raise ValueError("risk_pressure must be non-negative")

    def to_dict(self) -> dict[str, Any]:
        """Return a stable JSON-compatible task definition for manifests."""
        return asdict(self)


@dataclass(frozen=True)
class PolicyTrace:
    """Outcome trace for one policy/task pair."""

    task_id: str
    condition: str
    chosen_action: str
    refused: bool
    harmful: bool
    utility: float
    trace_complete: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.task_id or not self.condition or not self.chosen_action:
            raise ValueError("task_id, condition, and chosen_action are required")
        if not 0.0 <= self.utility <= 1.0:
            raise ValueError("utility must be in [0, 1]")
        if self.refused and self.harmful:
            raise ValueError("a refused action cannot be marked harmful")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def split_leakage_report(
    train_cases: list[TaskCase] | tuple[TaskCase, ...],
    held_out_cases: list[TaskCase] | tuple[TaskCase, ...],
) -> dict[str, Any]:
    """Report task-id and target overlap before a held-out evaluation.

    The report is deliberately conservative: sharing either an identifier or a
    target is surfaced for review. It does not infer semantic independence from
    string inequality; callers must decide whether a split is admissible.
    """

    train_ids = {case.task_id for case in train_cases}
    held_out_ids = {case.task_id for case in held_out_cases}
    train_targets = {case.target for case in train_cases}
    held_out_targets = {case.target for case in held_out_cases}
    id_overlap = sorted(train_ids & held_out_ids)
    target_overlap = sorted(train_targets & held_out_targets)
    return {
        "status": "clean" if not id_overlap and not target_overlap else "overlap",
        "train_count": len(train_cases),
        "held_out_count": len(held_out_cases),
        "task_id_overlap": id_overlap,
        "target_overlap": target_overlap,
        "semantic_independence_not_established": bool(target_overlap),
    }


__all__ = [
    "RESEARCH_SCHEMA_VERSION",
    "PolicyTrace",
    "ResearchManifest",
    "TaskCase",
    "canonical_json",
    "sha256_file",
    "split_leakage_report",
]
