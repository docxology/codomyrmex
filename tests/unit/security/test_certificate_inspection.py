"""Offline tests for CertificateValidator.inspect_pem using generated certificates."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID

from codomyrmex.security.digital.certificate_validator import CertificateValidator

NOW = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)


def _self_signed_pem(
    not_before: datetime,
    not_after: datetime,
    *,
    organization: str | None = "Example Org",
) -> str:
    key = ec.generate_private_key(ec.SECP256R1())
    attrs = [x509.NameAttribute(NameOID.COMMON_NAME, "example.test")]
    if organization:
        attrs.append(x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization))
    name = x509.Name(attrs)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(4242)
        .not_valid_before(not_before)
        .not_valid_after(not_after)
        .sign(key, hashes.SHA256())
    )
    return cert.public_bytes(serialization.Encoding.PEM).decode("ascii")


@pytest.mark.unit
def test_valid_certificate_details() -> None:
    pem = _self_signed_pem(NOW - timedelta(days=1), NOW + timedelta(days=30, hours=1))

    result = CertificateValidator().inspect_pem("example.test", 443, pem, now=NOW)

    assert result.valid is True
    assert result.validation_errors is None
    assert result.expiration_days == 30
    assert result.subject == "CN=example.test, O=Example Org"
    assert result.issuer == "CN=example.test, O=Example Org"
    assert result.serial_number == "4242"
    assert result.certificate_info == {
        "version": 2,
        "signature_algorithm": "ecdsa-with-SHA256",
        "not_before": "20260114120000Z",
        "not_after": "20260214130000Z",
    }


@pytest.mark.unit
def test_expired_certificate_is_reported() -> None:
    pem = _self_signed_pem(NOW - timedelta(days=60), NOW - timedelta(days=10))

    result = CertificateValidator().inspect_pem("example.test", 8443, pem, now=NOW)

    assert result.valid is False
    assert result.expiration_days == -10
    assert result.validation_errors == ["Certificate expired 10 days ago"]
    assert result.port == 8443


@pytest.mark.unit
def test_name_without_organization() -> None:
    pem = _self_signed_pem(
        NOW - timedelta(days=1), NOW + timedelta(days=1), organization=None
    )

    result = CertificateValidator().inspect_pem("example.test", 443, pem, now=NOW)

    assert result.subject == "CN=example.test"


@pytest.mark.unit
def test_unreachable_host_returns_invalid_result() -> None:
    # Port 9 on localhost is not listening in CI; the error is reported, not raised.
    result = CertificateValidator(timeout=2).validate_certificate("127.0.0.1", 9)

    assert result.valid is False
    assert result.certificate_info == {}
    assert result.validation_errors
