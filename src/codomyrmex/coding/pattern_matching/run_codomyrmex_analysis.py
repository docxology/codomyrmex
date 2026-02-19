"""Pattern Matching Analysis Runner for Codomyrmex.

Provides pattern matching analysis functionality.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring.logger_config import get_logger

logger = get_logger(__name__)


@dataclass
class PatternMatch:
    """Represents a pattern match."""
    pattern_name: str
    file_path: str
    line_number: int
    matched_text: str
    confidence: float = 1.0


@dataclass
class AnalysisResult:
    """Result of pattern analysis."""
    total_files: int
    files_analyzed: int
    matches: list[PatternMatch] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class PatternAnalyzer:
    """Analyzes code for patterns."""

    def __init__(self, patterns: dict[str, str] | None = None):
        """Initialize analyzer."""
        self.patterns = patterns or {}

    def analyze_file(self, file_path: str) -> list[PatternMatch]:
        """Analyze a single file for patterns."""
        matches = []
        try:
            with open(file_path, encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                for name, pattern in self.patterns.items():
                    if pattern in line:
                        matches.append(PatternMatch(
                            pattern_name=name,
                            file_path=file_path,
                            line_number=i,
                            matched_text=line.strip()[:100]
                        ))
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")

        return matches

    def analyze_directory(self, directory: str, extensions: list[str] | None = None) -> AnalysisResult:
        """Analyze all files in a directory."""
        extensions = extensions or ['.py', '.js', '.ts']
        all_matches = []
        errors = []
        files_analyzed = 0
        total_files = 0

        path = Path(directory)
        for ext in extensions:
            for file_path in path.rglob(f"*{ext}"):
                total_files += 1
                try:
                    matches = self.analyze_file(str(file_path))
                    all_matches.extend(matches)
                    files_analyzed += 1
                except Exception as e:
                    errors.append(f"{file_path}: {e}")

        return AnalysisResult(
            total_files=total_files,
            files_analyzed=files_analyzed,
            matches=all_matches,
            errors=errors
        )


# Convenience functions
def run_codomyrmex_analysis(directory: str, patterns: dict[str, str] | None = None) -> AnalysisResult:
    """Run pattern analysis on a directory."""
    analyzer = PatternAnalyzer(patterns or {})
    return analyzer.analyze_directory(directory)

    analyzer = PatternAnalyzer(patterns)
    return analyzer.analyze_file(file_path)

# DEPRECATED(v0.2.0): Stub functions for backward compatibility. Will be removed in v0.3.0.
def get_embedding_function() -> Any:
    """Get the embedding function used for analysis."""
    raise NotImplementedError("Embedding function requires configured embedding backend")

def analyze_repository_path(path: str) -> dict[str, Any]:
    """Analyze a repository path."""
    return {"path": path, "status": "analyzed"}

def run_full_analysis(path: str) -> dict[str, Any]:
    """Run full analysis sequence."""
    return {"path": path, "full_analysis": True}

def print_once(msg: str) -> None:
    """Print a message only once."""
    print(msg)

def _perform_repository_index(path: str) -> None:
    """Index repository."""
    logger.info(f"Indexing {path}")

def _perform_dependency_analysis(path: str) -> None:
    """Analyze dependencies."""
    logger.info(f"Analyzing dependencies for {path}")

def _perform_text_search(query: str, path: str) -> list[Any]:
    """Perform text search."""
    return []

def _perform_code_summarization(path: str) -> str:
    """Summarize code."""
    raise NotImplementedError("Code summarization requires configured LLM backend")

def _perform_docstring_indexing(path: str) -> None:
    """Index docstrings."""
    logger.info(f"Indexing docstrings for {path}")

def _perform_symbol_extraction(path: str) -> list[str]:
    """Extract symbols."""
    return []

def _perform_symbol_usage_analysis(path: str) -> dict[str, int]:
    """Analyze symbol usage."""
    return {}

def _perform_text_search_context_extraction(query: str, path: str) -> str:
    """Extract context for search."""
    raise NotImplementedError("Text search context extraction requires configured search backend")

def _perform_chunking_examples(text: str) -> list[str]:
    """Demonstrate chunking."""
    return [text]
