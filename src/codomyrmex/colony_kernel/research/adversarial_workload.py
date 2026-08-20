"""Adversarial workload adapter and evaluation runner for Colony Kernel (R3).

Executes structured hostile workloads against baseline and gate-mediated policies,
quantifying attack success rate, harmful action mitigation, and safety-utility trade-offs.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from codomyrmex.colony_kernel.reference import (
    ReferenceDecision,
    ReferenceGate,
    ReferenceInput,
)
from codomyrmex.colony_kernel.research.metrics import paired_bootstrap_delta
from codomyrmex.colony_kernel.research.schemas import PolicyTrace, TaskCase


@dataclass(frozen=True)
class ThreatStratifiedResult:
    """Evaluation metrics stratified by specific threat vector."""

    threat_category: str
    total_cases: int
    attack_attempts: int
    baseline_harmful_actions: int
    mediated_harmful_actions: int
    baseline_harm_rate: float
    mediated_harm_rate: float
    harm_reduction_pct: float
    mediated_utility: float


@dataclass(frozen=True)
class AdversarialBenchmarkReport:
    """Comprehensive adversarial evaluation report."""

    total_tasks: int
    threat_stratified: dict[str, ThreatStratifiedResult]
    overall_baseline_harm_rate: float
    overall_mediated_harm_rate: float
    harm_delta: dict[str, Any]
    utility_delta: dict[str, Any]
    traces: tuple[PolicyTrace, ...]


def load_adversarial_cases_from_json(path: str | Path) -> list[TaskCase]:
    """Load adversarial task cases from a JSON specification file."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Adversarial case file not found: {path}")
    raw_data = json.loads(path.read_text(encoding="utf-8"))
    cases: list[TaskCase] = []
    for item in raw_data:
        cases.append(
            TaskCase(
                task_id=item["task_id"],
                threat=item["threat"],
                target=item["target"],
                proposed_action=item["proposed_action"],
                allowed_actions=tuple(item["allowed_actions"]),
                harmful_actions=tuple(item["harmful_actions"]),
                expected_safe=item["expected_safe"],
                risk_pressure=item.get("risk_pressure", 0.0),
                trust_score=item.get("trust_score", 0.5),
            )
        )
    return cases


class AdversarialWorkloadEvaluator:
    """Evaluates policies against categorized hostile and benign workloads."""

    def __init__(self, gate: ReferenceGate | None = None) -> None:
        self.gate = gate or ReferenceGate()

    def evaluate_workload(
        self,
        cases: Iterable[TaskCase],
        *,
        seed: int = 0,
    ) -> AdversarialBenchmarkReport:
        """Run paired evaluation on all supplied adversarial/benign cases."""
        cases_list = list(cases)
        if not cases_list:
            raise ValueError("Workload evaluation requires at least one task case")

        traces: list[PolicyTrace] = []

        for case in cases_list:
            # 1. Baseline: always executes the proposed action
            base_refused = False
            base_harmful = case.proposed_action in case.harmful_actions
            base_utility = 0.0 if base_harmful else 1.0
            traces.append(
                PolicyTrace(
                    task_id=case.task_id,
                    condition="baseline_always_execute",
                    chosen_action=case.proposed_action,
                    refused=base_refused,
                    harmful=base_harmful,
                    utility=base_utility,
                    trace_complete=True,
                    metadata={"threat": case.threat, "target": case.target},
                )
            )

            # 2. Gate mediated evaluation
            verdict = self.gate.evaluate(
                ReferenceInput(
                    budget_approved=True,
                    role="repair_ant",
                    trust_score=case.trust_score,
                    risk_pressure=case.risk_pressure,
                    failure_pressure=0.0,
                    missing_fields=0,
                )
            )
            med_action = (
                "refuse"
                if verdict.decision != ReferenceDecision.EXECUTE
                else case.proposed_action
            )
            med_refused = med_action == "refuse"
            med_harmful = not med_refused and med_action in case.harmful_actions
            if med_refused:
                med_utility = 0.5 if case.expected_safe else 0.0
            else:
                med_utility = 0.0 if med_harmful else 1.0

            traces.append(
                PolicyTrace(
                    task_id=case.task_id,
                    condition="gate_mediated",
                    chosen_action=med_action,
                    refused=med_refused,
                    harmful=med_harmful,
                    utility=med_utility,
                    trace_complete=True,
                    metadata={"threat": case.threat, "target": case.target},
                )
            )

        baseline_traces = [
            t for t in traces if t.condition == "baseline_always_execute"
        ]
        mediated_traces = [t for t in traces if t.condition == "gate_mediated"]

        base_harm_list = [float(t.harmful) for t in baseline_traces]
        med_harm_list = [float(t.harmful) for t in mediated_traces]
        base_util_list = [t.utility for t in baseline_traces]
        med_util_list = [t.utility for t in mediated_traces]

        harm_delta = paired_bootstrap_delta(base_harm_list, med_harm_list, seed=seed)
        util_delta = paired_bootstrap_delta(base_util_list, med_util_list, seed=seed)

        # Threat-stratified breakdown
        threat_groups: dict[str, list[TaskCase]] = {}
        for c in cases_list:
            threat_groups.setdefault(c.threat, []).append(c)

        stratified_results: dict[str, ThreatStratifiedResult] = {}
        for threat, group_cases in threat_groups.items():
            g_ids = {c.task_id for c in group_cases}
            g_base = [t for t in baseline_traces if t.task_id in g_ids]
            g_med = [t for t in mediated_traces if t.task_id in g_ids]

            b_harm_cnt = sum(1 for t in g_base if t.harmful)
            m_harm_cnt = sum(1 for t in g_med if t.harmful)
            b_rate = b_harm_cnt / len(g_base) if g_base else 0.0
            m_rate = m_harm_cnt / len(g_med) if g_med else 0.0
            red_pct = ((b_rate - m_rate) / b_rate * 100.0) if b_rate > 0 else 0.0
            m_util = sum(t.utility for t in g_med) / len(g_med) if g_med else 0.0

            stratified_results[threat] = ThreatStratifiedResult(
                threat_category=threat,
                total_cases=len(group_cases),
                attack_attempts=sum(1 for c in group_cases if not c.expected_safe),
                baseline_harmful_actions=b_harm_cnt,
                mediated_harmful_actions=m_harm_cnt,
                baseline_harm_rate=b_rate,
                mediated_harm_rate=m_rate,
                harm_reduction_pct=red_pct,
                mediated_utility=m_util,
            )

        return AdversarialBenchmarkReport(
            total_tasks=len(cases_list),
            threat_stratified=stratified_results,
            overall_baseline_harm_rate=sum(base_harm_list) / len(base_harm_list),
            overall_mediated_harm_rate=sum(med_harm_list) / len(med_harm_list),
            harm_delta=harm_delta,
            utility_delta=util_delta,
            traces=tuple(traces),
        )
