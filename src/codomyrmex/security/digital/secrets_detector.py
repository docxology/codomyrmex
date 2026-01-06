"""
Secrets Detector for Codomyrmex Security Audit Module.

Provides comprehensive detection of potential secrets exposure including:
- API keys and tokens
- Passwords and credentials
- Private keys and certificates
- Database connection strings
- Cloud service credentials
"""

import os
import re
import hashlib
from typing import List, Dict, Any, Optional, Set
from pathlib import Path

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class SecretsDetector:
    """
    Advanced secrets detection and analysis system.

    Uses multiple detection methods:
    - Pattern matching with entropy analysis
    - Known secret formats (API keys, tokens, etc.)
    - Context-aware detection
    - False positive filtering
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the secrets detector.

        Args:
            config_path: Path to detector configuration file
        """
        self.config_path = config_path or os.path.join(
            os.getcwd(), "secrets_config.json"
        )
        self.config = self._load_config()
        self._compiled_patterns = self._compile_patterns()

    def _load_config(self) -> Dict[str, Any]:
        """Load detector configuration."""
        default_config = {
            "entropy_threshold": 3.5,  # Minimum entropy for suspicious strings
            "min_length": 8,  # Minimum length for potential secrets
            "max_file_size": 10 * 1024 * 1024,  # 10MB max file size
            "exclude_patterns": [
                "*.pyc", "*.pyo", "__pycache__/*", ".git/*",
                "node_modules/*", "*.log", "*.tmp"
            ],
            "exclude_paths": [".git", "node_modules", "__pycache__"],
            "custom_patterns": {},
            "whitelist_patterns": [],  # Known false positives
        }

        # Could load from config file if it exists
        return default_config

    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns for secret detection."""
        patterns = {
            # Generic high-entropy strings
            "high_entropy": re.compile(r'\b[A-Za-z0-9+/=]{20,}\b'),

            # AWS credentials
            "aws_access_key": re.compile(r'AKIA[0-9A-Z]{16}'),
            "aws_secret_key": re.compile(r'(?i)aws_secret_access_key\s*[=:]\s*["\']?([A-Za-z0-9/+=]{40})["\']?'),
            "aws_session_token": re.compile(r'(?i)aws_session_token\s*[=:]\s*["\']?([A-Za-z0-9/+=]{300,})["\']?'),

            # Azure
            "azure_key": re.compile(r'(?i)azure.*key\s*[=:]\s*["\']?([A-Za-z0-9+/=]{20,})["\']?'),

            # Google Cloud
            "gcp_key": re.compile(r'(?i)(?:google|gcp).*key\s*[=:]\s*["\']?([A-Za-z0-9+/=]{30,})["\']?'),

            # Generic API keys
            "api_key": re.compile(r'(?i)(?:api[_-]?key|apikey)\s*[=:]\s*["\']?([A-Za-z0-9]{20,})["\']?'),
            "bearer_token": re.compile(r'(?i)bearer\s+[A-Za-z0-9+/=]{20,}'),
            "jwt_token": re.compile(r'eyJ[A-Za-z0-9+/=]+\.eyJ[A-Za-z0-9+/=]+\.[A-Za-z0-9+/=\-_]+'),

            # Database credentials
            "db_password": re.compile(r'(?i)(?:password|pwd|passwd)\s*[=:]\s*["\']?([^"\s]{8,})["\']?'),
            "db_connection": re.compile(r'(?i)(?:mongodb|mysql|postgresql|redis)://[^:]+:[^@]+@'),

            # Private keys
            "private_key": re.compile(r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----'),
            "ssh_key": re.compile(r'-----BEGIN\s+(?:OPENSSH|RSA|DSA|ECDSA)\s+PRIVATE\s+KEY-----'),

            # Certificates
            "certificate": re.compile(r'-----BEGIN\s+CERTIFICATE-----'),

            # Passwords in comments/code
            "password_literal": re.compile(r'(?i)(?:password|pwd|passwd)\s*[=:]\s*["\']([^"\']{8,})["\']'),

            # OAuth tokens
            "oauth_token": re.compile(r'(?i)oauth.*token\s*[=:]\s*["\']?([A-Za-z0-9]{20,})["\']?'),

            # GitHub tokens
            "github_token": re.compile(r'ghp_[A-Za-z0-9]{36}'),
            "github_oauth": re.compile(r'gho_[A-Za-z0-9]{36}'),

            # Slack tokens
            "slack_token": re.compile(r'xox[baprs]-[0-9]+-[0-9]+-[0-9A-Za-z]+'),

            # Stripe keys
            "stripe_key": re.compile(r'(?:sk|rsk)_(?:test|live)_[A-Za-z0-9]{20,}'),
        }

        # Add custom patterns from config
        for name, pattern_str in self.config.get("custom_patterns", {}).items():
            try:
                patterns[name] = re.compile(pattern_str, re.IGNORECASE)
            except re.error as e:
                logger.warning(f"Invalid custom pattern '{name}': {e}")

        return patterns

    def audit_secrets_exposure(self, content: str, filepath: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Audit content for potential secrets exposure.

        Args:
            content: Text content to analyze
            filepath: Optional file path for context

        Returns:
            List of potential secret exposures
        """
        findings = []

        # Skip if content is too large
        if len(content) > self.config["max_file_size"]:
            logger.warning(f"Skipping large file: {filepath}")
            return findings

        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            line_findings = self._analyze_line(line, line_num, filepath)
            findings.extend(line_findings)

        # Filter out whitelisted patterns
        findings = self._filter_whitelist(findings)

        # Calculate confidence scores
        for finding in findings:
            finding["confidence"] = self._calculate_confidence(finding)

        return findings

    def _analyze_line(self, line: str, line_num: int, filepath: Optional[str] = None) -> List[Dict[str, Any]]:
        """Analyze a single line for potential secrets."""
        findings = []

        # Skip comments and obvious non-secrets
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith(('#', '//', '/*', '*', '"""', "'''")):
            return findings

        for pattern_name, pattern in self._compiled_patterns.items():
            matches = pattern.findall(line)
            if matches:
                for match in matches:
                    # Extract the actual secret value
                    if isinstance(match, tuple):
                        secret_value = match[0] if match[0] else match[1] if len(match) > 1 else str(match)
                    else:
                        secret_value = str(match)

                    # Skip if too short
                    if len(secret_value) < self.config["min_length"]:
                        continue

                    # Check entropy for generic patterns
                    if pattern_name == "high_entropy":
                        entropy = self._calculate_entropy(secret_value)
                        if entropy < self.config["entropy_threshold"]:
                            continue

                    finding = {
                        "type": "potential_secret",
                        "pattern": pattern_name,
                        "value_preview": secret_value[:20] + "..." if len(secret_value) > 20 else secret_value,
                        "line_number": line_num,
                        "line_content": line.strip()[:100] + "..." if len(line.strip()) > 100 else line.strip(),
                        "file_path": filepath,
                        "severity": self._determine_severity(pattern_name, secret_value),
                        "entropy": self._calculate_entropy(secret_value),
                        "context": self._extract_context(lines, line_num, 3),
                    }

                    findings.append(finding)

        return findings

    def _calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of a string."""
        if not text:
            return 0.0

        # Count character frequencies
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1

        entropy = 0.0
        length = len(text)
        for count in char_counts.values():
            probability = count / length
            entropy -= probability * (probability.bit_length() - 1)  # Approximation of log2

        return entropy

    def _determine_severity(self, pattern_name: str, secret_value: str) -> str:
        """Determine severity level for a finding."""
        # High severity patterns
        high_severity = {
            "private_key", "ssh_key", "certificate", "aws_secret_key",
            "stripe_key", "github_token", "slack_token"
        }

        # Medium severity patterns
        medium_severity = {
            "aws_access_key", "azure_key", "gcp_key", "db_password",
            "jwt_token", "oauth_token"
        }

        if pattern_name in high_severity:
            return "HIGH"
        elif pattern_name in medium_severity:
            return "MEDIUM"
        elif self._calculate_entropy(secret_value) > 4.0:
            return "MEDIUM"
        else:
            return "LOW"

    def _extract_context(self, lines: List[str], line_num: int, context_lines: int = 3) -> Dict[str, str]:
        """Extract context around a finding."""
        start_line = max(0, line_num - context_lines - 1)
        end_line = min(len(lines), line_num + context_lines)

        context_before = []
        context_after = []

        for i in range(start_line, line_num - 1):
            context_before.append(lines[i])

        for i in range(line_num, end_line):
            context_after.append(lines[i])

        return {
            "before": context_before[-context_lines:],  # Last N lines before
            "after": context_after[:context_lines],     # First N lines after
        }

    def _filter_whitelist(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out whitelisted patterns and known false positives."""
        whitelist_patterns = self.config.get("whitelist_patterns", [])

        filtered_findings = []
        for finding in findings:
            is_whitelisted = False

            for whitelist_pattern in whitelist_patterns:
                if re.search(whitelist_pattern, finding["line_content"], re.IGNORECASE):
                    is_whitelisted = True
                    break

            # Filter out obvious test/example values
            if "example" in finding["line_content"].lower() or "test" in finding["line_content"].lower():
                if finding["pattern"] in {"api_key", "password_literal", "high_entropy"}:
                    is_whitelisted = True

            if not is_whitelisted:
                filtered_findings.append(finding)

        return filtered_findings

    def _calculate_confidence(self, finding: Dict[str, Any]) -> float:
        """Calculate confidence score for a finding (0.0 to 1.0)."""
        confidence = 0.5  # Base confidence

        # Pattern-specific confidence adjustments
        pattern_confidence = {
            "private_key": 0.95,
            "aws_secret_key": 0.90,
            "stripe_key": 0.95,
            "github_token": 0.95,
            "slack_token": 0.90,
            "jwt_token": 0.85,
            "high_entropy": 0.60,
        }

        confidence *= pattern_confidence.get(finding["pattern"], 0.7)

        # Entropy-based adjustment
        entropy = finding.get("entropy", 0)
        if entropy > 4.5:
            confidence += 0.1
        elif entropy < 3.0:
            confidence -= 0.2

        # Context-based adjustments
        context = finding.get("context", {})
        before_lines = context.get("before", [])
        after_lines = context.get("after", [])

        # Look for suspicious context clues
        suspicious_context = ["secret", "key", "token", "password", "credential"]
        context_text = " ".join(before_lines + after_lines).lower()

        if any(word in context_text for word in suspicious_context):
            confidence += 0.15

        # Clamp to 0.0-1.0 range
        return max(0.0, min(1.0, confidence))

    def scan_file(self, filepath: str) -> List[Dict[str, Any]]:
        """
        Scan a single file for potential secrets.

        Args:
            filepath: Path to file to scan

        Returns:
            List of potential secret exposures
        """
        try:
            # Check if file should be excluded
            if self._should_exclude_file(filepath):
                return []

            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            return self.audit_secrets_exposure(content, filepath)

        except (OSError, UnicodeDecodeError) as e:
            logger.warning(f"Could not scan file {filepath}: {e}")
            return []

    def scan_directory(self, directory: str, recursive: bool = True) -> List[Dict[str, Any]]:
        """
        Scan a directory for potential secrets.

        Args:
            directory: Directory path to scan
            recursive: Whether to scan subdirectories

        Returns:
            List of all potential secret exposures found
        """
        all_findings = []
        directory_path = Path(directory)

        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"

        for file_path in directory_path.glob(pattern):
            if file_path.is_file():
                findings = self.scan_file(str(file_path))
                all_findings.extend(findings)

        return all_findings

    def _should_exclude_file(self, filepath: str) -> bool:
        """Check if a file should be excluded from scanning."""
        path_obj = Path(filepath)

        # Check exclude paths
        for exclude_path in self.config["exclude_paths"]:
            if exclude_path in str(path_obj):
                return True

        # Check exclude patterns
        filename = path_obj.name
        for pattern in self.config["exclude_patterns"]:
            if "*" in pattern:
                # Simple glob matching
                if pattern.startswith("*."):
                    extension = pattern[2:]
                    if filename.endswith(f".{extension}"):
                        return True
                elif "/*" in pattern:
                    if pattern.split("/*")[0] in str(path_obj.parent):
                        return True
            elif filename == pattern:
                return True

        return False


# Convenience functions
def audit_secrets_exposure(content: str, filepath: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Convenience function for secrets detection.

    Args:
        content: Text content to analyze
        filepath: Optional file path for context

    Returns:
        List of potential secret exposures
    """
    detector = SecretsDetector()
    return detector.audit_secrets_exposure(content, filepath)


def scan_file_for_secrets(filepath: str) -> List[Dict[str, Any]]:
    """
    Convenience function to scan a file for secrets.

    Args:
        filepath: Path to file to scan

    Returns:
        List of potential secret exposures
    """
    detector = SecretsDetector()
    return detector.scan_file(filepath)


def scan_directory_for_secrets(directory: str, recursive: bool = True) -> List[Dict[str, Any]]:
    """
    Convenience function to scan a directory for secrets.

    Args:
        directory: Directory path to scan
        recursive: Whether to scan subdirectories

    Returns:
        List of all potential secret exposures found
    """
    detector = SecretsDetector()
    return detector.scan_directory(directory, recursive)
