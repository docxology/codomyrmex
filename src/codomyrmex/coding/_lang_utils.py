"""Shared language detection utilities for the coding module."""

from __future__ import annotations

from pathlib import Path

SUPPORTED_EXTENSIONS: frozenset[str] = frozenset(
    {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".java",
        ".cpp",
        ".cc",
        ".cxx",
        ".cs",
        ".go",
        ".rs",
        ".php",
        ".rb",
    }
)


def should_analyze_file(file_path: str) -> bool:
    """Return True if the file extension is a supported language."""
    return Path(file_path).suffix.lower() in SUPPORTED_EXTENSIONS
