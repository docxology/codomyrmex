# Codomyrmex Agents — src/codomyrmex/coding/debugging

## Signposting
- **Parent**: [coding](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Code debugging including error analysis, patch generation, and fix verification. Provides comprehensive debugging capabilities for code execution errors.

## Active Components
- `__init__.py` – Module exports and public API
- `debugger.py` – Code debugger
- `error_analyzer.py` – Error analysis
- `patch_generator.py` – Code patch generation
- `verify_fix.py` – Fix verification

## Key Classes and Functions

### Debugger (`debugger.py`)
- `Debugger()` – Code debugger
- `debug_code(code: str, error: str) -> DebugResult` – Debug code with error
- `set_breakpoint(line: int) -> None` – Set breakpoint

### ErrorAnalyzer (`error_analyzer.py`)
- `ErrorAnalyzer()` – Analyze errors
- `analyze_error(error: str, code: str) -> ErrorDiagnosis` – Analyze error
- `get_error_suggestions(error: str) -> list[Suggestion]` – Get error suggestions

### PatchGenerator (`patch_generator.py`)
- `PatchGenerator()` – Generate code patches
- `generate_patch(code: str, error: str) -> Patch` – Generate patch for error
- `apply_patch(code: str, patch: Patch) -> str` – Apply patch to code

### FixVerifier (`verify_fix.py`)
- `FixVerifier()` – Verify fixes
- `verify_fix(original_code: str, fixed_code: str, test_cases: list) -> VerificationResult` – Verify fix

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [coding](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../../../README.md) - Main project documentation