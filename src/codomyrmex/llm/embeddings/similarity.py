"""Vector similarity functions: cosine similarity, Euclidean distance, dot product."""

import math


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    Returns value between -1 (opposite) and 1 (identical).
    """
    if len(vec1) != len(vec2):
        raise ValueError(f"Dimension mismatch: {len(vec1)} vs {len(vec2)}")

    dot_product = sum(a * b for a, b in zip(vec1, vec2, strict=False))
    magnitude1 = math.sqrt(sum(x * x for x in vec1))
    magnitude2 = math.sqrt(sum(x * x for x in vec2))

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    return dot_product / (magnitude1 * magnitude2)


def euclidean_distance(vec1: list[float], vec2: list[float]) -> float:
    """
    Compute Euclidean distance between two vectors.

    Returns value >= 0 (0 means identical).
    """
    if len(vec1) != len(vec2):
        raise ValueError(f"Dimension mismatch: {len(vec1)} vs {len(vec2)}")

    return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec1, vec2, strict=False)))


def dot_product(vec1: list[float], vec2: list[float]) -> float:
    """Compute dot product of two vectors."""
    if len(vec1) != len(vec2):
        raise ValueError(f"Dimension mismatch: {len(vec1)} vs {len(vec2)}")

    return sum(a * b for a, b in zip(vec1, vec2, strict=False))
