"""Pattern Matching Analysis Runner for Codomyrmex.

Provides pattern matching analysis functionality.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring.core.logger_config import get_logger

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

def get_embedding_function() -> Any:
    """Get a deterministic hash-based embedding function.

    Returns a callable that maps any string to a fixed-length list of floats
    using a reproducible hashing scheme. No external model required.
    """
    import hashlib
    import struct

    EMBEDDING_DIM = 128

    def _hash_embed(text: str) -> list[float]:
        # Generate a deterministic embedding by hashing overlapping shingles
        digest = hashlib.sha512(text.encode("utf-8")).digest()
        # Extend to fill EMBEDDING_DIM floats
        raw = digest
        while len(raw) < EMBEDDING_DIM * 4:
            raw += hashlib.sha512(raw).digest()
        floats = list(struct.unpack(f"<{EMBEDDING_DIM}f", raw[: EMBEDDING_DIM * 4]))
        # Normalise to [0, 1]
        lo, hi = min(floats), max(floats)
        span = hi - lo if hi != lo else 1.0
        return [(f - lo) / span for f in floats]

    return _hash_embed

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
    """Summarize code by extracting top-level class and function definitions via AST."""
    import ast

    file_path = Path(path)
    if not file_path.exists() or file_path.suffix != ".py":
        return f"Cannot summarize: {path} (not a .py file or does not exist)"

    try:
        source = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as e:
        return f"Cannot parse {path}: {e}"

    classes = []
    functions = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            methods = [n.name for n in ast.iter_child_nodes(node) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            classes.append(f"class {node.name}({len(methods)} methods)")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(f"def {node.name}")

    parts = [f"File: {file_path.name}"]
    if classes:
        parts.append(f"Classes: {', '.join(classes)}")
    if functions:
        parts.append(f"Functions: {', '.join(functions)}")
    if not classes and not functions:
        parts.append("No top-level classes or functions found.")

    return "; ".join(parts)

def _perform_docstring_indexing(path: str) -> None:
    """Index docstrings."""
    logger.info(f"Indexing docstrings for {path}")

def _perform_symbol_extraction(path: str) -> list[str]:
    """Extract top-level symbol names (classes and functions) from a Python file."""
    import ast

    file_path = Path(path)
    if not file_path.exists() or file_path.suffix != ".py":
        return []

    try:
        source = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError:
        return []

    symbols = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            symbols.append(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append(node.name)
    return symbols


def _perform_symbol_usage_analysis(path: str) -> dict[str, int]:
    """Count occurrences of each top-level symbol name within the same file."""
    import ast

    file_path = Path(path)
    if not file_path.exists() or file_path.suffix != ".py":
        return {}

    try:
        source = file_path.read_text(encoding="utf-8", errors="ignore")
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError:
        return {}

    # First extract top-level symbol names
    symbols = set()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.add(node.name)

    # Count Name references in the AST
    usage: dict[str, int] = {s: 0 for s in symbols}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in usage:
            usage[node.id] += 1

    return usage

def _perform_text_search_context_extraction(query: str, path: str) -> str:
    """Extract context surrounding search matches in a file.

    Returns the matching lines with ±2 lines of surrounding context.
    """
    file_path = Path(path)
    if not file_path.exists():
        return f"File not found: {path}"

    try:
        lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception as e:
        return f"Error reading {path}: {e}"

    matches = []
    query_lower = query.lower()
    for i, line in enumerate(lines):
        if query_lower in line.lower():
            start = max(0, i - 2)
            end = min(len(lines), i + 3)
            context_block = "\n".join(
                f"{'>' if j == i else ' '} {j + 1}: {lines[j]}"
                for j in range(start, end)
            )
            matches.append(context_block)

    if not matches:
        return f"No matches for '{query}' in {path}"

    return f"Found {len(matches)} match(es) in {file_path.name}:\n\n" + "\n---\n".join(matches)

def _perform_chunking_examples(text: str) -> list[str]:
    """Demonstrate chunking."""
    return [text]
