"""SSL/TLS certificate validator.

Provides SSL/TLS certificate validation, monitoring, and security assessment.
"""

import socket
import ssl
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import OpenSSL

from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)


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

    def validate_certificate(self, hostname: str, port: int = 443) -> SSLValidationResult:
        """Validate SSL certificate for a hostname.

        Args:
            hostname: Hostname to check
            port: Port to connect to

        Returns:
            Validation result
        """
        try:
            # Get certificate from server
            cert_pem = self._get_certificate(hostname, port)

            # Parse with OpenSSL
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert_pem)

            # Extract info
            subject = dict(x509.get_subject().get_components())
            issuer = dict(x509.get_issuer().get_components())
            serial = x509.get_serial_number()

            # Check expiration
            not_after_bytes = x509.get_notAfter()
            if not_after_bytes:
                not_after_str = not_after_bytes.decode('utf-8')
                # OpenSSL format: YYYYMMDDhhmmssZ
                expires_at = datetime.strptime(not_after_str, '%Y%m%d%H%M%SZ').replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                days_left = (expires_at - now).days
                is_expired = days_left < 0
            else:
                days_left = None
                is_expired = False

            # Basic validation status
            is_valid = not x509.has_expired() and not is_expired
            errors = []
            if x509.has_expired():
                errors.append("Certificate has expired (OpenSSL check)")
            if is_expired:
                errors.append(f"Certificate expired {abs(days_left)} days ago")

            # Simplify subject/issuer for display
            subject_str = self._format_x509_name(subject)
            issuer_str = self._format_x509_name(issuer)

            return SSLValidationResult(
                hostname=hostname,
                port=port,
                valid=is_valid,
                certificate_info={
                    "version": x509.get_version(),
                    "signature_algorithm": x509.get_signature_algorithm().decode('utf-8'),
                    "not_before": x509.get_notBefore().decode('utf-8'),
                    "not_after": not_after_str,
                },
                validation_errors=errors if errors else None,
                expiration_days=days_left,
                issuer=issuer_str,
                subject=subject_str,
                serial_number=str(serial)
            )

        except Exception as e:
            logger.error(f"Certificate validation failed for {hostname}:{port}: {e}")
            return SSLValidationResult(
                hostname=hostname,
                port=port,
                valid=False,
                certificate_info={},
                validation_errors=[str(e)]
            )

    def _get_certificate(self, hostname: str, port: int) -> str:
        """Retrieve certificate from server."""
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE  # We just want to fetch it, not enforce validation during fetch

        with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert_bin = ssock.getpeercert(binary_form=True)
                if not cert_bin:
                    raise ValueError("No certificate retrieved")
                return ssl.DER_cert_to_PEM_cert(cert_bin)

    def _format_x509_name(self, components: dict[bytes, bytes]) -> str:
        """Format OpenSSL X509 Name components to string."""
        parts = []
        # Common Name
        if b'CN' in components:
            parts.append(f"CN={components[b'CN'].decode('utf-8', errors='ignore')}")
        # Organization
        if b'O' in components:
            parts.append(f"O={components[b'O'].decode('utf-8', errors='ignore')}")

        return ", ".join(parts) or "Unknown"
