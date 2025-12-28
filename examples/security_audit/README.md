# Security Audit Examples

Demonstrates security vulnerability scanning and compliance checking using the Codomyrmex Security Audit module.

## Overview

The Security Audit module provides comprehensive security analysis including vulnerability scanning, secrets detection, and compliance validation against security standards.

## Examples

### Basic Usage (`example_basic.py`)

- Scan codebases for security vulnerabilities
- Detect secrets and sensitive data in code
- Check compliance with security standards
- Generate risk assessments and reports

**Tested Methods:**
- `scan_codebase()` - Scan for vulnerabilities (from `test_security_audit.py`)
- `check_vulnerabilities()` - Check dependencies (from `test_security_audit.py`)
- `scan_secrets()` - Detect secrets in code (from `test_security_audit.py`)

## Configuration

```yaml
audit:
  target_path: src/                    # Path to scan
  scan_types: [vulnerabilities, secrets, compliance]
  vulnerabilities:
    min_severity: low
    categories: [injection, xss, authentication]
  secrets:
    patterns: ["*.py", "*.js"]
    exclude_patterns: ["*/node_modules/*"]
  compliance_standards: [OWASP, NIST, CWE]

reporting:
  format: detailed
  include_recommendations: true
  risk_threshold: medium
```

## Running

```bash
cd examples/security_audit
python example_basic.py
```

## Expected Output

The example will:
1. Scan the specified codebase for vulnerabilities
2. Check for secrets and sensitive data
3. Validate compliance with security standards
4. Generate a risk assessment summary
5. Save detailed results to JSON file

## Security Scan Types

- **Vulnerabilities**: Code injection, XSS, authentication issues
- **Secrets**: API keys, passwords, tokens in source code
- **Compliance**: OWASP, NIST, CWE standard violations

## Risk Assessment

The example provides risk levels:
- **LOW**: No security issues detected
- **MEDIUM**: Minor security concerns found
- **HIGH**: Significant security issues detected

## Integration with CI/CD

The security audit module integrates with CI/CD pipelines to:
- Automatically scan code on commits and PRs
- Block merges with critical vulnerabilities
- Generate security reports and dashboards
- Monitor security trends over time

## Related Documentation

- [Module README](../../src/codomyrmex/security_audit/README.md)
- [Unit Tests](../../testing/unit/test_security_audit.py)

