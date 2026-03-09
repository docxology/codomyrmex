"""Tests for skills.arscontexta.models."""

import pytest

from codomyrmex.skills.arscontexta.models import (
    ArsContextaError,
    ConfigDimension,
    DimensionSignal,
    HealthStatus,
    KernelConfig,
    KernelLayer,
    KernelPrimitive,
    PipelineError,
    PipelineStage,
    PrimitiveValidationError,
    ResearchClaim,
    SkillType,
    StageResult,
    VaultConfig,
    VaultHealthReport,
    VaultNotFoundError,
    VaultSpace,
)


class TestVaultSpace:
    def test_all_values(self):
        values = {s.value for s in VaultSpace}
        assert "self" in values
        assert "notes" in values
        assert "ops" in values


class TestKernelLayer:
    def test_all_values(self):
        values = {l.value for l in KernelLayer}
        assert "foundation" in values
        assert "convention" in values
        assert "automation" in values


class TestPipelineStage:
    def test_all_six_stages(self):
        values = {s.value for s in PipelineStage}
        assert "record" in values
        assert "reduce" in values
        assert "reflect" in values
        assert "reweave" in values
        assert "verify" in values
        assert "rethink" in values

    def test_count(self):
        assert len(PipelineStage) == 6


class TestConfigDimension:
    def test_all_eight_dimensions(self):
        values = {d.value for d in ConfigDimension}
        assert "domain" in values
        assert "methodology" in values
        assert "abstraction_level" in values
        assert "temporal_scope" in values
        assert "collaboration_mode" in values
        assert "output_format" in values
        assert "toolchain" in values
        assert "learning_style" in values

    def test_count(self):
        assert len(ConfigDimension) == 8


class TestHealthStatus:
    def test_all_values(self):
        values = {h.value for h in HealthStatus}
        assert "healthy" in values
        assert "warning" in values
        assert "error" in values
        assert "unknown" in values


class TestSkillType:
    def test_all_values(self):
        values = {s.value for s in SkillType}
        assert "plugin" in values
        assert "generated" in values
        assert "hook" in values


class TestKernelPrimitive:
    def test_construction(self):
        kp = KernelPrimitive(
            name="daily_note",
            layer=KernelLayer.FOUNDATION,
            description="Creates a daily note entry.",
        )
        assert kp.name == "daily_note"
        assert kp.layer == KernelLayer.FOUNDATION
        assert kp.description == "Creates a daily note entry."

    def test_defaults(self):
        kp = KernelPrimitive(name="n", layer=KernelLayer.CONVENTION, description="d")
        assert kp.dependencies == []
        assert kp.validation_rule == ""
        assert kp.enabled is True

    def test_to_dict(self):
        kp = KernelPrimitive(
            name="template",
            layer=KernelLayer.AUTOMATION,
            description="Apply template.",
            dependencies=["daily_note"],
        )
        d = kp.to_dict()
        assert d["name"] == "template"
        assert d["layer"] == "automation"
        assert d["dependencies"] == ["daily_note"]
        assert d["enabled"] is True

    def test_independent_default_dependencies(self):
        kp1 = KernelPrimitive(name="a", layer=KernelLayer.FOUNDATION, description="a")
        kp2 = KernelPrimitive(name="b", layer=KernelLayer.FOUNDATION, description="b")
        kp1.dependencies.append("x")
        assert kp2.dependencies == []


class TestResearchClaim:
    def test_construction(self):
        rc = ResearchClaim(
            claim_id="C001",
            statement="Spaced repetition improves retention.",
            source="Ebbinghaus 1885",
            domain="cognitive_science",
        )
        assert rc.claim_id == "C001"
        assert rc.confidence == 0.8

    def test_to_dict(self):
        rc = ResearchClaim(
            claim_id="C002",
            statement="Interleaving increases learning.",
            source="Kornell 2008",
            domain="education",
            confidence=0.9,
        )
        d = rc.to_dict()
        assert d["claim_id"] == "C002"
        assert d["confidence"] == 0.9
        assert d["domain"] == "education"

    def test_independent_default_connected_primitives(self):
        rc1 = ResearchClaim(claim_id="a", statement="s", source="s", domain="d")
        rc2 = ResearchClaim(claim_id="b", statement="s", source="s", domain="d")
        rc1.connected_primitives.append("p1")
        assert rc2.connected_primitives == []


class TestDimensionSignal:
    def test_construction(self):
        ds = DimensionSignal(
            dimension=ConfigDimension.DOMAIN, value="software_engineering"
        )
        assert ds.dimension == ConfigDimension.DOMAIN
        assert ds.value == "software_engineering"
        assert ds.confidence == 0.5

    def test_timestamp_auto_set(self):
        ds = DimensionSignal(dimension=ConfigDimension.TOOLCHAIN, value="obsidian")
        assert ds.timestamp != ""
        assert "T" in ds.timestamp  # ISO format

    def test_to_dict(self):
        ds = DimensionSignal(
            dimension=ConfigDimension.OUTPUT_FORMAT,
            value="markdown",
            confidence=0.9,
            source="user_pref",
        )
        d = ds.to_dict()
        assert d["dimension"] == "output_format"
        assert d["value"] == "markdown"
        assert d["confidence"] == 0.9
        assert d["source"] == "user_pref"
        assert "timestamp" in d


class TestStageResult:
    def test_construction(self):
        sr = StageResult(
            stage=PipelineStage.RECORD,
            input_content="raw input",
            output_content="processed output",
        )
        assert sr.stage == PipelineStage.RECORD
        assert sr.input_content == "raw input"
        assert sr.success is True
        assert sr.error is None

    def test_failed_stage(self):
        sr = StageResult(
            stage=PipelineStage.VERIFY,
            input_content="in",
            output_content="",
            success=False,
            error="Validation failed",
        )
        assert sr.success is False
        assert sr.error == "Validation failed"

    def test_to_dict(self):
        sr = StageResult(
            stage=PipelineStage.REDUCE,
            input_content="long text",
            output_content="short text",
            duration_ms=25.5,
        )
        d = sr.to_dict()
        assert d["stage"] == "reduce"
        assert d["duration_ms"] == 25.5
        assert d["success"] is True
        assert d["error"] is None

    def test_independent_default_metadata(self):
        sr1 = StageResult(
            stage=PipelineStage.REFLECT, input_content="i", output_content="o"
        )
        sr2 = StageResult(
            stage=PipelineStage.REFLECT, input_content="i", output_content="o"
        )
        sr1.metadata["key"] = "val"
        assert sr2.metadata == {}


class TestVaultHealthReport:
    def test_construction(self):
        r = VaultHealthReport(status=HealthStatus.HEALTHY)
        assert r.status == HealthStatus.HEALTHY
        assert r.total_notes == 0
        assert r.orphaned_notes == 0
        assert r.broken_links == 0

    def test_warning_status(self):
        r = VaultHealthReport(
            status=HealthStatus.WARNING,
            warnings=["Missing daily note template."],
        )
        assert len(r.warnings) == 1

    def test_to_dict(self):
        r = VaultHealthReport(
            status=HealthStatus.ERROR,
            total_notes=150,
            orphaned_notes=5,
            broken_links=3,
            errors=["Critical link broken."],
        )
        d = r.to_dict()
        assert d["status"] == "error"
        assert d["total_notes"] == 150
        assert d["orphaned_notes"] == 5
        assert d["broken_links"] == 3
        assert len(d["errors"]) == 1

    def test_independent_default_warnings(self):
        r1 = VaultHealthReport(status=HealthStatus.HEALTHY)
        r2 = VaultHealthReport(status=HealthStatus.HEALTHY)
        r1.warnings.append("w")
        assert r2.warnings == []


class TestKernelConfig:
    def _make_primitive(self, name: str, layer: KernelLayer) -> KernelPrimitive:
        return KernelPrimitive(name=name, layer=layer, description=f"{name} primitive")

    def test_empty_config(self):
        kc = KernelConfig()
        assert kc.primitives == []

    def test_get_by_name_found(self):
        p = self._make_primitive("daily_note", KernelLayer.FOUNDATION)
        kc = KernelConfig(primitives=[p])
        assert kc.get_by_name("daily_note") is p

    def test_get_by_name_not_found(self):
        kc = KernelConfig()
        assert kc.get_by_name("missing") is None

    def test_get_by_layer(self):
        f1 = self._make_primitive("a", KernelLayer.FOUNDATION)
        f2 = self._make_primitive("b", KernelLayer.FOUNDATION)
        c1 = self._make_primitive("c", KernelLayer.CONVENTION)
        kc = KernelConfig(primitives=[f1, f2, c1])
        result = kc.get_by_layer(KernelLayer.FOUNDATION)
        assert len(result) == 2
        assert c1 not in result

    def test_validate_dependencies_all_resolved(self):
        p1 = self._make_primitive("a", KernelLayer.FOUNDATION)
        p2 = KernelPrimitive(
            name="b", layer=KernelLayer.CONVENTION, description="d", dependencies=["a"]
        )
        kc = KernelConfig(primitives=[p1, p2])
        missing = kc.validate_dependencies()
        assert missing == []

    def test_validate_dependencies_missing(self):
        p = KernelPrimitive(
            name="b",
            layer=KernelLayer.CONVENTION,
            description="d",
            dependencies=["missing_dep"],
        )
        kc = KernelConfig(primitives=[p])
        missing = kc.validate_dependencies()
        assert "missing_dep" in missing

    def test_validate_dependencies_empty(self):
        kc = KernelConfig()
        assert kc.validate_dependencies() == []


class TestVaultConfig:
    def test_construction(self, tmp_path):
        vc = VaultConfig(vault_path=tmp_path)
        assert vc.vault_path == tmp_path

    def test_default_active_spaces(self, tmp_path):
        vc = VaultConfig(vault_path=tmp_path)
        spaces = {s.value for s in vc.active_spaces}
        assert "self" in spaces
        assert "notes" in spaces
        assert "ops" in spaces

    def test_created_at_auto_set(self, tmp_path):
        vc = VaultConfig(vault_path=tmp_path)
        assert "T" in vc.created_at  # ISO format

    def test_to_dict(self, tmp_path):
        vc = VaultConfig(vault_path=tmp_path)
        d = vc.to_dict()
        assert "vault_path" in d
        assert "active_spaces" in d
        assert "kernel" in d
        assert "derivation_signals" in d

    def test_to_dict_active_spaces_as_strings(self, tmp_path):
        vc = VaultConfig(vault_path=tmp_path)
        d = vc.to_dict()
        assert all(isinstance(s, str) for s in d["active_spaces"])

    def test_with_signals(self, tmp_path):
        sig = DimensionSignal(dimension=ConfigDimension.DOMAIN, value="ml")
        vc = VaultConfig(vault_path=tmp_path, derivation_signals=[sig])
        d = vc.to_dict()
        assert len(d["derivation_signals"]) == 1


class TestExceptions:
    def test_arscontexta_error_is_exception(self):
        with pytest.raises(ArsContextaError):
            raise ArsContextaError("base error")

    def test_vault_not_found_is_arscontexta(self):
        with pytest.raises(ArsContextaError):
            raise VaultNotFoundError("/no/such/vault")

    def test_primitive_validation_error(self):
        with pytest.raises(PrimitiveValidationError):
            raise PrimitiveValidationError("Bad primitive")

    def test_pipeline_error(self):
        with pytest.raises(ArsContextaError):
            raise PipelineError("Pipeline stage failed")
