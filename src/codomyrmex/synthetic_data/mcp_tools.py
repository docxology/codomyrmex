"""MCP tool definitions for the synthetic_data module."""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="synthetic_data",
    description="Generate structured synthetic data from a schema definition.",
)
def synth_generate_structured(
    fields: dict[str, dict[str, Any]],
    n_samples: int = 100,
    seed: int = None,
) -> dict[str, Any]:
    """Generate structured data records matching a schema.

    Args:
        fields: Schema fields mapping name to type spec.
            Example: {"age": {"type": "int", "min": 18, "max": 65}}.
        n_samples: Number of records to generate.
        seed: Random seed for reproducibility.

    Returns:
        Dictionary with status, sample count, and generated records.
    """
    try:
        from .generator import DataSchema, SyntheticDataGenerator

        schema = DataSchema(fields=fields, n_samples=n_samples)
        gen = SyntheticDataGenerator()
        records = gen.generate_structured(schema, seed=seed)

        return {
            "status": "success",
            "n_samples": len(records),
            "records": records[:20],  # Return first 20 to avoid huge payloads
            "truncated": len(records) > 20,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(
    category="synthetic_data",
    description="Generate synthetic classification data with configurable class balance.",
)
def synth_generate_classification(
    n_samples: int = 100,
    n_classes: int = 2,
    n_features: int = 10,
    class_balance: str = "balanced",
    seed: int = None,
) -> dict[str, Any]:
    """Generate a classification dataset with features and labels.

    Args:
        n_samples: Total number of samples.
        n_classes: Number of target classes.
        n_features: Feature vector dimensionality.
        class_balance: 'balanced' or 'imbalanced'.
        seed: Random seed.

    Returns:
        Dictionary with features (first 20 rows), labels, and class distribution.
    """
    try:
        from .generator import SyntheticDataGenerator

        gen = SyntheticDataGenerator()
        features, labels = gen.generate_classification(
            n_samples=n_samples,
            n_classes=n_classes,
            n_features=n_features,
            class_balance=class_balance,
            seed=seed,
        )

        from collections import Counter

        dist = dict(Counter(labels))

        return {
            "status": "success",
            "n_samples": len(labels),
            "n_features": n_features,
            "n_classes": n_classes,
            "class_distribution": dist,
            "features_preview": features[:5],
            "labels_preview": labels[:20],
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(
    category="synthetic_data",
    description="Generate preference pairs for RLHF/DPO training.",
)
def synth_generate_preference_pairs(
    n_pairs: int = 100,
    seed: int = None,
) -> dict[str, Any]:
    """Generate preference pair data for RLHF/DPO.

    Args:
        n_pairs: Number of preference pairs.
        seed: Random seed.

    Returns:
        Dictionary with pairs and summary statistics.
    """
    try:
        from .generator import SyntheticDataGenerator

        gen = SyntheticDataGenerator()
        pairs = gen.generate_preference_pairs(n_pairs=n_pairs, seed=seed)

        return {
            "status": "success",
            "n_pairs": len(pairs),
            "pairs_preview": pairs[:5],
            "truncated": len(pairs) > 5,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
