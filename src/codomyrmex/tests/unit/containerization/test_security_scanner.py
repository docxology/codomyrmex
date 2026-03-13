"""Zero-mock tests for containerization.security.security_scanner."""

import shutil
from datetime import datetime

import pytest

from codomyrmex.containerization.security.security_scanner import (
    ContainerSecurityScanner,
    SecurityScanResult,
    Vulnerability,
    VulnerabilitySeverity,
    _parse_trivy_results,
    _trivy_cli,
    scan_container_security,
)

# ---------------------------------------------------------------------------
# VulnerabilitySeverity enum
# ---------------------------------------------------------------------------


class TestVulnerabilitySeverityEnum:
    def test_has_critical_member(self):
        assert VulnerabilitySeverity.CRITICAL.value == "critical"

    def test_has_high_member(self):
        assert VulnerabilitySeverity.HIGH.value == "high"

    def test_has_medium_member(self):
        assert VulnerabilitySeverity.MEDIUM.value == "medium"

    def test_has_low_member(self):
        assert VulnerabilitySeverity.LOW.value == "low"

    def test_has_info_member(self):
        assert VulnerabilitySeverity.INFO.value == "info"

    def test_exactly_five_members(self):
        assert len(VulnerabilitySeverity) == 5

    def test_members_are_distinct(self):
        values = [s.value for s in VulnerabilitySeverity]
        assert len(values) == len(set(values))


# ---------------------------------------------------------------------------
# Vulnerability dataclass
# ---------------------------------------------------------------------------


class TestVulnerabilityDataclass:
    def test_minimal_instantiation(self):
        v = Vulnerability(
            id="CVE-2024-0001",
            severity=VulnerabilitySeverity.HIGH,
            title="Test vuln",
            description="A test vulnerability",
        )
        assert v.id == "CVE-2024-0001"
        assert v.severity == VulnerabilitySeverity.HIGH
        assert v.title == "Test vuln"
        assert v.description == "A test vulnerability"
        assert v.package is None
        assert v.version is None
        assert v.fixed_version is None
        assert v.cve_ids == []

    def test_full_instantiation(self):
        v = Vulnerability(
            id="CVE-2024-1234",
            severity=VulnerabilitySeverity.CRITICAL,
            title="Critical vuln",
            description="Serious issue",
            package="openssl",
            version="1.0.0",
            fixed_version="1.0.1",
            cve_ids=["CVE-2024-1234"],
        )
        assert v.package == "openssl"
        assert v.version == "1.0.0"
        assert v.fixed_version == "1.0.1"
        assert "CVE-2024-1234" in v.cve_ids


# ---------------------------------------------------------------------------
# SecurityScanResult — properties and aggregation
# ---------------------------------------------------------------------------


def _make_vuln(severity: VulnerabilitySeverity, vuln_id: str = "V-001") -> Vulnerability:
    return Vulnerability(
        id=vuln_id,
        severity=severity,
        title="test",
        description="test description",
    )


class TestSecurityScanResult:
    def test_default_passed_is_true(self):
        result = SecurityScanResult(image="nginx:latest", scan_time=datetime.now())
        assert result.passed is True

    def test_empty_vulnerabilities_by_default(self):
        result = SecurityScanResult(image="nginx:latest", scan_time=datetime.now())
        assert result.vulnerabilities == []

    def test_critical_count_zero_on_empty(self):
        result = SecurityScanResult(image="nginx:latest", scan_time=datetime.now())
        assert result.critical_count == 0

    def test_high_count_zero_on_empty(self):
        result = SecurityScanResult(image="nginx:latest", scan_time=datetime.now())
        assert result.high_count == 0

    def test_critical_count_counts_only_critical(self):
        result = SecurityScanResult(
            image="nginx:latest",
            scan_time=datetime.now(),
            vulnerabilities=[
                _make_vuln(VulnerabilitySeverity.CRITICAL, "C1"),
                _make_vuln(VulnerabilitySeverity.CRITICAL, "C2"),
                _make_vuln(VulnerabilitySeverity.HIGH, "H1"),
                _make_vuln(VulnerabilitySeverity.LOW, "L1"),
            ],
        )
        assert result.critical_count == 2

    def test_high_count_counts_only_high(self):
        result = SecurityScanResult(
            image="nginx:latest",
            scan_time=datetime.now(),
            vulnerabilities=[
                _make_vuln(VulnerabilitySeverity.HIGH, "H1"),
                _make_vuln(VulnerabilitySeverity.HIGH, "H2"),
                _make_vuln(VulnerabilitySeverity.CRITICAL, "C1"),
            ],
        )
        assert result.high_count == 2

    def test_summary_returns_all_severity_keys(self):
        result = SecurityScanResult(image="nginx:latest", scan_time=datetime.now())
        summary = result.summary()
        for sev in VulnerabilitySeverity:
            assert sev.value in summary

    def test_summary_counts_correctly(self):
        result = SecurityScanResult(
            image="nginx:latest",
            scan_time=datetime.now(),
            vulnerabilities=[
                _make_vuln(VulnerabilitySeverity.CRITICAL, "C1"),
                _make_vuln(VulnerabilitySeverity.HIGH, "H1"),
                _make_vuln(VulnerabilitySeverity.HIGH, "H2"),
                _make_vuln(VulnerabilitySeverity.LOW, "L1"),
            ],
        )
        summary = result.summary()
        assert summary["critical"] == 1
        assert summary["high"] == 2
        assert summary["low"] == 1
        assert summary["medium"] == 0
        assert summary["info"] == 0

    def test_error_field_stored(self):
        result = SecurityScanResult(
            image="badimage:latest",
            scan_time=datetime.now(),
            passed=False,
            error="Trivy scan failed: image not found",
        )
        assert result.error == "Trivy scan failed: image not found"
        assert result.passed is False

    def test_metadata_stored(self):
        result = SecurityScanResult(
            image="nginx:latest",
            scan_time=datetime.now(),
            metadata={"trivy_schema_version": 2},
        )
        assert result.metadata["trivy_schema_version"] == 2


# ---------------------------------------------------------------------------
# _parse_trivy_results — module-level function
# ---------------------------------------------------------------------------


class TestParseTrivyResults:
    def test_empty_results_returns_empty_list(self):
        data = {"Results": []}
        vulns = _parse_trivy_results(data)
        assert vulns == []

    def test_missing_results_key_returns_empty_list(self):
        data = {}
        vulns = _parse_trivy_results(data)
        assert vulns == []

    def test_parses_critical_severity(self):
        data = {
            "Results": [
                {
                    "Vulnerabilities": [
                        {
                            "VulnerabilityID": "CVE-2024-9999",
                            "Severity": "CRITICAL",
                            "Title": "Critical issue",
                            "Description": "Very serious",
                            "PkgName": "libssl",
                            "InstalledVersion": "1.0.0",
                            "FixedVersion": "1.0.2",
                        }
                    ]
                }
            ]
        }
        vulns = _parse_trivy_results(data)
        assert len(vulns) == 1
        assert vulns[0].severity == VulnerabilitySeverity.CRITICAL
        assert vulns[0].id == "CVE-2024-9999"
        assert vulns[0].package == "libssl"

    def test_cve_ids_populated_for_cve_prefixed_id(self):
        data = {
            "Results": [
                {
                    "Vulnerabilities": [
                        {
                            "VulnerabilityID": "CVE-2024-1111",
                            "Severity": "HIGH",
                            "Title": "High issue",
                            "Description": "Serious",
                        }
                    ]
                }
            ]
        }
        vulns = _parse_trivy_results(data)
        assert "CVE-2024-1111" in vulns[0].cve_ids

    def test_cve_ids_empty_for_non_cve_id(self):
        data = {
            "Results": [
                {
                    "Vulnerabilities": [
                        {
                            "VulnerabilityID": "GHSA-xxxx-yyyy",
                            "Severity": "MEDIUM",
                            "Title": "Advisory",
                            "Description": "Some issue",
                        }
                    ]
                }
            ]
        }
        vulns = _parse_trivy_results(data)
        assert vulns[0].cve_ids == []

    def test_unknown_severity_maps_to_info(self):
        data = {
            "Results": [
                {
                    "Vulnerabilities": [
                        {
                            "VulnerabilityID": "MISC-001",
                            "Severity": "UNKNOWN",
                            "Title": "Unknown sev",
                            "Description": "",
                        }
                    ]
                }
            ]
        }
        vulns = _parse_trivy_results(data)
        assert vulns[0].severity == VulnerabilitySeverity.INFO

    def test_null_vulnerabilities_key_handled(self):
        data = {"Results": [{"Vulnerabilities": None}]}
        vulns = _parse_trivy_results(data)
        assert vulns == []

    def test_multiple_results_aggregated(self):
        data = {
            "Results": [
                {
                    "Vulnerabilities": [
                        {
                            "VulnerabilityID": "CVE-2024-0001",
                            "Severity": "HIGH",
                            "Title": "A",
                            "Description": "",
                        }
                    ]
                },
                {
                    "Vulnerabilities": [
                        {
                            "VulnerabilityID": "CVE-2024-0002",
                            "Severity": "LOW",
                            "Title": "B",
                            "Description": "",
                        }
                    ]
                },
            ]
        }
        vulns = _parse_trivy_results(data)
        assert len(vulns) == 2


# ---------------------------------------------------------------------------
# ContainerSecurityScanner — init, history, clear
# ---------------------------------------------------------------------------


class TestContainerSecurityScannerInit:
    def test_no_config_uses_empty_dict(self):
        scanner = ContainerSecurityScanner()
        assert scanner.config == {}

    def test_config_stored(self):
        scanner = ContainerSecurityScanner(config={"timeout": 60})
        assert scanner.config["timeout"] == 60

    def test_initial_scan_history_empty(self):
        scanner = ContainerSecurityScanner()
        assert scanner.get_scan_history() == []

    def test_clear_history_empties_list(self):
        scanner = ContainerSecurityScanner()
        # Manually inject a result to simulate post-scan state
        scanner._scan_history.append(
            SecurityScanResult(
                image="test:latest",
                scan_time=datetime.now(),
                passed=True,
            )
        )
        assert len(scanner.get_scan_history()) == 1
        scanner.clear_history()
        assert scanner.get_scan_history() == []

    def test_get_scan_history_returns_copy(self):
        scanner = ContainerSecurityScanner()
        h1 = scanner.get_scan_history()
        scanner.get_scan_history()
        # Mutating one should not affect the internal state
        h1.append("spurious")
        assert len(scanner.get_scan_history()) == 0


# ---------------------------------------------------------------------------
# _trivy_cli — raises NotImplementedError when trivy absent
# ---------------------------------------------------------------------------


@pytest.mark.skipif(
    shutil.which("trivy") is not None,
    reason="Trivy is installed; test verifies absence behaviour only",
)
class TestTrivyCliAbsent:
    def test_raises_not_implemented_error(self):
        with pytest.raises(NotImplementedError, match="Trivy"):
            _trivy_cli()


# ---------------------------------------------------------------------------
# scan_container_security helper — without Trivy
# ---------------------------------------------------------------------------


class TestScanContainerSecurityHelper:
    def test_raises_not_implemented_when_no_trivy(self):
        if shutil.which("trivy") is not None:
            pytest.skip("Trivy installed; would actually run scan")
        with pytest.raises(NotImplementedError):
            scan_container_security("alpine:latest")

    def test_accepts_pre_configured_scanner(self):
        if shutil.which("trivy") is not None:
            pytest.skip("Trivy installed; would actually run scan")
        scanner = ContainerSecurityScanner()
        with pytest.raises(NotImplementedError):
            scan_container_security("alpine:latest", scanner=scanner)


# ---------------------------------------------------------------------------
# Real Trivy integration (skipped unless trivy binary present)
# ---------------------------------------------------------------------------


@pytest.mark.skipif(shutil.which("trivy") is None, reason="Trivy not installed")
class TestRealTrivyScan:
    def test_scan_image_returns_scan_result(self):
        scanner = ContainerSecurityScanner()
        result = scanner.scan_image("alpine:latest")
        assert isinstance(result, SecurityScanResult)
        assert result.image == "alpine:latest"

    def test_scan_appends_to_history(self):
        scanner = ContainerSecurityScanner()
        scanner.scan_image("alpine:latest")
        assert len(scanner.get_scan_history()) == 1

    def test_summary_returns_dict_after_real_scan(self):
        scanner = ContainerSecurityScanner()
        result = scanner.scan_image("alpine:latest")
        summary = result.summary()
        for sev in VulnerabilitySeverity:
            assert sev.value in summary
