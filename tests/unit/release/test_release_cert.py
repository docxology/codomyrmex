"""Focused compatibility tests for release certification entry points."""

from __future__ import annotations

from codomyrmex.release import (
    DistributionManager,
    DistributionTarget,
    ReleaseValidator,
)


def test_strict_certification_passes_with_all_required_evidence(real_package):
    validator = ReleaseValidator(version=real_package.metadata.version)
    validator.check_tests(failures=0, total=100)
    validator.check_coverage(overall=60)
    validator.check_type_safety(errors=0)
    validator.check_security(cve_count=0, secrets_found=0)
    validator.check_documentation(complete=True)
    validator.check_artifacts(
        verified=True,
        artifact_count=len(real_package.report.artifacts),
    )
    certification = validator.certify()
    assert certification.certified
    assert certification.pass_rate == 1.0


def test_certification_fails_when_artifact_evidence_is_absent():
    validator = ReleaseValidator()
    validator.check_tests(failures=0, total=100)
    validator.check_coverage(overall=60)
    validator.check_type_safety(errors=0)
    validator.check_security(cve_count=0, secrets_found=0)
    validator.check_documentation(complete=True)
    certification = validator.certify()
    assert not certification.certified
    assert "Missing required evidence: artifacts" in certification.blockers


def test_local_distribution_copies_real_build(real_package, tmp_path):
    result = DistributionManager(real_package.report).publish(
        DistributionTarget.LOCAL,
        destination=tmp_path / "published",
    )
    assert result.success
    assert result.executed
    assert not result.dry_run


def test_github_distribution_is_only_a_plan(real_package):
    result = DistributionManager(real_package.report).publish(DistributionTarget.GITHUB)
    assert result.success
    assert result.dry_run
    assert not result.executed
