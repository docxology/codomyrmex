# coding/debugging

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Automated debugging tools. Implements an autonomous debugging loop that analyzes execution failures, generates candidate fix patches using LLMs, and verifies corrections through re-execution. The pipeline flows from error analysis through patch generation to fix verification.

## Key Exports

- **`Debugger`** -- Main orchestrator for the debugging loop; accepts an LLM client and drives the analyze-patch-verify cycle via `debug(source_code, stdout, stderr, exit_code)`
- **`ErrorAnalyzer`** -- Parses execution output (stdout, stderr, exit code) to diagnose errors
- **`ErrorDiagnosis`** -- Data class representing a diagnosed error with type, message, and location
- **`PatchGenerator`** -- Generates fix patches using LLM assistance given an error diagnosis
- **`Patch`** -- Data class representing a code patch with old/new content and location
- **`FixVerifier`** -- Verifies patches by re-executing the patched code
- **`VerificationResult`** -- Data class for verification outcomes (success, output, errors)

## Directory Contents

- `__init__.py` - Package init; re-exports all public classes
- `debugger.py` - Main Debugger orchestrator
- `error_analyzer.py` - ErrorAnalyzer and ErrorDiagnosis
- `patch_generator.py` - PatchGenerator and Patch
- `verify_fix.py` - FixVerifier and VerificationResult
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [coding](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
