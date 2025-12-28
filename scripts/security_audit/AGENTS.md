# Codomyrmex Agents — scripts/security_audit

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Security audit automation scripts providing command-line interfaces for vulnerability scanning, code security analysis, compliance checking, and security reporting. This script module enables automated security assessment workflows for the Codomyrmex platform.

The security_audit scripts serve as the primary interface for security teams and CI/CD systems to perform comprehensive security analysis and compliance validation.

## Module Overview

### Key Capabilities
- **Vulnerability Scanning**: Automated detection of security vulnerabilities
- **Code Security Analysis**: Static analysis of code for security issues
- **Compliance Checking**: Validation against security standards and frameworks
- **Security Reporting**: Generation of comprehensive security assessment reports
- **Risk Assessment**: Automated risk scoring and prioritization

### Key Features
- Command-line interface with argument parsing
- Integration with core security audit modules
- Structured output formatting (JSON, text, verbose)
- Error handling and validation
- Logging integration for security operations tracking

## Function Signatures

### Core CLI Functions

```python
def main() -> None
```

Main CLI entry point for the security audit orchestrator.

**Command-line Usage:**
```bash
python orchestrate.py [command] [options]
```

**Available Commands:**
- `scan-vulnerabilities` - Scan for security vulnerabilities
- `audit-code` - Perform code security analysis
- `check-compliance` - Check compliance with security standards
- `generate-report` - Generate security assessment reports

**Global Options:**
- `--verbose, -v` - Enable verbose output
- `--output, -o` - Output file path

```python
def handle_scan_vulnerabilities(args) -> bool
```

Handle vulnerability scanning command from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `target` (str, optional): Target to scan. Defaults to current directory
  - `scan_type` (str, optional): Type of scan ("full", "quick", "dependencies"). Defaults to "full"
  - `output` (str, optional): Output file path
  - `verbose` (bool, optional): Enable verbose output. Defaults to False

**Returns:** `bool` - True if vulnerability scan completed successfully, False otherwise

**Raises:**
- `SecurityAuditError`: When security scanning operations fail

```python
def handle_audit_code(args) -> bool
```

Handle code security audit command from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `target` (str, optional): Target code to audit. Defaults to current directory
  - `output` (str, optional): Output file path
  - `verbose` (bool, optional): Enable verbose output. Defaults to False

**Returns:** `bool` - True if code audit completed successfully, False otherwise

**Raises:**
- `SecurityAuditError`: When security audit operations fail

```python
def handle_check_compliance(args) -> bool
```

Handle compliance checking command from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `target` (str, optional): Target to check compliance for. Defaults to current directory
  - `standards` (list, optional): Security standards to check against
  - `output` (str, optional): Output file path
  - `verbose` (bool, optional): Enable verbose output. Defaults to False

**Returns:** `bool` - True if compliance check completed successfully, False otherwise

**Raises:**
- `SecurityAuditError`: When compliance checking operations fail

```python
def handle_generate_report(args) -> bool
```

Handle security report generation command from CLI arguments.

**Parameters:**
- `args` - Parsed command-line arguments containing:
  - `data` (str, optional): Input data file for report generation
  - `format` (str, optional): Report format ("html", "json", "pdf"). Defaults to "html"
  - `output` (str, optional): Output file path
  - `verbose` (bool, optional): Enable verbose output. Defaults to False

**Returns:** `bool` - True if report generation completed successfully, False otherwise

**Raises:**
- `SecurityAuditError`: When report generation operations fail

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `orchestrate.py` – Main CLI orchestrator script

### Documentation
- `README.md` – Script usage and overview
- `AGENTS.md` – This coordination document

### Supporting Files
- Integration with `_orchestrator_utils.py` for shared utilities

## Operating Contracts

### Universal Script Protocols

All scripts in this module must:

1. **CLI Standards**: Follow consistent command-line argument patterns
2. **Error Handling**: Provide clear error messages and exit codes
3. **Security**: Handle sensitive security information appropriately
4. **Accuracy**: Ensure accurate security assessment results
5. **Compliance**: Meet security and privacy requirements

### Module-Specific Guidelines

#### Vulnerability Scanning
- Support comprehensive vulnerability detection
- Provide severity classification and risk assessment
- Include remediation recommendations
- Handle different scan scopes and depths

#### Code Security Analysis
- Support multiple programming languages
- Provide detailed security findings
- Include code examples and fixes
- Handle false positives appropriately

#### Compliance Checking
- Support multiple security standards and frameworks
- Provide detailed compliance reports
- Include gap analysis and recommendations
- Handle regulatory requirements

#### Security Reporting
- Generate comprehensive security assessment reports
- Include executive summaries and technical details
- Provide actionable remediation plans
- Support multiple report formats

## Navigation Links

### Module Documentation
- **Script Overview**: [README.md](README.md) - Complete script documentation

### Related Scripts

### Platform Navigation
- **Scripts Directory**: [../README.md](../README.md) - Scripts directory overview

## Agent Coordination

### Integration Points

When integrating with other scripts:

1. **Shared Utilities**: Use `_orchestrator_utils.py` for common CLI patterns
2. **Quality Integration**: Coordinate with code_review scripts
3. **CI/CD Integration**: Provide security gates for automated pipelines
4. **Monitoring Integration**: Share security metrics with monitoring systems

### Quality Gates

Before script changes are accepted:

1. **CLI Testing**: All command-line options work correctly
2. **Security Testing**: Scripts handle security data appropriately
3. **Accuracy Testing**: Security assessments produce accurate results
4. **Performance Testing**: Scripts complete security scans efficiently
5. **Integration Testing**: Scripts work with core security audit modules

## Version History

- **v0.1.0** (December 2025) - Initial security audit automation scripts with vulnerability scanning and compliance checking capabilities
