"""Extended tests for security/sbom.py — SBOMGenerator, SBOM, SupplyChainVerifier."""

import hashlib
import json

import pytest

from codomyrmex.security.sbom import (
    SBOM,
    Component,
    LicenseType,
    SBOMFormat,
    SBOMGenerator,
    SupplyChainVerifier,
    VulnerabilityScanner,
)


class TestComponentDataclass:
    """Tests for the Component dataclass."""

    def test_create_minimal(self):
        """Component requires only name and version."""
        comp = Component(name="requests", version="2.31.0")
        assert comp.name == "requests"
        assert comp.version == "2.31.0"
        assert comp.purl == ""
        assert comp.license == LicenseType.UNKNOWN

    def test_create_full(self):
        """Component stores all provided fields."""
        comp = Component(
            name="flask",
            version="3.0.0",
            purl="pkg:pypi/flask@3.0.0",
            license=LicenseType.BSD_3,
            supplier="Pallets",
            checksum="abc123",
            dependencies=["werkzeug"],
        )
        assert comp.purl == "pkg:pypi/flask@3.0.0"
        assert comp.license == LicenseType.BSD_3
        assert comp.supplier == "Pallets"
        assert "werkzeug" in comp.dependencies

    def test_to_dict_has_required_keys(self):
        """to_dict() includes all expected keys."""
        comp = Component(name="requests", version="2.31.0")
        d = comp.to_dict()
        for key in (
            "name",
            "version",
            "purl",
            "license",
            "supplier",
            "checksum",
            "dependencies",
            "vulnerabilities",
        ):
            assert key in d

    def test_to_dict_license_is_string(self):
        """to_dict() serializes license as string value."""
        comp = Component(name="x", version="1.0", license=LicenseType.MIT)
        d = comp.to_dict()
        assert d["license"] == "MIT"


class TestSBOMDataclass:
    """Tests for the SBOM dataclass."""

    def test_create_minimal(self):
        """SBOM created with name and version."""
        sbom = SBOM(name="myapp", version="1.0.0")
        assert sbom.name == "myapp"
        assert sbom.version == "1.0.0"
        assert sbom.components == []
        assert sbom.format == SBOMFormat.CYCLONEDX

    def test_to_dict_structure(self):
        """to_dict() has all top-level keys."""
        sbom = SBOM(name="app", version="2.0")
        d = sbom.to_dict()
        for key in (
            "name",
            "version",
            "format",
            "created_at",
            "components",
            "metadata",
        ):
            assert key in d

    def test_to_dict_components_serialized(self):
        """to_dict() includes serialized component list."""
        comp = Component(name="requests", version="2.31.0")
        sbom = SBOM(name="app", version="1.0", components=[comp])
        d = sbom.to_dict()
        assert len(d["components"]) == 1
        assert d["components"][0]["name"] == "requests"

    def test_to_json_is_valid_json(self):
        """to_json() returns valid JSON string."""
        sbom = SBOM(name="app", version="1.0")
        result = sbom.to_json()
        parsed = json.loads(result)
        assert parsed["name"] == "app"
        assert parsed["version"] == "1.0"

    def test_save_writes_file(self, tmp_path):
        """save() writes JSON to disk."""
        sbom = SBOM(name="app", version="1.0")
        output = tmp_path / "sbom.json"
        sbom.save(str(output))
        assert output.exists()
        data = json.loads(output.read_text())
        assert data["name"] == "app"

    def test_format_spdx(self):
        """SBOM can be created with SPDX format."""
        sbom = SBOM(name="app", version="1.0", format=SBOMFormat.SPDX)
        d = sbom.to_dict()
        assert d["format"] == "spdx"


class TestSBOMGeneratorFromRequirements:
    """Tests for SBOMGenerator.from_requirements()."""

    def test_parse_pinned_requirements(self, tmp_path):
        """Parses packages with == pinned versions."""
        req = tmp_path / "requirements.txt"
        req.write_text("requests==2.31.0\nflask==3.0.0\n")
        gen = SBOMGenerator()
        components = gen.from_requirements(str(req))
        assert len(components) == 2
        names = {c.name for c in components}
        assert "requests" in names
        assert "flask" in names

    def test_parse_min_version_requirements(self, tmp_path):
        """Parses packages with >= min version."""
        req = tmp_path / "requirements.txt"
        req.write_text("click>=8.0.0\n")
        gen = SBOMGenerator()
        components = gen.from_requirements(str(req))
        assert len(components) == 1
        assert components[0].name == "click"
        assert "8.0.0" in components[0].version

    def test_parse_bare_package_name(self, tmp_path):
        """Parses bare package names without version."""
        req = tmp_path / "requirements.txt"
        req.write_text("somepackage\n")
        gen = SBOMGenerator()
        components = gen.from_requirements(str(req))
        assert len(components) == 1
        assert components[0].name == "somepackage"
        assert components[0].version == "unknown"

    def test_skip_comments_and_blanks(self, tmp_path):
        """Skips comment lines and blank lines."""
        req = tmp_path / "requirements.txt"
        req.write_text("# This is a comment\n\nrequests==2.31.0\n")
        gen = SBOMGenerator()
        components = gen.from_requirements(str(req))
        assert len(components) == 1

    def test_missing_file_returns_empty(self):
        """Missing requirements.txt returns empty list (no crash)."""
        gen = SBOMGenerator()
        components = gen.from_requirements("/nonexistent/requirements.txt")
        assert components == []

    def test_purl_generated(self, tmp_path):
        """Components get a pkg:pypi purl."""
        req = tmp_path / "requirements.txt"
        req.write_text("requests==2.31.0\n")
        gen = SBOMGenerator()
        components = gen.from_requirements(str(req))
        assert components[0].purl.startswith("pkg:pypi/")

    def test_components_accumulated(self, tmp_path):
        """Multiple from_requirements() calls accumulate components."""
        req1 = tmp_path / "req1.txt"
        req2 = tmp_path / "req2.txt"
        req1.write_text("requests==2.31.0\n")
        req2.write_text("flask==3.0.0\n")
        gen = SBOMGenerator()
        gen.from_requirements(str(req1))
        gen.from_requirements(str(req2))
        sbom = gen.generate("app", "1.0")
        assert len(sbom.components) == 2


class TestSBOMGeneratorFromPackageJson:
    """Tests for SBOMGenerator.from_package_json()."""

    def test_parse_dependencies(self, tmp_path):
        """Parses dependencies section from package.json."""
        pkg = tmp_path / "package.json"
        pkg.write_text(
            json.dumps(
                {
                    "dependencies": {
                        "react": "^18.0.0",
                        "axios": "~1.4.0",
                    }
                }
            )
        )
        gen = SBOMGenerator()
        components = gen.from_package_json(str(pkg))
        assert len(components) == 2
        names = {c.name for c in components}
        assert "react" in names
        assert "axios" in names

    def test_parse_dev_dependencies(self, tmp_path):
        """Parses devDependencies section."""
        pkg = tmp_path / "package.json"
        pkg.write_text(json.dumps({"devDependencies": {"jest": "^29.0.0"}}))
        gen = SBOMGenerator()
        components = gen.from_package_json(str(pkg))
        assert len(components) == 1
        assert components[0].name == "jest"

    def test_version_prefix_stripped(self, tmp_path):
        """^ and ~ prefixes stripped from npm versions."""
        pkg = tmp_path / "package.json"
        pkg.write_text(json.dumps({"dependencies": {"react": "^18.2.0"}}))
        gen = SBOMGenerator()
        components = gen.from_package_json(str(pkg))
        assert not components[0].version.startswith("^")

    def test_npm_purl_generated(self, tmp_path):
        """Components get pkg:npm purl."""
        pkg = tmp_path / "package.json"
        pkg.write_text(json.dumps({"dependencies": {"lodash": "4.17.21"}}))
        gen = SBOMGenerator()
        components = gen.from_package_json(str(pkg))
        assert components[0].purl.startswith("pkg:npm/")

    def test_missing_file_returns_empty(self):
        """Missing package.json returns empty list."""
        gen = SBOMGenerator()
        components = gen.from_package_json("/nonexistent/package.json")
        assert components == []

    def test_malformed_json_returns_empty(self, tmp_path):
        """Malformed JSON returns empty list."""
        pkg = tmp_path / "package.json"
        pkg.write_text("{invalid json}")
        gen = SBOMGenerator()
        components = gen.from_package_json(str(pkg))
        assert components == []


class TestSBOMGeneratorGenerate:
    """Tests for SBOMGenerator.generate()."""

    def test_generate_returns_sbom(self):
        """generate() returns an SBOM instance."""
        gen = SBOMGenerator()
        sbom = gen.generate("myapp", "1.0.0")
        assert isinstance(sbom, SBOM)

    def test_generate_sets_name_version(self):
        """generate() sets name and version."""
        gen = SBOMGenerator()
        sbom = gen.generate("codomyrmex", "2.0.0")
        assert sbom.name == "codomyrmex"
        assert sbom.version == "2.0.0"

    def test_generate_with_spdx_format(self):
        """generate() respects sbom_format parameter."""
        gen = SBOMGenerator()
        sbom = gen.generate("app", "1.0", sbom_format=SBOMFormat.SPDX)
        assert sbom.format == SBOMFormat.SPDX

    def test_generate_includes_parsed_components(self, tmp_path):
        """generate() includes components parsed before generation."""
        req = tmp_path / "requirements.txt"
        req.write_text("requests==2.31.0\nflask==3.0.0\n")
        gen = SBOMGenerator()
        gen.from_requirements(str(req))
        sbom = gen.generate("app", "1.0")
        assert len(sbom.components) == 2


class TestVulnerabilityScannerInSbom:
    """Tests for sbom.VulnerabilityScanner (SBOM-level, not scanning module)."""

    def test_scan_no_vulns(self):
        """scan() returns empty dict when no vulnerabilities."""
        comp = Component(name="safe-pkg", version="1.0.0")
        sbom = SBOM(name="app", version="1.0", components=[comp])
        scanner = VulnerabilityScanner()
        result = scanner.scan(sbom)
        assert result == {}

    def test_scan_detects_known_vuln(self):
        """scan() flags component with known vulnerability."""
        comp = Component(name="vuln-pkg", version="0.1.0")
        sbom = SBOM(name="app", version="1.0", components=[comp])
        scanner = VulnerabilityScanner()
        scanner.add_vulnerability_db({"vuln-pkg:0.1.0": ["CVE-2024-12345"]})
        result = scanner.scan(sbom)
        assert "vuln-pkg:0.1.0" in result
        assert "CVE-2024-12345" in result["vuln-pkg:0.1.0"]

    def test_scan_updates_component_vulnerabilities(self):
        """scan() updates component.vulnerabilities field."""
        comp = Component(name="vuln-pkg", version="0.1.0")
        sbom = SBOM(name="app", version="1.0", components=[comp])
        scanner = VulnerabilityScanner()
        scanner.add_vulnerability_db({"vuln-pkg:0.1.0": ["CVE-2024-99999"]})
        scanner.scan(sbom)
        assert "CVE-2024-99999" in comp.vulnerabilities

    def test_scan_multiple_components(self):
        """scan() checks all components."""
        c1 = Component(name="safe", version="1.0")
        c2 = Component(name="vuln", version="0.1")
        sbom = SBOM(name="app", version="1.0", components=[c1, c2])
        scanner = VulnerabilityScanner()
        scanner.add_vulnerability_db({"vuln:0.1": ["CVE-2024-00001"]})
        result = scanner.scan(sbom)
        assert "vuln:0.1" in result
        assert "safe:1.0" not in result

    def test_add_vulnerability_db_merges(self):
        """add_vulnerability_db() merges multiple calls."""
        scanner = VulnerabilityScanner()
        scanner.add_vulnerability_db({"pkg-a:1.0": ["CVE-1"]})
        scanner.add_vulnerability_db({"pkg-b:2.0": ["CVE-2"]})
        comp_a = Component(name="pkg-a", version="1.0")
        comp_b = Component(name="pkg-b", version="2.0")
        sbom = SBOM(name="app", version="1.0", components=[comp_a, comp_b])
        result = scanner.scan(sbom)
        assert "pkg-a:1.0" in result
        assert "pkg-b:2.0" in result


class TestSupplyChainVerifier:
    """Tests for SupplyChainVerifier."""

    def test_compute_file_hash_sha256(self, tmp_path):
        """compute_file_hash() produces correct SHA-256 hash."""
        f = tmp_path / "content.txt"
        f.write_bytes(b"hello world")
        verifier = SupplyChainVerifier()
        result = verifier.compute_file_hash(str(f))
        expected = hashlib.sha256(b"hello world").hexdigest()
        assert result == expected

    def test_compute_file_hash_sha512(self, tmp_path):
        """compute_file_hash() supports sha512 algorithm."""
        f = tmp_path / "content.txt"
        f.write_bytes(b"test data")
        verifier = SupplyChainVerifier()
        result = verifier.compute_file_hash(str(f), algorithm="sha512")
        expected = hashlib.sha512(b"test data").hexdigest()
        assert result == expected

    def test_verify_checksum_match(self):
        """verify_checksum() returns True when checksums match."""
        comp = Component(name="pkg", version="1.0", checksum="abc123")
        verifier = SupplyChainVerifier()
        assert verifier.verify_checksum(comp, "abc123") is True

    def test_verify_checksum_mismatch(self):
        """verify_checksum() returns False when checksums differ."""
        comp = Component(name="pkg", version="1.0", checksum="correct")
        verifier = SupplyChainVerifier()
        assert verifier.verify_checksum(comp, "wrong") is False

    def test_verify_digest_match(self, tmp_path):
        """verify_digest() accepts a matching hex digest (sha256sum format too)."""
        content = b"package content"
        f = tmp_path / "package.whl"
        f.write_bytes(content)
        digest = tmp_path / "package.whl.sha256"
        digest.write_text(f"{hashlib.sha256(content).hexdigest()}  package.whl\n")
        verifier = SupplyChainVerifier()
        assert verifier.verify_digest(str(f), str(digest)) is True

    def test_verify_digest_mismatch(self, tmp_path):
        """verify_digest() returns False when the digest differs."""
        f = tmp_path / "package.whl"
        f.write_bytes(b"real content")
        digest = tmp_path / "package.whl.sha256"
        digest.write_text("0" * 64)
        verifier = SupplyChainVerifier()
        assert verifier.verify_digest(str(f), str(digest)) is False

    def test_verify_digest_missing_file(self, tmp_path):
        """verify_digest() returns False when the digest file is missing."""
        f = tmp_path / "package.whl"
        f.write_bytes(b"content")
        verifier = SupplyChainVerifier()
        assert verifier.verify_digest(str(f), "/nonexistent/sha256") is False

    @pytest.mark.parametrize("key_type", ["ed25519", "rsa", "ec"])
    def test_verify_signature_real_keys(self, tmp_path, key_type):
        """verify_signature() checks a detached signature with the public key."""
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import ec, ed25519, padding, rsa

        content = b"package content"
        f = tmp_path / "package.whl"
        f.write_bytes(content)
        if key_type == "ed25519":
            key = ed25519.Ed25519PrivateKey.generate()
            signature = key.sign(content)
        elif key_type == "rsa":
            key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
            signature = key.sign(content, padding.PKCS1v15(), hashes.SHA256())
        else:
            key = ec.generate_private_key(ec.SECP256R1())
            signature = key.sign(content, ec.ECDSA(hashes.SHA256()))
        pub = tmp_path / "key.pub"
        pub.write_bytes(
            key.public_key().public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )
        sig = tmp_path / "package.whl.sig"
        sig.write_bytes(signature)
        verifier = SupplyChainVerifier()
        assert verifier.verify_signature(str(f), str(sig), str(pub)) is True

        # Tampered content fails.
        f.write_bytes(b"tampered content")
        assert verifier.verify_signature(str(f), str(sig), str(pub)) is False

    def test_verify_signature_base64_and_wrong_key(self, tmp_path):
        """Base64 signature files work; another key's signature does not."""
        import base64

        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ed25519

        content = b"release.tar.gz bytes"
        f = tmp_path / "release.tar.gz"
        f.write_bytes(content)
        signer = ed25519.Ed25519PrivateKey.generate()
        other = ed25519.Ed25519PrivateKey.generate()
        sig = tmp_path / "release.sig"
        sig.write_text(base64.b64encode(signer.sign(content)).decode() + "\n")

        def write_pub(key, name):
            path = tmp_path / name
            path.write_bytes(
                key.public_key().public_bytes(
                    serialization.Encoding.PEM,
                    serialization.PublicFormat.SubjectPublicKeyInfo,
                )
            )
            return str(path)

        verifier = SupplyChainVerifier()
        assert verifier.verify_signature(str(f), str(sig), write_pub(signer, "a.pub"))
        assert not verifier.verify_signature(
            str(f), str(sig), write_pub(other, "b.pub")
        )

    def test_verify_signature_rejects_a_bare_hash(self, tmp_path):
        """A hex digest in the .sig file is not a signature."""
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import ed25519

        content = b"package content"
        f = tmp_path / "package.whl"
        f.write_bytes(content)
        sig = tmp_path / "package.whl.sig"
        sig.write_text(hashlib.sha256(content).hexdigest())
        pub = tmp_path / "key.pub"
        pub.write_bytes(
            ed25519.Ed25519PrivateKey.generate()
            .public_key()
            .public_bytes(
                serialization.Encoding.PEM,
                serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )
        verifier = SupplyChainVerifier()
        assert verifier.verify_signature(str(f), str(sig), str(pub)) is False

    def test_verify_signature_missing_files(self, tmp_path):
        """Missing signature or key files return False."""
        f = tmp_path / "package.whl"
        f.write_bytes(b"content")
        verifier = SupplyChainVerifier()
        assert verifier.verify_signature(str(f), "/nonexistent/sig", "/no/key") is False
