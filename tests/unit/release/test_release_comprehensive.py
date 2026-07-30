"""Real-artifact and fail-closed tests for :mod:`codomyrmex.release`."""

from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from codomyrmex.release import (
    BuildArtifact,
    BuildReport,
    CertificationCheck,
    CertificationStatus,
    DistributionManager,
    DistributionTarget,
    PackageBuilder,
    PackageMetadata,
    PreflightResult,
    PublicationArtifact,
    PublicationBundle,
    PublicationManifest,
    PublicationMetadata,
    PublicationPlan,
    PublicationVerification,
    PublishResult,
    ReleaseCertification,
    ReleasePolicy,
    ReleaseValidator,
    plan_publication,
    prepare_publication_bundle,
    verify_publication_bundle,
)


def _complete_validator(*, version: str = "1.2.3") -> ReleaseValidator:
    validator = ReleaseValidator(version=version)
    validator.check_tests(failures=0, total=100)
    validator.check_coverage(overall=60.0)
    validator.check_type_safety(errors=0)
    validator.check_security(cve_count=0, secrets_found=0)
    validator.check_documentation(complete=True)
    validator.check_artifacts(verified=True, artifact_count=2)
    return validator


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.unit
class TestPublicSurface:
    def test_exports_are_importable(self):
        exports = (
            BuildArtifact,
            BuildReport,
            CertificationCheck,
            CertificationStatus,
            DistributionManager,
            DistributionTarget,
            PackageBuilder,
            PackageMetadata,
            PreflightResult,
            PublicationArtifact,
            PublicationBundle,
            PublicationManifest,
            PublicationMetadata,
            PublicationPlan,
            PublicationVerification,
            PublishResult,
            ReleaseCertification,
            ReleasePolicy,
            ReleaseValidator,
            plan_publication,
            prepare_publication_bundle,
            verify_publication_bundle,
        )
        assert all(item is not None for item in exports)

    def test_publication_metadata_is_immutable(self):
        metadata = PublicationMetadata(
            title="Report",
            version="1.0.0",
            authors=("Researcher",),
        )
        with pytest.raises(FrozenInstanceError):
            setattr(metadata, "title", "Mutated")  # noqa: B010

    def test_release_policy_defaults_to_strict(self):
        policy = ReleasePolicy()
        assert policy.strict is True
        assert set(policy.required_categories) == {
            "testing",
            "coverage",
            "typing",
            "security",
            "documentation",
            "artifacts",
        }


@pytest.mark.unit
class TestReleaseValidator:
    def test_no_evidence_fails_closed(self):
        certification = ReleaseValidator().certify()
        assert certification.certified is False
        assert len(certification.blockers) == 6
        assert all(
            "Missing required evidence" in item for item in certification.blockers
        )

    def test_complete_evidence_certifies(self):
        certification = _complete_validator().certify()
        assert certification.certified is True
        assert certification.pass_rate == pytest.approx(1.0)
        assert certification.certified_at > 0

    @pytest.mark.parametrize(
        ("method", "kwargs"),
        [
            ("check_tests", {"failures": 1, "total": 100}),
            ("check_coverage", {"overall": 59.9}),
            ("check_type_safety", {"errors": 1}),
            ("check_security", {"cve_count": 1, "secrets_found": 0}),
            ("check_documentation", {"complete": False}),
            ("check_artifacts", {"verified": False, "artifact_count": 2}),
        ],
    )
    def test_each_strict_gate_can_block(self, method, kwargs):
        validator = _complete_validator()
        getattr(validator, method)(**kwargs)
        certification = validator.certify()
        assert certification.certified is False

    def test_zero_test_total_is_not_evidence(self):
        validator = ReleaseValidator()
        check = validator.check_tests(failures=0, total=0)
        assert check.status is CertificationStatus.FAIL

    def test_relaxed_policy_preserves_warning_compatibility(self):
        validator = ReleaseValidator(
            policy=ReleasePolicy(strict=False),
        )
        validator.check_tests(failures=0, total=1)
        validator.check_coverage(overall=60)
        validator.check_type_safety(errors=2)
        validator.check_security(cve_count=0, secrets_found=0)
        validator.check_documentation(complete=False)
        validator.check_artifacts(verified=True, artifact_count=2)
        certification = validator.certify()
        assert certification.certified is True
        assert any(
            check.status is CertificationStatus.WARN for check in certification.checks
        )

    def test_markdown_includes_missing_evidence(self):
        validator = ReleaseValidator(version="2.0.0")
        certification = validator.certify()
        markdown = validator.to_markdown(certification)
        assert "NOT CERTIFIED" in markdown
        assert "Missing required evidence: testing" in markdown


@pytest.mark.unit
class TestPackageBuilder:
    def test_real_uv_build_produces_wheel_and_sdist(self, real_package):
        assert real_package.report.success is True
        assert {item.format for item in real_package.report.artifacts} == {
            "sdist",
            "wheel",
        }

    def test_real_artifact_receipts_are_complete(self, real_package):
        for artifact in real_package.report.artifacts:
            assert artifact.path.is_file()
            assert artifact.path.stat().st_size == artifact.size_bytes
            assert len(artifact.sha256) == 64
            assert len(artifact.sha512) == 128
            assert artifact.checksum == artifact.sha256
            assert _sha256(artifact.path) == artifact.sha256

    def test_build_receipt_records_real_command(self, real_package):
        assert real_package.report.command[0] == "uv"
        assert real_package.report.command[1] == "build"
        assert "--out-dir" in real_package.report.command

    def test_invalid_metadata_never_invokes_a_successful_build(self, tmp_path):
        report = PackageBuilder(
            PackageMetadata(name="", version=""),
            source_dir=tmp_path,
        ).build()
        assert report.success is False
        assert report.artifacts == ()
        assert report.warnings

    def test_metadata_mismatch_fails(self, real_package, tmp_path):
        report = PackageBuilder(
            PackageMetadata(name="different-name", version="9.9.9"),
            source_dir=real_package.root,
            output_dir=tmp_path / "dist",
        ).build()
        assert report.success is False
        assert any("built Name" in warning for warning in report.warnings)

    def test_unsafe_archive_members_fail_closed(self, tmp_path):
        root = tmp_path / "unsafe-package"
        package = root / "src" / "unsafe_fixture"
        package.mkdir(parents=True)
        (package / "__init__.py").write_text("VALUE = 1\n", encoding="utf-8")
        (package / ".git").write_text(
            "gitdir: /Users/example/private-checkout/.git/modules/unsafe\n",
            encoding="utf-8",
        )
        (package / "build-receipt.txt").write_text(
            f"source={root}\n",
            encoding="utf-8",
        )
        (root / "README.md").write_text("# Unsafe fixture\n", encoding="utf-8")
        (root / "pyproject.toml").write_text(
            """[build-system]
requires = ["uv_build>=0.9,<1"]
build-backend = "uv_build"

[project]
name = "unsafe-fixture"
version = "1.0.0"
description = "Unsafe release fixture"
readme = "README.md"
requires-python = ">=3.11"

[tool.uv.build-backend]
module-root = "src"
source-include = ["src/unsafe_fixture/**"]
""",
            encoding="utf-8",
        )

        report = PackageBuilder(
            PackageMetadata(name="unsafe-fixture", version="1.0.0"),
            source_dir=root,
            output_dir=tmp_path / "dist",
        ).build()

        assert report.success is False
        assert report.artifacts == ()
        assert any(
            "unsafe archive members" in warning and ".git" in warning
            for warning in report.warnings
        )
        assert any(
            "local path content in archive members" in warning
            and "build-receipt.txt" in warning
            for warning in report.warnings
        )


@pytest.mark.unit
class TestDistributionManager:
    def test_preflight_verifies_files_and_hashes(self, real_package):
        result = DistributionManager(real_package.report).preflight(
            DistributionTarget.LOCAL
        )
        assert result.ready is True
        assert result.checks_passed == result.checks_total == 4

    def test_preflight_rejects_tampered_receipt(self, real_package):
        artifact = real_package.report.artifacts[0]
        invalid = replace(artifact, sha256="0" * 64)
        report = replace(
            real_package.report,
            artifacts=(invalid, *real_package.report.artifacts[1:]),
        )
        result = DistributionManager(report).preflight(DistributionTarget.LOCAL)
        assert result.ready is False
        assert any("digest" in issue for issue in result.issues)

    @pytest.mark.parametrize(
        "target",
        [
            DistributionTarget.PYPI,
            DistributionTarget.TEST_PYPI,
            DistributionTarget.GITHUB,
        ],
    )
    def test_remote_targets_default_to_dry_run(self, real_package, target):
        result = DistributionManager(real_package.report).publish(target)
        assert result.success is True
        assert result.dry_run is True
        assert result.executed is False
        assert result.artifacts_published == 0
        assert result.receipt["action"] == "remote-dry-run"

    def test_remote_execution_is_rejected(self, real_package):
        result = DistributionManager(real_package.report).publish(
            DistributionTarget.PYPI,
            dry_run=False,
        )
        assert result.success is False
        assert result.executed is False
        assert "disabled" in result.error

    def test_local_distribution_is_a_verified_copy(self, real_package, tmp_path):
        destination = tmp_path / "published"
        manager = DistributionManager(real_package.report)
        result = manager.publish(
            DistributionTarget.LOCAL,
            destination=destination,
        )
        assert result.success is True
        assert result.executed is True
        assert result.dry_run is False
        assert result.artifacts_published == 2
        for artifact in real_package.report.artifacts:
            assert _sha256(destination / artifact.filename) == artifact.sha256
        assert manager.publish_history() == [result]

    def test_local_execution_requires_destination(self, real_package):
        result = DistributionManager(real_package.report).publish(
            DistributionTarget.LOCAL
        )
        assert result.success is False
        assert "destination" in result.error


@pytest.mark.unit
class TestPublicationBundle:
    def test_bundle_verifies(self, publication_bundle):
        result = verify_publication_bundle(publication_bundle)
        assert result.valid is True
        assert result.errors == ()
        assert len(result.verified_artifacts) >= 8

    def test_manifest_is_portable_and_detached(self, publication_bundle):
        raw = json.loads(publication_bundle.manifest_path.read_text(encoding="utf-8"))
        assert raw["schema_version"] == "1"
        assert str(Path.home()) not in json.dumps(raw)
        assert all(not Path(item["path"]).is_absolute() for item in raw["artifacts"])
        roles = {item["role"] for item in raw["artifacts"]}
        assert {
            "content-pdf",
            "distribution-pdf",
            "semantic-html",
            "citation-metadata",
            "zenodo-metadata",
        } <= roles
        assert all(
            item["path"] != "publication_manifest.json" for item in raw["artifacts"]
        )

    def test_unassigned_doi_is_not_invented(self, publication_bundle):
        citation = (publication_bundle.root / "CITATION.cff").read_text(
            encoding="utf-8"
        )
        zenodo = json.loads(
            (publication_bundle.root / ".zenodo.json").read_text(encoding="utf-8")
        )
        assert "\ndoi:" not in citation
        assert "doi" not in zenodo["metadata"]

    def test_tamper_detection(self, publication_bundle, tmp_path):
        copied = tmp_path / "tampered"
        shutil.copytree(publication_bundle.root, copied)
        report = next(copied.glob("*.html"))
        report.write_text("tampered\n", encoding="utf-8")
        result = verify_publication_bundle(copied)
        assert result.valid is False
        assert any("mismatch" in error.lower() for error in result.errors)

    def test_remote_plan_is_dry_run_and_receipted(self, publication_bundle):
        plan = plan_publication(
            publication_bundle,
            target="zenodo-sandbox",
        )
        receipt = json.loads(plan.receipt_path.read_text(encoding="utf-8"))
        assert plan.executed is False
        assert plan.dry_run is True
        assert receipt["executed"] is False
        assert receipt["dry_run"] is True
        assert receipt["receipt_sha256"] == plan.receipt_sha256

    def test_remote_plan_rejects_execution(self, publication_bundle):
        with pytest.raises(ValueError, match="dry_run=True"):
            plan_publication(
                publication_bundle,
                target="github",
                dry_run=False,
            )

    def test_plan_does_not_mutate_manifested_artifacts(self, publication_bundle):
        before = {
            item.path: _sha256(publication_bundle.root / item.path)
            for item in publication_bundle.manifest.artifacts
        }
        plan_publication(publication_bundle, target="github")
        after = {
            item.path: _sha256(publication_bundle.root / item.path)
            for item in publication_bundle.manifest.artifacts
        }
        assert after == before
