"""Tests for security.sbom module."""

import json

import pytest

try:
    from codomyrmex.security.sbom import (
        SBOM,
        Component,
        LicenseType,
        SBOMFormat,
        SBOMGenerator,
        SupplyChainVerifier,
        VulnerabilityScanner,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("security.sbom module not available", allow_module_level=True)


@pytest.mark.unit
class TestSBOMFormat:
    def test_spdx(self):
        assert SBOMFormat.SPDX is not None

    def test_cyclonedx(self):
        assert SBOMFormat.CYCLONEDX is not None

    def test_swid(self):
        assert SBOMFormat.SWID is not None


@pytest.mark.unit
class TestLicenseType:
    def test_mit(self):
        assert LicenseType.MIT is not None

    def test_apache(self):
        assert LicenseType.APACHE_2 is not None

    def test_gpl(self):
        assert LicenseType.GPL_3 is not None

    def test_unknown(self):
        assert LicenseType.UNKNOWN is not None


@pytest.mark.unit
class TestComponent:
    def test_create_component(self):
        comp = Component(name="requests", version="2.31.0")
        assert comp.name == "requests"
        assert comp.version == "2.31.0"

    def test_component_defaults(self):
        comp = Component(name="test", version="1.0")
        assert comp.purl == ""
        assert comp.license == LicenseType.UNKNOWN
        assert comp.supplier == ""
        assert comp.checksum == ""
        assert comp.dependencies == []
        assert comp.vulnerabilities == []

    def test_to_dict(self):
        comp = Component(name="test", version="1.0", license=LicenseType.MIT)
        d = comp.to_dict()
        assert isinstance(d, dict)
        assert d["name"] == "test"


@pytest.mark.unit
class TestSBOM:
    def test_create_sbom(self):
        sbom = SBOM(name="my-project", version="1.0.0")
        assert sbom.name == "my-project"
        assert sbom.format == SBOMFormat.CYCLONEDX
        assert sbom.components == []

    def test_sbom_with_components(self):
        components = [
            Component(name="requests", version="2.31.0"),
            Component(name="flask", version="3.0.0"),
        ]
        sbom = SBOM(name="test", version="1.0", components=components)
        assert len(sbom.components) == 2

    def test_to_dict(self):
        sbom = SBOM(name="test", version="1.0")
        d = sbom.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        sbom = SBOM(name="test", version="1.0")
        j = sbom.to_json()
        parsed = json.loads(j)
        assert parsed["name"] == "test"


@pytest.mark.unit
class TestSBOMGenerator:
    def test_create_generator(self):
        gen = SBOMGenerator()
        assert gen is not None


@pytest.mark.unit
class TestVulnerabilityScanner:
    def test_create_scanner(self):
        scanner = VulnerabilityScanner()
        assert scanner is not None

    def test_scan_empty_sbom(self):
        scanner = VulnerabilityScanner()
        sbom = SBOM(name="test", version="1.0")
        results = scanner.scan(sbom)
        assert isinstance(results, (list, dict))


@pytest.mark.unit
class TestSupplyChainVerifier:
    def test_create_verifier(self):
        verifier = SupplyChainVerifier()
        assert verifier is not None
