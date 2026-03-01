# Personal AI Infrastructure — Security Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Security module provides vulnerability scanning, secret detection, compliance auditing, and governance enforcement for AI-generated and human-authored code. It is central to the PAI Algorithm's VERIFY phase, ensuring all code artifacts meet security standards before deployment.

## PAI Capabilities

### Vulnerability Scanning

```python
from codomyrmex.security import scan_project_security

# Scan an entire project for security issues
results = scan_project_security(path=".")
# Returns: vulnerability counts, severity breakdown, remediation suggestions
```

### Security Audit

```python
from codomyrmex.security import security_audit_code

# Deep audit of a specific file or directory
audit = security_audit_code(path="src/codomyrmex/auth/")
# Returns: finding details with severity, CWE references, fix guidance
```

### Submodule Capabilities

| Submodule | Purpose | Key Operations |
|-----------|---------|----------------|
| `scanning` | Vulnerability detection | Pattern-based and AST-aware code scanning |
| `secrets` | Secret detection | API key, credential, and token leak prevention |
| `audit` | Security auditing | Comprehensive security posture assessment |
| `compliance` | Compliance checking | Policy and standard conformance verification |
| `governance` | Security governance | Policy enforcement and security decision tracking |

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| `scanning` | Module | Vulnerability detection engine |
| `secrets` | Module | Secret and credential leak scanning |
| `audit` | Module | Security auditing and assessment |
| `compliance` | Module | Compliance verification against standards |
| `governance` | Module | Security policy enforcement |
| `scan_project_security` | Function | MCP-exposed project-wide security scan |
| `security_audit_code` | Function | MCP-exposed code audit tool |

## PAI Algorithm Phase Mapping

| Phase | Security Contribution |
|-------|------------------------|
| **OBSERVE** | `secrets.scan()` detects exposed credentials in codebase |
| **PLAN** | `governance` enforces security policies during workflow planning |
| **BUILD** | `scanning` validates AI-generated code during creation |
| **VERIFY** | Full security audit: vulnerability scanning + secret detection + compliance checking |
| **LEARN** | Audit results captured for improving future security posture |

## MCP Tools

Three tools are auto-discovered via `@mcp_tool` and available through the PAI MCP bridge:

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `scan_vulnerabilities` | Scan code or a directory for security vulnerabilities | Safe | security |
| `scan_secrets` | Detect secrets and credentials in source files | Safe | security |
| `audit_code_security` | Run a full security audit on a file or project directory | Safe | security |

## Architecture Role

**Extended Layer** — Consumes `static_analysis` for code parsing. Consumed by `agents/pai/` trust gateway for security verification of agent actions.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
