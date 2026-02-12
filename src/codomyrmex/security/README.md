# security

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Comprehensive security module organized into four specialized submodules: digital, physical, cognitive, and theory. The digital submodule handles vulnerability scanning, secrets detection, encryption, SSL certificate validation, compliance checking, and security monitoring. The physical submodule manages access control, asset inventory, surveillance, and perimeter security. The cognitive submodule detects social engineering, phishing, and anomalous user behavior. The theory submodule provides threat modeling, risk assessment, and security pattern frameworks.


## Installation

```bash
uv uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Core Submodules

- **`audit`** -- Security audit logging and event tracking
- **`compliance`** -- Compliance standards and requirement checking
- **`secrets`** -- Secrets detection and exposure auditing
- **`scanning`** -- Vulnerability and security scanning

### Digital Security

- **`VulnerabilityScanner`** -- Scans code and systems for known vulnerabilities
- **`scan_vulnerabilities()`** -- Run a vulnerability scan and return results
- **`audit_code_security()`** -- Audit source code for security issues
- **`VulnerabilityReport`** -- Structured report from a vulnerability scan
- **`SecurityScanResult`** -- Result container for security scans
- **`SecretsDetector`** -- Detects hardcoded secrets, API keys, and credentials in code
- **`audit_secrets_exposure()`** -- Audit a project for exposed secrets
- **`scan_file_for_secrets()`** -- Scan a single file for secret patterns
- **`scan_directory_for_secrets()`** -- Recursively scan a directory for secrets
- **`SecurityAnalyzer`** -- Static analysis engine for security findings
- **`SecurityFinding`** -- Individual finding from security analysis
- **`SecurityIssue`** -- Categorized security issue with severity
- **`analyze_file_security()`** -- Analyze a single file for security issues
- **`analyze_directory_security()`** -- Analyze an entire directory tree
- **`ComplianceChecker`** -- Validates code against compliance standards (OWASP, CIS, etc.)
- **`ComplianceCheckResult`** -- Result of a compliance check
- **`ComplianceRequirement`** -- Individual compliance requirement definition
- **`ComplianceStandard`** -- Compliance standard definition (e.g., OWASP Top 10)
- **`check_compliance()`** -- Check project compliance against a standard
- **`SecurityMonitor`** -- Real-time security event monitoring
- **`monitor_security_events()`** -- Start monitoring for security events
- **`audit_access_logs()`** -- Audit access log files for anomalies
- **`SecurityEvent`** -- Structured security event record
- **`EncryptionManager`** -- Manages encryption/decryption of sensitive data
- **`encrypt_sensitive_data()`** -- Encrypt data using configured cipher
- **`decrypt_sensitive_data()`** -- Decrypt previously encrypted data
- **`CertificateValidator`** -- Validates SSL/TLS certificates
- **`validate_ssl_certificates()`** -- Validate SSL certificates for a host
- **`SSLValidationResult`** -- Result of SSL certificate validation
- **`SecurityReportGenerator`** -- Generates comprehensive security reports
- **`generate_security_report()`** -- Generate a full security report for a project

### Physical Security

- **`AccessControlSystem`** -- Physical access control management
- **`check_access_permission()`** -- Check if an entity has physical access
- **`grant_access()`** -- Grant physical access to an entity
- **`revoke_access()`** -- Revoke physical access from an entity
- **`AssetInventory`** -- Track and manage physical assets
- **`register_asset()`** -- Register a new physical asset
- **`track_asset()`** -- Track asset location and status
- **`get_asset_status()`** -- Get current status of an asset
- **`SurveillanceMonitor`** -- Physical surveillance and monitoring
- **`monitor_physical_access()`** -- Monitor physical access events
- **`log_physical_event()`** -- Log a physical security event
- **`PhysicalVulnerabilityScanner`** -- Scan for physical security vulnerabilities
- **`assess_physical_security()`** -- Assess overall physical security posture
- **`scan_physical_vulnerabilities()`** -- Scan for specific physical vulnerabilities
- **`PerimeterManager`** -- Perimeter security management
- **`check_perimeter_security()`** -- Check perimeter integrity
- **`manage_access_points()`** -- Manage physical access points

### Cognitive Security

- **`SocialEngineeringDetector`** -- Detects social engineering attempts
- **`detect_social_engineering()`** -- Analyze content for social engineering patterns
- **`analyze_communication()`** -- Analyze communications for manipulation
- **`PhishingAnalyzer`** -- Phishing email and message analysis
- **`analyze_email()`** -- Analyze an email for phishing indicators
- **`detect_phishing_attempt()`** -- Detect phishing in arbitrary content
- **`AwarenessTrainer`** -- Security awareness training management
- **`create_training_module()`** -- Create a security training module
- **`assess_training_effectiveness()`** -- Assess training program effectiveness
- **`CognitiveThreatAssessor`** -- Assess cognitive-level security threats
- **`assess_cognitive_threats()`** -- Assess cognitive threat landscape
- **`evaluate_human_factors()`** -- Evaluate human factor risks
- **`BehaviorAnalyzer`** -- User behavior analytics for security
- **`analyze_user_behavior()`** -- Analyze user behavior patterns
- **`detect_anomalous_behavior()`** -- Detect behavioral anomalies

### Security Theory

- **`SecurityPrinciple`** -- Core security principle definition
- **`get_security_principles()`** -- Retrieve applicable security principles
- **`apply_principle()`** -- Apply a security principle to a context
- **`SecurityFramework`** -- Security framework definition (e.g., NIST, ISO 27001)
- **`get_framework()`** -- Retrieve a security framework by name
- **`apply_framework()`** -- Apply a framework to evaluate security posture
- **`ThreatModel`** -- Threat model definition and analysis
- **`create_threat_model()`** -- Create a new threat model
- **`analyze_threats()`** -- Analyze threats within a model
- **`RiskAssessment`** -- Risk assessment container
- **`assess_risk()`** -- Perform a risk assessment
- **`calculate_risk_score()`** -- Calculate a numeric risk score
- **`SecurityPattern`** -- Reusable security design pattern
- **`get_security_patterns()`** -- Retrieve applicable security patterns
- **`apply_pattern()`** -- Apply a security pattern to architecture
- **`SecurityBestPractice`** -- Security best practice recommendation
- **`get_best_practices()`** -- Retrieve best practices for a domain
- **`check_compliance_with_practices()`** -- Check compliance with best practices

## Directory Contents

- `__init__.py` - Module entry point with dynamic submodule imports
- `scanning/` - Vulnerability scanning utilities
- `secrets/` - Secret detection and exposure auditing
- `compliance/` - Compliance standards and checking
- `audit/` - Security audit event logging
- `digital/` - Digital security: scanning, encryption, certificates, monitoring
- `physical/` - Physical security: access control, assets, surveillance, perimeters
- `cognitive/` - Cognitive security: social engineering, phishing, behavior analysis
- `theory/` - Security theory: threat models, risk, frameworks, patterns
- `security_theory/` - Additional security theory resources

## Quick Start

```python
from codomyrmex.security import SBOMFormat, LicenseType, Component

# Initialize SBOMFormat
instance = SBOMFormat()
```


## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k security -v
```

## Navigation

- **Full Documentation**: [docs/modules/security/](../../../docs/modules/security/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
