"""Tests for Sprint 41: Release Certification.

Covers ReleaseValidator, PackageBuilder, and DistributionManager.
"""

import pytest

from codomyrmex.release.release_validator import (
    CertificationStatus,
    ReleaseValidator,
)
from codomyrmex.release.package_builder import PackageBuilder, PackageMetadata
from codomyrmex.release.distribution import (
    DistributionManager,
    DistributionTarget,
)


# ─── ReleaseValidator ────────────────────────────────────────────────

class TestReleaseValidator:

    def test_full_certification_pass(self):
        v = ReleaseValidator(version="1.0.0")
        v.check_tests(failures=0, total=9000)
        v.check_coverage(overall=67, tier1=82)
        v.check_type_safety(errors=0)
        v.check_security(cve_count=0, secrets_found=0)
        v.check_documentation(complete=True)
        cert = v.certify()
        assert cert.certified
        assert cert.pass_rate == pytest.approx(1.0)

    def test_certification_fail_on_tests(self):
        v = ReleaseValidator()
        v.check_tests(failures=3, total=100)
        cert = v.certify()
        assert not cert.certified
        assert "Test Suite" in cert.blockers

    def test_certification_fail_on_coverage(self):
        v = ReleaseValidator()
        v.check_coverage(overall=50, tier1=60)
        cert = v.certify()
        assert not cert.certified

    def test_markdown_output(self):
        v = ReleaseValidator(version="1.0.0")
        v.check_tests(failures=0, total=100)
        cert = v.certify()
        md = v.to_markdown(cert)
        assert "v1.0.0" in md
        assert "CERTIFIED" in md


# ─── PackageBuilder ──────────────────────────────────────────────────

class TestPackageBuilder:

    def test_valid_build(self):
        builder = PackageBuilder(PackageMetadata(name="mypackage", version="1.0.0"))
        report = builder.build()
        assert report.success
        assert len(report.artifacts) == 2

    def test_checksums(self):
        builder = PackageBuilder(PackageMetadata(name="pkg", version="1.0"))
        report = builder.build()
        for artifact in report.artifacts:
            assert len(artifact.checksum) > 0

    def test_invalid_metadata(self):
        builder = PackageBuilder(PackageMetadata(name="", version=""))
        report = builder.build()
        assert not report.success

    def test_artifact_filenames(self):
        builder = PackageBuilder(PackageMetadata(name="mylib", version="2.0.0"))
        report = builder.build()
        formats = {a.format for a in report.artifacts}
        assert "sdist" in formats
        assert "wheel" in formats


# ─── DistributionManager ─────────────────────────────────────────────

class TestDistributionManager:

    def test_preflight_pass(self):
        builder = PackageBuilder(PackageMetadata(name="pkg", version="1.0"))
        report = builder.build()
        dm = DistributionManager(build=report)
        pf = dm.preflight(DistributionTarget.PYPI)
        assert pf.ready

    def test_preflight_fail_no_build(self):
        dm = DistributionManager()
        pf = dm.preflight(DistributionTarget.PYPI)
        assert not pf.ready

    def test_publish_pypi(self):
        builder = PackageBuilder(PackageMetadata(name="codomyrmex", version="1.0.0"))
        report = builder.build()
        dm = DistributionManager(build=report)
        result = dm.publish(DistributionTarget.PYPI)
        assert result.success
        assert "pypi.org" in result.url

    def test_publish_github(self):
        builder = PackageBuilder(PackageMetadata(name="codomyrmex", version="1.0.0"))
        report = builder.build()
        dm = DistributionManager(build=report)
        result = dm.publish(DistributionTarget.GITHUB)
        assert result.success
        assert "github.com" in result.url
