"""Analysis subpackage for pattern matching.

Re-exports the core analysis classes from run_codomyrmex_analysis so they
can be imported from ``pattern_matching.analysis``.
"""

from ..run_codomyrmex_analysis import (
    PatternAnalyzer,
    PatternMatch,
    AnalysisResult,
    run_codomyrmex_analysis,
)

__all__ = [
    "PatternAnalyzer",
    "PatternMatch",
    "AnalysisResult",
    "run_codomyrmex_analysis",
]
