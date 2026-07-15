"""MCP tool definitions for the Colony Kernel module.

Exposes the Colony Kernel control plane to AI agents via Model Context
Protocol.  Advisory, strict execution, evidence, and scope tools route through a single module-level
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
- colony_execute_authorized — consume a signed capability and execute a registered action
- colony_record_attested_outcome — link one receipt to one strict outcome
- colony_action_scope    — inspect the declared strict action scope

No external dependencies beyond stdlib and the colony_kernel / stigmergy
packages that are already part of codomyrmex.
"""

from __future__ import annotations

import json
import threading
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from codomyrmex.colony_kernel.authorization import (
    deserialize_authorization,
    deserialize_receipt,
    serialize_receipt,
)
from codomyrmex.colony_kernel.kernel import ColonyKernel
from codomyrmex.colony_kernel.models import (
    ActionProposal,
    AgentTrustProfile,
    ColonySignal,
    DecayRate,
    ExecutionAuthorization,
    FalsificationFinding,
    FalsificationSeverity,
    GateResult,
    OutcomeEvidence,
    PruningCandidate,
    ResourceCost,
    SignalSource,
    SignalType,
    make_trace_key,
    recommendation_for_severity,
    severity_rank,
    severity_weight,
)
from codomyrmex.model_context_protocol.decorators import mcp_tool

# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_kernel: ColonyKernel | None = None
# Lock protecting non-atomic lazy initialisation and scoped replacement of
# _kernel.  ``isolated_kernel`` is the real-component boundary used by tests
# and by callers that need a short-lived colony context.
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


@contextmanager
def isolated_kernel(config: Any | None = None) -> Iterator[ColonyKernel]:
    """Run MCP calls against a fresh real kernel for a bounded scope.

    This is an isolation/factory boundary, not a method stub or singleton
    replacement fixture.  The previous process singleton is restored after
    the context and the temporary consequence store is closed.
    """
    global _kernel
    with _KERNEL_LOCK:
        previous = _kernel
        replacement = ColonyKernel(config=config)
        _kernel = replacement
    try:
        yield replacement
    finally:
        replacement.consequence_memory.close()
        with _KERNEL_LOCK:
            _kernel = previous


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
        "Record a caller-reported action outcome. Advisory mode stores it with "
        "caller_reported_unattested evidence; strict mode quarantines it until "
        "a consumed authorization and signed executor receipt are supplied."
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
            proposal_id=str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    "colony-outcome:" + json.dumps(
                        {
                            "agent_id": agent_id,
                            "action_type": action_type,
                            "target": target,
                            "actual_outcome": actual_outcome,
                            "tests_passed": tests_passed,
                            "human_feedback": human_feedback,
                        },
                        sort_keys=True,
                    ),
                )
            ),
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
            "evidence_grade": record.evidence_grade,
        }
    except Exception as exc:
        return {"error": str(exc)}


@mcp_tool(
    category="colony_kernel",
    description=(
        "Execute a declared action with a signed, single-use authorization and "
        "return the executor receipt. Direct execution without a capability is rejected."
    ),
)
def colony_execute_authorized(
    authorization_json: str,
    agent_id: str,
    action_type: str,
    target: str,
    payload: str = "{}",
) -> dict[str, Any]:
    """Consume a capability and invoke a service-registered real handler."""

    try:
        token = deserialize_authorization(authorization_json)
        arguments = json.loads(payload) if payload.strip() else {}
        if not isinstance(arguments, dict):
            raise ValueError("payload must be a JSON object")
        run = _get_kernel().execute_authorized(
            token,
            agent_id=agent_id,
            action_type=action_type,
            target=target,
            payload=arguments,
        )
        return {
            "result": _dataclass_to_dict(run.result),
            "receipt": serialize_receipt(run.receipt),
        }
    except Exception as exc:
        return {"error": str(exc)}


@mcp_tool(
    category="colony_kernel",
    description=(
        "Convert a consumed authorization and signed executor receipt into an "
        "attested outcome; only this path can update strict-profile trust and signals."
    ),
)
def colony_record_attested_outcome(
    authorization_json: str,
    receipt_json: str,
    agent_id: str,
    action_type: str,
    target: str,
    actual_outcome: str,
    tests_passed: bool,
    human_feedback: float = 0.0,
) -> dict[str, Any]:
    """Record a receipt-linked outcome in the strict kernel profile."""

    try:
        token = deserialize_authorization(authorization_json)
        receipt = deserialize_receipt(receipt_json)
        proposal = ActionProposal(
            agent_id=agent_id,
            agent_type="mcp_agent",
            action_type=action_type,
            target=target,
            rationale="Receipt-linked outcome submitted through the Colony boundary.",
            expected_outcome=actual_outcome,
            proposal_id=token.proposal_id,
        )
        record = _get_kernel().record_attested_outcome(
            proposal=proposal,
            evidence=OutcomeEvidence(token.authorization_id, receipt),
            outcome={
                "summary": actual_outcome,
                "repair_needed": not tests_passed,
                "action_taken": f"{action_type} on {target}",
            },
            tests_passed=tests_passed,
            human_feedback=str(human_feedback) if human_feedback != 0.0 else None,
        )
        profile = _get_kernel().agent_profile(agent_id)
        return {
            "status": "recorded",
            "consequence_id": record.consequence_id,
            "evidence_grade": record.evidence_grade,
            "trust_score": round(profile.trust_score, 4),
        }
    except Exception as exc:
        return {"error": str(exc)}


@mcp_tool(
    category="colony_kernel",
    description="Return the governed action scope and current enforcement mode.",
)
def colony_action_scope() -> dict[str, Any]:
    """Expose the explicit declared/bypassable action-scope map."""

    kernel = _get_kernel()
    return {
        "enforcement_mode": kernel._config.enforcement_mode,
        "action_scope": kernel._config.action_scope,
        "bypass_behavior": (
            "unregistered mutating paths are refused in strict mode; "
            "advisory mode does not claim enforcement"
        ),
    }


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
        signal_type: One of ``failure``, ``policy_rejection``, ``success``,
                     ``risk``, ``need``, ``dependency``, ``human_priority``.

    Returns:
        List of serialised :class:`~codomyrmex.colony_kernel.models.ColonySignal` dicts;
        empty list if no signals are present.
    """
    try:
        sig_enum = SignalType(signal_type.lower())
        kernel = _get_kernel()
        # Use the kernel's pheromone_store directly for sensing
        strength = kernel.pheromone_store.sense(location, sig_enum)
        if strength:
            signals = kernel.pheromone_store.query_pressure(location, sig_enum)
            signal = signals[0] if signals else ColonySignal(
                location=location,
                signal_type=sig_enum,
                strength=strength,
                decay_rate=DecayRate.NORMAL,
                source=SignalSource.AGENT,
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
        # Compute severity_score and recommendation (not stored on
        # FalsificationReport). Severity is non-dilutable: mixed findings use
        # the strongest numeric rank, never an alphabetical label or mean.
        findings_list = result.get("findings", [])
        severity_values = {
            str(f.get("severity", "low")).lower() for f in findings_list
        }
        severity_map = {severity.value: severity for severity in FalsificationSeverity}
        severities = [severity_map[value] for value in severity_values if value in severity_map]
        strongest = max(severities, key=severity_rank, default=None)
        result["severity_score"] = severity_weight(strongest) if strongest else 0.0
        result["recommendation"] = recommendation_for_severity(strongest)
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
    "ColonyKernel",
    "FalsificationWorker",
    "colony_agent_profile",
    "colony_falsify_plan",
    "colony_pheromone_query",
    "colony_propose_action",
    "colony_pruning_report",
    "colony_record_outcome",
    "colony_status",
    "colony_tick",
    "isolated_kernel",
]
