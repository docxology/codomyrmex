# Config Audits Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `config_audits` module provides tools for security, compliance, and best-practice auditing of configuration files. It complements the `config_management` module by performing deep inspection of configuration content and file system metadata.

## Key Features

- **Security Auditing**: Detects hardcoded secrets, passwords, and API keys.
- **Permission Checking**: Verifies that configuration files have appropriate filesystem permissions.
- **Syntax Validation**: Ensures configuration files (JSON, YAML) are syntactically correct.
- **Environment Compliance**: Checks for environment-specific best practices (e.g., ensuring debug mode is disabled in production).
- **Report Generation**: Produces human-readable and machine-parsable audit reports.

## Key Components

- **`ConfigAuditor`**: The central orchestrator for performing audits on files and directories.
- **`AuditRule`**: Pluggable rules that define specific checks to be performed.
- **`AuditResult`**: Comprehensive results of an audit, including identified issues and compliance status.

## Quick Start

```python
from codomyrmex.config_audits import ConfigAuditor

auditor = ConfigAuditor()
results = auditor.audit_directory("config/", pattern="*.json")

report = auditor.generate_report(results)
print(report)
```

## Directory Contents

- `auditor.py`: Main `ConfigAuditor` implementation.
- `models.py`: Data models for audits, issues, and rules.
- `rules.py`: Collection of built-in audit rules.

## Navigation

- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
