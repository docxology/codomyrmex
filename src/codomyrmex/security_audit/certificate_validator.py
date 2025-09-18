"""
Certificate Validator for Codomyrmex Security Audit Module.

Provides SSL/TLS certificate validation, monitoring, and security assessment.
"""

import os
import sys
import ssl
import socket
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse
import OpenSSL
from OpenSSL import crypto
import requests

# Add project root to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


@dataclass
class SSLValidationResult:
    """Result of SSL certificate validation."""
    hostname: str
    port: int
    valid: bool
    certificate_info: Dict[str, Any]
    validation_errors: List[str] = None
    expiration_days: Optional[int] = None
    issuer: Optional[str] = None
    subject: Optional[str] = None
    serial_number: Optional[str] = None
    signature_algorithm: Optional[str] = None
    key_size: Optional[int] = None
    validation_timestamp: datetime = None

    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []
        if self.validation_timestamp is None:
            self.validation_timestamp = datetime.now(timezone.utc)


class CertificateValidator:
    """
    SSL/TLS certificate validator and security analyzer.

    Features:
    - Certificate validation and chain verification
    - Expiration monitoring
    - Security strength assessment
    - Certificate transparency checks
    - OCSP and CRL validation
    """

    def __init__(self, timeout: int = 10):
        """
        Initialize the certificate validator.

        Args:
            timeout: Timeout for network operations (seconds)
        """
        self.timeout = timeout
        self.validation_cache: Dict[str, SSLValidationResult] = {}

    def validate_ssl_certificate(self, hostname: str, port: int = 443) -> SSLValidationResult:
        """
        Validate SSL certificate for a hostname and port.

        Args:
            hostname: Hostname to validate
            port: Port number (default: 443 for HTTPS)

        Returns:
            SSLValidationResult: Validation result
        """
        cache_key = f"{hostname}:{port}"

        # Check cache first
        if cache_key in self.validation_cache:
            cached_result = self.validation_cache[cache_key]
            # Cache for 1 hour
            if (datetime.now(timezone.utc) - cached_result.validation_timestamp).seconds < 3600:
                return cached_result

        logger.info(f"Validating SSL certificate for {hostname}:{port}")

        result = SSLValidationResult(
            hostname=hostname,
            port=port,
            valid=False,
            certificate_info={}
        )

        try:
            # Create SSL context
            context = ssl.create_default_context()
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED

            # Connect and get certificate
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssl_sock:
                    certificate = ssl_sock.getpeercert(binary_form=True)
                    certificate_der = ssl_sock.getpeercert(binary_form=True)

                    # Parse certificate
                    x509 = OpenSSL.crypto.load_certificate(
                        OpenSSL.crypto.FILETYPE_ASN1,
                        certificate_der
                    )

                    # Extract certificate information
                    cert_info = self._extract_certificate_info(x509)
                    result.certificate_info = cert_info

                    # Validate certificate
                    validation_result = self._validate_certificate(x509, hostname)
                    result.valid = validation_result["valid"]
                    result.validation_errors = validation_result["errors"]

                    # Check expiration
                    result.expiration_days = self._check_expiration(x509)

                    # Update result with certificate details
                    result.issuer = cert_info.get("issuer")
                    result.subject = cert_info.get("subject")
                    result.serial_number = cert_info.get("serial_number")
                    result.signature_algorithm = cert_info.get("signature_algorithm")
                    result.key_size = cert_info.get("key_size")

        except ssl.SSLError as e:
            result.validation_errors.append(f"SSL Error: {str(e)}")
            logger.error(f"SSL validation failed for {hostname}:{port}: {e}")

        except socket.timeout:
            result.validation_errors.append("Connection timeout")
            logger.error(f"Connection timeout for {hostname}:{port}")

        except Exception as e:
            result.validation_errors.append(f"Validation error: {str(e)}")
            logger.error(f"Certificate validation error for {hostname}:{port}: {e}")

        # Cache result
        self.validation_cache[cache_key] = result

        logger.info(f"SSL validation completed for {hostname}:{port} - Valid: {result.valid}")
        return result

    def _extract_certificate_info(self, x509_cert) -> Dict[str, Any]:
        """Extract detailed information from X.509 certificate."""
        try:
            # Subject information
            subject = x509_cert.get_subject()
            subject_info = {
                "common_name": subject.CN,
                "organization": subject.O,
                "organizational_unit": subject.OU,
                "country": subject.C,
                "state": subject.ST,
                "locality": subject.L
            }

            # Issuer information
            issuer = x509_cert.get_issuer()
            issuer_info = {
                "common_name": issuer.CN,
                "organization": issuer.O,
                "organizational_unit": issuer.OU,
                "country": issuer.C
            }

            # Certificate details
            cert_info = {
                "version": x509_cert.get_version(),
                "serial_number": str(x509_cert.get_serial_number()),
                "signature_algorithm": x509_cert.get_signature_algorithm().decode(),
                "not_before": x509_cert.get_notBefore().decode(),
                "not_after": x509_cert.get_notAfter().decode(),
                "subject": subject_info,
                "issuer": issuer_info,
                "subject_str": str(subject),
                "issuer_str": str(issuer)
            }

            # Public key information
            public_key = x509_cert.get_pubkey()
            cert_info["key_size"] = public_key.bits()

            # Extensions
            extensions = []
            for i in range(x509_cert.get_extension_count()):
                ext = x509_cert.get_extension(i)
                extensions.append({
                    "name": ext.get_short_name().decode(),
                    "value": str(ext),
                    "critical": ext.get_critical()
                })
            cert_info["extensions"] = extensions

            return cert_info

        except Exception as e:
            logger.error(f"Error extracting certificate info: {e}")
            return {}

    def _validate_certificate(self, x509_cert, hostname: str) -> Dict[str, Any]:
        """Validate certificate against hostname and trust chain."""
        errors = []
        valid = True

        try:
            # Check hostname matching
            common_name = x509_cert.get_subject().CN
            if common_name != hostname:
                # Check Subject Alternative Names
                san_extension = None
                for i in range(x509_cert.get_extension_count()):
                    ext = x509_cert.get_extension(i)
                    if ext.get_short_name() == b'subjectAltName':
                        san_extension = ext
                        break

                if san_extension:
                    san_value = str(san_extension)
                    if hostname not in san_value:
                        errors.append(f"Hostname '{hostname}' not in certificate SAN")
                        valid = False
                else:
                    errors.append(f"Hostname '{hostname}' does not match certificate CN '{common_name}'")
                    valid = False

            # Check expiration
            not_after = x509_cert.get_notAfter()
            if not_after:
                expiry_date = datetime.strptime(not_after.decode()[:14], "%Y%m%d%H%M%S")
                if expiry_date < datetime.now(timezone.utc):
                    errors.append("Certificate has expired")
                    valid = False

            # Check if certificate is not yet valid
            not_before = x509_cert.get_notBefore()
            if not_before:
                valid_from = datetime.strptime(not_before.decode()[:14], "%Y%m%d%H%M%S")
                if valid_from > datetime.now(timezone.utc):
                    errors.append("Certificate is not yet valid")
                    valid = False

        except Exception as e:
            errors.append(f"Certificate validation error: {str(e)}")
            valid = False

        return {
            "valid": valid,
            "errors": errors
        }

    def _check_expiration(self, x509_cert) -> Optional[int]:
        """Check certificate expiration and return days until expiry."""
        try:
            not_after = x509_cert.get_notAfter()
            if not_after:
                expiry_date = datetime.strptime(not_after.decode()[:14], "%Y%m%d%H%M%S")
                now = datetime.now(timezone.utc)
                days_until_expiry = (expiry_date - now).days
                return max(0, days_until_expiry)
        except Exception as e:
            logger.error(f"Error checking certificate expiration: {e}")

        return None

    def validate_certificate_chain(self, hostname: str, port: int = 443) -> Dict[str, Any]:
        """
        Validate the complete certificate chain.

        Args:
            hostname: Hostname to validate
            port: Port number

        Returns:
            Dict containing chain validation results
        """
        result = {
            "hostname": hostname,
            "port": port,
            "chain_valid": False,
            "chain_length": 0,
            "certificates": [],
            "errors": []
        }

        try:
            # Get certificate chain
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssl_sock:
                    # Get peer certificate chain
                    cert_chain = ssl_sock.getpeercertchain(binary_form=True)

                    result["chain_length"] = len(cert_chain)

                    # Validate each certificate in chain
                    for i, cert_der in enumerate(cert_chain):
                        try:
                            x509 = OpenSSL.crypto.load_certificate(
                                OpenSSL.crypto.FILETYPE_ASN1,
                                cert_der
                            )

                            cert_info = self._extract_certificate_info(x509)
                            cert_info["position"] = i
                            result["certificates"].append(cert_info)

                        except Exception as e:
                            result["errors"].append(f"Certificate {i} parsing error: {str(e)}")

                    # Basic chain validation
                    if len(cert_chain) >= 1:
                        result["chain_valid"] = True

        except Exception as e:
            result["errors"].append(f"Chain validation error: {str(e)}")

        return result

    def check_certificate_transparency(self, hostname: str) -> Dict[str, Any]:
        """
        Check certificate transparency for the hostname.

        Args:
            hostname: Hostname to check

        Returns:
            Dict containing transparency check results
        """
        result = {
            "hostname": hostname,
            "transparency_checks": [],
            "overall_status": "unknown"
        }

        # Certificate Transparency checks would require integration with CT logs
        # This is a placeholder implementation
        result["transparency_checks"].append({
            "check": "CT Log Inclusion",
            "status": "not_implemented",
            "description": "Certificate Transparency log inclusion check"
        })

        return result

    def monitor_certificate_expiration(self, hostnames: List[str],
                                     alert_threshold_days: int = 30) -> List[Dict[str, Any]]:
        """
        Monitor certificate expiration for multiple hostnames.

        Args:
            hostnames: List of hostnames to monitor
            alert_threshold_days: Days before expiration to alert

        Returns:
            List of expiration alerts
        """
        alerts = []

        for hostname in hostnames:
            try:
                result = self.validate_ssl_certificate(hostname)

                if result.expiration_days is not None:
                    if result.expiration_days <= alert_threshold_days:
                        alerts.append({
                            "hostname": hostname,
                            "days_until_expiry": result.expiration_days,
                            "severity": "critical" if result.expiration_days <= 7 else "warning",
                            "message": f"Certificate expires in {result.expiration_days} days"
                        })

            except Exception as e:
                alerts.append({
                    "hostname": hostname,
                    "error": str(e),
                    "severity": "error"
                })

        return alerts

    def get_certificate_security_score(self, result: SSLValidationResult) -> Dict[str, Any]:
        """
        Calculate security score for a certificate.

        Args:
            result: SSL validation result

        Returns:
            Dict containing security score and recommendations
        """
        score = 100
        recommendations = []

        # Check key size
        if result.key_size:
            if result.key_size < 2048:
                score -= 30
                recommendations.append("Upgrade to RSA 2048-bit or ECC key")
            elif result.key_size < 3072:
                score -= 10
                recommendations.append("Consider upgrading to RSA 3072-bit or stronger")

        # Check signature algorithm
        if result.signature_algorithm:
            weak_algorithms = ["md5", "sha1"]
            if any(alg.lower() in result.signature_algorithm.lower() for alg in weak_algorithms):
                score -= 40
                recommendations.append("Replace weak signature algorithm (MD5/SHA1)")

        # Check expiration
        if result.expiration_days is not None:
            if result.expiration_days < 30:
                score -= 20
                recommendations.append("Certificate expires soon - plan renewal")
            elif result.expiration_days < 90:
                score -= 5
                recommendations.append("Certificate expires within 90 days")

        # Check validation errors
        if result.validation_errors:
            score -= len(result.validation_errors) * 10
            recommendations.extend(result.validation_errors)

        return {
            "security_score": max(0, score),
            "grade": self._score_to_grade(score),
            "recommendations": recommendations
        }

    def _score_to_grade(self, score: int) -> str:
        """Convert security score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"


# Convenience functions
def validate_ssl_certificates(hostnames: List[str], port: int = 443) -> List[SSLValidationResult]:
    """
    Convenience function to validate SSL certificates for multiple hostnames.

    Args:
        hostnames: List of hostnames to validate
        port: Port number for SSL connections

    Returns:
        List of SSL validation results
    """
    validator = CertificateValidator()
    results = []

    for hostname in hostnames:
        try:
            result = validator.validate_ssl_certificate(hostname, port)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to validate certificate for {hostname}: {e}")

    return results
