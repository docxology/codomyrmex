# Config Audits Tests

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `config_audits` module. Covers configuration file auditing including JSON validation, secret detection, permission checks, production debug flags, and report generation.

## Test Coverage

| Test Function | What It Tests |
|--------------|---------------|
| `test_audit_file_not_found` | Missing file handling |
| `test_audit_valid_json` | Valid JSON config audit |
| `test_audit_invalid_json` | Invalid JSON detection |
| `test_audit_hardcoded_secret` | Hardcoded secret detection in config files |
| `test_audit_permissive_permissions` | Overly permissive file permission detection |
| `test_audit_prod_debug` | Production debug flag detection |
| `test_audit_directory` | Directory-level config audit |
| `test_generate_report` | Audit report generation |

## Test Structure

```
tests/unit/config_audits/
    __init__.py
    test_auditor.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/config_audits/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/config_audits/ --cov=src/codomyrmex/config_audits -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../config_audits/README.md)
- [All Tests](../README.md)
