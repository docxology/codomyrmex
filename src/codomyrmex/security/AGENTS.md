# Agent Guidelines - Security

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

## Navigation

- [README](README.md) | [SPEC](SPEC.md) | [PAI](PAI.md)
