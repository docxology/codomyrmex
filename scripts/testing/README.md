# testing

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

Testing automation scripts for test suite generation, verification, and modular testing validation. These scripts support test-driven development (TDD) practices and ensure tests use real implementations rather than mocks.

## Directory Contents

### Test Assessment and Planning
- `assess_module_documentation_tests.py` – Assess module documentation and test coverage
- `generate_module_test_plan.py` – Generate comprehensive plan for module testing improvements

### Test Generation
- `create_comprehensive_test_suites.py` – Create comprehensive test suites for modules with low coverage

### Test Verification
- `verify_modular_testing.py` – Verify tests are modular and functional (no mocks, real implementations)
- `fix_test_mocks.py` – Identify and report test files using mocks that need to be fixed

### Test Execution
- `run_tests_batched.sh` – Run tests in batches
- `test_summary.py` – Generate test summary reports

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Repository Root**: [../README.md](../README.md)