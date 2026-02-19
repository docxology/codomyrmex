# scanning

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Static application security testing (SAST) for the security module. Provides a regex-based vulnerability scanner that checks source code for common security issues including SQL injection, hardcoded secrets, command injection, and insecure random number usage. Supports custom rule definitions, single-file scanning, and recursive directory scanning with configurable file extension filters and directory exclusions.

## Key Exports

- **`Severity`** -- Enum of finding severity levels: CRITICAL, HIGH, MEDIUM, LOW, INFO
- **`FindingType`** -- Enum of vulnerability categories: SQL_INJECTION, XSS, PATH_TRAVERSAL, COMMAND_INJECTION, HARDCODED_SECRET, INSECURE_RANDOM, WEAK_CRYPTO, EXPOSED_DEBUG, INSECURE_DESERIALIZATION, OPEN_REDIRECT
- **`SecurityFinding`** -- Dataclass representing a single vulnerability finding with type, severity, file path, line number, code snippet, remediation text, and confidence score
- **`ScanResult`** -- Dataclass capturing scan outcomes with findings list, files scanned count, errors, and computed properties for critical/high finding counts
- **`SecurityRule`** -- Abstract base class for security scan rules that check file content and return findings
- **`PatternRule`** -- Concrete rule implementation that matches lines against a compiled regex pattern and produces findings with configurable severity and remediation
- **`SQLInjectionRule`** -- Built-in rule detecting potential SQL injection via string formatting in query/execute calls
- **`HardcodedSecretRule`** -- Built-in rule detecting hardcoded passwords, API keys, secrets, and tokens in source code
- **`CommandInjectionRule`** -- Built-in rule detecting potential command injection via os.system/subprocess with string concatenation
- **`InsecureRandomRule`** -- Built-in rule detecting use of the random module where cryptographic randomness is needed
- **`SecurityScanner`** -- Main SAST scanner: registers default rules, supports custom rules, scans files or directories recursively with extension filters and directory exclusions

## Directory Contents

- `__init__.py` - All scanning classes, enums, dataclasses, built-in rules, and scanner engine
- `README.md` - This file
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI algorithm context
- `py.typed` - PEP 561 typing marker

## Navigation

- **Parent Module**: [security](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
