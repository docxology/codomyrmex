"""SemioticAnalyzer — decode signs and track semiotic drift."""

from __future__ import annotations

import re
from collections import Counter

from codomyrmex.meme.semiotic.models import (
    DriftReport,
    SemanticTerritory,
    Sign,
    SignType,
)


class SemioticAnalyzer:
    """Analyze text for semiotic content — signs, drift, and territories.

    Provides methods to decode text into signs, measure semiotic drift
    between corpora, and map semantic territories using frequency analysis.
    """

    # Unicode ranges for emoji and symbols (Icons)
    _ICON_PATTERNS = re.compile(
        r"[\U0001F300-\U0001F9FF]|[\u2600-\u26FF]", re.UNICODE
    )

    def decode(self, text: str) -> list[Sign]:
        """Extract signs from text via keyword and pattern heuristics.

        Args:
            text: Input text to analyze.

        Returns:
            List of Sign objects found in the text.
        """
        signs: list[Sign] = []
        words = text.split()
        seen: set[str] = set()

        for i, word in enumerate(words):
            clean = word.strip(".,!?;:\"'()[]{}").lower()
            if not clean or clean in seen or len(clean) < 2:
                continue

            # Context window: +/- 2 words
            start = max(0, i - 2)
            end = min(len(words), i + 3)
            context = " ".join(words[start:end])

            sign_type = self._infer_type(clean, context)
            seen.add(clean)

            signs.append(
                Sign(
                    signifier=clean,
                    signified=context,  # In this simplified model, context IS meaning
                    sign_type=sign_type,
                    cultural_context=context,
                )
            )
        return signs

    def _infer_type(self, word: str, context: str) -> SignType:
        """Heuristic sign type classification."""
        if self._ICON_PATTERNS.search(word):
            return SignType.ICON

        # Deictic words are typically Indices
        demonstratives = {"this", "that", "here", "there", "now", "then", "I", "you"}
        if word in demonstratives:
            return SignType.INDEX

        # Default to Symbol for arbitrary linguistic signs
        return SignType.SYMBOL

    def drift(self, corpus_a: list[str], corpus_b: list[str]) -> DriftReport:
        """Measure semiotic drift between two corpora.

        Compare how signs are used (their 'signified' context) in corpus A vs B.

        Args:
            corpus_a: Source text list (baseline).
            corpus_b: Target text list (comparison).

        Returns:
            DriftReport detailing shifts, stability, and new/lost signs.
        """
        signs_a = {}
        for text in corpus_a:
            for s in self.decode(text):
                # Simply update; last seen context wins in this simple model
                signs_a[s.signifier] = s

        signs_b = {}
        for text in corpus_b:
            for s in self.decode(text):
                signs_b[s.signifier] = s

        keys_a = set(signs_a.keys())
        keys_b = set(signs_b.keys())
        shared_keys = keys_a & keys_b

        shifted = []
        stable = []

        for k in shared_keys:
            # Check if signified (context) is substantially different
            # Simple check: word overlap Jaccard sim < threshold
            ctx_a = set(signs_a[k].signified.split())
            ctx_b = set(signs_b[k].signified.split())
            intersection = len(ctx_a & ctx_b)
            union = len(ctx_a | ctx_b)
            jaccard = intersection / union if union > 0 else 0.0

            if jaccard < 0.3:  # Low overlap = meaning shift
                shifted.append(signs_b[k])
            else:
                stable.append(signs_b[k])

        new_signs = [signs_b[k] for k in keys_b - keys_a]
        lost_signs = [signs_a[k] for k in keys_a - keys_b]

        total_changes = len(shifted) + len(new_signs) + len(lost_signs)
        total_observed = len(keys_a | keys_b)
        magnitude = total_changes / total_observed if total_observed > 0 else 0.0

        return DriftReport(
            shifted_signs=shifted,
            stable_signs=stable,
            new_signs=new_signs,
            lost_signs=lost_signs,
            drift_magnitude=magnitude,
        )

    def territory_map(
        self, corpus: list[str], n_domains: int = 5
    ) -> list[SemanticTerritory]:
        """Map semantic territories from a corpus.

        Identifies key semantic domains via frequent terms and clusters
        related signs around them.

        Args:
            corpus: Input texts to map.
            n_domains: Number of top-level territories to identify.

        Returns:
            List of SemanticTerritory objects.
        """
        all_signs = []
        for text in corpus:
            all_signs.extend(self.decode(text))

        # Find most frequent context words to use as domain anchors
        context_words = []
        for s in all_signs:
            context_words.extend(s.signified.split())

        # Filter stop words (simple list for now)
        stop_words = {"the", "a", "an", "is", "of", "to", "in", "and", "sign", "context"}
        clean_words = [w.lower().strip(".,!?") for w in context_words]
        clean_words = [w for w in clean_words if w not in stop_words and len(w) > 3]

        freq = Counter(clean_words)
        top_domains = [w for w, _ in freq.most_common(n_domains)]

        territories = []
        for domain in top_domains:
            # Gather signs that appear in this domain's context
            domain_signs = [
                s for s in all_signs if domain in s.signified.lower()
            ]
            # De-duplicate by signifier
            unique_signs = {s.signifier: s for s in domain_signs}.values()

            territories.append(
                SemanticTerritory(
                    domain=domain,
                    signs=list(unique_signs),
                    boundaries={domain: 1.0},  # Self-reference boundary
                )
            )

        return territories
