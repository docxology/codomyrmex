"""MCP tool definitions for the Colony Kernel module.

Exposes the Colony Kernel control plane to AI agents via Model Context
Protocol.  All eight tools route through a single module-level
``ColonyKernel`` singleton (imported from ``kernel.py``) so state is
shared across calls within a process.

Eight tools are registered:
- colony_propose_action  — submit an action proposal to the gate
- colony_record_outcome  — record a caller-reported consequence of an action
- colony_agent_profile   — read an agent's trust profile
- colony_status          — current pheromone and resource snapshot
- colony_pheromone_query — sense pheromone pressure at a location
- colony_falsify_plan    — adversarial evaluation of a plan dict
- colony_pruning_report  — stale-module candidates identified by the daemon
- colony_tick            — advance the colony one time-step

No external dependencies beyond stdlib and the colony_kernel / stigmergy
packages that are already part of codomyrmex.
"""

from __future__ import annotations

import json
import threading
from typing import Any

from codomyrmex.colony_kernel.kernel import ColonyKernel
from codomyrmex.colony_kernel.models import (
    ActionProposal,
    AgentTrustProfile,
    ColonySignal,
    DecayRate,
    FalsificationFinding,
    FalsificationSeverity,
    GateResult,
    ResourceCost,
    SignalSource,
    SignalType,
    make_trace_key,
)
from codomyrmex.model_context_protocol.decorators import mcp_tool

# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_kernel: ColonyKernel | None = None
# Lock protecting non-atomic lazy initialisation of _kernel.
_KERNEL_LOCK: threading.Lock = threading.Lock()


def _get_kernel() -> ColonyKernel:
    """Return (lazily initialising) the module-level kernel singleton.

    Thread-safe: uses ``_KERNEL_LOCK`` to ensure at most one
    :class:`ColonyKernel` instance is created even under concurrent first calls.
    """
    global _kernel
    if _kernel is None:
        with _KERNEL_LOCK:
            # Double-checked locking: re-test after acquiring the lock in case
            # another thread already initialised while we waited.
            if _kernel is None:
                _kernel = ColonyKernel()
    return _kernel


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _dataclass_to_dict(obj: Any) -> Any:
    """Recursively convert dataclass instances (and nested structures) to dicts.

    Enums are converted to their ``.value``; floats, ints, strings, bools,
    and ``None`` pass through unchanged.
    """
    import dataclasses

    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        result: dict[str, Any] = {}
        for f in dataclasses.fields(obj):
            result[f.name] = _dataclass_to_dict(getattr(obj, f.name))
        return result
    if isinstance(obj, list):
        return [_dataclass_to_dict(i) for i in obj]
    if isinstance(obj, dict):
        return {k: _dataclass_to_dict(v) for k, v in obj.items()}
    if hasattr(obj, "value"):  # Enum
        return obj.value
    return obj


# ---------------------------------------------------------------------------
# FalsificationWorker — imported from canonical standalone module
# ---------------------------------------------------------------------------
from codomyrmex.colony_kernel.falsification_worker import FalsificationWorker

# ---------------------------------------------------------------------------
# MCP tools
# ---------------------------------------------------------------------------


@mcp_tool(
    category="colony_kernel",
    description=(
        "Submit an action proposal to the Colony gate. "
        "Returns a GateResult (decision, score, reason, required_evidence)."
    ),
)
def colony_propose_action(
    agent_id: str,
    action_type: str,
    target: str,
    rationale: str,
    rollback_plan: str,
    evidence: str = "{}",
) -> dict[str, Any]:
    """Create an ActionProposal and run it through the Colony actuation gate.

    Args:
        agent_id: Unique identifier of the proposing agent.
        action_type: Type of action (e.g. ``"patch_file"``, ``"archive_module"``).
        target: Dotted module path or file path the action will affect.
        rationale: Explanation of why this action is necessary.
        rollback_plan: Concrete description of how to undo the action.
        evidence: JSON-serialised dict of supporting evidence (default: ``"{}"``).

    Returns:
        Serialised :class:`~codomyrmex.colony_kernel.models.GateResult` dict.
    """
    try:
        evidence_dict: dict[str, Any] = json.loads(evidence) if evidence.strip() else {}
        proposal = ActionProposal(
            agent_id=agent_id,
            agent_type="mcp_agent",
            action_type=action_type,
            target=target,
            rationale=rationale,
            expected_outcome=f"Successful execution of {action_type} on {target}.",
            budget_estimate=ResourceCost(llm_calls=1, runtime_seconds=5.0),
            rollback_plan=rollback_plan,
            evidence=evidence_dict,
        )
        result = _get_kernel().propose_action(proposal)
        return _dataclass_to_dict(result)
    except Exception as exc:
        return {"error": str(exc)}


@mcp_tool(
    category="colony_kernel",
    description=(
        "Record a caller-reported action outcome. The report is not linked to "
        "a consumed EXECUTE authorization. Updates trust and deposits SUCCESS "
        "or FAILURE plus a DEPENDENCY signal."
    ),
)
def colony_record_outcome(
    agent_id: str,
    action_type: str,
    target: str,
    actual_outcome: str,
    tests_passed: bool,
    human_feedback: float = 0.0,
) -> dict[str, Any]:
    """Record a caller-reported consequence without execution attestation.

    Args:
        agent_id: Identifier associated with the submitted report.
        action_type: Action type claimed by the report.
        target: Target claimed by the report.
        actual_outcome: Human-readable caller description of what happened.
        tests_passed: Caller-supplied post-action test status.
        human_feedback: Float in [-1.0, 1.0]; 0.0 means no feedback (default).

    Returns:
        Dict with ``status`` (``"recorded"``), ``trust_score`` of the agent
        after the update, ``role``, and ``consequence_id``.
    """
    try:
        kernel = _get_kernel()
        # Build a synthetic proposal for the record — we don't require the
        # original proposal_id to be passed; agents record outcomes by description.
        proposal = ActionProposal(
            agent_id=agent_id,
            agent_type="mcp_agent",
            action_type=action_type,
            target=target,
            rationale="Outcome recorded via colony_record_outcome MCP tool.",
            expected_outcome=actual_outcome,
        )
        record = kernel.record_outcome(
            proposal=proposal,
            outcome={
                "summary": actual_outcome,
                "repair_needed": not tests_passed,
                "action_taken": f"{action_type} on {target}",
            },
            tests_passed=tests_passed,
            human_feedback=str(human_feedback) if human_feedback != 0.0 else None,
        )
        profile = kernel.agent_profile(agent_id)
        return {
            "status": "recorded",
            "consequence_id": record.consequence_id,
            "trust_score": round(profile.trust_score, 4),
            "role": profile.role.value,
        }
    except Exception as exc:
        return {"error": str(exc)}


@mcp_tool(
    category="colony_kernel",
    description="Return the trust profile for an agent (role, trust_score, history length).",
)
def colony_agent_profile(agent_id: str) -> dict[str, Any]:
    """Fetch the trust profile for ``agent_id``.

    Args:
        agent_id: The agent to look up (auto-created as SANDBOX if unknown).

    Returns:
        Serialised :class:`~codomyrmex.colony_kernel.models.AgentTrustProfile` dict.
        Note: ``consequence_history`` is capped at the most recent 200 entries.
    """
    try:
        profile = _get_kernel().agent_profile(agent_id)
        return _dataclass_to_dict(profile)
    except Exception as exc:
        return {"error": str(exc)}


@mcp_tool(
    category="colony_kernel",
    description=(
        "Return a snapshot of the Colony: active traces, top signals, "
        "agent count, resource usage, and current tick."
    ),
)
def colony_status() -> dict[str, Any]:
    """Return the current colony status snapshot.

    Returns:
        Dict with ``pheromone_summary``, ``budget_usage``, ``role_distribution``,
        ``recent_consequences``, and ``pruning_candidates_count``.
    """
    try:
        return _get_kernel().colony_status()
    except Exception as exc:
        return {"error": str(exc)}


@mcp_tool(
    category="colony_kernel",
    description=(
        "Query pheromone pressure at a location for a given signal type. "
        "Returns a list of ColonySignal dicts."
    ),
)
def colony_pheromone_query(location: str, signal_type: str) -> list[dict[str, Any]]:
    """Sense pheromone signals at a location.

    Args:
        location: Dotted module path or file path (e.g. ``codomyrmex.git_operations.core``).
        signal_type: One of ``failure``, ``success``, ``risk``, ``need``,
                     ``dependency``, ``human_priority``.

    Returns:
        List of serialised :class:`~codomyrmex.colony_kernel.models.ColonySignal` dicts;
        empty list if no signals are present.
    """
    try:
        sig_enum = SignalType(signal_type.lower())
        kernel = _get_kernel()
        # Use the kernel's pheromone_store directly for sensing
        marker = kernel.pheromone_store._field.sense(make_trace_key(location, sig_enum))
        if marker is not None:
            signal = ColonySignal(
                location=location,
                signal_type=sig_enum,
                strength=marker.strength,
                decay_rate=DecayRate.NORMAL,
                source=SignalSource.AGENT,
                evidence=dict(marker.metadata),
                last_reinforced=marker.updated_at,
            )
            return [_dataclass_to_dict(signal)]
        return []
    except ValueError as exc:
        valid = [e.value for e in SignalType]
        return [
            {
                "error": f"Invalid signal_type '{signal_type}'. Valid values: {valid}. {exc}"
            }
        ]
    except Exception as exc:
        return [{"error": str(exc)}]


@mcp_tool(
    category="colony_kernel",
    description=(
        "Run adversarial falsification on a plan dict (JSON string). "
        "Returns findings, severity_score, and recommendation."
    ),
)
def colony_falsify_plan(plan_json: str) -> dict[str, Any]:
    """Adversarially evaluate a plan using FalsificationWorker.

    Args:
        plan_json: JSON string of the plan dict. Recognised keys:
                   ``action_type``, ``target``, ``rationale``, ``evidence``,
                   ``rollback_plan``, ``budget_estimate``, ``agent_id``.

    Returns:
        Dict with ``findings`` (list), ``severity_score`` (float 0.0–1.0),
        and ``recommendation`` (``"execute"`` / ``"hold"`` / ``"refuse"``).
    """
    try:
        plan: dict[str, Any] = json.loads(plan_json)
        worker = FalsificationWorker()
        report = worker.evaluate_plan(plan)
        result = _dataclass_to_dict(report)
        # Compute severity_score and recommendation (not stored on FalsificationReport).
        # severity_score is the mean weight across all findings (0.0 if no findings).
        _weight = {"low": 0.05, "medium": 0.20, "high": 0.45, "critical": 1.0}
        findings_list = result.get("findings", [])
        severity_score: float = 0.0
        if findings_list:
            weights = [
                _weight.get(str(f.get("severity", "low")).lower(), 0.05)
                for f in findings_list
            ]
            severity_score = sum(weights) / len(weights)
        result["severity_score"] = severity_score
        if severity_score < 0.4:
            result["recommendation"] = "execute"
        elif severity_score < 0.75:
            result["recommendation"] = "hold"
        else:
            result["recommendation"] = "refuse"
        return result
    except json.JSONDecodeError as exc:
        return {"error": f"plan_json is not valid JSON: {exc}"}
    except Exception as exc:
        return {"error": str(exc)}


@mcp_tool(
    category="colony_kernel",
    description=(
        "Return a report of stale or broken modules flagged by PruningDaemon, "
        "based on pheromone signal analysis."
    ),
)
def colony_pruning_report() -> dict[str, Any]:
    """Run the pruning daemon against the current pheromone field.

    Returns:
        Dict with ``candidates`` (list of
        :class:`~codomyrmex.colony_kernel.models.PruningCandidate` dicts),
        ``total_candidates``, and ``generated_at`` (Unix timestamp).
    """
    try:
        kernel = _get_kernel()
        return kernel.pruning_report()
    except Exception as exc:
        return {"error": str(exc)}


@mcp_tool(
    category="colony_kernel",
    description=(
        "Advance the Colony one tick: evaporate pheromone traces and "
        "return the post-tick status summary."
    ),
)
def colony_tick() -> dict[str, Any]:
    """Advance the colony by one time-step.

    Pheromone traces evaporate according to ``StigmergyConfig.evaporation_per_tick``.
    Traces that fall to or below ``min_strength`` are removed.

    Returns:
        Colony status dict (see :func:`colony_status`).
    """
    try:
        _get_kernel().tick()
        return _get_kernel().colony_status()
    except Exception as exc:
        return {"error": str(exc)}


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------

__all__ = [
    # Core classes (importable for testing / extension)
    "ColonyKernel",
    "FalsificationWorker",
    "colony_agent_profile",
    "colony_falsify_plan",
    "colony_pheromone_query",
    # MCP tools
    "colony_propose_action",
    "colony_pruning_report",
    "colony_record_outcome",
    "colony_status",
    "colony_tick",
]
