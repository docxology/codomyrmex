# Agent Guidelines - Security

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Security utilities: input validation, vulnerability scanning, and hardening.

## Key Classes

| Component | Description |
|-----------|-------------|
| `VulnerabilityScanner` | Comprehensive scanning for vulnerabilities |
| `SecretsDetector` | Identify exposed API keys and secrets |
| `SecurityAnalyzer` | Analyze source code for common security pitfalls |
| `ThreatModel` | Structured risk assessment for system architectures |
| `PolicyEngine` | Governance rule enforcement and compliance |

## Usage for Agents

### Vulnerability Scanning

```python
from codomyrmex.security import VulnerabilityScanner

scanner = VulnerabilityScanner()
results = scanner.scan_project_security("./src")
if results.get("vulnerabilities"):
    print(f"Found {results['vulnerabilities']['count']} vulnerabilities")
```

### Secrets Detection

```python
from codomyrmex.security import SecretsDetector

detector = SecretsDetector()
findings = detector.scan_directory_for_secrets("./src")
for finding in findings:
    print(f"Secret leaked in {finding.file_path}: {finding.secret_type}")
```

### Threat Modeling

```python
from codomyrmex.security import create_threat_model, analyze_threats

model = create_threat_model(
    system_name="Auth API",
    assets=["User DB", "API Keys"],
    attack_surface=["/login", "/signup"]
)
analysis = analyze_threats(model)
print(f"Total threats identified: {analysis['total_threats']}")
```

### Policy Enforcement

```python
from codomyrmex.security.governance import PolicyEngine, Policy

engine = PolicyEngine()
# Rule: password must be present in context
engine.add_policy(Policy("PasswordRule", lambda c: "password" in c, "Missing password"))

try:
    engine.enforce({"username": "admin"})
except Exception as e:
    print(f"Enforcement failed: {e}")
```

## MCP Tools Available

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Key Parameters | Trust Level |
|------|-------------|----------------|-------------|
| `scan_vulnerabilities` | Scan a project directory for known security vulnerabilities | `path` (default ".") | Safe |
| `scan_secrets` | Scan a specific file for leaked secrets, API keys, or credentials | `file_path` | Safe |
| `audit_code_security` | Audit code quality and security for a specific file or directory | `path` | Safe |

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full scan suite | `scan_vulnerabilities`, `scan_secrets`, `audit_code_security` | TRUSTED |
| **Architect** | Architectural review | `audit_code_security` | OBSERVED |
| **QATester** | Validation scans | `scan_vulnerabilities`, `scan_secrets` | OBSERVED |
| **Researcher** | Read analysis only | `audit_code_security` (read-only mode) | OBSERVED |

### Engineer Agent
**Access**: Full — all three scan tools, full project scope.
**Use Cases**: Running full security audits during BUILD phase, scanning newly written code for vulnerabilities before commit, ensuring secrets are not accidentally committed.

### Architect Agent
**Access**: Code audit — architectural security review without file-level scanning.
**Use Cases**: Reviewing architectural security patterns, identifying design-level vulnerabilities (e.g., missing authentication boundaries), threat modeling support.

### QATester Agent
**Access**: Scan validation — vulnerability and secrets scans as VERIFY-phase gates.
**Use Cases**: Confirming zero new CVEs in BUILD output, verifying no secrets leaked into test fixtures, running security regression checks before LEARN phase completes.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
