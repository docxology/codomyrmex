"""Code similarity detection using structural hashing and token comparison.

Provides methods for comparing code fragments, detecting duplicate or
near-duplicate files, and computing structural fingerprints that are
resilient to superficial formatting changes.
"""

from __future__ import annotations

import ast
import hashlib
import logging
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class DuplicateResult:
    """Describes a pair of files that exceed the similarity threshold.

    Attributes:
        file_a: Path to the first file.
        file_b: Path to the second file.
        similarity: Similarity score (0.0 - 1.0).
    """

    file_a: str
    file_b: str
    similarity: float


class CodeSimilarity:
    """Code similarity analysis via tokenisation and structural hashing.

    Usage::

        sim = CodeSimilarity()
        score = sim.compute_similarity(code_a, code_b)
        dupes = sim.find_duplicates(["a.py", "b.py", "c.py"], threshold=0.8)
        fingerprint = sim.structural_hash(code)
    """

    # Regex to strip comments and normalise whitespace for tokenisation
    _COMMENT_RE = re.compile(r"#.*$", re.MULTILINE)
    _DOCSTRING_RE = re.compile(r'(\"\"\"[\s\S]*?\"\"\"|\'\'\'[\s\S]*?\'\'\')')
    _WHITESPACE_RE = re.compile(r"\s+")

    def __init__(self) -> None:
        """Initialize this instance."""
        self._cache = {}  # Initialize similarity cache

    def compute_similarity(self, code_a: str, code_b: str) -> float:
        """Compute a similarity score between two code fragments.

        Uses a combined approach:
            1. **Token-level cosine similarity** -- tokenises both fragments
               (after stripping comments/docstrings) and computes the cosine
               of their token-frequency vectors.
            2. **Structural hash comparison** -- if the structural hashes
               match exactly, the score is boosted.

        Args:
            code_a: First code fragment.
            code_b: Second code fragment.

        Returns:
            A float between 0.0 (no similarity) and 1.0 (identical).
        """
        if not code_a.strip() and not code_b.strip():
            return 1.0
        if not code_a.strip() or not code_b.strip():
            return 0.0

        tokens_a = self._tokenise(code_a)
        tokens_b = self._tokenise(code_b)

        cosine = self._cosine_similarity(tokens_a, tokens_b)

        # Structural bonus
        hash_a = self.structural_hash(code_a)
        hash_b = self.structural_hash(code_b)
        if hash_a == hash_b:
            # If structures are identical, boost similarity
            cosine = min(1.0, cosine + 0.15)

        return round(cosine, 4)

    def find_duplicates(
        self,
        files: list[str],
        threshold: float = 0.8,
    ) -> list[DuplicateResult]:
        """Identify near-duplicate file pairs above a similarity threshold.

        Reads each file, computes pairwise similarity, and returns all pairs
        exceeding the threshold.

        Args:
            files: List of file paths to compare.
            threshold: Minimum similarity to report (0.0 - 1.0).

        Returns:
            A list of :class:`DuplicateResult` objects sorted by descending
            similarity.
        """
        if threshold < 0.0 or threshold > 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0.")

        # Read all files
        contents: dict[str, str] = {}
        for fpath in files:
            try:
                contents[fpath] = Path(fpath).read_text(encoding="utf-8", errors="ignore")
            except Exception as exc:
                logger.warning("Could not read %s: %s", fpath, exc)

        file_list = list(contents.keys())
        results: list[DuplicateResult] = []

        for i in range(len(file_list)):
            for j in range(i + 1, len(file_list)):
                fa, fb = file_list[i], file_list[j]
                score = self.compute_similarity(contents[fa], contents[fb])
                if score >= threshold:
                    results.append(DuplicateResult(
                        file_a=fa,
                        file_b=fb,
                        similarity=score,
                    ))

        results.sort(key=lambda r: r.similarity, reverse=True)
        return results

    def structural_hash(self, code: str) -> str:
        """Compute a hash of the AST structure, ignoring names and literals.

        Two code fragments that differ only in variable names, string
        literals, or formatting will produce the same structural hash.

        Args:
            code: Python source code.

        Returns:
            A hex-digest string representing the structural fingerprint.
            Returns a hash of the normalised token sequence if the code
            cannot be parsed as valid Python.
        """
        try:
            tree = ast.parse(code)
            structure = self._ast_structure(tree)
        except SyntaxError:
            # Fall back to normalised token hashing
            tokens = self._tokenise(code)
            structure = " ".join(sorted(tokens))

        return hashlib.sha256(structure.encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _tokenise(self, code: str) -> list[str]:
        """Normalise and tokenise code: strip comments, docstrings, whitespace."""
        text = self._COMMENT_RE.sub("", code)
        text = self._DOCSTRING_RE.sub("", text)
        text = self._WHITESPACE_RE.sub(" ", text).strip()
        # Split on non-alphanumeric boundaries to get meaningful tokens
        tokens = re.findall(r"[A-Za-z_]\w*|\d+|[^\s\w]", text)
        return tokens

    @staticmethod
    def _cosine_similarity(tokens_a: list[str], tokens_b: list[str]) -> float:
        """Compute cosine similarity between two token-frequency vectors."""
        counter_a = Counter(tokens_a)
        counter_b = Counter(tokens_b)

        all_tokens = set(counter_a.keys()) | set(counter_b.keys())
        if not all_tokens:
            return 0.0

        dot_product = sum(counter_a.get(t, 0) * counter_b.get(t, 0) for t in all_tokens)
        mag_a = sum(v ** 2 for v in counter_a.values()) ** 0.5
        mag_b = sum(v ** 2 for v in counter_b.values()) ** 0.5

        if mag_a == 0 or mag_b == 0:
            return 0.0

        return dot_product / (mag_a * mag_b)

    @classmethod
    def _ast_structure(cls, node: ast.AST) -> str:
        """Recursively build a canonical string of AST node types.

        Ignores concrete names, values, and literals -- only the tree
        shape and node types matter.
        """
        parts = [type(node).__name__]
        for child in ast.iter_child_nodes(node):
            parts.append(cls._ast_structure(child))
        return "(" + " ".join(parts) + ")"
