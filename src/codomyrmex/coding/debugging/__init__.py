"""Debugging Module.

Provides tools for automated error analysis, patch generation, and fix
verification. Implements an autonomous debugging loop that can analyze
execution failures, generate candidate fixes using LLMs, and verify
corrections through re-execution.

Public API:
    Debugger: Main orchestrator for the debugging loop.
    ErrorAnalyzer: Parses execution output to diagnose errors.
    ErrorDiagnosis: Data class representing a diagnosed error.
    PatchGenerator: Generates fix patches using LLM assistance.
    Patch: Data class representing a code patch.
    FixVerifier: Verifies patches by execution.
    VerificationResult: Data class for verification outcomes.

Example:
    >>> from codomyrmex.coding.debugging import Debugger
    >>> debugger = Debugger(llm_client=my_llm)
    >>> fixed_code = debugger.debug(
    ...     source_code="x = undefined_var",
    ...     stdout="",
    ...     stderr="NameError: name 'undefined_var' is not defined",
    ...     exit_code=1
    ... )
"""

from codomyrmex.coding.debugging.debugger import Debugger
from codomyrmex.coding.debugging.error_analyzer import ErrorAnalyzer, ErrorDiagnosis
from codomyrmex.coding.debugging.patch_generator import PatchGenerator, Patch
from codomyrmex.coding.debugging.verify_fix import FixVerifier, VerificationResult

__all__ = [
    "Debugger",
    "ErrorAnalyzer",
    "ErrorDiagnosis",
    "PatchGenerator",
    "Patch",
    "FixVerifier",
    "VerificationResult",
]
