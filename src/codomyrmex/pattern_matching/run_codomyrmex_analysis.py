"""Pattern Matching Analysis Runner for Codomyrmex.

Provides pattern matching analysis functionality.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

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
    matches: List[PatternMatch] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class PatternAnalyzer:
    """Analyzes code for patterns."""

    def __init__(self, patterns: Optional[Dict[str, str]] = None):
        """Initialize analyzer."""
        self.patterns = patterns or {}

    def analyze_file(self, file_path: str) -> List[PatternMatch]:
        """Analyze a single file for patterns."""
        matches = []
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
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

    def analyze_directory(self, directory: str, extensions: Optional[List[str]] = None) -> AnalysisResult:
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
def run_codomyrmex_analysis(directory: str, patterns: Optional[Dict[str, str]] = None) -> AnalysisResult:
    """Run pattern analysis on a directory."""
    analyzer = PatternAnalyzer(patterns or {})
    return analyzer.analyze_directory(directory)

def analyze_patterns(file_path: str, patterns: Dict[str, str]) -> List[PatternMatch]:
    """Analyze patterns in a single file."""
    analyzer = PatternAnalyzer(patterns)
    return analyzer.analyze_file(file_path)
