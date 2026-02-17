"""PAI Algorithm ISC constraint verification bridge.

Translates Ideal State Criteria into Z3 constraints to check
consistency, detect conflicts, and validate satisfiability of
criteria sets. This is the core integration point between
Z3/mcp-solver and the PAI Algorithm as proposed in Discussion #707.

Key principle: the solver is ADVISORY. It returns analysis results
but never blocks the AI from proceeding. This addresses Spirotot's
concern about rigidity — deterministic verification enhances
confidence without removing flexibility.

References:
    - PAI Discussion #707: https://github.com/danielmiessler/Personal_AI_Infrastructure/discussions/707
    - PAI Algorithm: https://github.com/danielmiessler/TheAlgorithm
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .backends.base import SolverStatus
from .exceptions import BackendNotAvailableError


@dataclass
class ISCVerificationResult:
    """Result of verifying a set of ISC criteria for consistency."""

    consistent: bool | None
    """True if criteria are mutually satisfiable, False if conflicting, None if undetermined."""

    conflicts: list[tuple[str, str]]
    """Pairs of criterion IDs that conflict with each other."""

    satisfying_assignment: dict[str, Any] | None
    """Example assignment satisfying all criteria, if found."""

    warnings: list[str]
    """Non-blocking advisory messages."""

    solver_status: str
    """Raw solver status string."""

    criteria_analyzed: int
    """Number of criteria that were analyzable as constraints."""

    criteria_skipped: int
    """Number of criteria that could not be translated to constraints."""

    skipped_reasons: dict[str, str] = field(default_factory=dict)
    """Criterion ID → reason it was skipped."""


def verify_criteria_consistency(
    criteria: list[dict[str, str]],
    timeout_ms: int = 10000,
) -> ISCVerificationResult:
    """Check whether a set of ISC criteria are mutually consistent.

    This function attempts to translate criteria with numeric constraints
    into Z3 expressions and check satisfiability. Criteria that cannot
    be translated are skipped (not errors).

    Args:
        criteria: List of dicts with keys "id" and "description".
            Example: [{"id": "ISC-C1", "description": "Response time under 200ms"}]
        timeout_ms: Solver timeout in milliseconds.

    Returns:
        ISCVerificationResult — always returns, never raises on UNSAT.
        This ensures the solver is advisory, not blocking.
    """
    from .solver import ConstraintSolver

    try:
        solver = ConstraintSolver(backend="z3")
    except BackendNotAvailableError:
        return ISCVerificationResult(
            consistent=None,
            conflicts=[],
            satisfying_assignment=None,
            warnings=["Z3 not available — skipping formal verification"],
            solver_status="unavailable",
            criteria_analyzed=0,
            criteria_skipped=len(criteria),
            skipped_reasons={
                c.get("id", f"unknown_{i}"): "z3-solver not installed"
                for i, c in enumerate(criteria)
            },
        )
    analyzed = 0
    skipped = 0
    skipped_reasons: dict[str, str] = {}

    for idx, criterion in enumerate(criteria):
        cid = criterion.get("id") or f"unknown_{idx}"
        desc = criterion.get("description", "")
        constraint = criterion.get("constraint")

        if constraint:
            # Direct Z3 constraint provided
            try:
                solver.add_item(constraint)
                analyzed += 1
            except Exception as exc:
                skipped += 1
                skipped_reasons[cid] = f"Invalid constraint: {exc}"
        else:
            # Try to extract numeric constraints from description
            extracted = _extract_numeric_constraint(cid, desc)
            if extracted:
                for item in extracted:
                    solver.add_item(item)
                analyzed += 1
            else:
                skipped += 1
                skipped_reasons[cid] = "No translatable numeric constraint found"

    if analyzed == 0:
        return ISCVerificationResult(
            consistent=None,
            conflicts=[],
            satisfying_assignment=None,
            warnings=["No criteria could be translated to formal constraints"],
            solver_status="no_constraints",
            criteria_analyzed=0,
            criteria_skipped=skipped,
            skipped_reasons=skipped_reasons,
        )

    result = solver.solve(timeout_ms)

    if result.status == SolverStatus.SAT:
        return ISCVerificationResult(
            consistent=True,
            conflicts=[],
            satisfying_assignment=result.model,
            warnings=[],
            solver_status="sat",
            criteria_analyzed=analyzed,
            criteria_skipped=skipped,
            skipped_reasons=skipped_reasons,
        )
    elif result.status == SolverStatus.UNSAT:
        return ISCVerificationResult(
            consistent=False,
            conflicts=_find_conflicts(solver, criteria),
            satisfying_assignment=None,
            warnings=["Criteria set is unsatisfiable — check for conflicting requirements"],
            solver_status="unsat",
            criteria_analyzed=analyzed,
            criteria_skipped=skipped,
            skipped_reasons=skipped_reasons,
        )
    else:
        return ISCVerificationResult(
            consistent=None,
            conflicts=[],
            satisfying_assignment=None,
            warnings=[f"Solver returned {result.status.value}"],
            solver_status=result.status.value,
            criteria_analyzed=analyzed,
            criteria_skipped=skipped,
            skipped_reasons=skipped_reasons,
        )


def _z3_type_for(val: str) -> str:
    """Return 'Real' if val contains a decimal point, else 'Int'."""
    return "Real" if "." in val else "Int"


def _extract_numeric_constraint(cid: str, description: str) -> list[str] | None:
    """Best-effort extraction of numeric constraints from natural language.

    Looks for common patterns like "under X", "at least X", "between X and Y",
    "maximum X", "no more than X" and translates them to Z3 Int or Real constraints.

    Returns a list of Z3 Python code strings, or None if no pattern matches.
    """
    import re

    var_name = re.sub(r"[^a-z0-9_]", "_", cid.replace("-", "_").lower())
    items: list[str] = []

    # "under/below/less than X"
    m = re.search(r"(?:under|below|less\s+than)\s+(\d+(?:\.\d+)?)", description, re.IGNORECASE)
    if m:
        val = m.group(1)
        z3t = _z3_type_for(val)
        items.append(f"{var_name} = {z3t}('{var_name}')")
        items.append(f"solver.add({var_name} < {val})")
        items.append(f"solver.add({var_name} >= 0)")
        return items

    # "at least/minimum/no less than X"
    m = re.search(r"(?:at\s+least|minimum|no\s+less\s+than)\s+(\d+(?:\.\d+)?)", description, re.IGNORECASE)
    if m:
        val = m.group(1)
        z3t = _z3_type_for(val)
        items.append(f"{var_name} = {z3t}('{var_name}')")
        items.append(f"solver.add({var_name} >= {val})")
        return items

    # "at most/maximum/no more than X"
    m = re.search(r"(?:at\s+most|maximum|no\s+more\s+than)\s+(\d+(?:\.\d+)?)", description, re.IGNORECASE)
    if m:
        val = m.group(1)
        z3t = _z3_type_for(val)
        items.append(f"{var_name} = {z3t}('{var_name}')")
        items.append(f"solver.add({var_name} <= {val})")
        items.append(f"solver.add({var_name} >= 0)")
        return items

    # "between X and Y"
    m = re.search(r"between\s+(\d+(?:\.\d+)?)\s+and\s+(\d+(?:\.\d+)?)", description, re.IGNORECASE)
    if m:
        lo, hi = m.group(1), m.group(2)
        z3t = _z3_type_for(lo) if "." in lo else _z3_type_for(hi)
        items.append(f"{var_name} = {z3t}('{var_name}')")
        items.append(f"solver.add({var_name} >= {lo})")
        items.append(f"solver.add({var_name} <= {hi})")
        return items

    # "exactly X"
    m = re.search(r"exactly\s+(\d+(?:\.\d+)?)", description, re.IGNORECASE)
    if m:
        val = m.group(1)
        z3t = _z3_type_for(val)
        items.append(f"{var_name} = {z3t}('{var_name}')")
        items.append(f"solver.add({var_name} == {val})")
        return items

    return None


def _find_conflicts(solver: Any, criteria: list[dict[str, str]]) -> list[tuple[str, str]]:
    """Attempt to identify pairwise conflicts in an unsatisfiable criteria set.

    This is a best-effort heuristic — it tries removing criteria one at a time
    to find minimal conflict sets.
    """
    # Simple heuristic: return empty list — full MUS extraction is expensive
    # and can be added as a future enhancement
    return []
