"""Secrets Detector for Codomyrmex Security Audit Module.

Provides automated detection of secrets, credentials, and sensitive data in code files.
"""

import math
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Pattern, Tuple

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class SecretFinding:
    """Represents a potential secret found in code."""
    file_path: str
    line_number: int
    line_content: str
    secret_type: str
    confidence: str  # HIGH, MEDIUM, LOW
    description: str
    start_index: int = 0
    end_index: int = 0
    entropy: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert finding to dictionary."""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "secret_type": self.secret_type,
            "confidence": self.confidence,
            "description": self.description,
            "snippet": self.line_content.strip()[:100],  # Truncate for safety
        }


class SecretsDetector:
    """Detects secrets and credentials in files."""

    # Common secret patterns
    PATTERNS = {
        "aws_access_key": r"AKIA[0-9A-Z]{16}",
        "aws_secret_key": r"(?i)aws_secret_access_key['\"]?\s*(?::|=)\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?",
        "private_key": r"-----BEGIN (?:RSA )?PRIVATE KEY-----",
        "github_token": r"gh[pousr]_[A-Za-z0-9_]{36,255}",
        "slack_token": r"xox[baprs]-([0-9a-zA-Z]{10,48})",
        "api_key_generic": r"(?i)(?:api_key|apikey|secret|token)['\"]?\s*(?::|=)\s*['\"]?([A-Za-z0-9/\+=]{16,})['\"]?",
        "password_generic": r"(?i)(?:password|passwd|pwd)['\"]?\s*(?::|=)\s*['\"]?([A-Za-z0-9/\+=]{8,})['\"]?",
    }

    # Files to exclude
    EXCLUDE_FILES = {
        ".git", ".env.example", "package-lock.json", "yarn.lock", 
        ".jpg", ".png", ".gif", ".ico", ".pdf", ".pyc"
    }
    
    # Entropy threshold (Shannon entropy)
    ENTROPY_THRESHOLD = 4.5

    def __init__(self, patterns: Optional[Dict[str, str]] = None):
        """Initialize detector."""
        self.patterns = patterns or self.PATTERNS.copy()
        self.compiled_patterns: Dict[str, Pattern] = {}
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns."""
        for name, pattern in self.patterns.items():
            try:
                self.compiled_patterns[name] = re.compile(pattern)
            except re.error as e:
                logger.error(f"Invalid regex for {name}: {e}")

    def scan_file(self, file_path: str) -> List[SecretFinding]:
        """Scan a single file for secrets."""
        findings = []
        if self._should_skip(file_path):
            return findings

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines, 1):
                findings.extend(self._scan_line(line, i, file_path))
                
        except Exception as e:
            logger.debug(f"Error scanning file {file_path}: {e}")
            
        return findings

    def scan_directory(self, directory_path: str, recursive: bool = True) -> List[SecretFinding]:
        """Scan a directory for secrets."""
        all_findings = []
        
        for root, dirs, files in os.walk(directory_path):
            # Skip excluded dirs
            dirs[:] = [d for d in dirs if d not in self.EXCLUDE_FILES and not d.startswith('.')]
            
            for file in files:
                file_path = os.path.join(root, file)
                all_findings.extend(self.scan_file(file_path))
                
            if not recursive:
                break
                
        return all_findings

    def _scan_line(self, line: str, line_number: int, file_path: str) -> List[SecretFinding]:
        """Scan a line for secrets."""
        line_findings = []
        stripped = line.strip()
        
        if not stripped or stripped.startswith(('#', '//', '/*', '*', '"""', "'''")):
            return []

        # Check regex patterns
        for name, pattern in self.compiled_patterns.items():
            match = pattern.search(line)
            if match:
                confidence = "HIGH" if name != "password_generic" else "MEDIUM"
                line_findings.append(SecretFinding(
                    file_path=file_path,
                    line_number=line_number,
                    line_content=line.strip(),
                    secret_type=name,
                    confidence=confidence,
                    description=f"Potential {name} detected",
                    start_index=match.start(),
                    end_index=match.end()
                ))

        # Check entropy for potential high-entropy strings (if not already matched)
        # Simplified: checking words in the line
        if not line_findings:
            words = re.findall(r'[A-Za-z0-9+/=]{16,}', line) # Look for long alphanum strings
            for word in words:
                entropy = self._shannon_entropy(word)
                if entropy > self.ENTROPY_THRESHOLD:
                    line_findings.append(SecretFinding(
                        file_path=file_path,
                        line_number=line_number,
                        line_content=line.strip(),
                        secret_type="high_entropy_string",
                        confidence="LOW",
                        description=f"High entropy string detected (entropy: {entropy:.2f})",
                        entropy=entropy
                    ))
        
        return line_findings

    def _shannon_entropy(self, data: str) -> float:
        """Calculate Shannon entropy of a string."""
        if not data:
            return 0
        entropy = 0
        for x in range(256):
            p_x = float(data.count(chr(x))) / len(data)
            if p_x > 0:
                entropy += - p_x * math.log(p_x, 2)
        return entropy

    def _should_skip(self, file_path: str) -> bool:
        """Check if file should be skipped."""
        filename = os.path.basename(file_path)
        if filename in self.EXCLUDE_FILES or filename.startswith('.'):
            return True
        ext = os.path.splitext(filename)[1]
        if ext in self.EXCLUDE_FILES:
            return True
        return False


# Convenience functions
def scan_secrets(target_path: str, recursive: bool = True) -> List[Dict[str, Any]]:
    """Convenience function to scan for secrets."""
    detector = SecretsDetector()
    if os.path.isfile(target_path):
        findings = detector.scan_file(target_path)
    else:
        findings = detector.scan_directory(target_path, recursive)
        
    return [f.to_dict() for f in findings]
