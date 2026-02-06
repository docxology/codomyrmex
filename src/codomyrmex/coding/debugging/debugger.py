"""Autonomous Debugger Module.

Provides an automated debugging loop that analyzes execution failures,
generates patches using LLM assistance, and verifies fixes through
re-execution. Designed for integration with code execution pipelines.

Example:
    >>> from codomyrmex.coding.debugging import Debugger
    >>> debugger = Debugger(llm_client=my_llm)
    >>> fixed_code = debugger.debug(
    ...     source_code="print(undefined_var)",
    ...     stdout="",
    ...     stderr="NameError: name 'undefined_var' is not defined",
    ...     exit_code=1
    ... )
"""

from __future__ import annotations

import logging
from typing import Any

from codomyrmex.coding.debugging.error_analyzer import ErrorAnalyzer
from codomyrmex.coding.debugging.patch_generator import PatchGenerator
from codomyrmex.coding.debugging.verify_fix import FixVerifier

logger = logging.getLogger(__name__)


class Debugger:
    """Main orchestrator for the autonomous debugging loop.

    Coordinates error analysis, patch generation, and fix verification
    to automatically repair failing code. Uses an LLM client for
    intelligent patch suggestions.

    Attributes:
        analyzer: The ErrorAnalyzer instance for diagnosing errors.
        patcher: The PatchGenerator instance for creating fixes.
        verifier: The FixVerifier instance for validating patches.

    Example:
        >>> debugger = Debugger(llm_client=anthropic_client)
        >>> result = debugger.debug(code, stdout, stderr, exit_code)
        >>> if result:
        ...     print("Code fixed automatically!")
    """

    def __init__(self, llm_client: Any | None = None):
        """Initialize the Debugger with optional LLM client.

        Args:
            llm_client: An LLM client instance for generating patches.
                If None, patch generation will be limited.
        """
        self.analyzer = ErrorAnalyzer()
        self.patcher = PatchGenerator(llm_client)
        self.verifier = FixVerifier()

    def debug(self, source_code: str, stdout: str, stderr: str, exit_code: int) -> str | None:
        """Attempt to automatically fix a failing code execution.

        Performs a complete debugging cycle: analyzing the error, generating
        candidate patches, and verifying each patch until a successful fix
        is found or all candidates are exhausted.

        Args:
            source_code: The source code that failed to execute correctly.
            stdout: Standard output captured from the failed execution.
            stderr: Standard error output from the failed execution,
                typically containing error messages and stack traces.
            exit_code: The exit code from the failed execution
                (non-zero indicates failure).

        Returns:
            The fixed source code as a string if a successful patch was found,
            or None if no fix could be determined.

        Example:
            >>> code = "x = 1 / 0"
            >>> fixed = debugger.debug(code, "", "ZeroDivisionError: ...", 1)
            >>> if fixed:
            ...     print(f"Fixed code:\\n{fixed}")
        """
        logger.info("Starting debug session...")

        # 1. Analyze Error
        diagnosis = self.analyzer.analyze(stdout, stderr, exit_code)
        if not diagnosis:
            logger.info("No error diagnosed or clean exit.")
            return None

        logger.info(f"Diagnosed error: {diagnosis.error_type} at line {diagnosis.line_number}")

        # 2. Generate Patches
        patches = self.patcher.generate(source_code, diagnosis)
        if not patches:
            logger.warning("No patches generated.")
            return None

        # 3. Verify Patches
        for patch in patches:
            verification = self.verifier.verify(source_code, patch)
            if verification.success:
                logger.info(f"Patch verified successfully: {patch.description}")
                # In a real impl, we'd return the patched source code
                return self.verifier._apply_patch(source_code, patch)

        logger.info("No patch verified successfully.")
        return None
