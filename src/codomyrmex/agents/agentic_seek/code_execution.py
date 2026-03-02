"""Multi-language code execution integration for agenticSeek.

Provides utilities for extracting code blocks from LLM responses,
identifying the programming language, and constructing execution
commands—mirroring the tool pipeline in agenticSeek's ``CoderAgent``.

Reference: https://github.com/Fosowl/agenticSeek/blob/main/sources/agents/code_agent.py
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from codomyrmex.agents.agentic_seek.agent_types import (
    SUPPORTED_LANGUAGES,
    AgenticSeekExecutionResult,
    resolve_language,
)

# ---------------------------------------------------------------------------
# Code-block extraction
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CodeBlock:
    """A fenced code block extracted from an LLM response.

    Attributes:
        language: Detected or declared language tag (lower-cased).
        code: The raw source code inside the fence.
        start_pos: Character offset where the opening fence was found.
        end_pos: Character offset of the closing fence.
    """

    language: str
    code: str
    start_pos: int = 0
    end_pos: int = 0


_FENCE_PATTERN = re.compile(
    r"```(\w*)\s*\n(.*?)```",
    re.DOTALL,
)


def extract_code_blocks(text: str) -> list[CodeBlock]:
    """Extract all fenced code blocks from *text*.

    Handles triple-backtick fenced blocks with an optional language
    tag.  Blocks without a tag default to ``"text"``.

    Args:
        text: Raw LLM response text.

    Returns:
        Ordered list of ``CodeBlock`` instances.
    """
    blocks: list[CodeBlock] = []
    for match in _FENCE_PATTERN.finditer(text):
        lang_tag = match.group(1).strip().lower() or "text"
        code = match.group(2)
        blocks.append(
            CodeBlock(
                language=lang_tag,
                code=code,
                start_pos=match.start(),
                end_pos=match.end(),
            )
        )
    return blocks


# ---------------------------------------------------------------------------
# Language classification
# ---------------------------------------------------------------------------

def classify_language(block: CodeBlock) -> str:
    """Resolve a ``CodeBlock``'s language tag to a canonical key.

    Falls back to the declared ``block.language`` when no alias is
    found in ``SUPPORTED_LANGUAGES``.

    Args:
        block: A code block to classify.

    Returns:
        Canonical language key (e.g. ``"python"``, ``"bash"``).
    """
    resolved = resolve_language(block.language)
    return resolved if resolved is not None else block.language


# ---------------------------------------------------------------------------
# Execution command building
# ---------------------------------------------------------------------------

def build_execution_command(
    block: CodeBlock,
    work_dir: str = "/tmp",
) -> list[str]:
    """Build a shell command list to execute a code block.

    For compiled languages (C, Java) the command compiles the source;
    for interpreted languages (Python, Bash, Go) the command runs
    directly.

    Args:
        block: The code block to execute.
        work_dir: Working directory for temporary files.

    Returns:
        Command as a list of strings suitable for ``subprocess.run()``.

    Raises:
        ValueError: If the language is not in ``SUPPORTED_LANGUAGES``.
    """
    lang = classify_language(block)
    if lang not in SUPPORTED_LANGUAGES:
        raise ValueError(
            f"Unsupported language {lang!r}. "
            f"Supported: {', '.join(SUPPORTED_LANGUAGES)}"
        )

    meta = SUPPORTED_LANGUAGES[lang]
    ext = meta["extension"]
    source_file = f"{work_dir}/agentic_seek_exec{ext}"
    runner: list[str] = list(meta["runner"])

    runner.append(source_file)
    return runner


# ---------------------------------------------------------------------------
# Output parsing
# ---------------------------------------------------------------------------

def parse_execution_output(
    stdout: str,
    stderr: str,
    execution_time: float = 0.0,
    tool_type: str = "unknown",
) -> AgenticSeekExecutionResult:
    """Parse subprocess output into an ``AgenticSeekExecutionResult``.

    Success is determined by whether *stderr* is empty or contains only
    warnings (lines that do not include ``error`` or ``traceback``).

    Args:
        stdout: Standard output from the subprocess.
        stderr: Standard error from the subprocess.
        execution_time: Wall-clock seconds elapsed.
        tool_type: Name of the language / tool.

    Returns:
        Structured execution result.
    """
    has_error = _stderr_has_error(stderr)
    feedback = stdout if not has_error else f"{stdout}\n--- stderr ---\n{stderr}"

    return AgenticSeekExecutionResult(
        code="",  # caller fills in if needed
        feedback=feedback.strip(),
        success=not has_error,
        tool_type=tool_type,
        execution_time=execution_time,
    )


def _stderr_has_error(stderr: str) -> bool:
    """Return ``True`` if stderr contains error-level messages."""
    if not stderr or not stderr.strip():
        return False
    lower = stderr.lower()
    error_signals = ("error", "traceback", "exception", "fatal", "panic")
    return any(sig in lower for sig in error_signals)


# ---------------------------------------------------------------------------
# Convenience: AgenticSeekCodeExecutor facade
# ---------------------------------------------------------------------------

class AgenticSeekCodeExecutor:
    """Facade that combines extraction, classification and command building.

    Example::

        executor = AgenticSeekCodeExecutor(work_dir="/home/user/workspace")
        blocks = executor.extract(llm_response)
        for block in blocks:
            cmd = executor.command_for(block)
            print(cmd)
    """

    def __init__(self, work_dir: str = "/tmp") -> None:
        self.work_dir = work_dir

    def extract(self, text: str) -> list[CodeBlock]:
        """Extract code blocks from LLM text."""
        return extract_code_blocks(text)

    def classify(self, block: CodeBlock) -> str:
        """Classify a code block's language."""
        return classify_language(block)

    def command_for(self, block: CodeBlock) -> list[str]:
        """Build the execution command for a code block."""
        return build_execution_command(block, self.work_dir)

    def parse_output(
        self,
        stdout: str,
        stderr: str,
        execution_time: float = 0.0,
        tool_type: str = "unknown",
    ) -> AgenticSeekExecutionResult:
        """Parse subprocess output into a result."""
        return parse_execution_output(stdout, stderr, execution_time, tool_type)
