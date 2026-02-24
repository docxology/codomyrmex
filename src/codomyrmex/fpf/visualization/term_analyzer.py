"""Term analysis for FPF specifications.

Provides term co-occurrence and importance analysis for
Formal Process Framework (FPF) specification documents.
"""

from collections import Counter
from typing import Any


class TermAnalyzer:
    """Analyzes terms in FPF specifications.

    The analyzer extracts textual terms from FPF specs and computes
    co-occurrence relationships and importance rankings using
    term-frequency heuristics.

    Example::

        analyzer = TermAnalyzer()
        matrix = analyzer.build_term_cooccurrence_matrix(spec)
        top_terms = analyzer.get_important_terms(spec, top_n=10)
    """

    # Common English stop-words to exclude from analysis
    _STOP_WORDS: frozenset[str] = frozenset({
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to",
        "for", "of", "with", "by", "from", "is", "are", "was", "were",
        "be", "been", "being", "have", "has", "had", "do", "does", "did",
        "will", "would", "could", "should", "may", "might", "shall",
        "not", "no", "this", "that", "it", "its", "as", "if", "so",
    })

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build_term_cooccurrence_matrix(self, spec: Any) -> dict[str, dict[str, int]]:
        """Build a term co-occurrence matrix from a specification.

        Two terms *co-occur* when they appear within the same logical
        block (e.g. within the same top-level key or list item).

        Args:
            spec: FPF specification — may be a ``dict``, ``list``, or
                  ``str``.  Nested structures are traversed recursively.

        Returns:
            Nested dict mapping ``term_a -> term_b -> count``.
        """
        blocks = self._extract_text_blocks(spec)
        matrix: dict[str, dict[str, int]] = {}

        for block in blocks:
            terms = self._tokenize(block)
            unique_terms = sorted(set(terms))
            for i, term_a in enumerate(unique_terms):
                if term_a not in matrix:
                    matrix[term_a] = {}
                for term_b in unique_terms[i + 1:]:
                    matrix[term_a][term_b] = matrix[term_a].get(term_b, 0) + 1
                    if term_b not in matrix:
                        matrix[term_b] = {}
                    matrix[term_b][term_a] = matrix[term_b].get(term_a, 0) + 1

        return matrix

    def get_important_terms(
        self, spec: Any, top_n: int = 100
    ) -> list[tuple[str, int, float]]:
        """Return the most important terms in a specification.

        Importance is measured by raw frequency and a simple
        TF-like score normalised to 0–1.

        Args:
            spec: FPF specification (dict, list, or str).
            top_n: Maximum number of terms to return.

        Returns:
            List of ``(term, count, score)`` tuples sorted by score
            descending.
        """
        blocks = self._extract_text_blocks(spec)
        all_text = " ".join(blocks)
        tokens = self._tokenize(all_text)

        if not tokens:
            return []

        counts = Counter(tokens)
        max_count = counts.most_common(1)[0][1]

        ranked = [
            (term, count, round(count / max_count, 4))
            for term, count in counts.most_common(top_n)
        ]
        return ranked

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_text_blocks(self, spec: Any) -> list[str]:
        """Recursively extract text blocks from a nested spec structure."""
        blocks: list[str] = []

        if isinstance(spec, str):
            blocks.append(spec)
        elif isinstance(spec, dict):
            for key, value in spec.items():
                # Each top-level key is a separate block
                key_block = str(key)
                child_blocks = self._extract_text_blocks(value)
                if child_blocks:
                    key_block += " " + " ".join(child_blocks)
                blocks.append(key_block)
        elif isinstance(spec, (list, tuple)):
            for item in spec:
                blocks.extend(self._extract_text_blocks(item))
        else:
            # Scalars (int, float, bool, None) — convert to string
            blocks.append(str(spec))

        return blocks

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into lowercase alphanumeric terms, filtering stop-words."""
        import re

        raw_tokens = re.findall(r"[a-z][a-z0-9_]*", text.lower())
        return [t for t in raw_tokens if len(t) > 2 and t not in self._STOP_WORDS]
