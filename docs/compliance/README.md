# Compliance Documentation

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Compliance documentation for the Codomyrmex project, including audit reports, policy compliance, and quality assurance artifacts.

## Compliance Status

| Policy | Status | Evidence |
|--------|--------|----------|
| Zero-Mock compliance | **100%** | Only 2 pass-only stubs remain repo-wide |
| RASP documentation | **100%** | All 128 modules have README, AGENTS, SPEC, PAI |
| License (MIT) | **Compliant** | All deps audited via pip-licenses |
| Security scanning | **Active** | CI: Bandit, CodeQL, pip-audit, TruffleHog |
| Code quality | **0 violations** | Ruff `select=ALL` from 119k→0 |

## Contents

| File | Description |
|------|-------------|
| [MOCK_AUDIT.md](MOCK_AUDIT.md) | Zero-Mock policy audit report |
| [AGENTS.md](AGENTS.md) | Agent coordination for compliance |
| [SPEC.md](SPEC.md) | Compliance specification |
| [PAI.md](PAI.md) | PAI compliance integration |

## Audit History

| Date | Audit | Result |
|------|-------|--------|
| Mar 2026 | Zero-Mock v1.0.7 | 227→2 pass-only stubs |
| Mar 2026 | Ruff triage v1.1.9 | 119,498→0 violations |
| Mar 2026 | Security scan | CI passing (Bandit + CodeQL) |

## Related Documentation

- [Testing Standards](../development/testing-strategy.md) — Testing strategy and policies
- [Security](../security/) — Security documentation
- [Security Reference](../reference/security.md) — Security quick reference

## Navigation

- **Parent**: [docs/](../README.md)
- **Root**: [Project Root](../../README.md)
