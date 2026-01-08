from typing import Any
import json

import hashlib





























"""Utility functions for CEREBRUM module."""



def compute_hash(data: Any) -> str:
    """Compute a hash for the given data.

    Args:
        data: Data to hash (must be JSON serializable)

    Returns:
        Hexadecimal hash string
    """
    data_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_str.encode()).hexdigest()


def normalize_features(features: dict[str, Any]) -> dict[str, float]:
    """Normalize feature values to [0, 1] range.

    Args:
        features: Dictionary of feature names to values

    Returns:
        Dictionary with normalized feature values
    """
    normalized = {}
    for key, value in features.items():
        if isinstance(value, (int, float)):
            # Simple normalization - in practice, use proper scaling
            normalized[key] = float(value) / (1.0 + abs(float(value)))
        else:
            # For non-numeric values, use a hash-based normalization
            normalized[key] = abs(hash(str(value))) % 1000 / 1000.0
    return normalized


def compute_euclidean_distance(vec1: dict[str, float], vec2: dict[str, float]) -> float:
    """Compute Euclidean distance between two feature vectors.

    Args:
        vec1: First feature vector
        vec2: Second feature vector

    Returns:
        Euclidean distance
    """
    all_keys = set(vec1.keys()) | set(vec2.keys())
    squared_diff = sum((vec1.get(k, 0.0) - vec2.get(k, 0.0)) ** 2 for k in all_keys)
    return (squared_diff ** 0.5) if squared_diff > 0 else 0.0


def compute_cosine_similarity(vec1: dict[str, float], vec2: dict[str, float]) -> float:
    """Compute cosine similarity between two feature vectors.

    Args:
        vec1: First feature vector
        vec2: Second feature vector

    Returns:
        Cosine similarity in [0, 1]
    """
    all_keys = set(vec1.keys()) | set(vec2.keys())
    dot_product = sum(vec1.get(k, 0.0) * vec2.get(k, 0.0) for k in all_keys)
    magnitude1 = sum(v ** 2 for v in vec1.values()) ** 0.5
    magnitude2 = sum(v ** 2 for v in vec2.values()) ** 0.5

    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    similarity = dot_product / (magnitude1 * magnitude2)
    return max(0.0, min(1.0, (similarity + 1.0) / 2.0))  # Normalize to [0, 1]


def softmax(values: list[float], temperature: float = 1.0) -> list[float]:
    """Compute softmax probabilities.

    Args:
        values: List of values
        temperature: Temperature parameter (higher = more uniform)

    Returns:
        List of probabilities
    """
    if not values:
        return []

    if temperature <= 0:
        temperature = 1.0

    exp_values = [v / temperature for v in values]
    max_exp = max(exp_values)
    exp_values = [v - max_exp for v in exp_values]  # Numerical stability
    exp_values = [2.718281828459045 ** v for v in exp_values]
    sum_exp = sum(exp_values)

    if sum_exp == 0:
        return [1.0 / len(values)] * len(values)

    return [v / sum_exp for v in exp_values]



