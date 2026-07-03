"""Falsification worker — adversarial plan review, the colony's "no" organ.

This module applies heuristic attacks against proposed action plans to surface
structural weaknesses before execution reaches the actuation gate.  It is
deliberately pessimistic: any doubt about rollback, test coverage, scope, or
dependency safety produces a finding.

No external dependencies are used.  Circular-dependency analysis is performed
via a stdlib AST + importlib walk of the file system when a repo root is
supplied.
"""

from __future__ import annotations

import ast
import logging
import os
import re
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from codomyrmex.colony_kernel.models import (
    ActionProposal,
    ColonySignal,
    DecayRate,
    FalsificationFinding,
    FalsificationSeverity,
    SignalSource,
    SignalType,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Attack vector taxonomy
# ---------------------------------------------------------------------------


class AttackVector(Enum):
    """Categories of adversarial attacks applied by FalsificationWorker.

    Each value is used as the ``attack_vector`` string on FalsificationFinding.
    """

    DEPENDENCY_RISK = "dependency_risk"
    SECURITY_RISK = "security_risk"
    CIRCULAR_ARCHITECTURE = "circular_architecture"
    FALSE_METRIC = "false_metric"
    OVER_BROAD_MODULE = "over_broad_module"
    HIDDEN_MAINTENANCE_COST = "hidden_maintenance_cost"
    NO_ROLLBACK = "no_rollback"
    NO_TEST_VALUE = "no_test_value"
    SCOPE_CREEP = "scope_creep"
    PREMATURE_ABSTRACTION = "premature_abstraction"


# ---------------------------------------------------------------------------
# Report dataclass
# ---------------------------------------------------------------------------


@dataclass
class FalsificationReport:
    """Aggregated result of running all heuristic checks against a plan.

    ``verdict`` is one of ``"PASS"``, ``"CONDITIONAL"``, or ``"FAIL"``:

    - ``PASS``:        zero findings with severity >= HIGH (numeric >= 3)
    - ``CONDITIONAL``: 1–2 findings, none exceeds MEDIUM (numeric <= 2), no HIGH/CRITICAL
    - ``FAIL``:        any finding reaches HIGH or CRITICAL severity (numeric >= 3)

    ``required_changes`` lists concrete remediation steps derived from the
    findings' ``remediation`` fields.
    """

    plan_summary: str
    findings: list[FalsificationFinding]
    verdict: str  # "PASS" | "CONDITIONAL" | "FAIL"
    required_changes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Severity helpers
# ---------------------------------------------------------------------------

_SEVERITY_RANK: dict[FalsificationSeverity, int] = {
    FalsificationSeverity.LOW: 1,
    FalsificationSeverity.MEDIUM: 2,
    FalsificationSeverity.HIGH: 3,
    FalsificationSeverity.CRITICAL: 4,
}


def _rank(sev: FalsificationSeverity) -> int:
    """Return numeric rank for a severity (1=LOW … 4=CRITICAL)."""
    return _SEVERITY_RANK[sev]


# ---------------------------------------------------------------------------
# Main worker
# ---------------------------------------------------------------------------


class FalsificationWorker:
    """Adversarial reviewer that attacks a plan dict before gate evaluation.

    Parameters
    ----------
    pheromone_store:
        Optional TraceField instance.  When supplied, findings with severity
        >= HIGH deposit a FAILURE-type trace at the plan's ``target`` key so
        downstream ants can sense danger without re-running checks.
    consequence_memory:
        Optional ConsequenceMemory instance.  When supplied, the worker
        consults recent failure records for the plan's ``target`` to amplify
        (or suppress) certain checks.
    """

    def __init__(
        self,
        pheromone_store: Any | None = None,
        consequence_memory: Any | None = None,
    ) -> None:
        self._pheromone_store = pheromone_store
        self._consequence_memory = consequence_memory

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

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
            self.check_no_rollback(plan),
            self.check_no_test_value(plan),
            self.check_scope_creep(plan),
            self.check_missing_metrics(plan),
            self.check_circular_deps(plan, repo_root),
            self._check_dependency_risk(plan),
            self._check_security_risk(plan),
            self._check_false_metric(plan),
            self._check_over_broad_module(plan),
            self._check_hidden_maintenance_cost(plan),
            self._check_premature_abstraction(plan),
        ]

        findings: list[FalsificationFinding] = [f for f in checks if f is not None]

        verdict = self._compute_verdict(findings)
        required_changes = [f.remediation for f in findings if f.remediation]

        # Deposit pheromone traces for findings
        #   FAILURE for severity >= HIGH — strong avoidance signal
        #   RISK   for severity >= MEDIUM — caution marker (gate reads RISK pressure)
        if self._pheromone_store is not None:
            target = plan.get("target", "unknown")
            for finding in findings:
                try:
                    if _rank(finding.severity) >= 3:
                        self._pheromone_store.deposit(
                            ColonySignal(
                                location=str(target),
                                signal_type=SignalType.FAILURE,
                                strength=float(_rank(finding.severity)),
                                decay_rate=DecayRate.FAST,
                                source=SignalSource.AGENT,
                                evidence={
                                    "attack_vector": finding.attack_vector,
                                    "claim": finding.claim,
                                },
                            )
                        )
                    elif _rank(finding.severity) >= 2:
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
        plan = {
            "target": proposal.target,
            "rationale": proposal.rationale,
            "rollback_plan": proposal.rollback_plan,
            "evidence": proposal.evidence,
            "action_type": proposal.action_type,
            "budget_estimate": {
                "llm_calls": proposal.budget_estimate.llm_calls,
                "runtime_seconds": proposal.budget_estimate.runtime_seconds,
                "risk_level": proposal.budget_estimate.risk_level,
                "human_attention_minutes": proposal.budget_estimate.human_attention_minutes,
                "merge_risk": proposal.budget_estimate.merge_risk,
                "doc_debt": proposal.budget_estimate.doc_debt,
                "security_exposure": proposal.budget_estimate.security_exposure,
            },
        }
        report = self.evaluate_plan(plan)
        return report.findings

    # ------------------------------------------------------------------
    # Mandated individual checks
    # ------------------------------------------------------------------

    def check_no_rollback(self, plan: dict[str, Any]) -> FalsificationFinding | None:
        """Attack: plan has no credible rollback path.

        Returns a HIGH finding if ``rollback_plan`` is absent, empty, or
        contains only placeholder language.
        """
        rollback = plan.get("rollback_plan", "")
        if not isinstance(rollback, str):
            rollback = str(rollback)
        rollback = rollback.strip()

        placeholder_patterns = [
            r"^\s*$",
            r"^(n/?a|none|tbd|todo|unknown|not\s+applicable)\.?$",
            r"^will\s+(revert|undo)\s+manually$",
        ]
        is_missing = not rollback or any(
            re.fullmatch(p, rollback, re.IGNORECASE) for p in placeholder_patterns
        )

        if is_missing:
            return FalsificationFinding(
                claim="The plan provides a credible rollback procedure.",
                attack_vector=AttackVector.NO_ROLLBACK.value,
                severity=FalsificationSeverity.HIGH,
                evidence={"rollback_plan": rollback or "<absent>"},
                remediation=(
                    "Provide a concrete rollback plan: the exact git revert command, "
                    "database migration down-script, or feature-flag toggle that restores "
                    "the previous state without manual intervention."
                ),
            )

        # Soft check: rollback present but suspiciously short (< 20 chars)
        if len(rollback) < 20:
            return FalsificationFinding(
                claim="The rollback plan is sufficiently detailed.",
                attack_vector=AttackVector.NO_ROLLBACK.value,
                severity=FalsificationSeverity.MEDIUM,
                evidence={"rollback_plan": rollback, "length": len(rollback)},
                remediation=(
                    "Expand the rollback plan to include the specific command or procedure "
                    "and the expected post-rollback state."
                ),
            )

        return None

    def check_no_test_value(self, plan: dict[str, Any]) -> FalsificationFinding | None:
        """Attack: plan adds no verifiable test coverage.

        Returns a HIGH finding when ``tests`` is absent, empty, or describes
        only manual verification steps.
        """
        tests = plan.get("tests")

        if tests is None:
            return FalsificationFinding(
                claim="The plan includes automated test coverage.",
                attack_vector=AttackVector.NO_TEST_VALUE.value,
                severity=FalsificationSeverity.HIGH,
                evidence={"tests": "<key absent>"},
                remediation=(
                    "Add a `tests` key listing the test file paths or test IDs that will "
                    "exercise the changed behaviour.  Automated tests are non-negotiable."
                ),
            )

        if isinstance(tests, (list, tuple)):
            if not tests:
                return FalsificationFinding(
                    claim="The plan includes automated test coverage.",
                    attack_vector=AttackVector.NO_TEST_VALUE.value,
                    severity=FalsificationSeverity.HIGH,
                    evidence={"tests": []},
                    remediation=(
                        "Provide at least one test path in the `tests` list that asserts "
                        "the expected post-change behaviour."
                    ),
                )
            tests_str = " ".join(str(t) for t in tests)
        else:
            tests_str = str(tests).strip()

        manual_patterns = [
            r"\bmanual(ly)?\b",
            r"\bsmoke\s+test\b",
            r"\bverify\s+by\s+hand\b",
            r"\bcheck\s+visually\b",
        ]
        if any(re.search(p, tests_str, re.IGNORECASE) for p in manual_patterns):
            return FalsificationFinding(
                claim="Tests rely on automated execution, not manual inspection.",
                attack_vector=AttackVector.NO_TEST_VALUE.value,
                severity=FalsificationSeverity.MEDIUM,
                evidence={"tests": tests_str[:200]},
                remediation=(
                    "Replace manual verification steps with automated assertions.  "
                    "Manual checks do not scale and are not captured in CI."
                ),
            )

        return None

    def check_scope_creep(self, plan: dict[str, Any]) -> FalsificationFinding | None:
        """Attack: plan's scope is broader than its stated target.

        Detects when:
        - the ``action_type`` is a destructive operation (delete, drop, remove, truncate)
          without explicit blast-radius documentation in ``scope``;
        - the ``scope`` description references modules or systems unrelated to ``target``;
        - the scope language is deliberately vague.
        """
        scope = plan.get("scope", "")
        target = plan.get("target", "")
        action_type = str(plan.get("action_type", "")).strip().lower()

        _DESTRUCTIVE_ACTIONS = {"delete", "drop", "remove", "truncate", "purge", "wipe"}
        if action_type in _DESTRUCTIVE_ACTIONS:
            return FalsificationFinding(
                claim="The plan documents the blast radius of its destructive action.",
                attack_vector=AttackVector.SCOPE_CREEP.value,
                severity=FalsificationSeverity.HIGH,
                evidence={
                    "action_type": action_type,
                    "target": str(target),
                    "scope_documented": bool(scope),
                },
                remediation=(
                    f"Destructive action '{action_type}' requires a `scope` field "
                    "enumerating all affected files, callers, and dependent modules. "
                    "Add an explicit blast-radius analysis before submitting."
                ),
            )

        if not scope:
            return None  # Absent scope is handled elsewhere; not a creep signal.

        scope_str = str(scope).strip()
        target_str = str(target).strip()

        # Vagueness indicators
        vague_patterns = [
            r"\bvarious\b",
            r"\bmultiple\s+(systems?|modules?|services?|components?)\b",
            r"\brelated\s+(things?|work|changes?)\b",
            r"\bas\s+needed\b",
            r"\bwherever\s+applicable\b",
            r"\bgeneral\s+(improvements?|refactor(ing)?)\b",
        ]
        vague_hits = [
            p for p in vague_patterns if re.search(p, scope_str, re.IGNORECASE)
        ]
        if len(vague_hits) >= 2:
            return FalsificationFinding(
                claim="The plan scope is precisely bounded to its stated target.",
                attack_vector=AttackVector.SCOPE_CREEP.value,
                severity=FalsificationSeverity.MEDIUM,
                evidence={
                    "scope": scope_str[:300],
                    "vague_patterns_matched": vague_hits,
                },
                remediation=(
                    "Rewrite the scope to name the specific files, functions, or modules "
                    "in scope.  Vague scope language hides unbounded work."
                ),
            )

        # Cross-module boundary detection: scope mentions modules not in target
        if target_str:
            # Extract dotted module names from scope
            module_refs = re.findall(
                r"\b([a-z_][a-z0-9_]*(?:\.[a-z_][a-z0-9_]*)+)\b", scope_str
            )
            target_root = target_str.split(".")[0] if "." in target_str else target_str
            foreign_refs = [m for m in module_refs if not m.startswith(target_root)]
            if len(foreign_refs) >= 3:
                return FalsificationFinding(
                    claim="The plan scope does not reach into unrelated modules.",
                    attack_vector=AttackVector.SCOPE_CREEP.value,
                    severity=FalsificationSeverity.HIGH,
                    evidence={
                        "target_root": target_root,
                        "foreign_module_refs": foreign_refs[:10],
                    },
                    remediation=(
                        f"Scope references {len(foreign_refs)} modules outside `{target_root}`.  "
                        "Split into separate proposals or explicitly justify each cross-module touch."
                    ),
                )

        return None

    def check_missing_metrics(
        self, plan: dict[str, Any]
    ) -> FalsificationFinding | None:
        """Attack: plan defines no verifiable success metric.

        Returns a MEDIUM finding when ``metrics`` is absent or contains only
        qualitative language with no measurable thresholds.
        """
        metrics = plan.get("metrics")

        if metrics is None:
            return FalsificationFinding(
                claim="The plan specifies at least one verifiable success metric.",
                attack_vector=AttackVector.FALSE_METRIC.value,
                severity=FalsificationSeverity.MEDIUM,
                evidence={"metrics": "<key absent>"},
                remediation=(
                    "Add a `metrics` key with at least one measurable criterion, e.g. "
                    "'coverage >= 80%', 'p99 latency < 200ms', or 'zero regressions in suite X'."
                ),
            )

        metrics_str = (
            str(metrics).strip()
            if not isinstance(metrics, (list, tuple))
            else " ".join(str(m) for m in metrics)
        )

        if not metrics_str:
            return FalsificationFinding(
                claim="The plan specifies at least one verifiable success metric.",
                attack_vector=AttackVector.FALSE_METRIC.value,
                severity=FalsificationSeverity.MEDIUM,
                evidence={"metrics": "<empty>"},
                remediation=(
                    "Provide concrete, measurable metrics so outcomes can be objectively verified."
                ),
            )

        # Detect purely qualitative metrics with no numbers or comparisons
        has_number = bool(re.search(r"\d", metrics_str))
        has_comparison = bool(
            re.search(
                r"[<>=≤≥%]|better|faster|less|more|reduce|increase",
                metrics_str,
                re.IGNORECASE,
            )
        )
        if not has_number and not has_comparison:
            return FalsificationFinding(
                claim="Metrics contain measurable thresholds, not subjective language.",
                attack_vector=AttackVector.FALSE_METRIC.value,
                severity=FalsificationSeverity.LOW,
                evidence={"metrics": metrics_str[:200]},
                remediation=(
                    "Add numeric thresholds or comparison operators to the metrics description. "
                    "'Improved performance' is not a metric; '< 100ms p95' is."
                ),
            )

        return None

    def check_circular_deps(
        self,
        plan: dict[str, Any],
        repo_root: str | None,
    ) -> FalsificationFinding | None:
        """Attack: proposed changes introduce a circular import dependency.

        When *repo_root* is supplied, walks Python source files under the
        target module path and builds a lightweight import graph using the
        stdlib ``ast`` module.  Detects cycles via DFS.

        When *repo_root* is ``None`` or the target path cannot be resolved,
        the check inspects the ``dependencies`` key in the plan for self-
        referential or obviously circular entries.
        """
        target = str(plan.get("target", "")).strip()
        dependencies: list[str] = []
        raw_deps = plan.get("dependencies", [])
        if isinstance(raw_deps, (list, tuple)):
            dependencies = [str(d) for d in raw_deps]
        elif isinstance(raw_deps, str) and raw_deps:
            dependencies = [
                s.strip() for s in re.split(r"[,\n;]", raw_deps) if s.strip()
            ]

        # Self-modification check — agent targeting itself is always circular
        agent_id = str(plan.get("agent_id", "")).strip()
        if agent_id and target and agent_id == target:
            return FalsificationFinding(
                claim="The agent is not modifying itself (no self-referential proposal).",
                attack_vector=AttackVector.CIRCULAR_ARCHITECTURE.value,
                severity=FalsificationSeverity.HIGH,
                evidence={"agent_id": agent_id, "target": target},
                remediation=(
                    f"Agent `{agent_id}` is targeting itself as `{target}`. "
                    "Self-modification proposals are inherently circular. "
                    "Use a separate agent or a sandboxed test environment."
                ),
            )

        # Static dependency list check — catch obvious self-references
        if target and target in dependencies:
            return FalsificationFinding(
                claim="The plan does not introduce a self-referential dependency.",
                attack_vector=AttackVector.CIRCULAR_ARCHITECTURE.value,
                severity=FalsificationSeverity.HIGH,
                evidence={"target": target, "dependencies": dependencies},
                remediation=(
                    f"`{target}` lists itself as a dependency.  Remove the self-reference "
                    "and ensure the module interface does not require importing itself."
                ),
            )

        # Mutual pair check in dependencies list
        for i, dep_a in enumerate(dependencies):
            for dep_b in dependencies[i + 1 :]:
                if dep_a.startswith(dep_b + ".") or dep_b.startswith(dep_a + "."):
                    return FalsificationFinding(
                        claim="No parent–child circular dependency exists in the dependency list.",
                        attack_vector=AttackVector.CIRCULAR_ARCHITECTURE.value,
                        severity=FalsificationSeverity.MEDIUM,
                        evidence={"dep_a": dep_a, "dep_b": dep_b},
                        remediation=(
                            f"`{dep_a}` and `{dep_b}` appear to be in a parent–child relationship. "
                            "Verify that neither imports from the other."
                        ),
                    )

        if not repo_root:
            return None  # Cannot do filesystem analysis without a root.

        # Filesystem AST-based cycle detection
        module_dir = _module_path_to_dir(target, repo_root)
        if module_dir is None or not os.path.isdir(module_dir):
            return None  # Target not found on disk — skip filesystem check.

        try:
            import_graph = _build_import_graph(module_dir)
            cycle = _find_cycle(import_graph)
        except (OSError, SyntaxError, RecursionError):
            return None  # Parse failure is not itself a circular dep finding.

        if cycle:
            return FalsificationFinding(
                claim="The module graph under the target path is acyclic.",
                attack_vector=AttackVector.CIRCULAR_ARCHITECTURE.value,
                severity=FalsificationSeverity.HIGH,
                evidence={"cycle": cycle},
                remediation=(
                    f"Circular import detected: {' -> '.join(cycle)}.  "
                    "Extract shared types to a lower-level module that neither side imports."
                ),
            )

        return None

    # ------------------------------------------------------------------
    # Additional checks (completing the 10-check suite)
    # ------------------------------------------------------------------

    def _check_dependency_risk(
        self, plan: dict[str, Any]
    ) -> FalsificationFinding | None:
        """Attack: plan introduces unvetted external dependencies."""
        deps = plan.get("dependencies", [])
        if isinstance(deps, str):
            dep_list = [d.strip() for d in re.split(r"[,\n;]", deps) if d.strip()]
        elif isinstance(deps, (list, tuple)):
            dep_list = [str(d).strip() for d in deps if str(d).strip()]
        else:
            dep_list = []

        # Flag dependencies that look like external packages (contain no dotted project prefix)
        # and are not stdlib — heuristic: no '/' in name, has '-' or is all-lowercase short
        risky = []
        for dep in dep_list:
            # Skip dotted internal module paths
            if "." in dep and not dep.startswith("http"):
                continue
            # External package heuristic: lowercase, optional hyphens, no path separators
            if re.fullmatch(r"[a-z][a-z0-9\-_]*", dep) and len(dep) <= 40:
                risky.append(dep)

        if len(risky) >= 3:
            return FalsificationFinding(
                claim="The plan does not introduce an unvetted external dependency footprint.",
                attack_vector=AttackVector.DEPENDENCY_RISK.value,
                severity=FalsificationSeverity.MEDIUM,
                evidence={"suspicious_external_deps": risky[:10]},
                remediation=(
                    f"The plan lists {len(risky)} apparent external packages ({', '.join(risky[:3])}, …). "
                    "Justify each addition: is it already vendored, does it have a security audit, "
                    "and is a lighter stdlib alternative available?"
                ),
            )

        return None

    def _check_security_risk(self, plan: dict[str, Any]) -> FalsificationFinding | None:
        """Attack: plan touches security-sensitive paths without explicit review annotation."""
        combined = " ".join(
            [
                str(plan.get("target", "")),
                str(plan.get("rationale", "")),
                str(plan.get("scope", "")),
            ]
        )

        sensitive_patterns = [
            r"\bauth(entication|orization|token)?\b",
            r"\bpassword\b",
            r"\bcredential\b",
            r"\bsecret\b",
            r"\bencrypt\b",
            r"\bprivilege(d)?\b",
            r"\bsudo\b",
            r"\broot\b",
            r"\bpermission\b",
            r"\baccess\s+control\b",
            r"\bsanitiz\b",
            r"\binjection\b",
        ]
        hits = [p for p in sensitive_patterns if re.search(p, combined, re.IGNORECASE)]

        if not hits:
            return None

        # Check whether the plan acknowledges the security surface
        security_ack_patterns = [
            r"\bsecurity\s+review\b",
            r"\bsecurity\s+audit\b",
            r"\bsast\b",
            r"\bguard_ant\b",
            r"\bthreat\s+model\b",
        ]
        has_ack = any(
            re.search(p, combined, re.IGNORECASE) for p in security_ack_patterns
        )

        if not has_ack:
            return FalsificationFinding(
                claim="Security-sensitive changes are accompanied by an explicit security review.",
                attack_vector=AttackVector.SECURITY_RISK.value,
                severity=FalsificationSeverity.HIGH,
                evidence={"sensitive_terms_found": hits[:5]},
                remediation=(
                    "The plan touches security-sensitive surface area but does not mention "
                    "a security review or GUARD_ANT sign-off.  Add a security review step "
                    "before execution and annotate the proposal with 'security_review: required'."
                ),
            )

        return None

    def _check_false_metric(self, plan: dict[str, Any]) -> FalsificationFinding | None:
        """Attack: plan's expected_outcome is non-falsifiable (cannot be proven false)."""
        outcome = str(plan.get("expected_outcome", "")).strip()
        if not outcome:
            return FalsificationFinding(
                claim="The plan states a falsifiable expected outcome.",
                attack_vector=AttackVector.FALSE_METRIC.value,
                severity=FalsificationSeverity.MEDIUM,
                evidence={"expected_outcome": "<absent>"},
                remediation=(
                    "Add an `expected_outcome` that can be objectively verified or falsified, "
                    "e.g. 'all unit tests pass', 'API response time < 200ms under load test'."
                ),
            )

        # Detect tautological / unfalsifiable language
        unfalsifiable_patterns = [
            r"^(it\s+)?(will\s+)?work(s)?\s*$",
            r"\bimprove[sd]?\b.*\boverall\b",
            r"\bbetter\b.*\bsystem\b",
            r"\bno\s+issues\b",
            r"\bsmoothly\b",
            r"\bseamlessly\b",
            r"\bstable\b",
        ]
        hits = [
            p for p in unfalsifiable_patterns if re.search(p, outcome, re.IGNORECASE)
        ]
        if len(hits) >= 2:
            return FalsificationFinding(
                claim="The expected outcome is concrete and falsifiable.",
                attack_vector=AttackVector.FALSE_METRIC.value,
                severity=FalsificationSeverity.LOW,
                evidence={"expected_outcome": outcome[:200], "vague_patterns": hits},
                remediation=(
                    "Replace vague outcome language with a concrete, testable assertion.  "
                    "Outcomes like 'works smoothly' cannot be verified by an automated gate."
                ),
            )

        return None

    def _check_over_broad_module(
        self, plan: dict[str, Any]
    ) -> FalsificationFinding | None:
        """Attack: plan proposes a module that tries to do too many things."""
        rationale = str(plan.get("rationale", "")).strip()
        scope_str = str(plan.get("scope", "")).strip()
        combined = f"{rationale} {scope_str}"

        # Signal: rationale lists many heterogeneous responsibilities
        responsibility_indicators = re.findall(
            r"\b(handles?|manages?|coordinates?|orchestrates?|provides?|implements?|supports?|wraps?)\b",
            combined,
            re.IGNORECASE,
        )
        if len(responsibility_indicators) >= 5:
            return FalsificationFinding(
                claim="The proposed module has a single, well-bounded responsibility.",
                attack_vector=AttackVector.OVER_BROAD_MODULE.value,
                severity=FalsificationSeverity.MEDIUM,
                evidence={
                    "responsibility_verb_count": len(responsibility_indicators),
                    "verbs_found": list(
                        {v.lower() for v in responsibility_indicators[:8]}
                    ),
                },
                remediation=(
                    f"The rationale uses {len(responsibility_indicators)} responsibility verbs, "
                    "suggesting a module that does too many things.  Apply the Single Responsibility "
                    "Principle: split into focused sub-modules or reduce the stated scope."
                ),
            )

        # Signal: target path contains more than 4 dotted segments (deep nesting)
        target = str(plan.get("target", ""))
        if target.count(".") >= 5:
            return FalsificationFinding(
                claim="The module target path is not excessively deep.",
                attack_vector=AttackVector.OVER_BROAD_MODULE.value,
                severity=FalsificationSeverity.LOW,
                evidence={"target": target, "depth": target.count(".")},
                remediation=(
                    f"`{target}` is {target.count('.') + 1} levels deep.  "
                    "Deep nesting often signals accumulated responsibilities.  "
                    "Consider flattening the hierarchy or extracting a top-level module."
                ),
            )

        return None

    def _check_hidden_maintenance_cost(
        self, plan: dict[str, Any]
    ) -> FalsificationFinding | None:
        action_type = str(plan.get("action_type", "")).strip().lower()
        target = str(plan.get("target", "")).strip().lower()
        rationale = str(plan.get("rationale", "")).strip()
        scope_str = str(plan.get("scope", "")).strip()
        combined = f"{action_type} {target} {rationale} {scope_str}"

        durable_change_patterns = [
            r"\b(create|add|introduce|migrate|refactor|replace)\b",
            r"\b(module|service|framework|platform|pipeline|integration)\b",
            r"\bnew\s+(api|schema|storage|dependency|subsystem)\b",
        ]
        durable_signals = [
            pattern
            for pattern in durable_change_patterns
            if re.search(pattern, combined, re.IGNORECASE)
        ]
        if len(durable_signals) < 2:
            return None

        maintenance_fields = (
            "maintenance_plan",
            "owner",
            "ownership",
            "deprecation_plan",
            "runbook",
        )
        acknowledged = any(
            str(plan.get(field, "")).strip() for field in maintenance_fields
        )
        if acknowledged:
            return None

        return FalsificationFinding(
            claim="The plan accounts for long-term ownership and maintenance burden.",
            attack_vector=AttackVector.HIDDEN_MAINTENANCE_COST.value,
            severity=FalsificationSeverity.MEDIUM,
            evidence={
                "durable_change_signals": durable_signals,
                "maintenance_fields_checked": list(maintenance_fields),
            },
            remediation=(
                "Add an owner, maintenance_plan, runbook, or deprecation_plan that explains "
                "who will operate the durable change and how future upkeep will be handled."
            ),
        )

    def _check_premature_abstraction(
        self, plan: dict[str, Any]
    ) -> FalsificationFinding | None:
        """Attack: plan introduces a generic abstraction without demonstrated need."""
        rationale = str(plan.get("rationale", "")).strip()
        scope_str = str(plan.get("scope", "")).strip()
        combined = f"{rationale} {scope_str}"

        abstraction_signals = [
            r"\bgeneric\b",
            r"\breusable?\b",
            r"\bextensible\b",
            r"\bplug-?in\b",
            r"\babstract\s+(base\s+)?class\b",
            r"\binterface\b",
            r"\bframework\b",
            r"\bplatform\b",
        ]
        hits = [p for p in abstraction_signals if re.search(p, combined, re.IGNORECASE)]

        if not hits:
            return None

        # Look for evidence that the abstraction is backed by multiple concrete callers
        evidence_patterns = [
            r"\b\d+\s+(callers?|uses?|consumers?|clients?)\b",
            r"\bthree\s+(or\s+more\s+)?(callers?|uses?)\b",
            r"\bexisting\s+(callers?|consumers?|uses?)\b",
            r"\bproven\b",
            r"\bdemonstrated\b",
        ]
        has_evidence = any(
            re.search(p, combined, re.IGNORECASE) for p in evidence_patterns
        )

        if not has_evidence and len(hits) >= 2:
            return FalsificationFinding(
                claim="The abstraction is justified by at least three distinct concrete use-sites.",
                attack_vector=AttackVector.PREMATURE_ABSTRACTION.value,
                severity=FalsificationSeverity.LOW,
                evidence={
                    "abstraction_signals": hits,
                    "combined_excerpt": combined[:300],
                },
                remediation=(
                    "Abstractions earn their complexity by reducing duplication across three or "
                    "more concrete use-sites.  Document the existing callers that motivated the "
                    "abstraction, or defer the generalisation until the need is demonstrated."
                ),
            )

        return None

    # ------------------------------------------------------------------
    # Verdict and summary helpers
    # ------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Filesystem helpers for circular-dependency check
# ---------------------------------------------------------------------------


def _module_path_to_dir(dotted_module: str, repo_root: str) -> str | None:
    """Convert a dotted module path to a filesystem directory path.

    Searches common source tree roots (``src/``, ``src/<package>/``, repo root).
    Returns ``None`` if the directory cannot be located.
    """
    parts = dotted_module.split(".")
    candidates = [
        os.path.join(repo_root, *parts),
        os.path.join(repo_root, "src", *parts),
    ]
    # Also handle src/<top_package>/<rest>
    if parts:
        candidates.append(os.path.join(repo_root, "src", parts[0], *parts[1:]))

    for candidate in candidates:
        if os.path.isdir(candidate):
            return candidate
    return None


def _build_import_graph(module_dir: str) -> dict[str, list[str]]:
    """Walk *module_dir* recursively and build a module-level import graph.

    Returns a dict mapping each Python file's dotted-like key (relative to
    *module_dir*) to the list of dotted-like keys it imports.

    Only relative imports and intra-tree absolute imports are tracked.
    """
    graph: dict[str, list[str]] = {}
    base_name = os.path.basename(module_dir)

    for dirpath, _dirs, filenames in os.walk(module_dir):
        for fname in filenames:
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(dirpath, fname)
            rel = os.path.relpath(fpath, module_dir)
            # Convert path to dotted key
            node = base_name + "." + rel.replace(os.sep, ".").removesuffix(".py")
            if node.endswith(".__init__"):
                node = node.removesuffix(".__init__")
            imports: list[str] = []
            try:
                source = _read_source(fpath)
                tree = ast.parse(source, filename=fpath)
            except (OSError, SyntaxError):
                graph[node] = imports
                continue

            for ast_node in ast.walk(tree):
                if isinstance(ast_node, ast.Import):
                    for alias in ast_node.names:
                        if alias.name.startswith(base_name):
                            imports.append(alias.name)
                elif isinstance(ast_node, ast.ImportFrom):
                    if ast_node.module and ast_node.module.startswith(base_name):
                        imports.append(ast_node.module)
                    elif ast_node.level and ast_node.level > 0:
                        # Relative import — resolve approximately
                        pkg_parts = node.split(".")
                        up = ast_node.level
                        prefix = ".".join(pkg_parts[: max(1, len(pkg_parts) - up)])
                        resolved = (
                            f"{prefix}.{ast_node.module}" if ast_node.module else prefix
                        )
                        imports.append(resolved)

            graph[node] = imports

    return graph


def _read_source(path: str) -> str:
    """Read a Python source file, trying UTF-8 then latin-1."""
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read()
    except UnicodeDecodeError:
        with open(path, encoding="latin-1") as fh:
            return fh.read()


def _find_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    """Return a non-empty list of node names forming a cycle, or ``None`` if acyclic.

    Uses Kahn's topological sort algorithm (BFS-based) which is O(V+E) and
    provably correct for all graph shapes including 3+ hop dependency chains.
    The previous DFS implementation prematurely discarded the ``on_stack`` set
    in its iterative loop, causing it to miss cycles reachable via multiple
    paths.

    Algorithm:
        1. Compute in-degree for every node.
        2. Enqueue all nodes with in-degree 0 (sources).
        3. Process the queue: for each dequeued node, decrement the in-degree
           of its neighbours; re-enqueue neighbours whose in-degree drops to 0.
        4. After the queue empties, any node with in-degree > 0 belongs to a
           cycle (Kahn's invariant: a DAG yields |V| processed nodes; a cyclic
           graph yields fewer).

    When a cycle is detected the function returns a short witness path that
    traverses one cycle: it performs a targeted DFS from one of the surviving
    high-in-degree nodes, following only edges that stay within the cycle
    residual subgraph, until a node is revisited.

    Args:
        graph: Adjacency list mapping each node to its neighbours.  Nodes
            present as neighbours but absent as keys are treated as sinks
            (in-degree counted, out-degree zero).

    Returns:
        A list of node names forming a cycle (first node == last node for
        clarity), or ``None`` if the graph is acyclic.
    """
    # Collect all nodes (keys + any neighbours not themselves keys).
    all_nodes: set[str] = set(graph)
    for neighbours in graph.values():
        all_nodes.update(neighbours)

    # Build in-degree table.
    in_degree: dict[str, int] = dict.fromkeys(all_nodes, 0)
    for node, neighbours in graph.items():
        for nbr in neighbours:
            in_degree[nbr] = in_degree.get(nbr, 0) + 1

    # BFS queue seeded with zero-in-degree nodes.
    queue: deque[str] = deque(n for n in all_nodes if in_degree[n] == 0)
    processed: int = 0

    while queue:
        node = queue.popleft()
        processed += 1
        for nbr in graph.get(node, []):
            in_degree[nbr] -= 1
            if in_degree[nbr] == 0:
                queue.append(nbr)

    if processed == len(all_nodes):
        # All nodes processed → graph is a DAG.
        return None

    # Cycle exists: collect the residual subgraph (nodes with in_degree > 0).
    # Walk one cycle starting from an arbitrary residual node using a path-aware DFS.
    residual: set[str] = {n for n in all_nodes if in_degree[n] > 0}

    # Recursive-style path tracking: stack carries (node, path_so_far).
    # We use a fresh visited set per DFS root so cross-path contamination cannot
    # produce a false cycle_start index.
    start = next(iter(residual))
    stack: list[tuple[str, list[str]]] = [(start, [start])]
    while stack:
        node, current_path = stack.pop()
        # If this node already appears in the current path we've closed a cycle.
        if node in current_path[:-1]:
            idx = current_path.index(node)
            # Slice from first occurrence to the repeated occurrence (inclusive).
            return current_path[idx:]
        if node not in residual:
            continue
        for nbr in graph.get(node, []):
            if nbr in residual:
                stack.append((nbr, [*current_path, nbr]))

    # Fallback: return any residual node list as evidence of a cycle.
    return list(residual)[:2]


# ---------------------------------------------------------------------------
# Public exports
# ---------------------------------------------------------------------------

__all__ = [
    "AttackVector",
    "FalsificationReport",
    "FalsificationWorker",
]
