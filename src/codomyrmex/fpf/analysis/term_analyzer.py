
"""Term analyzer for extracting shared terms and variables across FPF sections.


logger = get_logger(__name__)
This module provides functionality to analyze terms, variables, and concepts
that appear across different patterns and sections of the FPF specification.
"""

import re
from collections import Counter, defaultdict

from ..core.models import FPFSpec, Pattern


class TermAnalyzer:
    """Analyzer for shared terms and variables in FPF specifications."""

    def __init__(self):
        """Initialize the term analyzer."""
        # Patterns for extracting terms
        self.u_type_pattern = re.compile(r"`?U\.([A-Z][a-zA-Z0-9]*)`?")
        self.variable_pattern = re.compile(r"`([A-Z][a-zA-Z0-9]*(?:\.[A-Z][a-zA-Z0-9]*)*)`")
        self.term_pattern = re.compile(r"\b([A-Z][a-z]+(?:[A-Z][a-z]+)*)\b")  # CamelCase terms
        self.keyword_pattern = re.compile(r"\*\*?([A-Z][a-zA-Z\s-]+?)\*\*?")  # Bold terms

    def extract_terms_from_pattern(self, pattern: Pattern) -> set[str]:
        """Extract all terms from a pattern.

        Args:
            pattern: Pattern to extract terms from

        Returns:
            Set of unique terms
        """
        terms = set()
        content = pattern.content + " " + pattern.title

        # Extract U.Types
        u_types = self.u_type_pattern.findall(content)
        terms.update(f"U.{ut}" for ut in u_types)

        # Extract variables (backtick-enclosed)
        variables = self.variable_pattern.findall(content)
        terms.update(variables)

        # Extract CamelCase terms
        camel_case = self.term_pattern.findall(content)
        terms.update(cc for cc in camel_case if len(cc) > 3)  # Filter short matches

        # Extract bold terms
        bold_terms = self.keyword_pattern.findall(content)
        terms.update(bt.strip() for bt in bold_terms if len(bt.strip()) > 2)

        # Add keywords
        terms.update(pattern.keywords)

        return terms

    def build_term_cooccurrence_matrix(self, spec: FPFSpec) -> dict[str, dict[str, int]]:
        """Build a co-occurrence matrix of terms across patterns.

        Args:
            spec: The FPFSpec object

        Returns:
            Dictionary mapping term pairs to co-occurrence counts
        """
        term_patterns: dict[str, set[str]] = defaultdict(set)

        # Collect terms for each pattern
        for pattern in spec.patterns:
            terms = self.extract_terms_from_pattern(pattern)
            for term in terms:
                term_patterns[term].add(pattern.id)

        # Build co-occurrence matrix
        cooccurrence: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        terms_list = list(term_patterns.keys())

        for i, term1 in enumerate(terms_list):
            for term2 in terms_list[i + 1:]:
                # Count patterns where both terms appear
                patterns1 = term_patterns[term1]
                patterns2 = term_patterns[term2]
                overlap = len(patterns1 & patterns2)

                if overlap > 0:
                    cooccurrence[term1][term2] = overlap
                    cooccurrence[term2][term1] = overlap

        return dict(cooccurrence)

    def get_shared_terms(self, spec: FPFSpec, min_occurrences: int = 2) -> list[tuple[str, int, list[str]]]:
        """Get terms that appear in multiple patterns.

        Args:
            spec: The FPFSpec object
            min_occurrences: Minimum number of patterns a term must appear in

        Returns:
            List of tuples (term, occurrence_count, pattern_ids)
        """
        term_patterns: dict[str, set[str]] = defaultdict(set)

        for pattern in spec.patterns:
            terms = self.extract_terms_from_pattern(pattern)
            for term in terms:
                term_patterns[term].add(pattern.id)

        shared = [
            (term, len(patterns), sorted(patterns))
            for term, patterns in term_patterns.items()
            if len(patterns) >= min_occurrences
        ]

        # Sort by occurrence count (descending)
        shared.sort(key=lambda x: x[1], reverse=True)

        return shared

    def get_term_frequency(self, spec: FPFSpec) -> dict[str, int]:
        """Get frequency of each term across all patterns.

        Args:
            spec: The FPFSpec object

        Returns:
            Dictionary mapping terms to their frequency counts
        """
        term_counter = Counter()

        for pattern in spec.patterns:
            terms = self.extract_terms_from_pattern(pattern)
            term_counter.update(terms)

        return dict(term_counter)

    def get_important_terms(
        self, spec: FPFSpec, top_n: int = 50
    ) -> list[tuple[str, int, float]]:
        """Get most important terms based on frequency and distribution.

        Args:
            spec: The FPFSpec object
            top_n: Number of top terms to return

        Returns:
            List of tuples (term, frequency, importance_score)
        """
        term_frequency = self.get_term_frequency(spec)
        term_patterns: dict[str, set[str]] = defaultdict(set)

        for pattern in spec.patterns:
            terms = self.extract_terms_from_pattern(pattern)
            for term in terms:
                term_patterns[term].add(pattern.id)

        # Calculate importance: frequency * distribution
        importance_scores = []
        total_patterns = len(spec.patterns)

        for term, freq in term_frequency.items():
            pattern_count = len(term_patterns.get(term, set()))
            # Importance = frequency * (pattern_count / total_patterns)
            importance = freq * (pattern_count / max(total_patterns, 1))
            importance_scores.append((term, freq, importance))

        # Sort by importance
        importance_scores.sort(key=lambda x: x[2], reverse=True)

        return importance_scores[:top_n]

    def analyze_section_terms(self, spec: FPFSpec, part: str = None) -> dict[str, list[str]]:
        """Analyze terms by section/part.

        Args:
            spec: The FPFSpec object
            part: Optional part identifier to filter by

        Returns:
            Dictionary mapping section/part to list of unique terms
        """
        section_terms: dict[str, set[str]] = defaultdict(set)

        for pattern in spec.patterns:
            if part and pattern.part != part:
                continue

            section = pattern.part or "Other"
            terms = self.extract_terms_from_pattern(pattern)
            section_terms[section].update(terms)

        return {section: sorted(terms) for section, terms in section_terms.items()}

    def find_cross_section_terms(
        self, spec: FPFSpec, min_sections: int = 2
    ) -> list[tuple[str, int, list[str]]]:
        """Find terms that appear across multiple sections/parts.

        Args:
            spec: The FPFSpec object
            min_sections: Minimum number of sections a term must appear in

        Returns:
            List of tuples (term, section_count, section_names)
        """
        term_sections: dict[str, set[str]] = defaultdict(set)

        for pattern in spec.patterns:
            section = pattern.part or "Other"
            terms = self.extract_terms_from_pattern(pattern)
            for term in terms:
                term_sections[term].add(section)

        cross_section = [
            (term, len(sections), sorted(sections))
            for term, sections in term_sections.items()
            if len(sections) >= min_sections
        ]

        cross_section.sort(key=lambda x: x[1], reverse=True)

        return cross_section

