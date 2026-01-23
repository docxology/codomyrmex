# Codomyrmex Agents — src/codomyrmex/coding/debugging

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Provides automated debugging capabilities including error analysis, LLM-powered patch generation, and fix verification. This module orchestrates the autonomous debugging loop: analyze error, generate patches, verify fixes.

## Active Components

- `debugger.py` - Main orchestrator with `Debugger` class
- `error_analyzer.py` - Error diagnosis with `ErrorAnalyzer` class
- `patch_generator.py` - LLM-based patch generation with `PatchGenerator`
- `verify_fix.py` - Patch verification with `FixVerifier`
- `__init__.py` - Module exports

## Key Classes and Functions

### debugger.py
- **`Debugger`** - Main orchestrator for the autonomous debugging loop:
  - `__init__(llm_client)` - Initialize with optional LLM client for patch generation.
  - `debug(source_code, stdout, stderr, exit_code)` - Attempt to fix a failing execution:
    1. Analyze error using ErrorAnalyzer
    2. Generate patches using PatchGenerator
    3. Verify patches using FixVerifier
    4. Return fixed source code if successful, None otherwise.

### error_analyzer.py
- **`ErrorAnalyzer`** - Analyzes execution output to diagnose errors:
  - `analyze(stdout, stderr, exit_code)` - Identify the primary error from output.
  - Detects: SyntaxError, Python tracebacks, timeout errors, runtime errors.
  - Uses regex patterns to parse Python error messages and stack traces.
- **`ErrorDiagnosis`** - Dataclass representing a diagnosed error:
  - `error_type` - Type of error (e.g., SyntaxError, NameError, TimeoutError).
  - `message` - Error message text.
  - `file_path` - File where error occurred.
  - `line_number` - Line number of error.
  - `stack_trace` - Full stack trace text.
  - `is_syntax_error` - Boolean flag for syntax errors.
  - `is_timeout` - Boolean flag for timeout errors.

### patch_generator.py
- **`PatchGenerator`** - Generates patches for diagnosed errors using LLM:
  - `__init__(llm_client)` - Initialize with LLM client for code generation.
  - `generate(source_code, diagnosis)` - Generate candidate patches for the error.
  - `_construct_prompt(source_code, diagnosis)` - Build LLM prompt with error context.
- **`Patch`** - Dataclass representing a code patch:
  - `file_path` - Path to file being patched.
  - `diff` - Unified diff format patch content.
  - `description` - Human-readable fix description.
  - `confidence` - Confidence score for the patch.

### verify_fix.py
- **`FixVerifier`** - Verifies patches by applying and testing them:
  - `verify(original_source, patch, test_input)` - Apply patch and verify execution succeeds.
  - `_apply_patch(source, patch)` - Apply unified diff patch to source string.
- **`VerificationResult`** - Dataclass for verification results:
  - `success` - Boolean indicating if fix was successful.
  - `stdout` - Output from patched code execution.
  - `stderr` - Error output from patched code execution.
  - `exit_code` - Exit code from patched code execution.

## Operating Contracts

- Error analysis prioritizes the last traceback entry as the root cause.
- Patch generation requires an LLM client to be configured.
- Patches are verified by re-executing the patched code.
- The debugging loop returns on first successful patch verification.
- Timeout errors (exit code 124) are detected and reported.
- Syntax errors are distinguished from runtime errors for targeted fixes.

## Signposting

- **Dependencies**: Optional LLM client for patch generation (e.g., codomyrmex.llm).
- **Parent Directory**: [coding](../README.md) - Parent module documentation.
- **Related Modules**:
  - `execution/` - For executing patched code.
  - `review/` - For analyzing code issues.
- **Project Root**: [../../../../README.md](../../../../README.md) - Main project documentation.
