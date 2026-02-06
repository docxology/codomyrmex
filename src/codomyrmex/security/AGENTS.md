# Agent Guidelines - Security

## Module Overview

Security utilities: input validation, vulnerability scanning, and hardening.

## Key Classes

- **InputValidator** — Validate and sanitize input
- **VulnerabilityScanner** — Scan for security issues
- **SecurityHardener** — Apply security best practices
- **PermissionChecker** — Check access permissions

## Agent Instructions

1. **Validate all input** — Never trust user data
2. **Escape output** — Context-aware escaping
3. **Least privilege** — Minimal permissions
4. **Log security events** — Audit trail
5. **Scan dependencies** — Check for vulnerabilities

## Common Patterns

```python
from codomyrmex.security import (
    InputValidator, VulnerabilityScanner, sanitize_html
)

# Validate input
validator = InputValidator()
if not validator.validate_email(email):
    raise ValueError("Invalid email")

# Sanitize HTML
safe_html = sanitize_html(user_content)

# Scan for vulnerabilities
scanner = VulnerabilityScanner()
report = scanner.scan_dependencies("requirements.txt")
for vuln in report.vulnerabilities:
    print(f"{vuln.package}: {vuln.severity} - {vuln.cve}")

# Check permissions
checker = PermissionChecker()
if not checker.can_access(user, resource):
    raise PermissionDenied()
```

## Testing Patterns

```python
# Verify input validation
validator = InputValidator()
assert validator.validate_email("test@example.com")
assert not validator.validate_email("invalid")

# Verify sanitization
html = sanitize_html("<script>alert('xss')</script>")
assert "<script>" not in html
```

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
