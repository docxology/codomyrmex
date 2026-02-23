# secrets

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Secret detection, rotation, and secure storage utilities for the security module. Provides a pattern-based secret scanner that detects AWS keys, GitHub tokens, API keys, private keys, JWTs, database URLs, passwords, and generic high-entropy strings in source code with configurable confidence thresholds. Also includes a simple encrypted vault for storing and retrieving secrets with password-derived key encryption, plus utility functions for environment variable retrieval, secret masking, and cryptographically secure secret generation.

## Key Exports

- **`SecretType`** -- Enum of detectable secret categories: API_KEY, AWS_KEY, GITHUB_TOKEN, PRIVATE_KEY, PASSWORD, JWT, DATABASE_URL, GENERIC
- **`SecretSeverity`** -- Enum of detection severity levels: LOW, MEDIUM, HIGH, CRITICAL
- **`DetectedSecret`** -- Dataclass representing a detected secret with type, severity, location tuple, redacted value, line number, file path, context snippet, and confidence score
- **`ScanResult`** -- Dataclass capturing scan results with secrets list, files scanned count, scan duration, and computed properties for has_secrets and high_severity_count
- **`SecretPatterns`** -- Collection of compiled regex patterns for detecting secrets across AWS, GitHub, API keys, private keys, JWT, database URLs, passwords, and generic high-entropy strings; supports custom pattern extensions
- **`SecretScanner`** -- Main scanner: scans text, files, or directories for secrets with configurable confidence threshold and automatic path exclusions for .git, node_modules, __pycache__, and lock files
- **`SecretVault`** -- Simple encrypted secret storage with password-derived key, XOR encryption, base64 encoding, and JSON persistence to disk
- **`get_secret_from_env()`** -- Retrieve a secret from environment variables with optional default
- **`mask_secret()`** -- Mask a secret string for safe display, showing only the first and last N characters
- **`generate_secret()`** -- Generate a cryptographically secure random secret of configurable length with optional special characters

## Directory Contents

- `__init__.py` - All secrets classes, enums, dataclasses, scanner, vault, and utility functions
- `README.md` - This file
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI algorithm context
- `py.typed` - PEP 561 typing marker

## Navigation

- **Parent Module**: [security](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
