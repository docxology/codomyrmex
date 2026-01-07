# debugging

## Signposting
- **Parent**: [coding](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Code debugging including error analysis, patch generation, and fix verification. Provides comprehensive debugging capabilities for code execution errors.

## Directory Contents
- `__init__.py` – File
- `debugger.py` – File
- `error_analyzer.py` – File
- `patch_generator.py` – File
- `verify_fix.py` – File

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [coding](../README.md)
- **Project Root**: [README](../../../../README.md)

## Getting Started

To use this module in your project, import the necessary components:

```python
from codomyrmex.coding.debugging import (
    Debugger,
    ErrorAnalyzer,
    PatchGenerator,
    FixVerifier,
)

# Analyze an error
analyzer = ErrorAnalyzer()
diagnosis = analyzer.analyze_error(
    error_message="NameError: name 'x' is not defined",
    code="print(x)",
    traceback="..."
)
print(f"Root cause: {diagnosis.root_cause}")
print(f"Suggestions: {diagnosis.suggestions}")

# Generate a patch
patch_gen = PatchGenerator()
patch = patch_gen.generate_patch(
    error=diagnosis,
    code="print(x)"
)
print(f"Patch: {patch.diff}")

# Verify the fix
verifier = FixVerifier()
verification = verifier.verify_fix(
    original_code="print(x)",
    patched_code="x = 0; print(x)",
    test_cases=["test_basic"]
)
print(f"Fix verified: {verification.success}")
```

