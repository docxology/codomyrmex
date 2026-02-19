# Codomyrmex Agents - Security Module

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Purpose

The Security module provides comprehensive security capabilities across 8 specialized submodules. This document defines the active components, operating contracts, and agent integration points.

## Active Components

### Scanning Submodule
- `SecurityScanner` - Static application security testing engine with extensible rule system
- `PatternRule`, `SQLInjectionRule`, `HardcodedSecretRule`, `CommandInjectionRule`, `InsecureRandomRule` - Built-in security rules
- `SecurityFinding`, `ScanResult` - Scan result data models

### Secrets Submodule
- `SecretScanner` - Multi-pattern secret detection engine (13 built-in patterns)
- `SecretVault` - Encrypted secret storage with XOR encryption
- `SecretPatterns` - Configurable pattern collection with confidence scores
- `DetectedSecret`, `ScanResult` - Detection result data models

### Audit Submodule
- `AuditLogger` - Main audit logging service with pluggable storage
- `InMemoryAuditStore` - Thread-safe in-memory event storage (max 10,000 events)
- `FileAuditStore` - Append-only file-based event storage
- `AuditEvent` - Typed audit event with SHA-256 integrity signature

### Compliance Submodule
- `ComplianceChecker` - Compliance assessment engine for 6 frameworks
- `PolicyChecker` - Lambda-based control checker implementation
- `Control`, `ControlResult`, `ComplianceReport` - Compliance data models
- `SOC2_CONTROLS` - Pre-built SOC2 control definitions

### Digital Submodule
- `VulnerabilityScanner` - Vulnerability scanning and code security auditing
- `SecretsDetector` - Digital secrets detection in codebases
- `SecurityAnalyzer` - File and directory security analysis
- `EncryptionManager` - Data encryption/decryption operations
- `CertificateValidator` - SSL/TLS certificate validation
- `SecurityMonitor` - Security event monitoring and access log auditing
- `SecurityReportGenerator` - Security report generation
- `ComplianceChecker` (digital variant) - Digital compliance checking

### Physical Submodule
- `AccessControlSystem` - Physical access control with permission checking
- `AssetInventory` - Physical asset registration and tracking
- `SurveillanceMonitor` - Physical access monitoring and event logging
- `PhysicalVulnerabilityScanner` - Physical security vulnerability assessment
- `PerimeterManager` - Perimeter security and access point management

### Cognitive Submodule
- `SocialEngineeringDetector` - Social engineering attack detection
- `PhishingAnalyzer` - Email phishing analysis
- `AwarenessTrainer` - Security awareness training module creation
- `CognitiveThreatAssessor` - Cognitive threat and human factors assessment
- `BehaviorAnalyzer` - User behavior analysis and anomaly detection

### Theory Submodule
- `SecurityPrinciple` - Security principles with categories
- `SecurityFramework` - Security framework definitions and compliance checking
- `ThreatModel` / `ThreatModelBuilder` - Threat modeling and analysis
- `RiskAssessment` / `RiskAssessor` - Risk assessment and scoring
- `SecurityPattern` - Security architecture patterns
- `SecurityBestPractice` - Security best practices with prioritization

## Operating Contracts

### Logging
All submodules integrate with `logging_monitoring` via `get_logger()` for structured logging. Agents should respect log levels and not suppress security-relevant log output.

### Optional Dependency Handling
Each submodule uses conditional imports with `*_AVAILABLE` flags:
```python
try:
    from .digital import VulnerabilityScanner, ...
    DIGITAL_AVAILABLE = True
except ImportError:
    DIGITAL_AVAILABLE = False
```
Agents must check availability flags before invoking features that depend on optional packages (`cryptography`, `pyOpenSSL`, `jinja2`).

### Thread Safety
Core components use `threading.Lock` for concurrent access:
- `SecurityScanner._lock` for scan ID generation
- `AuditLogger._lock` for event ID generation
- `InMemoryAuditStore._lock` for event storage
- `FileAuditStore._lock` for file writes
- `ComplianceChecker._lock` for report ID generation

Agents operating in concurrent environments must not bypass these locks.

### Data Integrity
- `AuditEvent.signature` provides SHA-256 integrity verification
- `FileAuditStore` uses append-only writes for audit trail immutability
- `SecretVault` uses key derivation from master password

### Extensibility Points
Agents can extend the module via abstract base classes:
- `SecurityRule` (ABC) - Custom scanning rules
- `AuditStore` (ABC) - Custom audit storage backends
- `ControlChecker` (ABC) - Custom compliance checkers

## Agent Integration Points

### MCP Tool Interfaces
Security submodules expose MCP-compatible tool definitions (see source `MCP_TOOL_SPECIFICATION.md` files) for integration with LLM-based agents.

### Programmatic APIs
All public APIs are documented in source-level `API_SPECIFICATION.md` files. Key entry points:
- `SecurityScanner.scan_file()` / `scan_directory()` / `scan_content()`
- `SecretScanner.scan_text()` / `scan_file()` / `scan_directory()`
- `AuditLogger.log()` / `log_login()` / `log_data_access()` / `query()`
- `ComplianceChecker.assess()` / `check_control()`

## Navigation Links

- **Parent Directory**: [modules](../README.md)
- **Project Root**: [../../../README.md](../../../README.md)
- **Source**: [`src/codomyrmex/security/`](../../../src/codomyrmex/security/)
- **Technical Overview**: [technical_overview.md](technical_overview.md)
