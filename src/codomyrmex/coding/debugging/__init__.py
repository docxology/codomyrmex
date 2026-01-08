"""
Debugging Module

Provides tools for automated error analysis, patch generation, and fix verification.
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
