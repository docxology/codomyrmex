"""SSL/TLS certificate validator.

Provides SSL/TLS certificate validation, monitoring, and security assessment.
"""

import socket
import ssl
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from cryptography import x509
from cryptography.x509.oid import NameOID

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

# ASN.1 GeneralizedTime layout used by OpenSSL when printing validity dates.
_ASN1_TIME_FORMAT = "%Y%m%d%H%M%SZ"


@dataclass
class SSLValidationResult:
    """Result of SSL certificate validation."""

    hostname: str
    port: int
    valid: bool
    certificate_info: dict[str, Any]
    validation_errors: list[str] | None = None
    expiration_days: int | None = None
    issuer: str | None = None
    subject: str | None = None
    serial_number: str | None = None


class CertificateValidator:
    """Validator for SSL/TLS certificates."""

    def __init__(self, timeout: int = 10):
        """Initialize validator.

        Args:
            timeout: Connection timeout in seconds
        """
        self.timeout = timeout

    def validate_certificate(
        self, hostname: str, port: int = 443
    ) -> SSLValidationResult:
        """Validate SSL certificate for a hostname.

        Args:
            hostname: Hostname to check
            port: Port to connect to

        Returns:
            Validation result
        """
        try:
            cert_pem = self._get_certificate(hostname, port)
            return self.inspect_pem(hostname, port, cert_pem)

        except Exception as e:
            logger.error(
                "Certificate validation failed for %s:%s: %s", hostname, port, e
            )
            return SSLValidationResult(
                hostname=hostname,
                port=port,
                valid=False,
                certificate_info={},
                validation_errors=[str(e)],
            )

    def inspect_pem(
        self, hostname: str, port: int, cert_pem: str, now: datetime | None = None
    ) -> SSLValidationResult:
        """Assess a PEM-encoded certificate (expiry, subject, issuer, serial).

        Args:
            hostname: Hostname the certificate was retrieved for.
            port: Port the certificate was retrieved from.
            cert_pem: PEM-encoded certificate.
            now: Reference time (defaults to the current UTC time).

        Returns:
            Validation result.
        """
        cert = x509.load_pem_x509_certificate(cert_pem.encode("ascii"))
        now = now or datetime.now(UTC)

        expires_at = cert.not_valid_after_utc
        days_left = (expires_at - now).days
        is_valid = now <= expires_at
        errors = [] if is_valid else [f"Certificate expired {abs(days_left)} days ago"]

        return SSLValidationResult(
            hostname=hostname,
            port=port,
            valid=is_valid,
            certificate_info={
                # 0-based like the X.509 version field (2 == v3).
                "version": cert.version.value,
                "signature_algorithm": cert.signature_algorithm_oid._name,
                "not_before": cert.not_valid_before_utc.strftime(_ASN1_TIME_FORMAT),
                "not_after": expires_at.strftime(_ASN1_TIME_FORMAT),
            },
            validation_errors=errors or None,
            expiration_days=days_left,
            issuer=self._format_x509_name(cert.issuer),
            subject=self._format_x509_name(cert.subject),
            serial_number=str(cert.serial_number),
        )

    def _get_certificate(self, hostname: str, port: int) -> str:
        """Retrieve certificate from server."""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = (
            ssl.CERT_NONE
        )  # We just want to fetch it, not enforce validation during fetch

        with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert_bin = ssock.getpeercert(binary_form=True)
                if not cert_bin:
                    raise ValueError("No certificate retrieved")
                return ssl.DER_cert_to_PEM_cert(cert_bin)

    @staticmethod
    def _format_x509_name(name: x509.Name) -> str:
        """Format the CN and O attributes of an X.509 name for display."""
        parts = [
            f"{label}={attr.value}"
            for label, oid in (
                ("CN", NameOID.COMMON_NAME),
                ("O", NameOID.ORGANIZATION_NAME),
            )
            for attr in name.get_attributes_for_oid(oid)[:1]
        ]
        return ", ".join(parts) or "Unknown"


def validate_ssl_certificates(
    hostname: str, port: int = 443, timeout: int = 10
) -> dict[str, Any]:
    """Validate SSL certificate for *hostname* and return a plain dict result.

    Args:
        hostname: Hostname (or IP) to connect to.
        port: TCP port (default 443).
        timeout: Connection timeout in seconds (default 10).

    Returns:
        dict representation of :class:`SSLValidationResult`.
    """
    validator = CertificateValidator(timeout=timeout)
    result = validator.validate_certificate(hostname, port)
    return {
        "hostname": result.hostname,
        "port": result.port,
        "valid": result.valid,
        "certificate_info": result.certificate_info,
        "validation_errors": result.validation_errors,
        "expiration_days": result.expiration_days,
        "issuer": result.issuer,
        "subject": result.subject,
        "serial_number": result.serial_number,
    }
