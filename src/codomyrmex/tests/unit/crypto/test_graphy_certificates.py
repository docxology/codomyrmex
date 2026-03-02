"""Tests for codomyrmex.crypto.graphy.certificates."""

from __future__ import annotations

import datetime

import pytest
from cryptography import x509

from codomyrmex.crypto.exceptions import CertificateError
from codomyrmex.crypto.graphy.asymmetric import (
    KeyPair,
    generate_ec_keypair,
    generate_rsa_keypair,
)
from codomyrmex.crypto.graphy.certificates import (
    ValidationResult,
    export_certificate_pem,
    generate_csr,
    generate_self_signed_cert,
    load_certificate_pem,
    validate_certificate_chain,
)


@pytest.fixture(scope="module")
def rsa_keypair() -> KeyPair:
    return generate_rsa_keypair(2048)


@pytest.fixture(scope="module")
def ec_keypair() -> KeyPair:
    return generate_ec_keypair("secp256r1")


@pytest.mark.crypto
@pytest.mark.unit
class TestSelfSignedCert:
    """Test suite for SelfSignedCert."""
    def test_generate_rsa(self, rsa_keypair: KeyPair) -> None:
        """Test functionality: generate rsa."""
        cert = generate_self_signed_cert("test.example.com", rsa_keypair)
        assert isinstance(cert, x509.Certificate)
        cn = cert.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)
        assert cn[0].value == "test.example.com"

    def test_generate_ec(self, ec_keypair: KeyPair) -> None:
        """Test functionality: generate ec."""
        cert = generate_self_signed_cert("ec.example.com", ec_keypair)
        assert isinstance(cert, x509.Certificate)
        cn = cert.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)
        assert cn[0].value == "ec.example.com"

    def test_self_signed_issuer_equals_subject(self, rsa_keypair: KeyPair) -> None:
        """Test functionality: self signed issuer equals subject."""
        cert = generate_self_signed_cert("self.signed", rsa_keypair)
        assert cert.issuer == cert.subject

    def test_validity_period(self, rsa_keypair: KeyPair) -> None:
        """Test functionality: validity period."""
        cert = generate_self_signed_cert("validity.test", rsa_keypair, days=30)
        now = datetime.datetime.now(datetime.UTC)
        assert cert.not_valid_before_utc <= now
        delta = cert.not_valid_after_utc - cert.not_valid_before_utc
        assert 29 <= delta.days <= 31

    def test_basic_constraints_ca(self, rsa_keypair: KeyPair) -> None:
        """Test functionality: basic constraints ca."""
        cert = generate_self_signed_cert("ca.test", rsa_keypair)
        bc = cert.extensions.get_extension_for_class(x509.BasicConstraints)
        assert bc.value.ca is True


@pytest.mark.crypto
@pytest.mark.unit
class TestCSR:
    """Test suite for CSR."""
    def test_generate_basic(self, rsa_keypair: KeyPair) -> None:
        """Test functionality: generate basic."""
        csr = generate_csr("csr.example.com", rsa_keypair)
        assert isinstance(csr, x509.CertificateSigningRequest)
        cn = csr.subject.get_attributes_for_oid(x509.oid.NameOID.COMMON_NAME)
        assert cn[0].value == "csr.example.com"

    def test_generate_with_attrs(self, rsa_keypair: KeyPair) -> None:
        """Test functionality: generate with attrs."""
        csr = generate_csr(
            "attrs.example.com",
            rsa_keypair,
            organization="Test Org",
            country="US",
        )
        org = csr.subject.get_attributes_for_oid(x509.oid.NameOID.ORGANIZATION_NAME)
        assert org[0].value == "Test Org"
        country = csr.subject.get_attributes_for_oid(x509.oid.NameOID.COUNTRY_NAME)
        assert country[0].value == "US"

    def test_csr_is_valid(self, rsa_keypair: KeyPair) -> None:
        """Test functionality: csr is valid."""
        csr = generate_csr("valid.test", rsa_keypair)
        assert csr.is_signature_valid is True

    def test_ec_csr(self, ec_keypair: KeyPair) -> None:
        """Test functionality: ec csr."""
        csr = generate_csr("ec-csr.test", ec_keypair)
        assert csr.is_signature_valid is True


@pytest.mark.crypto
@pytest.mark.unit
class TestCertificatePEM:
    """Test suite for CertificatePEM."""
    def test_export_and_reimport(self, rsa_keypair: KeyPair) -> None:
        """Test functionality: export and reimport."""
        cert = generate_self_signed_cert("roundtrip.test", rsa_keypair)
        pem = export_certificate_pem(cert)
        assert pem.startswith(b"-----BEGIN CERTIFICATE-----")

        loaded = load_certificate_pem(pem)
        assert loaded.subject == cert.subject
        assert loaded.serial_number == cert.serial_number

    def test_export_ec_cert(self, ec_keypair: KeyPair) -> None:
        """Test functionality: export ec cert."""
        cert = generate_self_signed_cert("ec-pem.test", ec_keypair)
        pem = export_certificate_pem(cert)
        loaded = load_certificate_pem(pem)
        assert loaded.subject == cert.subject

    def test_load_invalid_pem(self) -> None:
        """Test functionality: load invalid pem."""
        with pytest.raises(CertificateError):
            load_certificate_pem(b"not a certificate")


@pytest.mark.crypto
@pytest.mark.unit
class TestCertificateChainValidation:
    """Test suite for CertificateChainValidation."""
    def test_single_self_signed_valid(self, rsa_keypair: KeyPair) -> None:
        """Test functionality: single self signed valid."""
        cert = generate_self_signed_cert("root.test", rsa_keypair)
        result = validate_certificate_chain([cert])
        assert isinstance(result, ValidationResult)
        assert result.valid is True
        assert result.chain_length == 1
        assert len(result.errors) == 0

    def test_empty_chain(self) -> None:
        """Test functionality: empty chain."""
        result = validate_certificate_chain([])
        assert result.valid is False
        assert "Empty certificate chain" in result.errors[0]
        assert result.chain_length == 0

    def test_two_cert_chain(self) -> None:
        """Test functionality: two cert chain."""
        # Generate CA
        ca_kp = generate_rsa_keypair(2048)
        ca_cert = generate_self_signed_cert("Root CA", ca_kp, days=365)

        # Generate leaf signed by CA
        leaf_kp = generate_rsa_keypair(2048)
        now = datetime.datetime.now(datetime.UTC)
        leaf_cert = (
            x509.CertificateBuilder()
            .subject_name(x509.Name([x509.NameAttribute(x509.oid.NameOID.COMMON_NAME, "leaf.test")]))
            .issuer_name(ca_cert.subject)
            .public_key(leaf_kp.public_key)
            .serial_number(x509.random_serial_number())
            .not_valid_before(now)
            .not_valid_after(now + datetime.timedelta(days=30))
            .sign(ca_kp.private_key, algorithm=__import__("cryptography.hazmat.primitives.hashes", fromlist=["SHA256"]).SHA256())
        )

        result = validate_certificate_chain([leaf_cert, ca_cert])
        assert result.valid is True
        assert result.chain_length == 2

    def test_mismatched_chain_issuer(self, rsa_keypair: KeyPair) -> None:
        """Test functionality: mismatched chain issuer."""
        # Two independent self-signed certs have mismatched issuer/subject
        kp1 = generate_rsa_keypair(2048)
        kp2 = generate_rsa_keypair(2048)
        cert1 = generate_self_signed_cert("Cert A", kp1)
        cert2 = generate_self_signed_cert("Cert B", kp2)

        result = validate_certificate_chain([cert1, cert2])
        assert result.valid is False
        assert any("issuer does not match" in e for e in result.errors)
