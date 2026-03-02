"""Comprehensive unit tests for the release module.

Covers:
- ReleaseValidator: check methods, certify(), to_markdown()
- ReleaseCertification: properties (pass_rate, total_checks, passed_checks)
- CertificationCheck: dataclass fields
- CertificationStatus: enum values
- PackageBuilder: validate_metadata(), build()
- PackageMetadata: dataclass defaults and fields
- BuildArtifact / BuildReport: structure
- DistributionManager: preflight(), publish(), publish_history()
- DistributionTarget: enum values
- Module __init__.py: all exports accessible

Zero-Mock Policy: all tests use real implementations only.
"""

import time

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
    PublishResult,
    ReleaseCertification,
    ReleaseValidator,
)

# ---------------------------------------------------------------------------
# Tests: Module imports
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestReleaseImports:
    """Verify all __all__ exports are importable."""

    def test_all_classes_importable(self):
        for cls in (
            ReleaseValidator, ReleaseCertification, CertificationCheck, CertificationStatus,
            PackageBuilder, PackageMetadata, BuildArtifact, BuildReport,
            DistributionManager, DistributionTarget, PreflightResult, PublishResult,
        ):
            assert cls is not None

    def test_certification_status_has_correct_values(self):
        assert CertificationStatus.PASS.value == "pass"
        assert CertificationStatus.FAIL.value == "fail"
        assert CertificationStatus.SKIP.value == "skip"
        assert CertificationStatus.WARN.value == "warn"

    def test_distribution_target_has_pypi(self):
        assert DistributionTarget.PYPI.value == "pypi"

    def test_distribution_target_has_test_pypi(self):
        assert DistributionTarget.TEST_PYPI.value == "test_pypi"

    def test_distribution_target_has_github(self):
        assert DistributionTarget.GITHUB.value == "github"

    def test_distribution_target_has_local(self):
        assert DistributionTarget.LOCAL.value == "local"


# ---------------------------------------------------------------------------
# Tests: CertificationCheck dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestCertificationCheck:
    """CertificationCheck dataclass fields and defaults."""

    def test_instantiation_name_only(self):
        check = CertificationCheck(name="Tests")
        assert check.name == "Tests"

    def test_default_status_is_skip(self):
        check = CertificationCheck(name="X")
        assert check.status == CertificationStatus.SKIP

    def test_set_all_fields(self):
        check = CertificationCheck(
            name="Coverage",
            category="quality",
            status=CertificationStatus.PASS,
            value="85%",
            threshold="68%",
            message="Coverage met",
        )
        assert check.name == "Coverage"
        assert check.category == "quality"
        assert check.status == CertificationStatus.PASS
        assert check.value == "85%"
        assert check.threshold == "68%"
        assert check.message == "Coverage met"


# ---------------------------------------------------------------------------
# Tests: ReleaseCertification dataclass
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestReleaseCertification:
    """ReleaseCertification properties."""

    def test_total_checks_empty(self):
        cert = ReleaseCertification(version="1.0.0")
        assert cert.total_checks == 0

    def test_passed_checks_empty(self):
        cert = ReleaseCertification(version="1.0.0")
        assert cert.passed_checks == 0

    def test_pass_rate_empty_is_zero(self):
        cert = ReleaseCertification(version="1.0.0")
        assert cert.pass_rate == 0.0

    def test_total_checks_with_items(self):
        checks = [
            CertificationCheck("A", status=CertificationStatus.PASS),
            CertificationCheck("B", status=CertificationStatus.FAIL),
        ]
        cert = ReleaseCertification(version="1.0.0", checks=checks)
        assert cert.total_checks == 2

    def test_passed_checks_counts_only_pass(self):
        checks = [
            CertificationCheck("A", status=CertificationStatus.PASS),
            CertificationCheck("B", status=CertificationStatus.FAIL),
            CertificationCheck("C", status=CertificationStatus.WARN),
        ]
        cert = ReleaseCertification(version="1.0.0", checks=checks)
        assert cert.passed_checks == 1

    def test_pass_rate_calculation(self):
        checks = [
            CertificationCheck("A", status=CertificationStatus.PASS),
            CertificationCheck("B", status=CertificationStatus.PASS),
            CertificationCheck("C", status=CertificationStatus.FAIL),
            CertificationCheck("D", status=CertificationStatus.FAIL),
        ]
        cert = ReleaseCertification(version="2.0.0", checks=checks)
        assert cert.pass_rate == pytest.approx(0.5)

    def test_version_stored(self):
        cert = ReleaseCertification(version="3.1.4")
        assert cert.version == "3.1.4"

    def test_certified_false_by_default(self):
        cert = ReleaseCertification(version="1.0.0")
        assert cert.certified is False


# ---------------------------------------------------------------------------
# Tests: ReleaseValidator
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestReleaseValidatorBasics:
    """ReleaseValidator instantiation and basic methods."""

    def test_instantiation_default_version(self):
        validator = ReleaseValidator()
        assert validator is not None

    def test_instantiation_custom_version(self):
        validator = ReleaseValidator(version="2.5.0")
        assert validator is not None

    def test_initial_check_count_zero(self):
        validator = ReleaseValidator()
        assert validator.check_count == 0

    def test_check_tests_pass(self):
        validator = ReleaseValidator()
        check = validator.check_tests(failures=0, total=5000)
        assert check.status == CertificationStatus.PASS

    def test_check_tests_fail_on_failures(self):
        validator = ReleaseValidator()
        check = validator.check_tests(failures=3, total=5000)
        assert check.status == CertificationStatus.FAIL

    def test_check_tests_increments_count(self):
        validator = ReleaseValidator()
        validator.check_tests(failures=0, total=1000)
        assert validator.check_count == 1

    def test_check_coverage_pass_above_threshold(self):
        validator = ReleaseValidator()
        check = validator.check_coverage(overall=80.0)
        assert check.status == CertificationStatus.PASS

    def test_check_coverage_fail_below_threshold(self):
        validator = ReleaseValidator()
        check = validator.check_coverage(overall=40.0)
        assert check.status == CertificationStatus.FAIL

    def test_check_coverage_with_tier1(self):
        validator = ReleaseValidator()
        check = validator.check_coverage(overall=70.0, tier1=85.0)
        assert check.status == CertificationStatus.PASS

    def test_check_coverage_fail_tier1_below(self):
        validator = ReleaseValidator()
        check = validator.check_coverage(overall=70.0, tier1=75.0)
        assert check.status == CertificationStatus.FAIL

    def test_check_type_safety_pass_zero_errors(self):
        validator = ReleaseValidator()
        check = validator.check_type_safety(errors=0)
        assert check.status == CertificationStatus.PASS

    def test_check_type_safety_warn_on_errors(self):
        validator = ReleaseValidator()
        check = validator.check_type_safety(errors=10)
        assert check.status == CertificationStatus.WARN

    def test_check_security_pass(self):
        validator = ReleaseValidator()
        check = validator.check_security(cve_count=0, secrets_found=0)
        assert check.status == CertificationStatus.PASS

    def test_check_security_fail_on_cves(self):
        validator = ReleaseValidator()
        check = validator.check_security(cve_count=1, secrets_found=0)
        assert check.status == CertificationStatus.FAIL

    def test_check_security_fail_on_secrets(self):
        validator = ReleaseValidator()
        check = validator.check_security(cve_count=0, secrets_found=1)
        assert check.status == CertificationStatus.FAIL

    def test_check_documentation_pass(self):
        validator = ReleaseValidator()
        check = validator.check_documentation(complete=True)
        assert check.status == CertificationStatus.PASS

    def test_check_documentation_warn_incomplete(self):
        validator = ReleaseValidator()
        check = validator.check_documentation(complete=False)
        assert check.status == CertificationStatus.WARN


@pytest.mark.unit
class TestReleaseValidatorCertify:
    """certify() and custom checks."""

    def test_certify_returns_release_certification(self):
        validator = ReleaseValidator(version="1.0.0")
        cert = validator.certify()
        assert isinstance(cert, ReleaseCertification)

    def test_certify_no_checks_is_certified(self):
        """No failing checks → certified."""
        validator = ReleaseValidator(version="1.0.0")
        cert = validator.certify()
        assert cert.certified is True

    def test_certify_all_pass_is_certified(self):
        validator = ReleaseValidator(version="1.0.0")
        validator.check_tests(failures=0, total=9000)
        validator.check_coverage(overall=68.0)
        cert = validator.certify()
        assert cert.certified is True

    def test_certify_with_failure_not_certified(self):
        validator = ReleaseValidator(version="1.0.0")
        validator.check_tests(failures=5, total=9000)
        cert = validator.certify()
        assert cert.certified is False

    def test_certify_blockers_list_populated(self):
        validator = ReleaseValidator(version="1.0.0")
        validator.check_tests(failures=1, total=100)
        cert = validator.certify()
        assert len(cert.blockers) > 0

    def test_certify_version_matches(self):
        validator = ReleaseValidator(version="2.0.1")
        cert = validator.certify()
        assert cert.version == "2.0.1"

    def test_certify_certified_at_set_when_certified(self):
        validator = ReleaseValidator()
        before = time.time()
        cert = validator.certify()
        after = time.time()
        assert before <= cert.certified_at <= after

    def test_certify_certified_at_zero_when_not_certified(self):
        validator = ReleaseValidator()
        validator.check_tests(failures=1, total=100)
        cert = validator.certify()
        assert cert.certified_at == 0.0

    def test_add_custom_check(self):
        validator = ReleaseValidator()
        custom = CertificationCheck("Custom", status=CertificationStatus.PASS)
        validator.add_custom_check(custom)
        assert validator.check_count == 1

    def test_custom_check_appears_in_certification(self):
        validator = ReleaseValidator()
        custom = CertificationCheck("Custom Gate", status=CertificationStatus.FAIL, category="custom")
        validator.add_custom_check(custom)
        cert = validator.certify()
        assert "Custom Gate" in cert.blockers

    def test_to_markdown_returns_string(self):
        validator = ReleaseValidator(version="1.0.0")
        validator.check_tests(failures=0, total=5000)
        cert = validator.certify()
        md = validator.to_markdown(cert)
        assert isinstance(md, str)
        assert "1.0.0" in md

    def test_to_markdown_includes_check_names(self):
        validator = ReleaseValidator(version="1.0.0")
        validator.check_tests(failures=0, total=5000)
        cert = validator.certify()
        md = validator.to_markdown(cert)
        assert "Test Suite" in md

    def test_to_markdown_certified_shows_certified(self):
        validator = ReleaseValidator(version="1.0.0")
        cert = validator.certify()
        md = validator.to_markdown(cert)
        assert "CERTIFIED" in md

    def test_to_markdown_not_certified_shows_blockers(self):
        validator = ReleaseValidator(version="1.0.0")
        validator.check_tests(failures=3, total=5000)
        cert = validator.certify()
        md = validator.to_markdown(cert)
        assert "Blockers" in md or "Test Suite" in md


# ---------------------------------------------------------------------------
# Tests: PackageMetadata
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPackageMetadata:
    """PackageMetadata dataclass defaults."""

    def test_default_name(self):
        meta = PackageMetadata()
        assert meta.name == "codomyrmex"

    def test_default_version(self):
        meta = PackageMetadata()
        assert meta.version == "1.0.0"

    def test_default_license(self):
        meta = PackageMetadata()
        assert meta.license == "MIT"

    def test_default_python_requires(self):
        meta = PackageMetadata()
        assert meta.python_requires == ">=3.11"

    def test_custom_fields(self):
        meta = PackageMetadata(
            name="mypkg",
            version="2.0.0",
            description="My package",
            author="Alice",
        )
        assert meta.name == "mypkg"
        assert meta.version == "2.0.0"
        assert meta.description == "My package"
        assert meta.author == "Alice"

    def test_default_empty_dependencies(self):
        meta = PackageMetadata()
        assert meta.dependencies == []


# ---------------------------------------------------------------------------
# Tests: PackageBuilder
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestPackageBuilder:
    """PackageBuilder validation and build."""

    def test_instantiation_default_metadata(self):
        builder = PackageBuilder()
        assert builder is not None
        assert builder.metadata.name == "codomyrmex"

    def test_instantiation_custom_metadata(self):
        meta = PackageMetadata(name="custom", version="3.0.0")
        builder = PackageBuilder(meta)
        assert builder.metadata.name == "custom"

    def test_validate_metadata_valid(self):
        builder = PackageBuilder()
        errors = builder.validate_metadata()
        assert errors == []

    def test_validate_metadata_missing_name(self):
        meta = PackageMetadata(name="")
        builder = PackageBuilder(meta)
        errors = builder.validate_metadata()
        assert any("name" in e.lower() for e in errors)

    def test_validate_metadata_missing_version(self):
        meta = PackageMetadata(version="")
        builder = PackageBuilder(meta)
        errors = builder.validate_metadata()
        assert any("version" in e.lower() for e in errors)

    def test_build_success_with_valid_metadata(self):
        builder = PackageBuilder()
        report = builder.build()
        assert isinstance(report, BuildReport)
        assert report.success is True

    def test_build_produces_two_artifacts(self):
        builder = PackageBuilder()
        report = builder.build()
        assert len(report.artifacts) == 2

    def test_build_artifacts_have_filename(self):
        builder = PackageBuilder()
        report = builder.build()
        for artifact in report.artifacts:
            assert artifact.filename != ""

    def test_build_includes_sdist(self):
        builder = PackageBuilder()
        report = builder.build()
        formats = {a.format for a in report.artifacts}
        assert "sdist" in formats

    def test_build_includes_wheel(self):
        builder = PackageBuilder()
        report = builder.build()
        formats = {a.format for a in report.artifacts}
        assert "wheel" in formats

    def test_build_artifacts_have_checksum(self):
        builder = PackageBuilder()
        report = builder.build()
        for artifact in report.artifacts:
            assert artifact.checksum != ""

    def test_build_failure_with_invalid_metadata(self):
        meta = PackageMetadata(name="", version="")
        builder = PackageBuilder(meta)
        report = builder.build()
        assert report.success is False
        assert len(report.warnings) > 0

    def test_build_report_metadata_matches(self):
        meta = PackageMetadata(name="testpkg", version="0.1.0")
        builder = PackageBuilder(meta)
        report = builder.build()
        assert report.metadata.name == "testpkg"

    def test_sdist_filename_format(self):
        meta = PackageMetadata(name="mypkg", version="1.2.3")
        builder = PackageBuilder(meta)
        report = builder.build()
        sdist = next(a for a in report.artifacts if a.format == "sdist")
        assert "mypkg" in sdist.filename
        assert "1.2.3" in sdist.filename
        assert sdist.filename.endswith(".tar.gz")

    def test_wheel_filename_format(self):
        meta = PackageMetadata(name="mypkg", version="1.2.3")
        builder = PackageBuilder(meta)
        report = builder.build()
        wheel = next(a for a in report.artifacts if a.format == "wheel")
        assert "mypkg" in wheel.filename
        assert "1.2.3" in wheel.filename
        assert wheel.filename.endswith(".whl")


# ---------------------------------------------------------------------------
# Tests: DistributionManager
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestDistributionManagerBasics:
    """DistributionManager initialization and properties."""

    def test_instantiation_no_build(self):
        dm = DistributionManager()
        assert dm is not None

    def test_has_build_false_without_build(self):
        dm = DistributionManager()
        assert dm.has_build is False

    def test_has_build_true_with_successful_build(self):
        builder = PackageBuilder()
        report = builder.build()
        dm = DistributionManager(build=report)
        assert dm.has_build is True

    def test_has_build_false_with_failed_build(self):
        meta = PackageMetadata(name="", version="")
        builder = PackageBuilder(meta)
        report = builder.build()
        dm = DistributionManager(build=report)
        assert dm.has_build is False


@pytest.mark.unit
class TestDistributionManagerPreflight:
    """DistributionManager.preflight() tests."""

    def test_preflight_returns_preflight_result(self):
        dm = DistributionManager()
        result = dm.preflight(DistributionTarget.LOCAL)
        assert isinstance(result, PreflightResult)

    def test_preflight_not_ready_without_build(self):
        dm = DistributionManager()
        result = dm.preflight(DistributionTarget.PYPI)
        assert result.ready is False

    def test_preflight_ready_with_successful_build(self):
        builder = PackageBuilder()
        report = builder.build()
        dm = DistributionManager(build=report)
        result = dm.preflight(DistributionTarget.PYPI)
        assert result.ready is True

    def test_preflight_target_recorded(self):
        builder = PackageBuilder()
        report = builder.build()
        dm = DistributionManager(build=report)
        result = dm.preflight(DistributionTarget.TEST_PYPI)
        assert result.target == DistributionTarget.TEST_PYPI

    def test_preflight_issues_empty_when_ready(self):
        builder = PackageBuilder()
        report = builder.build()
        dm = DistributionManager(build=report)
        result = dm.preflight(DistributionTarget.LOCAL)
        assert result.issues == []

    def test_preflight_issues_populated_when_not_ready(self):
        dm = DistributionManager()
        result = dm.preflight(DistributionTarget.PYPI)
        assert len(result.issues) > 0

    def test_preflight_checks_total(self):
        dm = DistributionManager()
        result = dm.preflight(DistributionTarget.PYPI)
        assert result.checks_total == 3


@pytest.mark.unit
class TestDistributionManagerPublish:
    """DistributionManager.publish() tests."""

    def test_publish_fails_without_build(self):
        dm = DistributionManager()
        result = dm.publish(DistributionTarget.PYPI)
        assert result.success is False

    def test_publish_succeeds_with_build(self):
        builder = PackageBuilder()
        report = builder.build()
        dm = DistributionManager(build=report)
        result = dm.publish(DistributionTarget.LOCAL)
        assert result.success is True

    def test_publish_returns_publish_result(self):
        builder = PackageBuilder()
        report = builder.build()
        dm = DistributionManager(build=report)
        result = dm.publish(DistributionTarget.LOCAL)
        assert isinstance(result, PublishResult)

    def test_publish_pypi_generates_url(self):
        meta = PackageMetadata(name="mypkg", version="1.0.0")
        builder = PackageBuilder(meta)
        report = builder.build()
        dm = DistributionManager(build=report)
        result = dm.publish(DistributionTarget.PYPI)
        assert "pypi.org" in result.url
        assert "mypkg" in result.url

    def test_publish_test_pypi_generates_url(self):
        meta = PackageMetadata(name="mypkg", version="1.0.0")
        builder = PackageBuilder(meta)
        report = builder.build()
        dm = DistributionManager(build=report)
        result = dm.publish(DistributionTarget.TEST_PYPI)
        assert "test.pypi.org" in result.url

    def test_publish_github_generates_url(self):
        meta = PackageMetadata(name="mypkg", version="1.0.0")
        builder = PackageBuilder(meta)
        report = builder.build()
        dm = DistributionManager(build=report)
        result = dm.publish(DistributionTarget.GITHUB)
        assert "github.com" in result.url

    def test_publish_artifacts_count(self):
        builder = PackageBuilder()
        report = builder.build()
        dm = DistributionManager(build=report)
        result = dm.publish(DistributionTarget.LOCAL)
        assert result.artifacts_published == 2  # sdist + wheel

    def test_publish_history_empty_initially(self):
        builder = PackageBuilder()
        report = builder.build()
        dm = DistributionManager(build=report)
        assert dm.publish_history() == []

    def test_publish_history_records_result(self):
        builder = PackageBuilder()
        report = builder.build()
        dm = DistributionManager(build=report)
        dm.publish(DistributionTarget.LOCAL)
        history = dm.publish_history()
        assert len(history) == 1

    def test_publish_history_multiple_publishes(self):
        builder = PackageBuilder()
        report = builder.build()
        dm = DistributionManager(build=report)
        dm.publish(DistributionTarget.LOCAL)
        dm.publish(DistributionTarget.LOCAL)
        assert len(dm.publish_history()) == 2

    def test_publish_history_returns_copy(self):
        builder = PackageBuilder()
        report = builder.build()
        dm = DistributionManager(build=report)
        dm.publish(DistributionTarget.LOCAL)
        h1 = dm.publish_history()
        h2 = dm.publish_history()
        assert h1 is not h2

    def test_publish_failure_error_message(self):
        dm = DistributionManager()
        result = dm.publish(DistributionTarget.PYPI)
        assert result.error != ""
