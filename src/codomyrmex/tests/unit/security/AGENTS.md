# Codomyrmex Agents — src/codomyrmex/tests/unit/security

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Test files and validation suites.

## Active Components
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `audit/` – Directory containing audit components
- `compliance/` – Directory containing compliance components
- `integration/` – Directory containing integration components
- `scanning/` – Directory containing scanning components
- `secrets_tests/` – Unit tests for `codomyrmex.security.secrets` (folder name avoids stdlib `secrets` shadowing)
- `test_architecture_patterns.py` – Project file
- `test_audit_trail.py` – Project file
- `test_best_practices.py` – Project file
- `test_compliance_report.py` – Project file
- `test_dashboard.py` – Project file
- `test_governance.py` – Project file
- `test_mcp_tools.py` – Project file
- `test_permissions.py` – Project file
- `test_risk_assessment.py` – Project file
- `test_sbom.py` – Project file
- `test_sbom_extended.py` – Project file
- `test_secrets_detector.py` – Project file
- `test_security_audit.py` – Project file
- `test_security_cognitive.py` – Project file
- `test_security_digital.py` – Project file
- `test_security_hardening.py` – Project file
- `test_security_physical.py` – Project file
- `test_security_theory.py` – Project file
- `test_threat_modeling.py` – Project file
- `test_vulnerability_scanner.py` – Project file
- `test_vulnerability_scanner_impl.py` – Project file
- `theory/` – Directory containing theory components
- `unit/` – Directory containing unit components

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `PAI.md`
- `README.md`
- `SPEC.md`
- `test_architecture_patterns.py`
- `test_audit_trail.py`
- `test_best_practices.py`
- `test_compliance_report.py`
- `test_dashboard.py`
- `test_governance.py`
- `test_mcp_tools.py`
- `test_permissions.py`
- `test_risk_assessment.py`
- `test_sbom.py`
- `test_sbom_extended.py`
- `test_secrets_detector.py`
- `test_security_audit.py`
- `test_security_cognitive.py`
- `test_security_digital.py`
- `test_security_hardening.py`
- `test_security_physical.py`
- `test_security_theory.py`
- `test_threat_modeling.py`
- `test_vulnerability_scanner.py`
- `test_vulnerability_scanner_impl.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [unit](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../../../README.md - Main project documentation
