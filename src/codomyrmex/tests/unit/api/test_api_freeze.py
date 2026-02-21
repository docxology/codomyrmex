"""Tests for Sprint 39: API Freeze & Migration Guide.

Covers APIContract, ContractValidator, MigrationEngine,
and APISurface analyzer.
"""

import pytest

from codomyrmex.api.api_contract import (
    APIContract,
    APIEndpoint,
    BreakingChangeKind,
    ContractValidator,
)
from codomyrmex.api.migration_engine import MigrationEngine, MigrationPlan
from codomyrmex.api.api_surface import APISurface


# ─── APIContract ──────────────────────────────────────────────────────

class TestAPIContract:

    def test_add_and_freeze(self):
        contract = APIContract(name="test")
        contract.add_endpoint(APIEndpoint(name="search", signature="(query: str)"))
        checksum = contract.freeze()
        assert contract.frozen
        assert len(checksum) > 0

    def test_frozen_blocks_modification(self):
        contract = APIContract()
        contract.freeze()
        with pytest.raises(RuntimeError):
            contract.add_endpoint(APIEndpoint(name="x"))

    def test_checksum_deterministic(self):
        c1 = APIContract()
        c1.add_endpoint(APIEndpoint(name="a", signature="(x)"))
        c2 = APIContract()
        c2.add_endpoint(APIEndpoint(name="a", signature="(x)"))
        assert c1.freeze() == c2.freeze()

    def test_to_dict(self):
        contract = APIContract(name="test")
        contract.add_endpoint(APIEndpoint(name="foo"))
        d = contract.to_dict()
        assert d["name"] == "test"
        assert "foo" in d["endpoints"]


# ─── ContractValidator ───────────────────────────────────────────────

class TestContractValidator:

    def test_compatible(self):
        baseline = APIContract()
        baseline.add_endpoint(APIEndpoint(name="search", signature="(q)"))
        baseline.freeze()

        current = APIContract()
        current.add_endpoint(APIEndpoint(name="search", signature="(q)"))

        validator = ContractValidator(baseline)
        assert validator.is_compatible(current)

    def test_detects_removal(self):
        baseline = APIContract()
        baseline.add_endpoint(APIEndpoint(name="old_fn", signature="()"))
        baseline.freeze()

        current = APIContract()  # old_fn removed

        validator = ContractValidator(baseline)
        changes = validator.validate(current)
        assert len(changes) == 1
        assert changes[0].kind == BreakingChangeKind.REMOVED

    def test_detects_signature_change(self):
        baseline = APIContract()
        baseline.add_endpoint(APIEndpoint(name="fn", signature="(x)"))
        baseline.freeze()

        current = APIContract()
        current.add_endpoint(APIEndpoint(name="fn", signature="(x, y)"))

        validator = ContractValidator(baseline)
        changes = validator.validate(current)
        assert any(c.kind == BreakingChangeKind.SIGNATURE_CHANGED for c in changes)


# ─── MigrationEngine ────────────────────────────────────────────────

class TestMigrationEngine:

    def test_add_steps(self):
        engine = MigrationEngine()
        engine.add_rename("search", "search_code")
        engine.add_removal("deprecated_fn")
        assert engine.total_steps == 2

    def test_generate_plan(self):
        engine = MigrationEngine()
        engine.add_rename("a", "b")
        plan = engine.generate_plan("0.9.0", "1.0.0")
        assert plan.from_version == "0.9.0"
        assert plan.step_count == 1
        assert plan.breaking_count == 1

    def test_safe_plan(self):
        engine = MigrationEngine()
        engine.add_deprecation("old", replacement="new")
        plan = engine.generate_plan("0.9.0", "1.0.0")
        assert plan.is_safe

    def test_markdown_output(self):
        engine = MigrationEngine()
        engine.add_rename("x", "y")
        plan = engine.generate_plan("0.9", "1.0")
        md = engine.to_markdown(plan)
        assert "Migration Guide" in md
        assert "breaking" in md.lower()


# ─── APISurface ──────────────────────────────────────────────────────

class TestAPISurface:

    def test_analyze(self):
        contract = APIContract()
        contract.add_endpoint(APIEndpoint(name="a", module="mod1", signature="()"))
        contract.add_endpoint(APIEndpoint(name="b", module="mod1"))
        contract.add_endpoint(APIEndpoint(name="c", module="mod2", signature="(x)"))
        surface = APISurface(contract)
        report = surface.analyze()
        assert report.total_endpoints == 3
        assert report.modules == 2

    def test_frozen_percentage(self):
        contract = APIContract()
        contract.add_endpoint(APIEndpoint(name="a"))
        contract.add_endpoint(APIEndpoint(name="b"))
        contract.freeze()
        surface = APISurface(contract)
        assert surface.frozen_percentage() == pytest.approx(1.0)

    def test_unfrozen_endpoints(self):
        contract = APIContract()
        contract.add_endpoint(APIEndpoint(name="a"))
        contract.add_endpoint(APIEndpoint(name="b", frozen=True))
        surface = APISurface(contract)
        unfrozen = surface.unfrozen_endpoints()
        assert "a" in unfrozen
        assert "b" not in unfrozen
