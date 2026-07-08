"""Unit tests for colony_kernel.config_loader.

Zero-mock policy: no MagicMock, no unittest.mock.
All tests use real files written to tmp_path and real YAML content.

The public surface under test:
  load_kernel_yaml()            — reads kernel.yaml from resolved config dir
  load_roles_yaml()             — reads roles.yaml
  load_decay_yaml()             — reads decay_rates.yaml
  default_budget_from_yaml()    — builds ResourceBudget from budget section
  default_gate_config_from_yaml() — returns gate section dict
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest

from codomyrmex.colony_kernel import config_loader as _cl
from codomyrmex.colony_kernel.resource_ledger import ResourceBudget

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write_yaml(directory: Path, filename: str, content: str) -> Path:
    """Write *content* to *directory/filename* and return the path."""
    path = directory / filename
    path.write_text(content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# load_kernel_yaml
# ---------------------------------------------------------------------------


class TestLoadKernelYaml:
    """Tests for load_kernel_yaml() using CODOMYRMEX_COLONY_CONFIG env override."""

    def test_valid_yaml_returns_expected_dict(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A well-formed kernel.yaml is parsed into a nested dict."""
        _write_yaml(
            tmp_path,
            "kernel.yaml",
            """\
budget:
  max_llm_calls: 200
  max_runtime_seconds: 1800.0
gate:
  score_execute: 0.60
  score_hold: 0.35
""",
        )
        monkeypatch.setenv("CODOMYRMEX_COLONY_CONFIG", str(tmp_path))

        result = _cl.load_kernel_yaml()

        assert isinstance(result, dict)
        assert result["budget"]["max_llm_calls"] == 200
        assert result["budget"]["max_runtime_seconds"] == pytest.approx(1800.0)
        assert result["gate"]["score_execute"] == pytest.approx(0.60)
        assert result["gate"]["score_hold"] == pytest.approx(0.35)

    def test_non_existent_path_returns_empty_dict(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When kernel.yaml is absent the loader returns {} without raising."""
        absent_dir = tmp_path / "no_such_dir"
        monkeypatch.setenv("CODOMYRMEX_COLONY_CONFIG", str(absent_dir))

        result = _cl.load_kernel_yaml()

        assert result == {}

    def test_malformed_yaml_returns_empty_dict(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Malformed YAML content causes a graceful fallback to {} and emits a warning."""
        _write_yaml(
            tmp_path,
            "kernel.yaml",
            """\
budget: {
  max_llm_calls: [unclosed list
  bad_indent:   key: value
""",
        )
        monkeypatch.setenv("CODOMYRMEX_COLONY_CONFIG", str(tmp_path))

        with pytest.warns(
            UserWarning, match="Failed to load colony_kernel config file"
        ):
            result = _cl.load_kernel_yaml()

        assert result == {}


# ---------------------------------------------------------------------------
# load_roles_yaml
# ---------------------------------------------------------------------------


class TestLoadRolesYaml:
    """Tests for load_roles_yaml()."""

    def test_valid_roles_yaml_returns_expected_dict(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A well-formed roles.yaml is parsed into the expected structure."""
        _write_yaml(
            tmp_path,
            "roles.yaml",
            """\
sandbox:
  max_proposals: 0
repair_ant:
  min_trust: 0.20
dispatcher:
  min_trust: 0.50
min_proposals_for_promotion: 3
""",
        )
        monkeypatch.setenv("CODOMYRMEX_COLONY_CONFIG", str(tmp_path))

        result = _cl.load_roles_yaml()

        assert isinstance(result, dict)
        assert result["sandbox"]["max_proposals"] == 0
        assert result["repair_ant"]["min_trust"] == pytest.approx(0.20)
        assert result["dispatcher"]["min_trust"] == pytest.approx(0.50)
        assert result["min_proposals_for_promotion"] == 3

    def test_missing_roles_yaml_returns_empty_dict(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Absent roles.yaml returns {} without raising."""
        monkeypatch.setenv("CODOMYRMEX_COLONY_CONFIG", str(tmp_path))

        result = _cl.load_roles_yaml()

        assert result == {}


# ---------------------------------------------------------------------------
# load_decay_yaml
# ---------------------------------------------------------------------------


class TestLoadDecayYaml:
    """Tests for load_decay_yaml()."""

    def test_valid_decay_rates_yaml_returns_expected_dict(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A well-formed decay_rates.yaml is parsed with correct float values."""
        _write_yaml(
            tmp_path,
            "decay_rates.yaml",
            """\
fast: 0.30
normal: 0.10
slow: 0.03
permanent: 0.0
""",
        )
        monkeypatch.setenv("CODOMYRMEX_COLONY_CONFIG", str(tmp_path))

        result = _cl.load_decay_yaml()

        assert isinstance(result, dict)
        assert result["fast"] == pytest.approx(0.30)
        assert result["normal"] == pytest.approx(0.10)
        assert result["slow"] == pytest.approx(0.03)
        assert result["permanent"] == pytest.approx(0.0)

    def test_missing_decay_yaml_returns_empty_dict(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Absent decay_rates.yaml returns {} without raising."""
        monkeypatch.setenv("CODOMYRMEX_COLONY_CONFIG", str(tmp_path))

        result = _cl.load_decay_yaml()

        assert result == {}


# ---------------------------------------------------------------------------
# default_budget_from_yaml
# ---------------------------------------------------------------------------


class TestDefaultBudgetFromYaml:
    """Tests for default_budget_from_yaml()."""

    def test_valid_budget_section_returns_resource_budget_with_those_values(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When kernel.yaml has a budget section the returned ResourceBudget reflects it."""
        _write_yaml(
            tmp_path,
            "kernel.yaml",
            """\
budget:
  max_llm_calls: 150
  max_runtime_seconds: 900.0
  max_risk_level: 0.6
  max_human_attention_minutes: 45.0
  max_merge_risk: 0.5
  max_doc_debt: 300.0
  max_security_exposure: 0.3
  period_seconds: 21600.0
""",
        )
        monkeypatch.setenv("CODOMYRMEX_COLONY_CONFIG", str(tmp_path))

        budget = _cl.default_budget_from_yaml()

        assert isinstance(budget, ResourceBudget)
        assert budget.max_llm_calls == 150
        assert budget.max_runtime_seconds == pytest.approx(900.0)
        assert budget.max_risk_level == pytest.approx(0.6)
        assert budget.max_human_attention_minutes == pytest.approx(45.0)
        assert budget.max_merge_risk == pytest.approx(0.5)
        assert budget.max_doc_debt == pytest.approx(300.0)
        assert budget.max_security_exposure == pytest.approx(0.3)
        assert budget.period_seconds == pytest.approx(21600.0)

    def test_empty_dict_returns_default_resource_budget(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When config dir is empty (no kernel.yaml), returns ResourceBudget() with all defaults."""
        monkeypatch.setenv("CODOMYRMEX_COLONY_CONFIG", str(tmp_path))

        budget = _cl.default_budget_from_yaml()

        assert isinstance(budget, ResourceBudget)
        default = ResourceBudget()
        assert budget.max_llm_calls == default.max_llm_calls
        assert budget.max_runtime_seconds == pytest.approx(default.max_runtime_seconds)
        assert budget.max_risk_level == pytest.approx(default.max_risk_level)
        assert budget.period_seconds == pytest.approx(default.period_seconds)

    def test_kernel_yaml_without_budget_key_returns_default_resource_budget(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A kernel.yaml that has no 'budget' section returns ResourceBudget() defaults."""
        _write_yaml(
            tmp_path,
            "kernel.yaml",
            """\
gate:
  score_execute: 0.55
""",
        )
        monkeypatch.setenv("CODOMYRMEX_COLONY_CONFIG", str(tmp_path))

        budget = _cl.default_budget_from_yaml()

        assert isinstance(budget, ResourceBudget)
        assert budget.max_llm_calls == ResourceBudget().max_llm_calls


# ---------------------------------------------------------------------------
# default_gate_config_from_yaml
# ---------------------------------------------------------------------------


class TestDefaultGateConfigFromYaml:
    """Tests for default_gate_config_from_yaml()."""

    def test_valid_gate_section_returns_dict_with_expected_keys(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A kernel.yaml with a gate section is returned as a plain dict."""
        _write_yaml(
            tmp_path,
            "kernel.yaml",
            """\
gate:
  score_execute: 0.60
  score_hold: 0.35
budget:
  max_llm_calls: 100
""",
        )
        monkeypatch.setenv("CODOMYRMEX_COLONY_CONFIG", str(tmp_path))

        gate_cfg = _cl.default_gate_config_from_yaml()

        assert isinstance(gate_cfg, dict)
        assert "score_execute" in gate_cfg
        assert "score_hold" in gate_cfg
        assert gate_cfg["score_execute"] == pytest.approx(0.60)
        assert gate_cfg["score_hold"] == pytest.approx(0.35)

    def test_missing_gate_section_returns_empty_dict(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A kernel.yaml without a gate section returns {}."""
        _write_yaml(
            tmp_path,
            "kernel.yaml",
            """\
budget:
  max_llm_calls: 100
""",
        )
        monkeypatch.setenv("CODOMYRMEX_COLONY_CONFIG", str(tmp_path))

        gate_cfg = _cl.default_gate_config_from_yaml()

        assert gate_cfg == {}

    def test_absent_kernel_yaml_returns_empty_gate_dict(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """When kernel.yaml is absent the gate config is {} (no exception)."""
        monkeypatch.setenv("CODOMYRMEX_COLONY_CONFIG", str(tmp_path))

        gate_cfg = _cl.default_gate_config_from_yaml()

        assert gate_cfg == {}
