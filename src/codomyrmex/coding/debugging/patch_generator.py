"""Patch Generator for Autonomous Debugging.

Generates code patches to fix diagnosed errors using LLM assistance.
Constructs prompts from error diagnoses and parses LLM responses into
structured patch objects.

Example:
    >>> from codomyrmex.coding.debugging.patch_generator import PatchGenerator
    >>> generator = PatchGenerator(llm_client=my_llm)
    >>> patches = generator.generate(source_code, diagnosis)
    >>> for patch in patches:
    ...     print(f"Fix: {patch.description} (confidence: {patch.confidence})")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from codomyrmex.coding.debugging.error_analyzer import ErrorDiagnosis

# We define a minimal interface for the LLM to avoid circular hard dependencies
# or complex setup if the user hasn't configured 'codomyrmex.llm' yet.
# In a real scenario, this would import from codomyrmex.llm.

logger = logging.getLogger(__name__)


@dataclass
class Patch:
    """Represents a code patch for fixing an error.

    Contains the patch content in unified diff format along with
    metadata about the fix including description and confidence level.

    Attributes:
        file_path: Path to the file being patched.
        diff: The patch content in unified diff format.
        description: Human-readable description of what the patch fixes.
        confidence: Confidence score from 0.0 to 1.0 indicating
            likelihood of the patch being correct.

    Example:
        >>> patch = Patch(
        ...     file_path="script.py",
        ...     diff="--- a/script.py\\n+++ b/script.py\\n@@ -1 +1 @@\\n-x = undefined\\n+x = 0",
        ...     description="Initialize variable x with default value",
        ...     confidence=0.85
        ... )
    """
    file_path: str
    diff: str  # Unified diff format
    description: str
    confidence: float


class PatchGenerator:
    """Generates patches for diagnosed errors using LLM assistance.

    Uses a language model to analyze errors and generate candidate
    patches. Constructs prompts with error context and parses
    responses into structured Patch objects.

    Attributes:
        llm_client: The LLM client used for patch generation.

    Example:
        >>> generator = PatchGenerator(llm_client=anthropic_client)
        >>> patches = generator.generate(buggy_code, error_diagnosis)
        >>> best_patch = max(patches, key=lambda p: p.confidence)
    """

    def __init__(self, llm_client: Any | None = None):
        """Initialize the PatchGenerator.

        Args:
            llm_client: An LLM client instance for generating patches.
                If None, generate() will return an empty list.
        """
        self.llm_client = llm_client

    def generate(self, source_code: str, diagnosis: ErrorDiagnosis) -> list[Patch]:
        """Generate candidate patches for the given error diagnosis.

        Uses the LLM client to analyze the error and source code,
        then generates one or more candidate patches ranked by
        confidence.

        Args:
            source_code: The original source code containing the error.
            diagnosis: The ErrorDiagnosis object describing the error
                to be fixed.

        Returns:
            A list of Patch objects, possibly empty if no patches
            could be generated or no LLM client is configured.

        Example:
            >>> diagnosis = ErrorDiagnosis(
            ...     error_type="NameError",
            ...     message="name 'foo' is not defined",
            ...     line_number=10,
            ...     file_path="script.py"
            ... )
            >>> patches = generator.generate(source_code, diagnosis)
        """
        if not diagnosis.file_path:
             logger.warning("No file path in diagnosis, cannot generate specific patch.")
             return []

        prompt = self._construct_prompt(source_code, diagnosis)

        # If no LLM client is available, return an empty list or mock for now
        if not self.llm_client:
            logger.warning("No LLM client configured for PatchGenerator.")
            return []

        try:
            raise NotImplementedError("Patch generation requires configured LLM backend — use llm module")
        except NotImplementedError:
            raise
        except Exception as e:
            logger.error(f"Failed to generate patch: {e}")
            return []

    def _construct_prompt(self, source_code: str, diagnosis: ErrorDiagnosis) -> str:
        """Construct the LLM prompt for patch generation.

        Builds a structured prompt containing the error details, stack trace,
        and source code to guide the LLM in generating an appropriate fix.

        Args:
            source_code: The original source code with the error.
            diagnosis: The ErrorDiagnosis containing error details.

        Returns:
            A formatted prompt string for the LLM.
        """
        return f"""
You are an expert automated debugger.
The following code failed to execute.

ERROR TYPE: {diagnosis.error_type}
MESSAGE: {diagnosis.message}
LINE: {diagnosis.line_number}
FILE: {diagnosis.file_path}

STACK TRACE:
{diagnosis.stack_trace}

SOURCE CODE:
```python
{source_code}
```

Please provide a unified diff patch to fix this error.
Explain your fix briefly.
"""
