"""Tests for Sprint 14: Security Hardening.

Tests for wallet/encrypted_storage.py, ci_cd_automation/dependency_scan.py,
and ci_cd_automation/sbom.py.
"""

from __future__ import annotations

import json
import os
import tempfile

import pytest

from codomyrmex.wallet.encrypted_storage import (
    EncryptedEntry,
    EncryptedStore,
)
from codomyrmex.ci_cd_automation.dependency_scan import (
    DependencyScanner,
    ScanReport,
    Vulnerability,
)
from codomyrmex.ci_cd_automation.sbom import (
    SBOMComponent,
    SBOMDocument,
    SBOMGenerator,
)


# ── EncryptedStore ───────────────────────────────────────────────


class TestEncryptedEntry:
    def test_round_trip_dict(self) -> None:
        entry = EncryptedEntry(
            key="test", ciphertext="abc", nonce="def", tag="ghi",
            created_at=1.0, rotated_at=2.0,
        )
        d = entry.to_dict()
        restored = EncryptedEntry.from_dict(d)
        assert restored.key == "test"
        assert restored.ciphertext == "abc"


class TestEncryptedStore:
    def test_put_and_get(self) -> None:
        store = EncryptedStore()
        store.put("api_key", "sk-secret-12345")
        assert store.get("api_key") == "sk-secret-12345"

    def test_get_missing(self) -> None:
        store = EncryptedStore()
        assert store.get("nonexistent") is None

    def test_has(self) -> None:
        store = EncryptedStore()
        assert not store.has("key")
        store.put("key", "value")
        assert store.has("key")

    def test_delete(self) -> None:
        store = EncryptedStore()
        store.put("key", "value")
        assert store.delete("key") is True
        assert store.has("key") is False
        assert store.delete("key") is False

    def test_list_keys(self) -> None:
        store = EncryptedStore()
        store.put("b", "1")
        store.put("a", "2")
        assert store.list_keys() == ["a", "b"]

    def test_size(self) -> None:
        store = EncryptedStore()
        assert store.size == 0
        store.put("k", "v")
        assert store.size == 1

    def test_rotate_master_key(self) -> None:
        store = EncryptedStore()
        store.put("key1", "secret1")
        store.put("key2", "secret2")
        new_key = os.urandom(32)
        count = store.rotate_master_key(new_key)
        assert count == 2
        assert store.get("key1") == "secret1"
        assert store.get("key2") == "secret2"

    def test_different_keys_different_ciphertext(self) -> None:
        store = EncryptedStore()
        e1 = store.put("k1", "same_value")
        e2 = store.put("k2", "same_value")
        assert e1.ciphertext != e2.ciphertext  # Different nonces

    def test_large_value(self) -> None:
        store = EncryptedStore()
        large = "x" * 10000
        store.put("big", large)
        assert store.get("big") == large


# ── DependencyScanner ────────────────────────────────────────────


class TestVulnerability:
    def test_to_dict(self) -> None:
        v = Vulnerability(package="requests", severity="high", cve_id="CVE-123")
        d = v.to_dict()
        assert d["package"] == "requests"
        assert d["severity"] == "high"


class TestDependencyScanner:
    def test_scan_direct(self) -> None:
        scanner = DependencyScanner()
        report = scanner.scan_dependencies({"requests": ">=2.28.0"})
        assert report.packages_scanned == 1
        # Should find known advisory for requests
        assert len(report.vulnerabilities) >= 1

    def test_scan_clean_package(self) -> None:
        scanner = DependencyScanner()
        report = scanner.scan_dependencies({"my_private_pkg": "1.0.0"})
        assert report.is_clean

    def test_scan_pyproject_file(self) -> None:
        content = '''
[project]
name = "test-project"
version = "0.1.0"
dependencies = [
    "requests>=2.28.0",
    "numpy>=1.24.0",
]
'''
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(content)
            f.flush()
            scanner = DependencyScanner()
            report = scanner.scan_pyproject(f.name)
            os.unlink(f.name)

        assert report.packages_scanned >= 2
        pkg_names = [v.package for v in report.vulnerabilities]
        assert "requests" in pkg_names

    def test_scan_missing_file(self) -> None:
        scanner = DependencyScanner()
        report = scanner.scan_pyproject("/nonexistent/pyproject.toml")
        assert report.scan_source == "file_not_found"

    def test_report_has_critical(self) -> None:
        report = ScanReport(vulnerabilities=[
            Vulnerability(package="x", severity="critical"),
        ])
        assert report.has_critical

    def test_report_count_by_severity(self) -> None:
        report = ScanReport(vulnerabilities=[
            Vulnerability(package="a", severity="high"),
            Vulnerability(package="b", severity="medium"),
            Vulnerability(package="c", severity="high"),
        ])
        assert report.count_by_severity == {"high": 2, "medium": 1}


# ── SBOMGenerator ────────────────────────────────────────────


class TestSBOMComponent:
    def test_auto_purl(self) -> None:
        c = SBOMComponent(name="requests", version="2.31.0")
        assert c.purl == "pkg:pypi/requests@2.31.0"

    def test_purl_no_version(self) -> None:
        c = SBOMComponent(name="requests")
        assert c.purl == "pkg:pypi/requests"

    def test_to_dict(self) -> None:
        c = SBOMComponent(name="numpy", version="1.24.0")
        d = c.to_dict()
        assert d["name"] == "numpy"
        assert d["type"] == "library"


class TestSBOMDocument:
    def test_cyclonedx_format(self) -> None:
        doc = SBOMDocument(
            project_name="test", project_version="1.0.0",
            components=[SBOMComponent(name="a", version="1.0")],
        )
        cdx = doc.to_cyclonedx()
        assert cdx["bomFormat"] == "CycloneDX"
        assert cdx["specVersion"] == "1.5"
        assert len(cdx["components"]) == 1

    def test_to_json(self) -> None:
        doc = SBOMDocument(project_name="test", project_version="1.0")
        j = doc.to_json()
        parsed = json.loads(j)
        assert parsed["bomFormat"] == "CycloneDX"

    def test_component_count(self) -> None:
        doc = SBOMDocument(components=[
            SBOMComponent(name="a"), SBOMComponent(name="b"),
        ])
        assert doc.component_count == 2


class TestSBOMGenerator:
    def test_from_dependencies(self) -> None:
        gen = SBOMGenerator()
        sbom = gen.from_dependencies("proj", "1.0", {"requests": "2.31.0", "numpy": "1.24"})
        assert sbom.project_name == "proj"
        assert sbom.component_count == 2

    def test_from_pyproject(self) -> None:
        content = '''
[project]
name = "my-project"
version = "0.5.0"
dependencies = [
    "requests>=2.31.0",
    "pydantic>=2.0",
]
'''
        with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
            f.write(content)
            f.flush()
            gen = SBOMGenerator()
            sbom = gen.from_pyproject(f.name)
            os.unlink(f.name)

        assert sbom.project_name == "my-project"
        assert sbom.project_version == "0.5.0"
        assert sbom.component_count >= 2

    def test_missing_file(self) -> None:
        gen = SBOMGenerator()
        sbom = gen.from_pyproject("/nonexistent/pyproject.toml")
        assert sbom.component_count == 0
