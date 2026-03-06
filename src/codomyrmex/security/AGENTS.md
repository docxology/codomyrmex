# Agent Guidelines - Security

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Module Overview

Security utilities covering vulnerability scanning, secret detection, source code auditing, threat
modeling, and governance policy enforcement. Provides `VulnerabilityScanner` for project-level CVE
detection, `SecretsDetector` for API key and credential leakage scanning, `SecurityAnalyzer` for
OWASP-pattern code analysis, and `PolicyEngine` for governance rule enforcement. Three MCP tools
expose the full scan suite to PAI agents.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Exports `VulnerabilityScanner`, `SecretsDetector`, `SecurityAnalyzer`, `ThreatModel`, `PolicyEngine`, `create_threat_model`, `analyze_threats` |
| `vulnerability_scanner.py` | `VulnerabilityScanner` — project-level CVE scanning |
| `secrets_detector.py` | `SecretsDetector` — API key and credential leakage detection |
| `security_analyzer.py` | `SecurityAnalyzer` — OWASP-pattern source code analysis |
| `threat_model.py` | `ThreatModel`, `create_threat_model()`, `analyze_threats()` |
| `governance.py` | `PolicyEngine`, `Policy` — rule enforcement and compliance |
| `mcp_tools.py` | MCP tools: `scan_vulnerabilities`, `scan_secrets`, `audit_code_security` |

## Key Classes

- **VulnerabilityScanner** — Comprehensive scanning for known CVEs (`scan_project_security()`)
- **SecretsDetector** — Identify exposed API keys and secrets (`scan_directory_for_secrets()`)
- **SecurityAnalyzer** — Analyze source code for OWASP top-10 pitfalls
- **ThreatModel** — Structured risk assessment for system architectures
- **PolicyEngine** — Governance rule enforcement and compliance

## MCP Tools Available

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `scan_vulnerabilities` | Scan a project directory for known security vulnerabilities | SAFE |
| `scan_secrets` | Scan a specific file for leaked secrets, API keys, or credentials | SAFE |
| `audit_code_security` | Audit code quality and security for a specific file or directory | SAFE |

## Agent Instructions

1. **Scan before commit** — Run `scan_secrets` on changed files before any git commit
2. **CVE gate** — Block deployments if `scan_vulnerabilities` returns critical findings
3. **Audit in VERIFY** — Run `audit_code_security` as a VERIFY-phase gate
4. **Threat model new APIs** — Create a `ThreatModel` for any new public API surface
5. **Policy as code** — Use `PolicyEngine` to codify compliance rules, not manual checks

## Operating Contracts

- `scan_vulnerabilities` and `scan_secrets` are read-only — they do not modify files
- `audit_code_security` scores are 0-100; scores below 70 require remediation before BUILD passes
- `SecretsDetector.scan_directory_for_secrets()` raises on permission errors — ensure path is readable
- `PolicyEngine.enforce()` raises a policy exception on first failure — catch and log all violations
- **DO NOT** commit code without running `scan_secrets` on modified files

## Common Patterns

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
engine.add_policy(Policy("PasswordRule", lambda c: "password" in c, "Missing password"))

try:
    engine.enforce({"username": "admin"})
except Exception as e:
    print(f"Enforcement failed: {e}")
```

## PAI Agent Role Access Matrix

| PAI Agent | Access Level | MCP Tools | Trust Level |
|-----------|-------------|-----------|-------------|
| **Engineer** | Full scan suite | `scan_vulnerabilities`, `scan_secrets`, `audit_code_security` | TRUSTED |
| **Architect** | Architectural review | `audit_code_security` — architectural security pattern review | OBSERVED |
| **QATester** | Validation scans | `scan_vulnerabilities`, `scan_secrets` — VERIFY-phase security gates | OBSERVED |
| **Researcher** | Read analysis only | `audit_code_security` — read-only security pattern analysis | SAFE |

### Engineer Agent
**Use Cases**: Running full security audits during BUILD, scanning newly written code for vulnerabilities before commit, ensuring secrets are not accidentally committed.

### Architect Agent
**Use Cases**: Reviewing architectural security patterns, identifying design-level vulnerabilities, threat modeling support.

### QATester Agent
**Use Cases**: Confirming zero new CVEs in BUILD output during VERIFY, verifying no secrets in test fixtures, running security regression checks.

### Researcher Agent
**Use Cases**: Read-only code security analysis for research and architecture review.

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)


## Rule Reference

This module is governed by the following rule file:

- [`src/codomyrmex/agentic_memory/rules/modules/security.cursorrules`](src/codomyrmex/agentic_memory/rules/modules/security.cursorrules)
