# Codomyrmex Agents — src/codomyrmex/security/secrets

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Regex and entropy-based detection of exposed secrets (API keys, tokens, passwords, private keys) in source code. Provides a `SecretScanner` with 6 built-in detection patterns and automatic redaction of matched content.

## Key Components

| File | Class / Function | Role |
|------|-----------------|------|
| `secret_scanner.py` | `SecretFinding` | Dataclass with `file_path`, `line_number`, `secret_type`, `snippet` (redacted), `confidence`, `entropy` |
| `secret_scanner.py` | `SecretScanner` | Main scanner: `scan_string()` and `scan_lines()` methods; configurable `min_entropy` threshold (default 3.0) |
| `secret_scanner.py` | `_SECRET_PATTERNS` | 6 built-in patterns: `api_key` (0.9), `aws_access_key` (0.95), `private_key` (0.99), `password` (0.7), `bearer_token` (0.85), `generic_secret` (0.6) |
| `secret_scanner.py` | `_shannon_entropy()` | Static method computing Shannon entropy for match quality assessment |
| `secret_scanner.py` | `_redact()` | Static method showing first/last 4 characters with `***` in between |

## Operating Contracts

- All patterns are compiled with `re.IGNORECASE` at `SecretScanner.__init__()` time.
- `scan_string()` returns all matches across all patterns; no deduplication across pattern types for the same line.
- Matched text is always redacted in the `snippet` field -- raw secrets are never stored in findings.
- `_shannon_entropy()` returns 0.0 for empty strings.
- `_redact()` returns `"***"` for strings shorter than `visible * 2` (default 8 characters).
- Errors must be logged via `logging_monitoring` before re-raising.

## Integration Points

- **Depends on**: Standard library only (`re`, `math`)
- **Used by**: `security` parent module MCP tool `scan_secrets`, CI/CD pre-commit hooks

## Navigation

- **Parent**: [security](../README.md)
- **Root**: [Root](../../../../README.md)
