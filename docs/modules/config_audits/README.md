# Config Audits Module

**Version**: v1.2.7 | **Status**: Active | **Last Updated**: May 2026

## Overview

`codomyrmex.config_audits` audits configuration files for correctness, security posture, and operational compliance. It provides rule-based checks, audit result models, report generation, and MCP-facing audit tools.

## Source of Truth

- Source implementation: [../../../src/codomyrmex/config_audits/](../../../src/codomyrmex/config_audits/)
- Source README: [../../../src/codomyrmex/config_audits/README.md](../../../src/codomyrmex/config_audits/README.md)
- Source SPEC: [../../../src/codomyrmex/config_audits/SPEC.md](../../../src/codomyrmex/config_audits/SPEC.md)
- Source AGENTS: [../../../src/codomyrmex/config_audits/AGENTS.md](../../../src/codomyrmex/config_audits/AGENTS.md)

## Operating Notes

- Keep audit rules explicit, composable, and severity-tagged.
- Use synthetic or redacted examples for secret-pattern checks; never commit real credentials.
- Validate path containment before reading user-supplied files.
- Preserve enough metadata in reports for agents to route remediation tasks.

## Navigation

- **Parent Directory**: [modules](../README.md)
- **Project Root**: [../../../README.md](../../../README.md)
