"""Pruning daemon — identifies stale or duplicate modules as PruningCandidates.

The daemon does not perform any deletions by default — it only produces candidates
for human or GUARD_ANT review (dry_run=True).  With dry_run=False, archive() moves
the target to docs/plans/archived/.

Supports two usage styles:

* **Standalone** — ``PruningDaemon(repo_root_str)`` where the first positional
  argument is a path string to the repository root.  pheromone_store defaults
  to None.
* **Kernel** — ``PruningDaemon(pheromone_store=ps, repo_root=".")`` where the
  store is a PheromoneStore-like object.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from codomyrmex.colony_kernel.models import PruningCandidate, SignalType

_PRUNING_MIN_CONFIDENCE = 0.5


class PruningDaemon:
    """Identifies stale or duplicate modules as PruningCandidates."""

    def __init__(
        self,
        pheromone_store_or_root: Any = None,
        repo_root: str = ".",
        *,
        pheromone_store: Any = None,
    ) -> None:
        if isinstance(pheromone_store_or_root, str):
            resolved_root = pheromone_store_or_root
            resolved_store = pheromone_store
        else:
            resolved_store = pheromone_store_or_root or pheromone_store
            resolved_root = repo_root

        root_path = Path(resolved_root).resolve()

        # Only validate existence in standalone mode (pheromone_store_or_root was a string).
        # In kernel mode (non-string first arg or keyword-only pheromone_store), the repo_root
        # may reference a path that does not yet exist locally (e.g. a remote or staging repo).
        if isinstance(pheromone_store_or_root, str) and not root_path.exists():
            raise ValueError(
                f"repo_root {resolved_root!r} does not exist on disk. "
                "Provide a valid path to an existing repository root."
            )

        self._pheromone = resolved_store
        self._repo_root = root_path
        self._last_scan_count: int = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sense(self, location: str, signal_type: SignalType) -> float:
        if self._pheromone is None:
            return 0.0
        return self._pheromone.sense(location, signal_type)

    def _src_dir(self) -> Path:
        candidate = self._repo_root / "src" / "codomyrmex"
        if candidate.is_dir():
            return candidate
        return self._repo_root

    # ------------------------------------------------------------------
    # Core scan (kernel API)
    # ------------------------------------------------------------------

    def scan(
        self, module_registry: dict[str, dict[str, Any]]
    ) -> list[PruningCandidate]:
        """Scan module_registry and return candidates for pruning."""
        import time

        now = time.time()
        _STALENESS = 30 * 86400
        candidates: list[PruningCandidate] = []

        for module_path, meta in module_registry.items():
            last_used: float = float(meta.get("last_used", 0.0))
            call_count: int = int(meta.get("call_count", 0))
            duplicate_of: str | None = meta.get("duplicate_of")

            if self._sense(module_path, SignalType.HUMAN_PRIORITY) > 0.0:
                continue
            if self._sense(module_path, SignalType.DEPENDENCY) >= 2.0:
                continue

            candidate: PruningCandidate | None = None

            if duplicate_of:
                candidate = PruningCandidate(
                    module_path=module_path,
                    last_used=last_used,
                    call_count=call_count,
                    duplicate_of=duplicate_of,
                    reason=f"duplicate of {duplicate_of}",
                    confidence=0.85,
                )
            elif call_count == 0 and last_used == 0.0:
                candidate = PruningCandidate(
                    module_path=module_path,
                    last_used=0.0,
                    call_count=0,
                    duplicate_of=None,
                    reason="never used since registration",
                    confidence=0.90,
                )
            elif call_count == 0 and (now - last_used) > _STALENESS:
                candidate = PruningCandidate(
                    module_path=module_path,
                    last_used=last_used,
                    call_count=0,
                    duplicate_of=None,
                    reason=f"no calls; last used {(now - last_used) / 86400:.1f} days ago",
                    confidence=0.70,
                )
            elif (now - last_used) > _STALENESS and call_count < 5:
                candidate = PruningCandidate(
                    module_path=module_path,
                    last_used=last_used,
                    call_count=call_count,
                    duplicate_of=None,
                    reason=(
                        f"low usage ({call_count} calls); "
                        f"last used {(now - last_used) / 86400:.1f} days ago"
                    ),
                    confidence=0.50,
                )

            if (
                candidate is not None
                and candidate.confidence >= _PRUNING_MIN_CONFIDENCE
            ):
                candidates.append(candidate)

        candidates.sort(key=lambda c: c.confidence, reverse=True)
        self._last_scan_count = len(candidates)
        return candidates

    # ------------------------------------------------------------------
    # Standalone scan methods
    # ------------------------------------------------------------------

    def scan_unused_tools(
        self, threshold_days: int = 30
    ) -> list[PruningCandidate]:
        """Return modules under src/codomyrmex/ with no recorded pheromone usage.

        Always produces last_used=0.0 and call_count=0 since this method has
        no call history; it uses filesystem presence only.  A module with
        last_used==0.0 is flagged with confidence 0.90 regardless of threshold.
        """
        src = self._src_dir()
        if not src.is_dir():
            return []

        candidates: list[PruningCandidate] = []

        for child in sorted(src.iterdir()):
            if not child.is_dir():
                continue
            init_file = child / "__init__.py"
            if not init_file.exists():
                continue

            dot_path = child.name

            if self._sense(dot_path, SignalType.DEPENDENCY) >= 2.0:
                continue

            # scan_unused_tools has no invocation history — it operates on
            # filesystem presence only.  All modules with no pheromone DEPENDENCY
            # signal are reported as unused (last_used=0.0, call_count=0).
            # threshold_days is honoured when a real invocation timestamp is
            # available, but since we only have filesystem presence here, every
            # module without a pheromone signal is flagged unconditionally.
            candidates.append(
                PruningCandidate(
                    module_path=str(child),
                    last_used=0.0,
                    call_count=0,
                    duplicate_of=None,
                    reason="no invocation record; no pheromone signal detected",
                    confidence=0.90,
                )
            )

        return candidates

    def scan_unused(self) -> list[PruningCandidate]:
        """Alias for scan_unused_tools()."""
        return self.scan_unused_tools()

    def scan_duplicate_patterns(self) -> list[PruningCandidate]:
        """Return modules whose SPEC.md content is near-identical to another module.

        Computes line-level Jaccard similarity; pairs with similarity >= 0.8 are flagged.
        """
        src = self._src_dir()
        if not src.is_dir():
            return []

        spec_contents: dict[str, set[str]] = {}
        for child in sorted(src.iterdir()):
            if not child.is_dir():
                continue
            spec = child / "SPEC.md"
            if spec.exists():
                try:
                    lines = set(spec.read_text().splitlines())
                except OSError:
                    lines = set()
                spec_contents[child.name] = lines

        candidates: list[PruningCandidate] = []
        names = list(spec_contents.keys())
        for i, name_a in enumerate(names):
            for name_b in names[i + 1:]:
                a_lines = spec_contents[name_a]
                b_lines = spec_contents[name_b]
                union = a_lines | b_lines
                if not union:
                    continue
                similarity = len(a_lines & b_lines) / len(union)
                if similarity >= 0.8:
                    mod_path = str(src / name_b)
                    candidates.append(
                        PruningCandidate(
                            module_path=mod_path,
                            last_used=0.0,
                            call_count=0,
                            duplicate_of=name_a,
                            reason=f"SPEC.md similarity {similarity:.0%} with {name_a}",
                            confidence=0.85,
                        )
                    )

        return candidates

    def scan_duplicate(self) -> list[PruningCandidate]:
        """Alias for scan_duplicate_patterns() used by report()."""
        return self.scan_duplicate_patterns()

    def scan_stale_docs(self) -> list[PruningCandidate]:
        """Return modules whose documentation has not been updated recently.

        Returns empty list — full implementation requires git history.
        """
        return []

    def scan_no_tests(self) -> list[PruningCandidate]:
        """Return modules with no corresponding test files.

        Checks:
        1. tests/unit/<module_name>/ at repo root with test_*.py files
        2. <module_dir>/tests/ subdirectory with test_*.py files
        """
        src = self._src_dir()
        if not src.is_dir():
            return []

        tests_root = self._repo_root / "tests" / "unit"
        candidates: list[PruningCandidate] = []

        for child in sorted(src.iterdir()):
            if not child.is_dir():
                continue
            if not (child / "__init__.py").exists():
                continue

            has_tests = _has_tests(tests_root / child.name) or _has_tests(
                child / "tests"
            )
            if not has_tests:
                candidates.append(
                    PruningCandidate(
                        module_path=str(child),
                        last_used=0.0,
                        call_count=0,
                        duplicate_of=None,
                        reason="no test directory found",
                        confidence=0.60,
                    )
                )

        return candidates

    # ------------------------------------------------------------------
    # Report (standalone API)
    # ------------------------------------------------------------------

    def report(self) -> dict[str, list[PruningCandidate]]:
        """Return a categorised pruning report.

        Returns a dict with exactly the keys: unused, duplicate, stale_docs, no_tests.
        """
        return {
            "unused": self.scan_unused_tools(),
            "duplicate": self.scan_duplicate_patterns(),
            "stale_docs": self.scan_stale_docs(),
            "no_tests": self.scan_no_tests(),
        }

    # ------------------------------------------------------------------
    # Archive
    # ------------------------------------------------------------------

    def archive(
        self, candidate: PruningCandidate, dry_run: bool = True
    ) -> str:
        """Archive or plan to archive a pruning candidate.

        Args:
            candidate: A PruningCandidate to archive.
            dry_run: When True (default), return a description string without
                     modifying the filesystem.  When False, move the candidate's
                     path to docs/plans/archived/ under the repo root.

        Returns:
            A string describing what would happen or what happened.

        Raises:
            ValueError: if candidate.module_path escapes the repo root.
            FileNotFoundError: if dry_run=False and the path does not exist.
        """
        # Resolve to absolute; treat relative paths as relative to repo root
        module_path = Path(candidate.module_path)
        if not module_path.is_absolute():
            abs_path = (self._repo_root / module_path).resolve()
        else:
            abs_path = module_path.resolve()

        # Security: check containment
        try:
            abs_path.relative_to(self._repo_root)
        except ValueError:
            raise ValueError(
                f"candidate.module_path {candidate.module_path!r} is outside "
                f"the repo root {self._repo_root!r}"
            )

        confidence_pct = f"{candidate.confidence * 100:.0f}%"
        dest_dir = self._repo_root / "docs" / "plans" / "archived"
        dest_path = dest_dir / abs_path.name

        description = (
            f"PruningDaemon archive plan:\n"
            f"  path:       {candidate.module_path}\n"
            f"  reason:     {candidate.reason}\n"
            f"  confidence: {confidence_pct}\n"
            f"  action:     move to {dest_path}\n"
        )

        if dry_run:
            return f"[DRY RUN] {description}"

        # Real run: verify path exists
        if not abs_path.exists():
            raise FileNotFoundError(
                f"candidate.module_path {candidate.module_path!r} does not exist; "
                "cannot archive a non-existent path."
            )

        # Create archive dir and move
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(abs_path), str(dest_dir / abs_path.name))

        return description


def _has_tests(test_dir: Path) -> bool:
    """Return True if test_dir contains at least one test_*.py file."""
    if not test_dir.is_dir():
        return False
    return any(test_dir.glob("test_*.py"))


__all__ = ["PruningDaemon"]
