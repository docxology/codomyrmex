"""MCP tool definitions for the interpretability module."""

from __future__ import annotations

from typing import Any

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="interpretability",
    description="Train a Sparse Autoencoder on activation data for mechanistic interpretability.",
)
def sae_train(
    d_input: int,
    d_features: int | None = None,
    n_samples: int = 200,
    n_steps: int = 50,
    lambda_l1: float = 1e-3,
    seed: int | None = None,
) -> dict[str, Any]:
    """Train an SAE on randomly generated activations (for testing/demo).

    Args:
        d_input: Input activation dimensionality.
        d_features: Number of sparse features (defaults to 4x d_input).
        n_samples: Number of random activation samples to generate.
        n_steps: Training steps.
        lambda_l1: L1 sparsity penalty.
        seed: Random seed.

    Returns:
        Dictionary with training loss, sparsity metrics, and top features.
    """
    try:
        import numpy as np

        from .sae import analyze_features, train_sae

        if seed is not None:
            np.random.seed(seed)

        activations = np.random.randn(n_samples, d_input)
        sae = train_sae(
            activations,
            d_features=d_features,
            n_steps=n_steps,
            lambda_l1=lambda_l1,
            seed=seed,
        )

        analysis = analyze_features(sae, activations)
        final_loss = sae.loss(activations)

        return {
            "status": "success",
            "d_input": d_input,
            "d_features": sae.d_features,
            "final_loss": final_loss,
            "analysis": analysis,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp_tool(
    category="interpretability",
    description="Analyze features learned by a Sparse Autoencoder on provided activations.",
)
def sae_analyze(
    d_input: int,
    d_features: int | None = None,
    n_samples: int = 200,
    seed: int = 42,
) -> dict[str, Any]:
    """Create an SAE and analyze its feature activation patterns.

    Args:
        d_input: Input dimensionality.
        d_features: Number of sparse features.
        n_samples: Number of activation samples.
        seed: Random seed.

    Returns:
        Dictionary with feature analysis: top features, sparsity, activation frequencies.
    """
    try:
        import numpy as np

        from .sae import SparseAutoencoder, analyze_features

        np.random.seed(seed)
        activations = np.random.randn(n_samples, d_input)

        d_features = d_features or d_input * 4
        sae = SparseAutoencoder(d_input, d_features)
        analysis = analyze_features(sae, activations)

        return {"status": "success", **analysis}
    except Exception as e:
        return {"status": "error", "message": str(e)}
