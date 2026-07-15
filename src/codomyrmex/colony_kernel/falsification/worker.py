"""FalsificationWorker orchestrator."""

from __future__ import annotations

import logging
from typing import Any

from codomyrmex.colony_kernel.falsification.checks import (
    check_circular_deps,
    check_dependency_risk,
    check_false_metric,
    check_hidden_maintenance_cost,
    check_missing_metrics,
    check_no_rollback,
    check_no_test_value,
    check_over_broad_module,
    check_premature_abstraction,
    check_scope_creep,
    check_security_risk,
)
from codomyrmex.colony_kernel.falsification.models import (
    FalsificationPlan,
    FalsificationReport,
    _rank,
)
from codomyrmex.colony_kernel.models import (
    ActionProposal,
    ColonySignal,
    DecayRate,
    FalsificationFinding,
    SignalSource,
    SignalType,
)

logger = logging.getLogger(__name__)


class FalsificationWorker:
    """Adversarial reviewer that attacks a plan dict before gate evaluation."""

    def __init__(
        self,
        pheromone_store: Any | None = None,
        consequence_memory: Any | None = None,
    ) -> None:
        self._pheromone_store = pheromone_store
        self._consequence_memory = consequence_memory

    # Backward-compatible method wrappers (tests and callers use worker.check_*).
    def check_no_rollback(self, plan: dict[str, Any]) -> FalsificationFinding | None:
        return check_no_rollback(plan)

    def check_no_test_value(self, plan: dict[str, Any]) -> FalsificationFinding | None:
        return check_no_test_value(plan)

    def check_scope_creep(self, plan: dict[str, Any]) -> FalsificationFinding | None:
        return check_scope_creep(plan)

    def check_missing_metrics(self, plan: dict[str, Any]) -> FalsificationFinding | None:
        return check_missing_metrics(plan)

    def check_circular_deps(
        self, plan: dict[str, Any], repo_root: str | None
    ) -> FalsificationFinding | None:
        return check_circular_deps(plan, repo_root)

    def _check_dependency_risk(self, plan: dict[str, Any]) -> FalsificationFinding | None:
        return check_dependency_risk(plan)

    def _check_security_risk(self, plan: dict[str, Any]) -> FalsificationFinding | None:
        return check_security_risk(plan)

    def _check_false_metric(self, plan: dict[str, Any]) -> FalsificationFinding | None:
        return check_false_metric(plan)

    def _check_over_broad_module(self, plan: dict[str, Any]) -> FalsificationFinding | None:
        return check_over_broad_module(plan)

    def _check_hidden_maintenance_cost(
        self, plan: dict[str, Any]
    ) -> FalsificationFinding | None:
        return check_hidden_maintenance_cost(plan)

    def _check_premature_abstraction(
        self, plan: dict[str, Any]
    ) -> FalsificationFinding | None:
        return check_premature_abstraction(plan)

    def evaluate_plan(self, plan: dict[str, Any]) -> FalsificationReport:
        """Run heuristic checks across all 10 attack-vector categories.

        Expected plan keys (all optional — missing keys produce findings):
        ``target``, ``rationale``, ``rollback_plan``, ``tests``, ``metrics``,
        ``scope``, ``dependencies``.

        Parameters
        ----------
        plan:
            Arbitrary dict describing the proposed action.

        Returns
        -------
        FalsificationReport
            Aggregated findings, verdict, and required changes.
        """
        repo_root: str | None = plan.get("repo_root") or plan.get("_repo_root")

        checks = [
            check_no_rollback(plan),
            check_no_test_value(plan),
            check_scope_creep(plan),
            check_missing_metrics(plan),
            check_circular_deps(plan, repo_root),
            check_dependency_risk(plan),
            check_security_risk(plan),
            check_false_metric(plan),
            check_over_broad_module(plan),
            check_hidden_maintenance_cost(plan),
            check_premature_abstraction(plan),
        ]

        findings: list[FalsificationFinding] = [f for f in checks if f is not None]

        verdict = self._compute_verdict(findings)
        required_changes = [f.remediation for f in findings if f.remediation]

        # Prospective falsification findings are not observed execution
        # outcomes.  They therefore use the RISK/finding channel at MEDIUM+
        # severity; FAILURE remains reserved for caller-reported adverse
        # consequences.  One finding produces at most one signal here.
        if self._pheromone_store is not None:
            target = plan.get("target", "unknown")
            for finding in findings:
                try:
                    if _rank(finding.severity) >= 2:
                        self._pheromone_store.deposit(
                            ColonySignal(
                                location=str(target),
                                signal_type=SignalType.RISK,
                                strength=float(_rank(finding.severity)) * 0.5,
                                decay_rate=DecayRate.FAST,
                                source=SignalSource.AGENT,
                                evidence={
                                    "attack_vector": finding.attack_vector,
                                    "claim": finding.claim,
                                },
                            )
                        )
                except Exception:
                    logger.warning(
                        "PheromoneStore deposit failed for target %r (finding: %s): ",
                        target,
                        finding.attack_vector,
                        exc_info=True,
                    )

        summary = self._build_summary(plan)
        return FalsificationReport(
            plan_summary=summary,
            findings=findings,
            verdict=verdict,
            required_changes=required_changes,
        )

    def analyze(self, proposal: ActionProposal) -> list[FalsificationFinding]:
        """Run all falsification checks against *proposal*.

        Converts the ActionProposal to a plan dict, calls evaluate_plan,
        and returns only the findings list for ColonyKernel compatibility.
        """
        plan = proposal_to_falsification_plan(proposal)
        report = self.evaluate_plan(plan)
        return report.findings

    @staticmethod
    def _compute_verdict(findings: list[FalsificationFinding]) -> str:
        """Compute the final verdict string from a list of findings.

        Rules (numeric rank: LOW=1, MED=2, HIGH=3, CRIT=4):

        - FAIL:        any finding with rank >= 3 (HIGH or CRITICAL)
        - CONDITIONAL: 1–2 findings, all with rank <= 2 (LOW or MEDIUM)
        - PASS:        zero findings
        """
        if not findings:
            return "PASS"

        max_rank = max(_rank(f.severity) for f in findings)
        if max_rank >= 3:
            return "FAIL"

        # All findings are LOW or MEDIUM
        if len(findings) <= 2:
            return "CONDITIONAL"

        # More than 2 findings even if all low severity = CONDITIONAL (borderline)
        return "CONDITIONAL"

    @staticmethod
    def _build_summary(plan: dict[str, Any]) -> str:
        """Build a human-readable one-line summary of the plan."""
        action = str(plan.get("action_type", "action")).strip() or "action"
        target = str(plan.get("target", "unknown")).strip() or "unknown"
        agent = str(plan.get("agent_id", "unknown-agent")).strip() or "unknown-agent"
        return f"{agent}: {action} on {target}"


__all__ = ["FalsificationWorker", "proposal_to_falsification_plan"]


def proposal_to_falsification_plan(proposal: ActionProposal) -> FalsificationPlan:
    """Convert an :class:`ActionProposal` to the complete check input shape.

    Proposal fields remain authoritative.  Optional falsification fields are
    read from ``proposal.evidence`` so the conversion is deterministic and no
    check silently receives a missing field merely because the caller used the
    typed proposal API.
    """
    evidence = dict(proposal.evidence)

    def evidence_value(key: str, default: Any) -> Any:
        return evidence.get(key, default)

    tests = evidence_value("tests", evidence_value("test_ids", evidence.get("test", [])))
    return {
        "agent_id": proposal.agent_id,
        "action_type": proposal.action_type,
        "target": proposal.target,
        "rationale": proposal.rationale,
        "expected_outcome": proposal.expected_outcome,
        "rollback_plan": proposal.rollback_plan,
        "tests": tests,
        "metrics": evidence_value("metrics", ""),
        "scope": evidence_value("scope", ""),
        "dependencies": evidence_value("dependencies", []),
        "evidence": evidence,
        "budget_estimate": {
            "llm_calls": proposal.budget_estimate.llm_calls,
            "runtime_seconds": proposal.budget_estimate.runtime_seconds,
            "risk_level": proposal.budget_estimate.risk_level,
            "human_attention_minutes": proposal.budget_estimate.human_attention_minutes,
            "merge_risk": proposal.budget_estimate.merge_risk,
            "doc_debt": proposal.budget_estimate.doc_debt,
            "security_exposure": proposal.budget_estimate.security_exposure,
        },
        "repo_root": str(evidence_value("repo_root", "")),
    }
