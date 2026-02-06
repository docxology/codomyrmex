"""Term analysis for FPF."""

from typing import Any


class TermAnalyzer:
    """Analyzes terms in FPF specifications."""

    def build_term_cooccurrence_matrix(self, spec: Any) -> dict:
        """Build co-occurrence matrix."""
        return {}

    def get_important_terms(self, spec: Any, top_n: int = 100) -> list[tuple[str, int, float]]:
        """Get important terms."""
        return []
