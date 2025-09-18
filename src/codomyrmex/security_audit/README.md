# Security Audit Module

The Security Audit module provides comprehensive security analysis, vulnerability scanning, compliance checking, and security monitoring capabilities for the Codomyrmex ecosystem.

## Features

### 🔍 Vulnerability Scanning
- **Dependency Analysis**: Scan Python and Node.js dependencies for known vulnerabilities
- **Code Security**: Analyze source code for security issues using bandit and semgrep
- **Real-time Monitoring**: Continuous security event monitoring and alerting
- **Compliance Checking**: Verify compliance with OWASP, NIST, ISO standards

### 🔐 Encryption & Certificate Management
- **Data Encryption**: Secure encryption/decryption using AES-256
- **Password Hashing**: Secure password storage with PBKDF2
- **SSL Validation**: Certificate validation and security assessment
- **Key Management**: Secure key generation and rotation

### 📊 Security Reporting
- **Comprehensive Reports**: Detailed security assessment reports
- **Risk Assessment**: Automated risk scoring and prioritization
- **Compliance Dashboards**: Visual compliance status tracking
- **Trend Analysis**: Security metrics and historical analysis

## Quick Start

```python
from codomyrmex.security_audit import VulnerabilityScanner, SecurityMonitor

# Scan for vulnerabilities
scanner = VulnerabilityScanner()
report = scanner.scan_vulnerabilities("/path/to/project")
print(f"Risk Score: {report.risk_score}/100")

# Start security monitoring
monitor = SecurityMonitor()
monitor.start_monitoring()

# Generate security report
from codomyrmex.security_audit import generate_security_report
report = generate_security_report(vuln_data, compliance_data, monitoring_data)
```

## API Reference

### VulnerabilityScanner

```python
from codomyrmex.security_audit import VulnerabilityScanner

scanner = VulnerabilityScanner()
report = scanner.scan_vulnerabilities(target_path, scan_types=["dependencies", "code"])
```

### SecurityMonitor

```python
from codomyrmex.security_audit import SecurityMonitor

monitor = SecurityMonitor()
monitor.start_monitoring()
monitor.add_alert_rule(AlertRule(...))
```

### EncryptionManager

```python
from codomyrmex.security_audit import EncryptionManager

encryptor = EncryptionManager()
result = encryptor.encrypt_data("sensitive data")
decrypted = encryptor.decrypt_data(result.data)
```

## Configuration

Create a `security_config.json` file:

```json
{
  "scan_types": ["dependencies", "code", "compliance"],
  "severity_threshold": "MEDIUM",
  "compliance_standards": ["OWASP_TOP_10", "NIST_800_53"],
  "monitoring_interval": 10,
  "alert_cooldown": 300
}
```

## Security Standards Supported

- **OWASP Top 10**: Web application security
- **NIST 800-53**: Federal information security
- **ISO 27001**: Information security management
- **PCI DSS**: Payment card industry security
- **GDPR**: Data protection compliance
- **HIPAA**: Healthcare data security

## Integration Points

- **logging_monitoring**: All security events are logged
- **static_analysis**: Code security analysis integration
- **environment_setup**: Environment security validation
- **data_visualization**: Security metrics visualization

## Security Best Practices

1. **Regular Scanning**: Run vulnerability scans weekly
2. **Monitor Alerts**: Review security alerts promptly
3. **Key Rotation**: Rotate encryption keys regularly
4. **Compliance Audits**: Perform quarterly compliance assessments
5. **Access Control**: Implement least privilege access
6. **Backup Security**: Encrypt sensitive backups

## Dependencies

- `cryptography`: For encryption and certificate validation
- `pyOpenSSL`: For SSL certificate parsing
- `bandit`: For Python code security analysis
- `requests`: For external security service integration

## Contributing

When contributing to the Security Audit module:

1. Follow secure coding practices
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Perform security review for sensitive code
5. Ensure compliance with security standards

## License

This module is part of Codomyrmex and follows the same license terms.
