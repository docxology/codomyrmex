# Codomyrmex Agents — config_audits

## Purpose
Security and compliance auditing for system configurations.

## Operating Contracts
- **Zero-Mock Testing**: All tests must use real file system operations or in-memory equivalents without mocking core logic.
- **Rule Extensibility**: New rules should be added to `rules.py` and included in `DEFAULT_RULES` if applicable.
- **Logging**: Use `logging_monitoring` for all audit activities.

## PAI Integration
- **VERIFY**: Used during the VERIFY phase to ensure configurations are safe and compliant before or after deployment.
- **OBSERVE**: Used during OBSERVE to detect drift or unauthorized changes in configuration security posture.

## Navigation
- **📁 Parent Directory**: [codomyrmex](../README.md)
- **🏠 Project Root**: ../../../README.md
