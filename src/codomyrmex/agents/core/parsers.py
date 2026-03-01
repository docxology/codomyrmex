"""
Agent Output Parsers.

Utilities for parsing structured content from agent responses,
including JSON extraction, code block parsing, and pattern matching.
"""

import json
import re
from dataclasses import dataclass
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


@dataclass
class CodeBlock:
    """Represents an extracted code block."""

    language: str
    code: str
    start_line: int = 0
    end_line: int = 0

    def __str__(self) -> str:
        """Execute   Str   operations natively."""
        return self.code


@dataclass
class ParseResult:
    """Result of parsing operation."""

    success: bool
    data: Any = None
    error: str | None = None
    raw_text: str = ""

    def __bool__(self) -> bool:
        """Execute   Bool   operations natively."""
        return self.success


def parse_json_response(text: str, strict: bool = False) -> ParseResult:
    """
    Extract and parse JSON from mixed text output.

    Handles:
    - Pure JSON responses
    - JSON embedded in markdown code blocks
    - JSON with surrounding text/explanation

    Args:
        text: Raw text containing JSON
        strict: If True, fail on any parse error

    Returns:
        ParseResult with parsed data or error
    """
    if not text or not text.strip():
        return ParseResult(success=False, error="Empty input", raw_text=text)

    # Try direct parse first
    try:
        data = json.loads(text.strip())
        return ParseResult(success=True, data=data, raw_text=text)
    except json.JSONDecodeError as e:
        logger.debug("Direct JSON parse failed, trying code-block extraction: %s", e)
        pass

    # Try extracting from markdown code blocks
    json_patterns = [
        r"```json\s*\n([\s\S]*?)\n```",
        r"```\s*\n([\s\S]*?)\n```",
        r"\{[\s\S]*\}",
        r"\[[\s\S]*\]",
    ]

    for pattern in json_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                data = json.loads(match)
                return ParseResult(success=True, data=data, raw_text=text)
            except json.JSONDecodeError:
                continue

    if strict:
        return ParseResult(success=False, error="No valid JSON found", raw_text=text)

    # Return raw text as fallback
    return ParseResult(success=False, error="No JSON found", data=text.strip(), raw_text=text)


def parse_code_blocks(text: str, language: str | None = None) -> list[CodeBlock]:
    """
    Extract fenced code blocks from text.

    Args:
        text: Text containing code blocks
        language: Filter by specific language (e.g., "python", "javascript")

    Returns:
        List of extracted CodeBlock objects
    """
    if not text:
        return []

    pattern = r"```(\w*)\s*\n([\s\S]*?)\n```"
    matches = re.finditer(pattern, text)

    blocks = []
    for match in matches:
        lang = match.group(1) or "text"
        code = match.group(2)

        if language and lang.lower() != language.lower():
            continue

        # Calculate line numbers
        start_pos = match.start()
        start_line = text[:start_pos].count("\n") + 1
        end_line = start_line + code.count("\n")

        blocks.append(CodeBlock(
            language=lang,
            code=code,
            start_line=start_line,
            end_line=end_line,
        ))

    logger.debug(f"Extracted {len(blocks)} code blocks")
    return blocks


def parse_first_code_block(text: str, language: str | None = None) -> CodeBlock | None:
    """Extract the first code block, optionally filtered by language."""
    blocks = parse_code_blocks(text, language)
    return blocks[0] if blocks else None


def parse_structured_output(
    text: str,
    patterns: dict[str, str],
    flags: int = re.MULTILINE,
) -> dict[str, str | None]:
    """
    Extract structured data using regex patterns.

    Args:
        text: Text to parse
        patterns: Dict mapping field names to regex patterns
        flags: Regex flags

    Returns:
        Dict of extracted values (None if not found)
    """
    result = {}

    for name, pattern in patterns.items():
        match = re.search(pattern, text, flags)
        result[name] = match.group(1) if match else None

    return result


def extract_between(text: str, start: str, end: str) -> str | None:
    """
    Extract text between two markers.

    Args:
        text: Source text
        start: Start marker
        end: End marker

    Returns:
        Extracted text or None
    """
    start_idx = text.find(start)
    if start_idx == -1:
        return None

    start_idx += len(start)
    end_idx = text.find(end, start_idx)

    if end_idx == -1:
        return None

    return text[start_idx:end_idx]


def parse_key_value_pairs(
    text: str,
    separator: str = ":",
    line_separator: str = "\n",
) -> dict[str, str]:
    """
    Parse key-value pairs from text.

    Args:
        text: Text containing key:value pairs
        separator: Key-value separator
        line_separator: Line separator

    Returns:
        Dict of parsed pairs
    """
    result = {}

    for line in text.split(line_separator):
        line = line.strip()
        if separator not in line:
            continue

        parts = line.split(separator, 1)
        if len(parts) == 2:
            key = parts[0].strip()
            value = parts[1].strip()
            if key:
                result[key] = value

    return result


def clean_response(text: str) -> str:
    """
    Clean agent response by removing common artifacts.

    Removes:
    - Leading/trailing whitespace
    - Multiple consecutive blank lines
    - Common AI response prefixes
    """
    if not text:
        return ""

    # Strip whitespace
    text = text.strip()

    # Remove multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove common prefixes
    prefixes = [
        r"^(Sure,?\s*)?Here('s| is)?\s*(the|your)?\s*",
        r"^(Certainly!?\s*)",
        r"^(Of course!?\s*)",
    ]

    for prefix in prefixes:
        text = re.sub(prefix, "", text, count=1, flags=re.IGNORECASE)

    return text.strip()


def split_on_pattern(text: str, pattern: str) -> list[str]:
    """Split text on regex pattern while keeping delimiters."""
    parts = re.split(f"({pattern})", text)
    result = []

    for i in range(0, len(parts), 2):
        chunk = parts[i]
        if i + 1 < len(parts):
            chunk += parts[i + 1]
        if chunk.strip():
            result.append(chunk)

    return result
