# Security Module API Specification

**Version**: v1.1.9 | **Status**: Stable | **Last Updated**: February 2026

## 1. Overview

The `security` module is a comprehensive suite for digital, physical, and cognitive security operations. It integrates vulnerability scanning, secrets detection, access control, and compliance checking into a single unified API.

## 2. Core Components

### 2.1 Digital Security

- **Scanning**: `scan_vulnerabilities`, `scan_secrets` (file or directory), `analyze_file_security`, `analyze_directory_security`.
- **Auditing**: `audit_code_security`, `audit_access_logs`.
- **Compliance**: `check_compliance(target_path, standards=None)`.
- **Encryption**: `encrypt_sensitive_data`, `decrypt_sensitive_data`.
- **Certificates**: `validate_ssl_certificates`.
- **Reporting**: `generate_security_report`.

### 2.2 Physical Security (Optional)

- **Access Control**: `check_access_permission`, `grant_access`, `revoke_access`.
- **Asset Management**: `track_asset`, `register_asset`.
- **Surveillance**: `monitor_physical_access`.

### 2.3 Cognitive Security (Optional)

- **Social Engineering**: `detect_social_engineering`, `detect_phishing_attempt`.
- **Behavior Analysis**: `analyze_user_behavior`, `detect_anomalous_behavior`.
- **Training**: `create_training_module`.

### 2.4 Theory & Frameworks (Optional)

- **Threat Modeling**: `create_threat_model`, `analyze_threats`.
- **Risk Assessment**: `assess_risk`, `calculate_risk_score`.

## 3. Data Structures

- **`SecurityScanResult`**: Encapsulates findings from scans.
- **`VulnerabilityReport`**: Aggregated vulnerability data.
- **`SecurityIssue`**: Details of a specific finding.
- **`SecurityEvent`**: Record of a security-relevant occurrence.

## 4. Usage Example

```python
from codomyrmex.security import scan_secrets

# Scan for secrets (a single file, or a directory recursively)
findings = scan_secrets("./src")

# Each finding is a dict: file_path, line_number, secret_type, confidence, description, snippet
for finding in findings:
    print(f"{finding['file_path']}:{finding['line_number']} {finding['secret_type']}")
print(f"Found {len(findings)} potential secrets.")
```
