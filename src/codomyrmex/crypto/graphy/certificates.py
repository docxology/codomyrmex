"""X.509 certificate operations: generation, CSR, validation, PEM I/O."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Any

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, rsa
from cryptography.x509.oid import NameOID

from codomyrmex.crypto.exceptions import CertificateError
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class ValidationResult:
    """Result of certificate chain validation."""

    valid: bool
    errors: list[str] = field(default_factory=list)
    chain_length: int = 0


def _get_signing_params(private_key: Any) -> dict:
    """Determine the signing algorithm based on key type."""
    if isinstance(private_key, rsa.RSAPrivateKey):
        return {"algorithm": hashes.SHA256()}
    elif isinstance(private_key, ec.EllipticCurvePrivateKey):
        return {"algorithm": hashes.SHA256()}
    elif isinstance(private_key, ed25519.Ed25519PrivateKey):
        return {"algorithm": None}
    else:
        return {"algorithm": hashes.SHA256()}


def generate_self_signed_cert(
    common_name: str,
    key_pair: Any,
    days: int = 365,
) -> Any:
    """Generate a self-signed X.509 certificate.

    Args:
        common_name: The CN (Common Name) for the certificate subject.
        key_pair: Object with .private_key and .public_key attributes, or a private key directly.
        days: Certificate validity period in days.

    Returns:
        x509.Certificate object.

    Raises:
        CertificateError: On certificate generation failure.
    """
    try:
        # Support both KeyPair objects and raw private keys
        if hasattr(key_pair, "private_key"):
            private_key = key_pair.private_key
            public_key = key_pair.public_key
        else:
            private_key = key_pair
            public_key = private_key.public_key()

        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])

        now = datetime.datetime.now(datetime.timezone.utc)
        signing_params = _get_signing_params(private_key)

        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(public_key)
            .serial_number(x509.random_serial_number())
            .not_valid_before(now)
            .not_valid_after(now + datetime.timedelta(days=days))
            .add_extension(
                x509.BasicConstraints(ca=True, path_length=None),
                critical=True,
            )
            .sign(private_key, **signing_params)
        )
        logger.debug("Self-signed certificate generated for CN=%s, valid %d days", common_name, days)
        return cert
    except Exception as exc:
        raise CertificateError(f"Self-signed certificate generation failed: {exc}") from exc


def generate_csr(
    common_name: str,
    key_pair: Any,
    **subject_attrs: str,
) -> Any:
    """Generate a Certificate Signing Request (CSR).

    Args:
        common_name: The CN for the CSR subject.
        key_pair: Object with .private_key attribute, or a private key directly.
        **subject_attrs: Additional subject attributes (e.g., organization, country).
            Supported keys: organization, country, state, locality, email.

    Returns:
        x509.CertificateSigningRequest object.

    Raises:
        CertificateError: On CSR generation failure.
    """
    try:
        if hasattr(key_pair, "private_key"):
            private_key = key_pair.private_key
        else:
            private_key = key_pair

        name_attributes = [x509.NameAttribute(NameOID.COMMON_NAME, common_name)]

        attr_map = {
            "organization": NameOID.ORGANIZATION_NAME,
            "country": NameOID.COUNTRY_NAME,
            "state": NameOID.STATE_OR_PROVINCE_NAME,
            "locality": NameOID.LOCALITY_NAME,
            "email": NameOID.EMAIL_ADDRESS,
        }
        for attr_name, oid in attr_map.items():
            if attr_name in subject_attrs:
                name_attributes.append(x509.NameAttribute(oid, subject_attrs[attr_name]))

        signing_params = _get_signing_params(private_key)

        csr = (
            x509.CertificateSigningRequestBuilder()
            .subject_name(x509.Name(name_attributes))
            .sign(private_key, **signing_params)
        )
        logger.debug("CSR generated for CN=%s", common_name)
        return csr
    except Exception as exc:
        raise CertificateError(f"CSR generation failed: {exc}") from exc


def validate_certificate_chain(cert_chain: list) -> ValidationResult:
    """Validate a certificate chain (basic checks).

    Performs:
    - Date validity checks (not_valid_before, not_valid_after)
    - Issuer/subject chain linkage (each cert's issuer matches next cert's subject)
    - Signature verification (each cert signed by next cert's key)

    Args:
        cert_chain: List of x509.Certificate objects, leaf first, root last.

    Returns:
        ValidationResult with validity status and any errors.

    Raises:
        CertificateError: On unexpected validation errors.
    """
    errors: list[str] = []

    if not cert_chain:
        return ValidationResult(valid=False, errors=["Empty certificate chain"], chain_length=0)

    now = datetime.datetime.now(datetime.timezone.utc)

    try:
        for i, cert in enumerate(cert_chain):
            # Check date validity
            if now < cert.not_valid_before_utc:
                errors.append(f"Certificate {i}: not yet valid (not_valid_before={cert.not_valid_before_utc})")
            if now > cert.not_valid_after_utc:
                errors.append(f"Certificate {i}: expired (not_valid_after={cert.not_valid_after_utc})")

        # Check issuer/subject chain linkage
        for i in range(len(cert_chain) - 1):
            current = cert_chain[i]
            issuer_cert = cert_chain[i + 1]

            if current.issuer != issuer_cert.subject:
                errors.append(
                    f"Certificate {i}: issuer does not match subject of certificate {i + 1}"
                )

            # Verify signature
            try:
                issuer_public_key = issuer_cert.public_key()
                issuer_public_key.verify(
                    current.signature,
                    current.tbs_certificate_bytes,
                    *_get_verify_params(current),
                )
            except Exception as verify_exc:
                errors.append(f"Certificate {i}: signature verification failed: {verify_exc}")

        valid = len(errors) == 0
        logger.debug(
            "Certificate chain validation: valid=%s, chain_length=%d, errors=%d",
            valid,
            len(cert_chain),
            len(errors),
        )
        return ValidationResult(valid=valid, errors=errors, chain_length=len(cert_chain))

    except Exception as exc:
        raise CertificateError(f"Certificate chain validation failed: {exc}") from exc


def _get_verify_params(cert: Any) -> tuple:
    """Get verification parameters based on the certificate's signature algorithm."""
    from cryptography.hazmat.primitives.asymmetric import padding as asym_padding

    sig_algo = cert.signature_algorithm_oid.dotted_string

    # RSA algorithms
    if sig_algo.startswith("1.2.840.113549"):
        return (
            asym_padding.PKCS1v15(),
            cert.signature_hash_algorithm,
        )
    # EC algorithms
    elif sig_algo.startswith("1.2.840.10045"):
        return (
            ec.ECDSA(cert.signature_hash_algorithm),
        )
    # Ed25519
    elif sig_algo == "1.3.101.112":
        return ()
    else:
        # Default to PKCS1v15 for unknown
        return (
            asym_padding.PKCS1v15(),
            cert.signature_hash_algorithm,
        )


def load_certificate_pem(pem_data: bytes) -> Any:
    """Load an X.509 certificate from PEM data.

    Args:
        pem_data: PEM-encoded certificate bytes.

    Returns:
        x509.Certificate object.

    Raises:
        CertificateError: On loading failure.
    """
    try:
        cert = x509.load_pem_x509_certificate(pem_data)
        logger.debug("Certificate loaded from PEM, subject=%s", cert.subject)
        return cert
    except Exception as exc:
        raise CertificateError(f"Failed to load certificate from PEM: {exc}") from exc


def export_certificate_pem(certificate: Any) -> bytes:
    """Export an X.509 certificate to PEM format.

    Args:
        certificate: x509.Certificate object.

    Returns:
        PEM-encoded certificate bytes.

    Raises:
        CertificateError: On export failure.
    """
    try:
        pem = certificate.public_bytes(serialization.Encoding.PEM)
        logger.debug("Certificate exported to PEM, length=%d", len(pem))
        return pem
    except Exception as exc:
        raise CertificateError(f"Certificate PEM export failed: {exc}") from exc
