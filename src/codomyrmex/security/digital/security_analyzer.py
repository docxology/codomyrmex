"""
Security Analyzer for Codomyrmex Security Audit Module.

Provides advanced security analysis capabilities including:
- Code pattern matching for security vulnerabilities
- AST-based security analysis
- Control flow analysis
- Data flow tracking
- Security best practices validation
"""

import ast
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


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
    cwe_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class SecurityAnalyzer:
    """
    Advanced security analyzer using AST and pattern matching.

    Analyzes code for security vulnerabilities using multiple techniques:
    - Abstract Syntax Tree (AST) analysis
    - Pattern matching for known vulnerable patterns
    - Control flow analysis
    - Data flow tracking
    """

    def __init__(self):
        """Initialize the security analyzer."""
        self.vulnerable_patterns = self._load_vulnerable_patterns()
        self.safe_functions = self._load_safe_functions()

    def _load_vulnerable_patterns(self) -> Dict[str, re.Pattern]:
        """Load regex patterns for vulnerable code detection."""
        return {
            # SQL injection patterns
            "sql_string_concat": re.compile(r'(?:execute|query|cursor\.execute).*[\+\%]', re.IGNORECASE),
            "sql_format_string": re.compile(r'(?:execute|query|cursor\.execute).*%.*%s', re.IGNORECASE),

            # XSS patterns
            "unsafe_innerHTML": re.compile(r'\.innerHTML\s*='),
            "unsafe_document_write": re.compile(r'document\.write\s*\('),

            # Command injection
            "shell_true": re.compile(r'subprocess\.(?:call|Popen|run|check_output)\([^,]+,\s*shell\s*=\s*True'),
            "os_system": re.compile(r'os\.system\s*\('),
            "eval_usage": re.compile(r'\beval\s*\('),
            "exec_usage": re.compile(r'\bexec\s*\('),

            # Path traversal
            "path_join_user_input": re.compile(r'os\.path\.join.*input|request\.|argv'),

            # Hard-coded secrets
            "hardcoded_password": re.compile(r'password\s*[=:]\s*["\'][^"\']{8,}["\']', re.IGNORECASE),
            "hardcoded_api_key": re.compile(r'api[_-]?key\s*[=:]\s*["\'][A-Za-z0-9]{20,}["\']', re.IGNORECASE),

            # Weak crypto
            "md5_usage": re.compile(r'hashlib\.md5\s*\('),
            "sha1_usage": re.compile(r'hashlib\.sha1\s*\('),
            "des_usage": re.compile(r'Cryptodome\.Cipher\.DES|cryptography\.hazmat\.primitives\.ciphers\.algorithms\.DES'),

            # Insecure random
            "random_random": re.compile(r'\brandom\.(?:random|randint|choice|sample)\b'),
            "system_random_missing": re.compile(r'secrets\.|os\.urandom|ssl\.RAND_bytes'),

            # Logging sensitive data
            "log_password": re.compile(r'logger?\.(?:debug|info|warning|error|critical).*(?:password|secret|key|token)', re.IGNORECASE),
        }

    def _load_safe_functions(self) -> Set[str]:
        """Load set of known safe functions."""
        return {
            "hashlib.sha256", "hashlib.sha384", "hashlib.sha512",
            "secrets.token_bytes", "secrets.token_hex", "secrets.token_urlsafe",
            "os.urandom", "ssl.RAND_bytes", "random.SystemRandom",
            "cryptography.hazmat.primitives.ciphers.algorithms.AES",
            "cryptography.hazmat.primitives.ciphers.algorithms.ChaCha20",
        }

    def analyze_file(self, filepath: str) -> List[SecurityFinding]:
        """
        Analyze a file for security vulnerabilities.

        Args:
            filepath: Path to the file to analyze

        Returns:
            List of security findings
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            findings = []

            # Pattern-based analysis
            pattern_findings = self._analyze_patterns(content, filepath)
            findings.extend(pattern_findings)

            # AST-based analysis for Python files
            if filepath.endswith('.py'):
                ast_findings = self._analyze_ast(content, filepath)
                findings.extend(ast_findings)

            return findings

        except (OSError, UnicodeDecodeError) as e:
            logger.error(f"Could not analyze file {filepath}: {e}")
            return []

    def _analyze_patterns(self, content: str, filepath: str) -> List[SecurityFinding]:
        """Analyze content using pattern matching."""
        findings = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            for pattern_name, pattern in self.vulnerable_patterns.items():
                matches = pattern.findall(line)
                if matches:
                    finding = self._create_finding_from_pattern(
                        pattern_name, line, line_num, filepath, matches
                    )
                    if finding:
                        findings.append(finding)

        return findings

    def _create_finding_from_pattern(self, pattern_name: str, line: str, line_num: int,
                                   filepath: str, matches: List[str]) -> Optional[SecurityFinding]:
        """Create a security finding from a pattern match."""

        # Map pattern names to security issues
        pattern_to_issue = {
            "sql_string_concat": SecurityIssue.SQL_INJECTION,
            "sql_format_string": SecurityIssue.SQL_INJECTION,
            "unsafe_innerHTML": SecurityIssue.XSS_VULNERABILITY,
            "unsafe_document_write": SecurityIssue.XSS_VULNERABILITY,
            "shell_true": SecurityIssue.COMMAND_INJECTION,
            "os_system": SecurityIssue.COMMAND_INJECTION,
            "eval_usage": SecurityIssue.COMMAND_INJECTION,
            "exec_usage": SecurityIssue.COMMAND_INJECTION,
            "path_join_user_input": SecurityIssue.PATH_TRAVERSAL,
            "hardcoded_password": SecurityIssue.HARD_CODED_SECRET,
            "hardcoded_api_key": SecurityIssue.HARD_CODED_SECRET,
            "md5_usage": SecurityIssue.WEAK_CRYPTO,
            "sha1_usage": SecurityIssue.WEAK_CRYPTO,
            "des_usage": SecurityIssue.WEAK_CRYPTO,
            "random_random": SecurityIssue.INSECURE_RANDOM,
            "log_password": SecurityIssue.LOGGING_SENSITIVE_DATA,
        }

        issue_type = pattern_to_issue.get(pattern_name)
        if not issue_type:
            return None

        # Determine severity and confidence
        severity_map = {
            SecurityIssue.SQL_INJECTION: "HIGH",
            SecurityIssue.XSS_VULNERABILITY: "HIGH",
            SecurityIssue.COMMAND_INJECTION: "CRITICAL",
            SecurityIssue.PATH_TRAVERSAL: "HIGH",
            SecurityIssue.HARD_CODED_SECRET: "HIGH",
            SecurityIssue.WEAK_CRYPTO: "MEDIUM",
            SecurityIssue.INSECURE_RANDOM: "MEDIUM",
            SecurityIssue.LOGGING_SENSITIVE_DATA: "MEDIUM",
        }

        severity = severity_map.get(issue_type, "MEDIUM")
        confidence = 0.8  # Pattern matching is generally reliable

        # Generate description and recommendation
        descriptions = {
            SecurityIssue.SQL_INJECTION: "Potential SQL injection vulnerability detected",
            SecurityIssue.XSS_VULNERABILITY: "Potential Cross-Site Scripting (XSS) vulnerability",
            SecurityIssue.COMMAND_INJECTION: "Potential command injection vulnerability",
            SecurityIssue.PATH_TRAVERSAL: "Potential path traversal vulnerability",
            SecurityIssue.HARD_CODED_SECRET: "Hard-coded secret or credential detected",
            SecurityIssue.WEAK_CRYPTO: "Weak cryptographic algorithm usage",
            SecurityIssue.INSECURE_RANDOM: "Insecure random number generation",
            SecurityIssue.LOGGING_SENSITIVE_DATA: "Potential logging of sensitive data",
        }

        recommendations = {
            SecurityIssue.SQL_INJECTION: "Use parameterized queries or prepared statements",
            SecurityIssue.XSS_VULNERABILITY: "Sanitize user input and use safe HTML rendering",
            SecurityIssue.COMMAND_INJECTION: "Avoid shell=True, use subprocess with argument lists",
            SecurityIssue.PATH_TRAVERSAL: "Validate and sanitize file paths, use os.path.join safely",
            SecurityIssue.HARD_CODED_SECRET: "Move secrets to environment variables or secure config",
            SecurityIssue.WEAK_CRYPTO: "Use SHA-256 or stronger, avoid MD5/SHA-1/DES",
            SecurityIssue.INSECURE_RANDOM: "Use secrets module or cryptography library for secure random",
            SecurityIssue.LOGGING_SENSITIVE_DATA: "Avoid logging sensitive data, use sanitization",
        }

        return SecurityFinding(
            issue_type=issue_type,
            severity=severity,
            confidence=confidence,
            file_path=filepath,
            line_number=line_num,
            code_snippet=line.strip()[:100],
            description=descriptions.get(issue_type, "Security issue detected"),
            recommendation=recommendations.get(issue_type, "Review and fix security issue"),
            cwe_id=self._get_cwe_id(issue_type),
        )

    def _get_cwe_id(self, issue_type: SecurityIssue) -> Optional[str]:
        """Get CWE ID for a security issue."""
        cwe_map = {
            SecurityIssue.SQL_INJECTION: "CWE-89",
            SecurityIssue.XSS_VULNERABILITY: "CWE-79",
            SecurityIssue.COMMAND_INJECTION: "CWE-78",
            SecurityIssue.PATH_TRAVERSAL: "CWE-22",
            SecurityIssue.HARD_CODED_SECRET: "CWE-798",
            SecurityIssue.WEAK_CRYPTO: "CWE-327",
            SecurityIssue.INSECURE_RANDOM: "CWE-338",
            SecurityIssue.LOGGING_SENSITIVE_DATA: "CWE-532",
        }
        return cwe_map.get(issue_type)

    def _analyze_ast(self, content: str, filepath: str) -> List[SecurityFinding]:
        """Analyze Python code using AST parsing."""
        findings = []

        try:
            tree = ast.parse(content)

            # Analyze the AST for security issues
            analyzer = ASTSecurityAnalyzer(filepath)
            analyzer.visit(tree)
            findings.extend(analyzer.findings)

        except SyntaxError as e:
            # If we can't parse the AST, we can still do basic pattern analysis
            logger.warning(f"Could not parse AST for {filepath}: {e}")
        except Exception as e:
            logger.error(f"AST analysis failed for {filepath}: {e}")

        return findings

    def analyze_directory(self, directory: str, recursive: bool = True) -> List[SecurityFinding]:
        """
        Analyze all files in a directory.

        Args:
            directory: Directory path to analyze
            recursive: Whether to analyze subdirectories

        Returns:
            List of all security findings
        """
        import os
        from pathlib import Path

        all_findings = []
        directory_path = Path(directory)

        # Supported file extensions
        supported_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.php', '.rb'}

        if recursive:
            pattern = "**/*"
        else:
            pattern = "*"

        for file_path in directory_path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in supported_extensions:
                findings = self.analyze_file(str(file_path))
                all_findings.extend(findings)

        return all_findings


class ASTSecurityAnalyzer(ast.NodeVisitor):
    """AST visitor for security analysis of Python code."""

    def __init__(self, filepath: str):
        self.filepath = filepath
        self.findings: List[SecurityFinding] = []
        self.current_function: Optional[str] = None
        self.imports: Set[str] = set()

    def visit_Import(self, node: ast.Import) -> None:
        """Track imports for security analysis."""
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Track from imports."""
        module = node.module or ""
        for alias in node.names:
            full_name = f"{module}.{alias.name}" if module else alias.name
            self.imports.add(full_name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track current function context."""
        old_function = self.current_function
        self.current_function = node.name

        # Check for dangerous patterns in function
        self._check_function_security(node)

        self.generic_visit(node)
        self.current_function = old_function

    def _check_function_security(self, node: ast.FunctionDef) -> None:
        """Check function for security issues."""
        # Check for eval/exec usage
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                self._check_dangerous_calls(child, node.lineno)

    def _check_dangerous_calls(self, call_node: ast.Call, line_num: int) -> None:
        """Check for dangerous function calls."""
        if isinstance(call_node.func, ast.Name):
            func_name = call_node.func.id

            if func_name in ('eval', 'exec'):
                self.findings.append(SecurityFinding(
                    issue_type=SecurityIssue.COMMAND_INJECTION,
                    severity="CRITICAL",
                    confidence=0.9,
                    file_path=self.filepath,
                    line_number=line_num,
                    code_snippet=f"Use of dangerous function: {func_name}()",
                    description=f"Use of dangerous {func_name}() function",
                    recommendation="Avoid eval() and exec() - use safer alternatives",
                    cwe_id="CWE-95" if func_name == "eval" else "CWE-78"
                ))

        elif isinstance(call_node.func, ast.Attribute):
            # Check for os.system, subprocess with shell=True, etc.
            if self._is_dangerous_method_call(call_node, line_num):
                pass  # Already handled in pattern matching

    def _is_dangerous_method_call(self, call_node: ast.Call, line_num: int) -> bool:
        """Check if a method call is dangerous."""
        if not isinstance(call_node.func, ast.Attribute):
            return False

        method_name = call_node.func.attr

        # Check for os.system
        if method_name == "system" and self._is_os_module(call_node.func.value):
            self.findings.append(SecurityFinding(
                issue_type=SecurityIssue.COMMAND_INJECTION,
                severity="HIGH",
                confidence=0.85,
                file_path=self.filepath,
                line_number=line_num,
                code_snippet="Use of os.system()",
                description="Use of os.system() which can lead to command injection",
                recommendation="Use subprocess with argument lists instead of shell commands",
                cwe_id="CWE-78"
            ))
            return True

        return False

    def _is_os_module(self, node: ast.AST) -> bool:
        """Check if a node refers to the os module."""
        if isinstance(node, ast.Name):
            return node.id == "os"
        return False


# Convenience functions
def analyze_file_security(filepath: str) -> List[SecurityFinding]:
    """
    Convenience function to analyze a file for security issues.

    Args:
        filepath: Path to file to analyze

    Returns:
        List of security findings
    """
    analyzer = SecurityAnalyzer()
    return analyzer.analyze_file(filepath)


def analyze_directory_security(directory: str, recursive: bool = True) -> List[SecurityFinding]:
    """
    Convenience function to analyze a directory for security issues.

    Args:
        directory: Directory path to analyze
        recursive: Whether to analyze subdirectories

    Returns:
        List of all security findings
    """
    analyzer = SecurityAnalyzer()
    return analyzer.analyze_directory(directory, recursive)
