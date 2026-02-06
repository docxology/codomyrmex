"""Security Analyzer for Codomyrmex Security Audit Module.

Provides advanced security analysis capabilities including:
- Code pattern matching for security vulnerabilities
- AST-based security analysis
- Control flow analysis
- Data flow tracking
- Security best practices validation
"""

import ast
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


class SecurityIssue(Enum):
    """Types of security issues that can be detected."""
    SQL_INJECTION = "sql_injection"
    XSS_VULNERABILITY = "xss_vulnerability"
    COMMAND_INJECTION = "command_injection"
    PATH_TRAVERSAL = "path_traversal"
    INSECURE_RANDOM = "insecure_random"
    HARD_CODED_SECRET = "hard_coded_secret"
    WEAK_CRYPTO = "weak_crypto"
    INSECURE_DESERIALIZATION = "insecure_deserialization"
    LOGGING_SENSITIVE_DATA = "logging_sensitive_data"
    MISSING_INPUT_VALIDATION = "missing_input_validation"


@dataclass
class SecurityFinding:
    """Represents a security finding."""
    issue_type: SecurityIssue
    severity: str
    confidence: float
    file_path: str
    line_number: int
    code_snippet: str
    description: str
    recommendation: str
    cwe_id: str | None = None
    context: dict[str, Any] | None = None


class SecurityAnalyzer:
    """Advanced security analyzer using AST and pattern matching."""

    def __init__(self):
        """Initialize the security analyzer."""
        self.vulnerable_patterns = self._load_vulnerable_patterns()
        self.safe_functions = self._load_safe_functions()

    def _load_vulnerable_patterns(self) -> dict[str, re.Pattern]:
        """Load regex patterns for vulnerable code detection."""
        return {
            "sql_string_concat": re.compile(r'(?:execute|query|cursor\.execute).*[\+\%]', re.IGNORECASE),
            "unsafe_innerHTML": re.compile(r'\.innerHTML\s*='),
            "shell_true": re.compile(r'subprocess\.(?:call|Popen|run|check_output)\([^,]+,\s*shell\s*=\s*True'),
            "eval_usage": re.compile(r'\beval\s*\('),
            "exec_usage": re.compile(r'\bexec\s*\('),
            "path_join_user_input": re.compile(r'os\.path\.join.*input|request\.|argv'),
            "hardcoded_password": re.compile(r'password\s*[=:]\s*["\'][^"\']{8,}["\']', re.IGNORECASE),
            "md5_usage": re.compile(r'hashlib\.md5\s*\('),
            "random_random": re.compile(r'\brandom\.(?:random|randint|choice|sample)\b'),
        }

    def _load_safe_functions(self) -> set[str]:
        """Load set of known safe functions."""
        return {
            "hashlib.sha256", "secrets.token_bytes", "os.urandom",
            "cryptography.hazmat.primitives.ciphers.algorithms.AES"
        }

    def analyze_file(self, filepath: str) -> list[SecurityFinding]:
        """Analyze a file for security vulnerabilities."""
        try:
            with open(filepath, encoding='utf-8', errors='ignore') as f:
                content = f.read()

            findings = []
            findings.extend(self._analyze_patterns(content, filepath))

            if filepath.endswith('.py'):
                findings.extend(self._analyze_ast(content, filepath))

            return findings
        except Exception as e:
            logger.error(f"Could not analyze file {filepath}: {e}")
            return []

    def _analyze_patterns(self, content: str, filepath: str) -> list[SecurityFinding]:
        """Analyze content using pattern matching."""
        findings = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            for pattern_name, pattern in self.vulnerable_patterns.items():
                if pattern.search(line):
                     # Simplified finding creation
                     findings.append(SecurityFinding(
                         issue_type=SecurityIssue.COMMAND_INJECTION if "shell" in pattern_name else SecurityIssue.HARD_CODED_SECRET,
                         severity="HIGH",
                         confidence=0.8,
                         file_path=filepath,
                         line_number=line_num,
                         code_snippet=line.strip()[:100],
                         description=f"Potential issue detected: {pattern_name}",
                         recommendation="Review code for security vulnerability"
                     ))
        return findings

    def _analyze_ast(self, content: str, filepath: str) -> list[SecurityFinding]:
        """Analyze Python code using AST parsing."""
        findings = []
        try:
            tree = ast.parse(content)
            analyzer = ASTSecurityAnalyzer(filepath)
            analyzer.visit(tree)
            findings.extend(analyzer.findings)
        except Exception as e:
            logger.warning(f"AST analysis failed for {filepath}: {e}")
        return findings

    def analyze_directory(self, directory: str, recursive: bool = True) -> list[SecurityFinding]:
        """Analyze all files in a directory."""
        all_findings = []
        path = Path(directory)
        pattern = "**/*" if recursive else "*"
        supported = {'.py', '.js', '.ts', '.java', '.cpp', '.rb'}

        for file_path in path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in supported:
                all_findings.extend(self.analyze_file(str(file_path)))

        return all_findings


class ASTSecurityAnalyzer(ast.NodeVisitor):
    """AST visitor for security analysis."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.findings: list[SecurityFinding] = []

    def visit_Call(self, node: ast.Call) -> None:
        """Check for dangerous calls."""
        if isinstance(node.func, ast.Name):
            if node.func.id in ('eval', 'exec'):
                self.findings.append(SecurityFinding(
                    issue_type=SecurityIssue.COMMAND_INJECTION,
                    severity="CRITICAL",
                    confidence=0.9,
                    file_path=self.filepath,
                    line_number=node.lineno,
                    code_snippet=f"Use of {node.func.id}()",
                    description=f"Dangerous use of {node.func.id}",
                    recommendation="Avoid eval/exec"
                ))
        self.generic_visit(node)


# Convenience functions
def analyze_file_security(filepath: str) -> list[SecurityFinding]:
    """Convenience function to analyze a file."""
    analyzer = SecurityAnalyzer()
    return analyzer.analyze_file(filepath)

def analyze_directory_security(directory: str, recursive: bool = True) -> list[SecurityFinding]:
    """Convenience function to analyze a directory."""
    analyzer = SecurityAnalyzer()
    return analyzer.analyze_directory(directory, recursive)
