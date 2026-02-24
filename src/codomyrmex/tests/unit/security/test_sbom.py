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
    """Test suite for SBOMFormat."""
    def test_spdx(self):
        """Test functionality: spdx."""
        assert SBOMFormat.SPDX is not None

    def test_cyclonedx(self):
        """Test functionality: cyclonedx."""
        assert SBOMFormat.CYCLONEDX is not None

    def test_swid(self):
        """Test functionality: swid."""
        assert SBOMFormat.SWID is not None


@pytest.mark.unit
class TestLicenseType:
    """Test suite for LicenseType."""
    def test_mit(self):
        """Test functionality: mit."""
        assert LicenseType.MIT is not None

    def test_apache(self):
        """Test functionality: apache."""
        assert LicenseType.APACHE_2 is not None

    def test_gpl(self):
        """Test functionality: gpl."""
        assert LicenseType.GPL_3 is not None

    def test_unknown(self):
        """Test functionality: unknown."""
        assert LicenseType.UNKNOWN is not None


@pytest.mark.unit
class TestComponent:
    """Test suite for Component."""
    def test_create_component(self):
        """Test functionality: create component."""
        comp = Component(name="requests", version="2.31.0")
        assert comp.name == "requests"
        assert comp.version == "2.31.0"

    def test_component_defaults(self):
        """Test functionality: component defaults."""
        comp = Component(name="test", version="1.0")
        assert comp.purl == ""
        assert comp.license == LicenseType.UNKNOWN
        assert comp.supplier == ""
        assert comp.checksum == ""
        assert comp.dependencies == []
        assert comp.vulnerabilities == []

    def test_to_dict(self):
        """Test functionality: to dict."""
        comp = Component(name="test", version="1.0", license=LicenseType.MIT)
        d = comp.to_dict()
        assert isinstance(d, dict)
        assert d["name"] == "test"


@pytest.mark.unit
class TestSBOM:
    """Test suite for SBOM."""
    def test_create_sbom(self):
        """Test functionality: create sbom."""
        sbom = SBOM(name="my-project", version="1.0.0")
        assert sbom.name == "my-project"
        assert sbom.format == SBOMFormat.CYCLONEDX
        assert sbom.components == []

    def test_sbom_with_components(self):
        """Test functionality: sbom with components."""
        components = [
            Component(name="requests", version="2.31.0"),
            Component(name="flask", version="3.0.0"),
        ]
        sbom = SBOM(name="test", version="1.0", components=components)
        assert len(sbom.components) == 2

    def test_to_dict(self):
        """Test functionality: to dict."""
        sbom = SBOM(name="test", version="1.0")
        d = sbom.to_dict()
        assert isinstance(d, dict)

    def test_to_json(self):
        """Test functionality: to json."""
        sbom = SBOM(name="test", version="1.0")
        j = sbom.to_json()
        parsed = json.loads(j)
        assert parsed["name"] == "test"


@pytest.mark.unit
class TestSBOMGenerator:
    """Test suite for SBOMGenerator."""
    def test_create_generator(self):
        """Test functionality: create generator."""
        gen = SBOMGenerator()
        assert gen is not None


@pytest.mark.unit
class TestVulnerabilityScanner:
    """Test suite for VulnerabilityScanner."""
    def test_create_scanner(self):
        """Test functionality: create scanner."""
        scanner = VulnerabilityScanner()
        assert scanner is not None

    def test_scan_empty_sbom(self):
        """Test functionality: scan empty sbom."""
        scanner = VulnerabilityScanner()
        sbom = SBOM(name="test", version="1.0")
        results = scanner.scan(sbom)
        assert isinstance(results, (list, dict))


@pytest.mark.unit
class TestSupplyChainVerifier:
    """Test suite for SupplyChainVerifier."""
    def test_create_verifier(self):
        """Test functionality: create verifier."""
        verifier = SupplyChainVerifier()
        assert verifier is not None
