# Security Audit Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.security_audit` module.

## Purpose

This orchestrator provides command-line interface for security analysis, vulnerability scanning, and compliance checking.

## Usage

```bash
# Scan for vulnerabilities
python scripts/security_audit/orchestrate.py scan-vulnerabilities --path src/

# Audit code security
python scripts/security_audit/orchestrate.py audit-code --path src/

# Check compliance
python scripts/security_audit/orchestrate.py check-compliance --path src/ --standard OWASP

# Generate security report
python scripts/security_audit/orchestrate.py generate-report --path src/ --output security_report.json
```

## Commands

- `scan-vulnerabilities` - Scan for security vulnerabilities
- `audit-code` - Perform comprehensive code security analysis
- `check-compliance` - Verify compliance with security standards
- `generate-report` - Generate detailed security assessment reports

## Related Documentation

- **[Module README](../../src/codomyrmex/security_audit/README.md)**: Complete module documentation
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.security_audit.scan_vulnerabilities`
- `codomyrmex.security_audit.audit_code_security`
- `codomyrmex.security_audit.check_compliance`
- `codomyrmex.security_audit.generate_security_report`

See `codomyrmex.cli.py` for main CLI integration.

