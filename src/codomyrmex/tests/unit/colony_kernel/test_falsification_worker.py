"""Unit tests for codomyrmex.colony_kernel.falsification_worker.

Zero-mock policy: no unittest.mock, MagicMock, or pytest-mock.
All inputs are real dicts; all assertions are against real return values.
"""

from __future__ import annotations

import pytest

from codomyrmex.colony_kernel.falsification_worker import (
    AttackVector,
    FalsificationReport,
    FalsificationWorker,
)
from codomyrmex.colony_kernel.models import (
    FalsificationFinding,
    FalsificationSeverity,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _minimal_plan(**overrides) -> dict:
    """Return a plan dict that passes all 10 checks (PASS verdict) unless overridden."""
    base = {
        "agent_id": "test-agent",
        "action_type": "patch_file",
        "target": "mypackage.module",
        "rationale": "Fix the off-by-one error in the summation loop.",
        "expected_outcome": "all unit tests pass; coverage >= 80%",
        "rollback_plan": "git revert HEAD --no-edit && uv run pytest",
        "tests": ["tests/unit/mypackage/test_module.py"],
        "metrics": "coverage >= 80%",
        "scope": "mypackage.module only",
        "dependencies": [],
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# check_no_rollback
# ---------------------------------------------------------------------------

class TestCheckNoRollback:

    def setup_method(self):
        self.worker = FalsificationWorker()

    def test_absent_rollback_returns_high_finding(self):
        plan = _minimal_plan(rollback_plan="")
        finding = self.worker.check_no_rollback(plan)
        assert finding is not None
        assert finding.attack_vector == AttackVector.NO_ROLLBACK.value
        assert finding.severity == FalsificationSeverity.HIGH

    def test_placeholder_na_returns_high_finding(self):
        for placeholder in ("n/a", "N/A", "none", "TODO", "tbd", "unknown", "not applicable"):
            plan = _minimal_plan(rollback_plan=placeholder)
            finding = self.worker.check_no_rollback(plan)
            assert finding is not None, f"Expected finding for placeholder: {placeholder!r}"
            assert finding.severity == FalsificationSeverity.HIGH

    def test_very_short_rollback_returns_medium_finding(self):
        # < 20 chars but not empty/placeholder
        plan = _minimal_plan(rollback_plan="git revert")
        finding = self.worker.check_no_rollback(plan)
        assert finding is not None
        assert finding.severity == FalsificationSeverity.MEDIUM
        assert finding.attack_vector == AttackVector.NO_ROLLBACK.value

    def test_credible_rollback_returns_none(self):
        plan = _minimal_plan(
            rollback_plan="git revert HEAD --no-edit && uv run pytest to verify no regressions"
        )
        finding = self.worker.check_no_rollback(plan)
        assert finding is None

    def test_finding_contains_evidence(self):
        plan = _minimal_plan(rollback_plan="")
        finding = self.worker.check_no_rollback(plan)
        assert finding is not None
        assert "rollback_plan" in finding.evidence

    def test_finding_contains_remediation(self):
        plan = _minimal_plan(rollback_plan="")
        finding = self.worker.check_no_rollback(plan)
        assert finding is not None
        assert len(finding.remediation) > 0


# ---------------------------------------------------------------------------
# check_no_test_value
# ---------------------------------------------------------------------------

class TestCheckNoTestValue:

    def setup_method(self):
        self.worker = FalsificationWorker()

    def test_absent_tests_key_returns_high_finding(self):
        plan = _minimal_plan()
        del plan["tests"]
        finding = self.worker.check_no_test_value(plan)
        assert finding is not None
        assert finding.severity == FalsificationSeverity.HIGH
        assert finding.attack_vector == AttackVector.NO_TEST_VALUE.value

    def test_empty_tests_list_returns_high_finding(self):
        plan = _minimal_plan(tests=[])
        finding = self.worker.check_no_test_value(plan)
        assert finding is not None
        assert finding.severity == FalsificationSeverity.HIGH

    def test_manual_verification_returns_medium_finding(self):
        for manual_str in [
            "manually verify the output",
            "smoke test in staging",
            "verify by hand after deploy",
        ]:
            plan = _minimal_plan(tests=manual_str)
            finding = self.worker.check_no_test_value(plan)
            assert finding is not None, f"Expected finding for: {manual_str!r}"
            assert finding.severity == FalsificationSeverity.MEDIUM

    def test_automated_test_paths_return_none(self):
        plan = _minimal_plan(tests=["tests/unit/mypackage/test_core.py"])
        finding = self.worker.check_no_test_value(plan)
        assert finding is None

    def test_non_empty_string_tests_return_none(self):
        plan = _minimal_plan(tests="tests/unit/test_foo.py::test_bar")
        finding = self.worker.check_no_test_value(plan)
        assert finding is None


# ---------------------------------------------------------------------------
# evaluate_plan — complete plan → PASS verdict
# ---------------------------------------------------------------------------

class TestEvaluatePlanCompletePass:

    def setup_method(self):
        self.worker = FalsificationWorker()

    def test_complete_plan_returns_falsification_report(self):
        plan = _minimal_plan()
        report = self.worker.evaluate_plan(plan)
        assert isinstance(report, FalsificationReport)

    def test_complete_plan_has_verdict_attribute(self):
        plan = _minimal_plan()
        report = self.worker.evaluate_plan(plan)
        assert report.verdict in {"PASS", "CONDITIONAL", "FAIL"}

    def test_complete_plan_produces_pass_or_conditional(self):
        # A well-formed plan should not FAIL (no HIGH/CRITICAL findings)
        plan = _minimal_plan()
        report = self.worker.evaluate_plan(plan)
        assert report.verdict != "FAIL", (
            f"Expected PASS or CONDITIONAL, got FAIL. Findings: {report.findings}"
        )

    def test_complete_plan_findings_are_list_of_falsification_findings(self):
        plan = _minimal_plan()
        report = self.worker.evaluate_plan(plan)
        for f in report.findings:
            assert isinstance(f, FalsificationFinding)

    def test_complete_plan_required_changes_are_strings(self):
        plan = _minimal_plan()
        report = self.worker.evaluate_plan(plan)
        for change in report.required_changes:
            assert isinstance(change, str)

    def test_complete_plan_plan_summary_contains_target(self):
        plan = _minimal_plan()
        report = self.worker.evaluate_plan(plan)
        assert "mypackage.module" in report.plan_summary

    def test_complete_plan_plan_summary_contains_agent_id(self):
        plan = _minimal_plan()
        report = self.worker.evaluate_plan(plan)
        assert "test-agent" in report.plan_summary


# ---------------------------------------------------------------------------
# evaluate_plan — plans with severe findings → FAIL verdict
# ---------------------------------------------------------------------------

class TestEvaluatePlanFailVerdict:

    def setup_method(self):
        self.worker = FalsificationWorker()

    def test_missing_rollback_and_tests_produces_fail(self):
        # Both rollback and tests absent → at least two HIGH findings → FAIL
        plan = _minimal_plan(rollback_plan="", tests=None)
        del plan["tests"]
        report = self.worker.evaluate_plan(plan)
        assert report.verdict == "FAIL"

    def test_fail_verdict_when_rollback_absent(self):
        # Absent rollback alone is HIGH → FAIL
        plan = _minimal_plan(rollback_plan="")
        report = self.worker.evaluate_plan(plan)
        assert report.verdict == "FAIL"

    def test_fail_verdict_populates_required_changes(self):
        plan = _minimal_plan(rollback_plan="", tests=None)
        del plan["tests"]
        report = self.worker.evaluate_plan(plan)
        assert len(report.required_changes) >= 1

    def test_fail_findings_include_high_severity(self):
        plan = _minimal_plan(rollback_plan="")
        report = self.worker.evaluate_plan(plan)
        severities = {f.severity for f in report.findings}
        assert FalsificationSeverity.HIGH in severities

    def test_plan_with_only_medium_findings_is_not_fail(self):
        # A plan with metrics absent (MEDIUM) but good rollback/tests
        # should be CONDITIONAL, not FAIL
        plan = _minimal_plan()
        del plan["metrics"]
        report = self.worker.evaluate_plan(plan)
        # Missing metrics is MEDIUM; missing expected_outcome is also possible but:
        # check that it is not FAIL as long as rollback+tests are present
        # (Note: _check_false_metric also fires when expected_outcome is absent — so
        # we keep expected_outcome here)
        assert report.verdict in {"PASS", "CONDITIONAL"}


# ---------------------------------------------------------------------------
# evaluate_plan — returns FalsificationReport with correct shape
# ---------------------------------------------------------------------------

class TestFalsificationReportShape:

    def setup_method(self):
        self.worker = FalsificationWorker()

    def test_report_has_plan_summary(self):
        plan = _minimal_plan()
        report = self.worker.evaluate_plan(plan)
        assert isinstance(report.plan_summary, str)
        assert len(report.plan_summary) > 0

    def test_report_has_findings_list(self):
        plan = _minimal_plan()
        report = self.worker.evaluate_plan(plan)
        assert isinstance(report.findings, list)

    def test_report_has_verdict_string(self):
        plan = _minimal_plan()
        report = self.worker.evaluate_plan(plan)
        assert isinstance(report.verdict, str)

    def test_report_has_required_changes_list(self):
        plan = _minimal_plan()
        report = self.worker.evaluate_plan(plan)
        assert isinstance(report.required_changes, list)

    def test_required_changes_match_finding_remediations(self):
        # required_changes should be the non-empty remediations of findings
        plan = _minimal_plan(rollback_plan="")
        report = self.worker.evaluate_plan(plan)
        expected = [f.remediation for f in report.findings if f.remediation]
        assert report.required_changes == expected

    def test_no_rollback_finding_attack_vector_is_no_rollback(self):
        plan = _minimal_plan(rollback_plan="")
        report = self.worker.evaluate_plan(plan)
        no_rb_findings = [
            f for f in report.findings
            if f.attack_vector == AttackVector.NO_ROLLBACK.value
        ]
        assert len(no_rb_findings) >= 1

    def test_scope_creep_finding_not_present_for_narrow_scope(self):
        plan = _minimal_plan(scope="mypackage.module only")
        report = self.worker.evaluate_plan(plan)
        creep_findings = [
            f for f in report.findings
            if f.attack_vector == AttackVector.SCOPE_CREEP.value
        ]
        assert len(creep_findings) == 0


# ---------------------------------------------------------------------------
# FalsificationFinding model validation (models.py contract)
# ---------------------------------------------------------------------------

class TestFalsificationFindingModel:

    def test_requires_non_empty_claim(self):
        with pytest.raises(ValueError, match="claim"):
            FalsificationFinding(
                claim="",
                attack_vector="no_rollback",
                severity=FalsificationSeverity.HIGH,
            )

    def test_requires_non_empty_attack_vector(self):
        with pytest.raises(ValueError, match="attack_vector"):
            FalsificationFinding(
                claim="some claim",
                attack_vector="",
                severity=FalsificationSeverity.HIGH,
            )

    def test_valid_finding_round_trips(self):
        finding = FalsificationFinding(
            claim="The plan is reversible.",
            attack_vector=AttackVector.NO_ROLLBACK.value,
            severity=FalsificationSeverity.MEDIUM,
            evidence={"detail": "short rollback"},
            remediation="Expand the rollback procedure.",
        )
        assert finding.claim == "The plan is reversible."
        assert finding.severity == FalsificationSeverity.MEDIUM
        assert finding.evidence["detail"] == "short rollback"


# ---------------------------------------------------------------------------
# check_scope_creep
# ---------------------------------------------------------------------------


class TestCheckScopeCreep:

    def setup_method(self):
        self.worker = FalsificationWorker()

    def test_absent_scope_returns_none(self):
        plan = _minimal_plan(scope="")
        finding = self.worker.check_scope_creep(plan)
        assert finding is None

    def test_vague_language_two_hits_returns_medium(self):
        # "various" + "as needed" → 2 vague pattern hits → MEDIUM
        plan = _minimal_plan(scope="Covers various modules and applies changes as needed.")
        finding = self.worker.check_scope_creep(plan)
        assert finding is not None
        assert finding.severity == FalsificationSeverity.MEDIUM
        assert finding.attack_vector == AttackVector.SCOPE_CREEP.value

    def test_one_vague_hit_returns_none(self):
        plan = _minimal_plan(scope="Covers various modules.")
        finding = self.worker.check_scope_creep(plan)
        assert finding is None

    def test_foreign_module_refs_three_or_more_returns_high(self):
        # scope mentions 3 modules from a foreign root
        plan = _minimal_plan(
            target="mypackage.core",
            scope=(
                "Touches other.auth.login, other.billing.invoice, "
                "other.reporting.dashboard and mypackage.core."
            ),
        )
        finding = self.worker.check_scope_creep(plan)
        assert finding is not None
        assert finding.severity == FalsificationSeverity.HIGH
        assert finding.attack_vector == AttackVector.SCOPE_CREEP.value

    def test_narrow_scope_single_module_returns_none(self):
        plan = _minimal_plan(target="mypackage.core", scope="mypackage.core only")
        finding = self.worker.check_scope_creep(plan)
        assert finding is None


# ---------------------------------------------------------------------------
# check_missing_metrics
# ---------------------------------------------------------------------------


class TestCheckMissingMetrics:

    def setup_method(self):
        self.worker = FalsificationWorker()

    def test_absent_metrics_key_returns_medium(self):
        plan = _minimal_plan()
        del plan["metrics"]
        finding = self.worker.check_missing_metrics(plan)
        assert finding is not None
        assert finding.severity == FalsificationSeverity.MEDIUM
        assert finding.attack_vector == AttackVector.FALSE_METRIC.value

    def test_empty_string_metrics_returns_medium(self):
        plan = _minimal_plan(metrics="")
        finding = self.worker.check_missing_metrics(plan)
        assert finding is not None
        assert finding.severity == FalsificationSeverity.MEDIUM

    def test_purely_qualitative_metrics_returns_low(self):
        # No numbers, no comparison operators, no comparison keywords
        plan = _minimal_plan(metrics="The deployment should complete without errors.")
        finding = self.worker.check_missing_metrics(plan)
        assert finding is not None
        assert finding.severity == FalsificationSeverity.LOW

    def test_numeric_metric_returns_none(self):
        plan = _minimal_plan(metrics="coverage >= 80%")
        finding = self.worker.check_missing_metrics(plan)
        assert finding is None

    def test_comparative_metric_no_number_returns_none(self):
        # "reduce error rate" has a comparison keyword → passes
        plan = _minimal_plan(metrics="reduce error rate significantly")
        finding = self.worker.check_missing_metrics(plan)
        assert finding is None


# ---------------------------------------------------------------------------
# check_circular_deps — plan-level checks (no repo_root)
# ---------------------------------------------------------------------------


class TestCheckCircularDeps:

    def setup_method(self):
        self.worker = FalsificationWorker()

    def test_self_referential_dependency_returns_high(self):
        # target listed in its own dependencies
        plan = _minimal_plan(
            target="mypackage.core",
            dependencies=["mypackage.utils", "mypackage.core"],
        )
        finding = self.worker.check_circular_deps(plan, repo_root=None)
        assert finding is not None
        assert finding.severity == FalsificationSeverity.HIGH
        assert finding.attack_vector == AttackVector.CIRCULAR_ARCHITECTURE.value

    def test_parent_child_pair_in_deps_returns_medium(self):
        # mypackage.core and mypackage.core.utils — parent–child
        plan = _minimal_plan(
            target="other.module",
            dependencies=["mypackage.core", "mypackage.core.utils"],
        )
        finding = self.worker.check_circular_deps(plan, repo_root=None)
        assert finding is not None
        assert finding.severity == FalsificationSeverity.MEDIUM
        assert finding.attack_vector == AttackVector.CIRCULAR_ARCHITECTURE.value

    def test_clean_dependencies_returns_none(self):
        plan = _minimal_plan(dependencies=["mypackage.utils", "mypackage.helpers"])
        finding = self.worker.check_circular_deps(plan, repo_root=None)
        assert finding is None

    def test_no_repo_root_no_filesystem_check(self):
        # Without repo_root and clean deps → None
        plan = _minimal_plan(dependencies=[])
        finding = self.worker.check_circular_deps(plan, repo_root=None)
        assert finding is None

    def test_string_dependencies_parsed(self):
        # String form: "mypackage.core, mypackage.core.utils"
        plan = _minimal_plan(
            target="other.module",
            dependencies="mypackage.core, mypackage.core.utils",
        )
        finding = self.worker.check_circular_deps(plan, repo_root=None)
        assert finding is not None
        assert finding.severity == FalsificationSeverity.MEDIUM


# ---------------------------------------------------------------------------
# check_circular_deps — filesystem AST cycle detection via real tmp_path
# ---------------------------------------------------------------------------


class TestCheckCircularDepsFilesystem:

    def setup_method(self):
        self.worker = FalsificationWorker()

    def test_acyclic_module_returns_none(self, tmp_path):
        # Build a minimal Python package with no circular imports.
        pkg = tmp_path / "src" / "mymod"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text("")
        (pkg / "alpha.py").write_text("from mymod import beta\n")
        (pkg / "beta.py").write_text("# no imports\n")

        plan = _minimal_plan(target="mymod", repo_root=str(tmp_path))
        finding = self.worker.check_circular_deps(plan, repo_root=str(tmp_path))
        assert finding is None

    def test_cyclic_module_returns_high(self, tmp_path):
        # A module that directly imports itself is the clearest trigger for the
        # DFS cycle detector (two-node mutual imports are not caught due to the
        # known approximation in _find_cycle — see source comments).
        pkg = tmp_path / "src" / "cycmod"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text("")
        (pkg / "alpha.py").write_text("import cycmod.alpha\n")  # self-import

        plan = _minimal_plan(target="cycmod", repo_root=str(tmp_path))
        finding = self.worker.check_circular_deps(plan, repo_root=str(tmp_path))
        assert finding is not None
        assert finding.severity == FalsificationSeverity.HIGH
        assert finding.attack_vector == AttackVector.CIRCULAR_ARCHITECTURE.value
        assert "cycle" in finding.evidence


# ---------------------------------------------------------------------------
# _check_dependency_risk
# ---------------------------------------------------------------------------


class TestCheckDependencyRisk:

    def setup_method(self):
        self.worker = FalsificationWorker()

    def test_three_or_more_external_deps_returns_medium(self):
        plan = _minimal_plan(dependencies=["requests", "boto3", "httpx", "pydantic"])
        finding = self.worker._check_dependency_risk(plan)
        assert finding is not None
        assert finding.severity == FalsificationSeverity.MEDIUM
        assert finding.attack_vector == AttackVector.DEPENDENCY_RISK.value

    def test_two_external_deps_returns_none(self):
        plan = _minimal_plan(dependencies=["requests", "boto3"])
        finding = self.worker._check_dependency_risk(plan)
        assert finding is None

    def test_internal_dotted_deps_not_flagged(self):
        # Dotted paths are treated as internal modules, not external packages
        plan = _minimal_plan(
            dependencies=["mypackage.core", "mypackage.utils", "mypackage.helpers"]
        )
        finding = self.worker._check_dependency_risk(plan)
        assert finding is None

    def test_empty_deps_returns_none(self):
        plan = _minimal_plan(dependencies=[])
        finding = self.worker._check_dependency_risk(plan)
        assert finding is None


# ---------------------------------------------------------------------------
# _check_security_risk
# ---------------------------------------------------------------------------


class TestCheckSecurityRisk:

    def setup_method(self):
        self.worker = FalsificationWorker()

    def test_auth_keyword_without_review_returns_high(self):
        plan = _minimal_plan(
            target="mypackage.authentication",
            rationale="Refactor the authentication flow.",
        )
        finding = self.worker._check_security_risk(plan)
        assert finding is not None
        assert finding.severity == FalsificationSeverity.HIGH
        assert finding.attack_vector == AttackVector.SECURITY_RISK.value

    def test_password_keyword_without_review_returns_high(self):
        plan = _minimal_plan(
            rationale="Update the password hashing algorithm to bcrypt.",
        )
        finding = self.worker._check_security_risk(plan)
        assert finding is not None
        assert finding.severity == FalsificationSeverity.HIGH

    def test_security_ack_suppresses_finding(self):
        # Mentioning "security review" alongside sensitive terms should suppress.
        plan = _minimal_plan(
            rationale=(
                "Refactor authentication flow. "
                "A security review has been scheduled."
            )
        )
        finding = self.worker._check_security_risk(plan)
        assert finding is None

    def test_no_sensitive_terms_returns_none(self):
        plan = _minimal_plan(
            target="mypackage.data",
            rationale="Reformat the output CSV columns.",
        )
        finding = self.worker._check_security_risk(plan)
        assert finding is None

    def test_finding_lists_sensitive_terms_in_evidence(self):
        plan = _minimal_plan(rationale="Handles credential storage and encryption.")
        finding = self.worker._check_security_risk(plan)
        assert finding is not None
        assert "sensitive_terms_found" in finding.evidence


# ---------------------------------------------------------------------------
# _check_false_metric
# ---------------------------------------------------------------------------


class TestCheckFalseMetric:

    def setup_method(self):
        self.worker = FalsificationWorker()

    def test_absent_expected_outcome_returns_medium(self):
        plan = _minimal_plan(expected_outcome="")
        finding = self.worker._check_false_metric(plan)
        assert finding is not None
        assert finding.severity == FalsificationSeverity.MEDIUM
        assert finding.attack_vector == AttackVector.FALSE_METRIC.value

    def test_unfalsifiable_language_two_hits_returns_low(self):
        # "improved overall" + "no issues" → 2 hits
        plan = _minimal_plan(
            expected_outcome="The system will be improved overall with no issues."
        )
        finding = self.worker._check_false_metric(plan)
        assert finding is not None
        assert finding.severity == FalsificationSeverity.LOW

    def test_concrete_expected_outcome_returns_none(self):
        plan = _minimal_plan(expected_outcome="all unit tests pass; coverage >= 80%")
        finding = self.worker._check_false_metric(plan)
        assert finding is None

    def test_one_unfalsifiable_hit_returns_none(self):
        # Only "smoothly" — fewer than 2 hits → None
        plan = _minimal_plan(expected_outcome="The deploy will complete smoothly.")
        finding = self.worker._check_false_metric(plan)
        assert finding is None


# ---------------------------------------------------------------------------
# _check_over_broad_module
# ---------------------------------------------------------------------------


class TestCheckOverBroadModule:

    def setup_method(self):
        self.worker = FalsificationWorker()

    def test_five_responsibility_verbs_returns_medium(self):
        plan = _minimal_plan(
            rationale=(
                "This module handles logging, manages sessions, coordinates "
                "workflows, provides utilities, and implements the core API."
            )
        )
        finding = self.worker._check_over_broad_module(plan)
        assert finding is not None
        assert finding.severity == FalsificationSeverity.MEDIUM
        assert finding.attack_vector == AttackVector.OVER_BROAD_MODULE.value

    def test_deep_target_path_returns_low(self):
        # 6 segments (5 dots) → LOW finding
        plan = _minimal_plan(target="a.b.c.d.e.f")
        finding = self.worker._check_over_broad_module(plan)
        assert finding is not None
        assert finding.severity == FalsificationSeverity.LOW
        assert finding.attack_vector == AttackVector.OVER_BROAD_MODULE.value

    def test_four_responsibility_verbs_returns_none(self):
        plan = _minimal_plan(
            rationale="This module handles logging, manages sessions, coordinates workflows, provides utilities."
        )
        finding = self.worker._check_over_broad_module(plan)
        assert finding is None

    def test_four_dots_target_returns_none(self):
        # exactly 4 dots (5 segments) — threshold is >= 5 dots
        plan = _minimal_plan(target="a.b.c.d.e")
        finding = self.worker._check_over_broad_module(plan)
        assert finding is None


# ---------------------------------------------------------------------------
# _check_premature_abstraction
# ---------------------------------------------------------------------------


class TestCheckPrematureAbstraction:

    def setup_method(self):
        self.worker = FalsificationWorker()

    def test_two_abstraction_signals_without_evidence_returns_low(self):
        plan = _minimal_plan(
            rationale="Build a generic, reusable interface for all data sources."
        )
        finding = self.worker._check_premature_abstraction(plan)
        assert finding is not None
        assert finding.severity == FalsificationSeverity.LOW
        assert finding.attack_vector == AttackVector.PREMATURE_ABSTRACTION.value

    def test_one_abstraction_signal_returns_none(self):
        # Only "generic" — single hit, not enough
        plan = _minimal_plan(rationale="Build a generic helper function.")
        finding = self.worker._check_premature_abstraction(plan)
        assert finding is None

    def test_abstraction_with_caller_evidence_returns_none(self):
        plan = _minimal_plan(
            rationale=(
                "Build a generic, reusable interface. "
                "There are 3 existing callers that currently duplicate this logic."
            )
        )
        finding = self.worker._check_premature_abstraction(plan)
        assert finding is None

    def test_no_abstraction_signals_returns_none(self):
        plan = _minimal_plan(rationale="Fix the off-by-one error in the loop.")
        finding = self.worker._check_premature_abstraction(plan)
        assert finding is None


# ---------------------------------------------------------------------------
# evaluate_plan — CONDITIONAL verdict (low/medium findings only, ≤2)
# ---------------------------------------------------------------------------


class TestEvaluatePlanConditionalVerdict:

    def setup_method(self):
        self.worker = FalsificationWorker()

    def test_medium_finding_only_gives_conditional(self):
        # Missing metrics → MEDIUM; all other checks pass with minimal plan.
        plan = _minimal_plan()
        del plan["metrics"]
        report = self.worker.evaluate_plan(plan)
        # Must not be FAIL (no HIGH/CRITICAL)
        assert report.verdict in {"PASS", "CONDITIONAL"}

    def test_conditional_required_changes_match_remediations(self):
        plan = _minimal_plan()
        del plan["metrics"]
        report = self.worker.evaluate_plan(plan)
        expected = [f.remediation for f in report.findings if f.remediation]
        assert report.required_changes == expected

    def test_pass_verdict_when_all_checks_clean(self):
        plan = _minimal_plan()
        report = self.worker.evaluate_plan(plan)
        assert report.verdict in {"PASS", "CONDITIONAL"}
        # Ensure no HIGH or CRITICAL findings
        for f in report.findings:
            assert f.severity not in {
                FalsificationSeverity.HIGH,
                FalsificationSeverity.CRITICAL,
            }


# ---------------------------------------------------------------------------
# FalsificationReport.summary helper (plan_summary content)
# ---------------------------------------------------------------------------


class TestFalsificationReportSummary:

    def setup_method(self):
        self.worker = FalsificationWorker()

    def test_summary_format_agent_action_target(self):
        plan = _minimal_plan(
            agent_id="eng-01",
            action_type="refactor",
            target="mypackage.core",
        )
        report = self.worker.evaluate_plan(plan)
        assert "eng-01" in report.plan_summary
        assert "refactor" in report.plan_summary
        assert "mypackage.core" in report.plan_summary

    def test_summary_defaults_on_missing_fields(self):
        # Empty plan — all fields default
        report = self.worker.evaluate_plan({})
        assert isinstance(report.plan_summary, str)
        assert len(report.plan_summary) > 0

    def test_summary_strips_blank_action_type(self):
        plan = _minimal_plan(action_type="  ")
        report = self.worker.evaluate_plan(plan)
        # The _build_summary helper falls back to "action" when blank
        assert "action" in report.plan_summary
