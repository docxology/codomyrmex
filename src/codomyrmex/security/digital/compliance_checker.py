from datetime import datetime, timezone
from pathlib import Path
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Tuple
import logging
import os
import os
import os
import os
import os
import os

from dataclasses import dataclass
from enum import Enum

from codomyrmex.logging_monitoring.logger_config import get_logger







Compliance Checker for Codomyrmex Security Audit Module.

Provides compliance validation against security standards including:
- OWASP Top 10
- NIST 800-53
- ISO 27001
- PCI DSS
- GDPR
- HIPAA
"""

try:
    logger = get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)

class ComplianceStandard(Enum):
    """Supported compliance standards."""
    OWASP_TOP_10 = "OWASP_TOP_10"
    NIST_800_53 = "NIST_800_53"
    ISO_27001 = "ISO_27001"
    PCI_DSS = "PCI_DSS"
    GDPR = "GDPR"
    HIPAA = "HIPAA"

@dataclass
class ComplianceRequirement:
    """Represents a compliance requirement."""
    standard: str
    requirement_id: str
    title: str
    description: str
    severity: str
    category: str
    automated_check: bool = True
    evidence_required: bool = False

@dataclass
class ComplianceCheckResult:
    """Result of a compliance check."""
    requirement: ComplianceRequirement
    status: str  # "compliant", "non_compliant", "not_applicable", "manual_review_required"
    evidence: str
    findings: List[str]
    remediation: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        """Brief description of __post_init__.
        
        Args:
            self : Description of self
        
            Returns: Description of return value
        """
"""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

class ComplianceChecker:
    """
    Comprehensive compliance checker against multiple security standards.

    Validates code and configurations against industry security standards
    and provides detailed compliance reports with remediation guidance.
    """

    def __init__(self, standards: Optional[List[str]] = None):
        """
        Initialize the compliance checker.

        Args:
            standards: List of compliance standards to check against
        """
        self.standards = standards or ["OWASP_TOP_10"]
        self.requirements = self._load_requirements()
        self.check_functions = self._load_check_functions()

    def _load_requirements(self) -> Dict[str, List[ComplianceRequirement]]:
        """Load compliance requirements for all supported standards."""
        requirements = {}

        # OWASP Top 10 2021
        requirements["OWASP_TOP_10"] = [
            ComplianceRequirement(
                standard="OWASP_TOP_10",
                requirement_id="A01:2021",
                title="Broken Access Control",
                description="Restrict access to authorized users only",
                severity="CRITICAL",
                category="Access Control",
                automated_check=False,
                evidence_required=True
            ),
            ComplianceRequirement(
                standard="OWASP_TOP_10",
                requirement_id="A02:2021",
                title="Cryptographic Failures",
                description="Protect sensitive data with proper cryptography",
                severity="HIGH",
                category="Cryptography",
                automated_check=True
            ),
            ComplianceRequirement(
                standard="OWASP_TOP_10",
                requirement_id="A03:2021",
                title="Injection",
                description="Prevent injection attacks (SQL, command, etc.)",
                severity="CRITICAL",
                category="Injection",
                automated_check=True
            ),
            ComplianceRequirement(
                standard="OWASP_TOP_10",
                requirement_id="A04:2021",
                title="Insecure Design",
                description="Secure by design principles",
                severity="HIGH",
                category="Design",
                automated_check=False,
                evidence_required=True
            ),
            ComplianceRequirement(
                standard="OWASP_TOP_10",
                requirement_id="A05:2021",
                title="Security Misconfiguration",
                description="Secure default configurations",
                severity="HIGH",
                category="Configuration",
                automated_check=True
            ),
            ComplianceRequirement(
                standard="OWASP_TOP_10",
                requirement_id="A06:2021",
                title="Vulnerable Components",
                description="Use secure and patched components",
                severity="HIGH",
                category="Dependencies",
                automated_check=True
            ),
            ComplianceRequirement(
                standard="OWASP_TOP_10",
                requirement_id="A07:2021",
                title="Identification and Authentication Failures",
                description="Proper authentication mechanisms",
                severity="HIGH",
                category="Authentication",
                automated_check=False,
                evidence_required=True
            ),
            ComplianceRequirement(
                standard="OWASP_TOP_10",
                requirement_id="A08:2021",
                title="Software Integrity Failures",
                description="Verify software integrity",
                severity="HIGH",
                category="Integrity",
                automated_check=True
            ),
            ComplianceRequirement(
                standard="OWASP_TOP_10",
                requirement_id="A09:2021",
                title="Security Logging Failures",
                description="Proper security logging and monitoring",
                severity="MEDIUM",
                category="Logging",
                automated_check=True
            ),
            ComplianceRequirement(
                standard="OWASP_TOP_10",
                requirement_id="A10:2021",
                title="Server-Side Request Forgery",
                description="Prevent SSRF attacks",
                severity="MEDIUM",
                category="Network",
                automated_check=True
            ),
        ]

        # NIST 800-53 (subset - most critical controls)
        requirements["NIST_800_53"] = [
            ComplianceRequirement(
                standard="NIST_800_53",
                requirement_id="AC-2",
                title="Account Management",
                description="Manage user accounts and access",
                severity="HIGH",
                category="Access Control",
                automated_check=False,
                evidence_required=True
            ),
            ComplianceRequirement(
                standard="NIST_800_53",
                requirement_id="AC-3",
                title="Access Enforcement",
                description="Enforce access control policies",
                severity="HIGH",
                category="Access Control",
                automated_check=False,
                evidence_required=True
            ),
            ComplianceRequirement(
                standard="NIST_800_53",
                requirement_id="SI-2",
                title="Flaw Remediation",
                description="Regularly patch and remediate vulnerabilities",
                severity="HIGH",
                category="Vulnerability Management",
                automated_check=True
            ),
            ComplianceRequirement(
                standard="NIST_800_53",
                requirement_id="SC-8",
                title="Transmission Confidentiality",
                description="Protect data in transit",
                severity="MEDIUM",
                category="Cryptography",
                automated_check=True
            ),
        ]

        # ISO 27001 (subset - most relevant controls)
        requirements["ISO_27001"] = [
            ComplianceRequirement(
                standard="ISO_27001",
                requirement_id="A.9",
                title="Access Control",
                description="Business requirements for access control",
                severity="HIGH",
                category="Access Control",
                automated_check=False,
                evidence_required=True
            ),
            ComplianceRequirement(
                standard="ISO_27001",
                requirement_id="A.12",
                title="Operations Security",
                description="Protection against malware and secure operations",
                severity="HIGH",
                category="Operations",
                automated_check=True
            ),
            ComplianceRequirement(
                standard="ISO_27001",
                requirement_id="A.13",
                title="Communications Security",
                description="Network security and information transfer",
                severity="MEDIUM",
                category="Network",
                automated_check=True
            ),
        ]

        # PCI DSS (subset - most critical requirements)
        requirements["PCI_DSS"] = [
            ComplianceRequirement(
                standard="PCI_DSS",
                requirement_id="2.2",
                title="Configuration Standards",
                description="Develop configuration standards for security parameters",
                severity="HIGH",
                category="Configuration",
                automated_check=True
            ),
            ComplianceRequirement(
                standard="PCI_DSS",
                requirement_id="3.4",
                title="Data Encryption",
                description="Encrypt transmission of cardholder data",
                severity="CRITICAL",
                category="Cryptography",
                automated_check=True
            ),
            ComplianceRequirement(
                standard="PCI_DSS",
                requirement_id="6.2",
                title="Security Updates",
                description="Ensure security vulnerabilities are addressed",
                severity="HIGH",
                category="Vulnerability Management",
                automated_check=True
            ),
        ]

        # GDPR (subset - most relevant articles for technical controls)
        requirements["GDPR"] = [
            ComplianceRequirement(
                standard="GDPR",
                requirement_id="Article 25",
                title="Data Protection by Design",
                description="Implement data protection principles",
                severity="HIGH",
                category="Privacy",
                automated_check=False,
                evidence_required=True
            ),
            ComplianceRequirement(
                standard="GDPR",
                requirement_id="Article 32",
                title="Security of Processing",
                description="Implement appropriate security measures",
                severity="HIGH",
                category="Security",
                automated_check=True
            ),
            ComplianceRequirement(
                standard="GDPR",
                requirement_id="Article 35",
                title="Data Protection Impact Assessment",
                description="Conduct DPIA for high-risk processing",
                severity="MEDIUM",
                category="Privacy",
                automated_check=False,
                evidence_required=True
            ),
        ]

        # HIPAA (subset - Security Rule)
        requirements["HIPAA"] = [
            ComplianceRequirement(
                standard="HIPAA",
                requirement_id="164.312",
                title="Technical Safeguards",
                description="Implement technical safeguards for ePHI",
                severity="HIGH",
                category="Security",
                automated_check=True
            ),
            ComplianceRequirement(
                standard="HIPAA",
                requirement_id="164.308",
                title="Administrative Safeguards",
                description="Implement administrative safeguards",
                severity="HIGH",
                category="Administration",
                automated_check=False,
                evidence_required=True
            ),
        ]

        return requirements

    def _load_check_functions(self) -> Dict[str, callable]:
        """Load automated check functions."""
        return {
            "OWASP_TOP_10_A02": self._check_cryptographic_failures,
            "OWASP_TOP_10_A03": self._check_injection_vulnerabilities,
            "OWASP_TOP_10_A05": self._check_security_misconfiguration,
            "OWASP_TOP_10_A06": self._check_vulnerable_components,
            "OWASP_TOP_10_A08": self._check_software_integrity,
            "OWASP_TOP_10_A09": self._check_security_logging,
            "OWASP_TOP_10_A10": self._check_ssrf_protection,
            "NIST_800_53_SI-2": self._check_flaw_remediation,
            "NIST_800_53_SC-8": self._check_transmission_confidentiality,
            "ISO_27001_A12": self._check_operations_security,
            "ISO_27001_A13": self._check_communications_security,
            "PCI_DSS_2.2": self._check_configuration_standards,
            "PCI_DSS_3.4": self._check_data_encryption,
            "PCI_DSS_6.2": self._check_security_updates,
            "GDPR_Article32": self._check_security_of_processing,
            "HIPAA_164.312": self._check_technical_safeguards,
        }

    def check_compliance(self, target_path: str, standards: Optional[List[str]] = None) -> List[ComplianceCheckResult]:
        """
        Perform comprehensive compliance checking.

        Args:
            target_path: Path to codebase or configuration to check
            standards: List of standards to check against (defaults to initialized standards)

        Returns:
            List of compliance check results
        """
        if standards is None:
            standards = self.standards

        results = []

        for standard in standards:
            if standard in self.requirements:
                standard_results = self._check_standard(target_path, standard)
                results.extend(standard_results)

        return results

    def _check_standard(self, target_path: str, standard: str) -> List[ComplianceCheckResult]:
        """Check compliance against a specific standard."""
        results = []

        for requirement in self.requirements[standard]:
            result = self._check_requirement(target_path, requirement)
            results.append(result)

        return results

    def _check_requirement(self, target_path: str, requirement: ComplianceRequirement) -> ComplianceCheckResult:
        """Check compliance for a specific requirement."""
        if requirement.automated_check:
            # Use automated check function
            check_func_key = f"{requirement.standard}_{requirement.requirement_id}".replace(":", "").replace(".", "_")
            check_func = self.check_functions.get(check_func_key)

            if check_func:
                try:
                    status, evidence, findings, remediation = check_func(target_path, requirement)
                    return ComplianceCheckResult(
                        requirement=requirement,
                        status=status,
                        evidence=evidence,
                        findings=findings,
                        remediation=remediation
                    )
                except Exception as e:
                    logger.error(f"Automated check failed for {requirement.requirement_id}: {e}")
                    return ComplianceCheckResult(
                        requirement=requirement,
                        status="manual_review_required",
                        evidence=f"Automated check failed: {e}",
                        findings=["Automated compliance check encountered an error"],
                        remediation="Manual review required due to automated check failure"
                    )
            else:
                # No automated check available
                return ComplianceCheckResult(
                    requirement=requirement,
                    status="manual_review_required",
                    evidence="No automated check available for this requirement",
                    findings=["Manual review required"],
                    remediation="Implement automated compliance check or perform manual review"
                )
        else:
            # Manual review required
            return ComplianceCheckResult(
                requirement=requirement,
                status="manual_review_required",
                evidence="Manual review required for this requirement",
                findings=["Manual review required"],
                remediation="Perform manual compliance assessment and provide evidence"
            )

    # Automated check functions

    def _check_cryptographic_failures(self, target_path: str, requirement: ComplianceRequirement) -> Tuple[str, str, List[str], Optional[str]]:
        """Check for cryptographic failures (OWASP A02:2021)."""
        # Look for weak crypto usage in code
        weak_crypto_patterns = [
            r'hashlib\.md5\s*\(',
            r'hashlib\.sha1\s*\(',
            r'Cryptodome\.Cipher\.DES',
            r'cryptography\.hazmat\.primitives\.ciphers\.algorithms\.DES'
        ]

        findings = []

        for root, dirs, files in os.walk(target_path):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        for pattern in weak_crypto_patterns:
                            if re.search(pattern, content, re.IGNORECASE):
                                findings.append(f"Weak cryptography usage in {filepath}: {pattern}")
                    except Exception as e:
                        logger.warning(f"Could not check {filepath}: {e}")

        if findings:
            return ("non_compliant", "Weak cryptographic algorithms detected", findings,
                   "Replace weak algorithms (MD5, SHA-1, DES) with strong alternatives (SHA-256, AES)")
        else:
            return ("compliant", "No weak cryptographic algorithms detected", [], None)

    def _check_injection_vulnerabilities(self, target_path: str, requirement: ComplianceRequirement) -> Tuple[str, str, List[str], Optional[str]]:
        """Check for injection vulnerabilities (OWASP A03:2021)."""
        injection_patterns = [
            r'(?:execute|query|cursor\.execute).*[\+\%]',  # SQL injection
            r'subprocess\.(?:call|Popen|run|check_output)\([^,]+,\s*shell\s*=\s*True',  # Command injection
            r'os\.system\s*\(',  # Command injection
            r'\beval\s*\(',  # Code injection
            r'\bexec\s*\(',  # Code injection
        ]

        findings = []

        for root, dirs, files in os.walk(target_path):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        for pattern in injection_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            if matches:
                                findings.append(f"Potential injection vulnerability in {filepath}: {pattern}")
                    except Exception as e:
                        logger.warning(f"Could not check {filepath}: {e}")

        if findings:
            return ("non_compliant", "Injection vulnerabilities detected", findings,
                   "Use parameterized queries, avoid shell=True, validate and sanitize all inputs")
        else:
            return ("compliant", "No injection vulnerabilities detected", [], None)

    def _check_security_misconfiguration(self, target_path: str, requirement: ComplianceRequirement) -> Tuple[str, str, List[str], Optional[str]]:
        """Check for security misconfiguration (OWASP A05:2021)."""
        findings = []

        # Check for common misconfigurations
        config_files_to_check = ['requirements.txt', 'pyproject.toml', 'setup.py', 'Dockerfile']

        for config_file in config_files_to_check:
            config_path = os.path.join(target_path, config_file)
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Check for insecure configurations
                    if 'DEBUG = True' in content or 'debug=True' in content.lower():
                        findings.append(f"Debug mode enabled in {config_file}")

                    if 'SECRET_KEY' in content and ('123456' in content or 'secret' in content.lower()):
                        findings.append(f"Weak or default secret key in {config_file}")

                except Exception as e:
                    logger.warning(f"Could not check {config_path}: {e}")

        if findings:
            return ("non_compliant", "Security misconfigurations detected", findings,
                   "Disable debug mode in production, use strong secret keys, review all configuration files")
        else:
            return ("compliant", "No security misconfigurations detected", [], None)

    def _check_vulnerable_components(self, target_path: str, requirement: ComplianceRequirement) -> Tuple[str, str, List[str], Optional[str]]:
        """Check for vulnerable components (OWASP A06:2021)."""
        # This would integrate with vulnerability scanners
        # For now, return manual review status
        return ("manual_review_required", "Component vulnerability checking requires dependency analysis",
               ["Manual review required for dependency vulnerabilities"], None)

    def _check_software_integrity(self, target_path: str, requirement: ComplianceRequirement) -> Tuple[str, str, List[str], Optional[str]]:
        """Check for software integrity failures (OWASP A08:2021)."""
        findings = []

        # Check for integrity verification
        if not os.path.exists(os.path.join(target_path, 'requirements.txt')) and \
           not os.path.exists(os.path.join(target_path, 'pyproject.toml')):
            findings.append("No dependency pinning or integrity verification found")

        if findings:
            return ("non_compliant", "Software integrity issues detected", findings,
                   "Implement dependency pinning, use checksums, verify software integrity")
        else:
            return ("compliant", "Software integrity measures in place", [], None)

    def _check_security_logging(self, target_path: str, requirement: ComplianceRequirement) -> Tuple[str, str, List[str], Optional[str]]:
        """Check for security logging failures (OWASP A09:2021)."""
        findings = []

        # Check for logging configuration
        has_logging = False
        for root, dirs, files in os.walk(target_path):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        if 'logger' in content.lower() or 'logging' in content.lower():
                            has_logging = True
                            break
                    except Exception:
                        continue

        if not has_logging:
            findings.append("No logging implementation detected")

        if findings:
            return ("non_compliant", "Security logging issues detected", findings,
                   "Implement comprehensive logging for security events and monitoring")
        else:
            return ("compliant", "Security logging appears to be implemented", [], None)

    def _check_ssrf_protection(self, target_path: str, requirement: ComplianceRequirement) -> Tuple[str, str, List[str], Optional[str]]:
        """Check for SSRF protection (OWASP A10:2021)."""
        ssrf_patterns = [
            r'requests\.(?:get|post|put|delete)\s*\([^)]*url[^)]*\)',
            r'urllib\.request\.urlopen\s*\(',
            r'httpx\.(?:get|post|put|delete)\s*\(',
        ]

        findings = []

        for root, dirs, files in os.walk(target_path):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        for pattern in ssrf_patterns:
                            if re.search(pattern, content):
                                findings.append(f"Potential SSRF vulnerability in {filepath}: {pattern}")
                    except Exception as e:
                        logger.warning(f"Could not check {filepath}: {e}")

        if findings:
            return ("non_compliant", "SSRF vulnerabilities detected", findings,
                   "Validate and sanitize URLs, implement allowlists for external requests")
        else:
            return ("compliant", "No SSRF vulnerabilities detected", [], None)

    # Additional standard-specific check functions would be implemented here
    # For brevity, using placeholder implementations

    def _check_vulnerable_components(self, target_path: str, requirement: ComplianceRequirement) -> Tuple[str, str, List[str], Optional[str]]:
        """Check for potentially vulnerable components by scanning for dependency files."""
        findings = []
        dep_files = ["requirements.txt", "package.json", "Gemfile", "pom.xml", "go.mod"]
        found_files = []
        
        for root, _, files in os.walk(target_path):
            for f in files:
                if f in dep_files:
                    found_files.append(os.path.join(root, f))
                    
        if not found_files:
            return ("compliant", "No standard dependency files found (potential isolation)", [], None)
            
        findings.append(f"Dependency files found: {', '.join([os.path.basename(f) for f in found_files])}")
        findings.append("Automated vulnerability scanning against these files is recommended (e.g., using 'safety' or 'npm audit')")
        
        return ("manual_review_required", "Dependency files detected; manual verification of versions required", findings, 
                "Integrate with automated dependency scanning tools")

    def _check_transmission_confidentiality(self, target_path: str, requirement: ComplianceRequirement) -> Tuple[str, str, List[str], Optional[str]]:
        """Scan for hardcoded unencrypted endpoints (http://)."""
        findings = []
        http_pattern = re.compile(r'http://[a-zA-Z0-9.-]+')
        
        for root, _, files in os.walk(target_path):
            for filename in files:
                if filename.endswith(('.py', '.js', '.ts', '.html', '.json', '.yaml', '.yml')):
                    filepath = os.path.join(root, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            matches = http_pattern.findall(content)
                            for match in matches:
                                if not any(local in match for local in ["localhost", "127.0.0.1", "0.0.0.0"]):
                                    findings.append(f"Unencrypted endpoint found in {filename}: {match}")
                    except Exception as e:
                        logger.warning(f"Could not check {filepath}: {e}")
                        
        if findings:
            return ("non_compliant", "Potential unencrypted transmissions detected", findings,
                   "Use HTTPS for all external communications")
        else:
            return ("compliant", "No unencrypted external endpoints detected", [], None)

    def _check_operations_security(self, target_path: str, requirement: ComplianceRequirement) -> Tuple[str, str, List[str], Optional[str]]:
        """Brief description of _check_operations_security.
        
        Args:
            self : Description of self
            target_path : Description of target_path
            requirement : Description of requirement
        
            Returns: Description of return value (type: Any)
        """
"""
        return ("manual_review_required", "Operations security requires comprehensive security audit",
               ["Manual review required"], None)

    def _check_communications_security(self, target_path: str, requirement: ComplianceRequirement) -> Tuple[str, str, List[str], Optional[str]]:
        """Brief description of _check_communications_security.
        
        Args:
            self : Description of self
            target_path : Description of target_path
            requirement : Description of requirement
        
            Returns: Description of return value (type: Any)
        """
"""
        return ("manual_review_required", "Communications security requires network security audit",
               ["Manual review required"], None)

    def _check_configuration_standards(self, target_path: str, requirement: ComplianceRequirement) -> Tuple[str, str, List[str], Optional[str]]:
        """Brief description of _check_configuration_standards.
        
        Args:
            self : Description of self
            target_path : Description of target_path
            requirement : Description of requirement
        
            Returns: Description of return value (type: Any)
        """
"""
        return ("manual_review_required", "Configuration standards require security policy review",
               ["Manual review required"], None)

    def _check_data_encryption(self, target_path: str, requirement: ComplianceRequirement) -> Tuple[str, str, List[str], Optional[str]]:
        """Brief description of _check_data_encryption.
        
        Args:
            self : Description of self
            target_path : Description of target_path
            requirement : Description of requirement
        
            Returns: Description of return value (type: Any)
        """
"""
        return ("manual_review_required", "Data encryption requires cryptography audit",
               ["Manual review required"], None)

    def _check_security_updates(self, target_path: str, requirement: ComplianceRequirement) -> Tuple[str, str, List[str], Optional[str]]:
        """Brief description of _check_security_updates.
        
        Args:
            self : Description of self
            target_path : Description of target_path
            requirement : Description of requirement
        
            Returns: Description of return value (type: Any)
        """
"""
        return ("manual_review_required", "Security updates require patch management audit",
               ["Manual review required"], None)

    def _check_security_of_processing(self, target_path: str, requirement: ComplianceRequirement) -> Tuple[str, str, List[str], Optional[str]]:
        """Brief description of _check_security_of_processing.
        
        Args:
            self : Description of self
            target_path : Description of target_path
            requirement : Description of requirement
        
            Returns: Description of return value (type: Any)
        """
"""
        return ("manual_review_required", "Security of processing requires GDPR compliance audit",
               ["Manual review required"], None)

    def _check_technical_safeguards(self, target_path: str, requirement: ComplianceRequirement) -> Tuple[str, str, List[str], Optional[str]]:
        """Brief description of _check_technical_safeguards.
        
        Args:
            self : Description of self
            target_path : Description of target_path
            requirement : Description of requirement
        
            Returns: Description of return value (type: Any)
        """
"""
        return ("manual_review_required", "Technical safeguards require HIPAA compliance audit",
               ["Manual review required"], None)

# Convenience functions
def check_compliance(target_path: str, standards: Optional[List[str]] = None) -> List[ComplianceCheckResult]:
    """
    Convenience function for compliance checking.

    Args:
        target_path: Path to check for compliance
        standards: List of compliance standards to check

    Returns:
        List of compliance check results
    """
    checker = ComplianceChecker(standards)
    return checker.check_compliance(target_path, standards)
