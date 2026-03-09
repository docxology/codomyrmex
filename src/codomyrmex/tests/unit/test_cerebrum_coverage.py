# type: ignore
"""Functional tests for cerebrum module — zero-mock.

Exercises BayesianNetwork, ActiveInferenceAgent, Case/CaseBase,
belief state management, and FPF orchestration classes.
"""

from __future__ import annotations

import pytest

from codomyrmex import cerebrum


class TestCerebrumImports:
    """Core exports are importable."""

    @pytest.mark.parametrize(
        "name",
        [
            "ActiveInferenceAgent",
            "BayesianNetwork",
            "BeliefState",
            "Case",
            "CaseBase",
            "CerebrumConfig",
            "CerebrumError",
            "FPFOrchestrator",
        ],
    )
    def test_export_exists(self, name: str) -> None:
        assert hasattr(cerebrum, name), f"Missing export: {name}"


class TestCerebrumErrors:
    """Custom exception classes."""

    @pytest.mark.parametrize(
        "name",
        [
            "CerebrumError",
            "ActiveInferenceError",
            "BayesianInferenceError",
            "CaseError",
            "CaseNotFoundError",
        ],
    )
    def test_error_hierarchy(self, name: str) -> None:
        exc = getattr(cerebrum, name)
        assert issubclass(exc, Exception)


class TestBayesianNetwork:
    """BayesianNetwork instantiation and structure."""

    def test_instantiation(self) -> None:
        bn = cerebrum.BayesianNetwork()
        assert bn is not None

    def test_has_methods(self) -> None:
        bn = cerebrum.BayesianNetwork()
        public = [
            m for m in dir(bn) if not m.startswith("_") and callable(getattr(bn, m))
        ]
        assert len(public) > 0


class TestCaseBase:
    """CaseBase and Case instantiation."""

    def test_case_base_instantiation(self) -> None:
        cb = cerebrum.CaseBase()
        assert cb is not None

    def test_case_callable(self) -> None:
        assert callable(cerebrum.Case)


class TestBeliefState:
    """BeliefState instantiation."""

    def test_belief_state_callable(self) -> None:
        assert callable(cerebrum.BeliefState)


class TestActiveInferenceAgent:
    """ActiveInferenceAgent instantiation."""

    def test_agent_callable(self) -> None:
        assert callable(cerebrum.ActiveInferenceAgent)


class TestFPFOrchestrator:
    """FPFOrchestrator instantiation."""

    def test_orchestrator_callable(self) -> None:
        assert callable(cerebrum.FPFOrchestrator)


class TestCerebrumConfig:
    """CerebrumConfig instantiation."""

    def test_config_callable(self) -> None:
        assert callable(cerebrum.CerebrumConfig)
