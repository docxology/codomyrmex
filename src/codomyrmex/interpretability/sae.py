"""Sparse Autoencoder (SAE) for mechanistic interpretability."""

import numpy as np


class SparseAutoencoder:
    """
    Sparse Autoencoder (SAE) for mechanistic interpretability.

    SAEs learn a sparse overcomplete basis for neural network activations.
    Used to decompose superposition in transformer residual streams into
    interpretable "features" (Elhage et al. 2022, Cunningham et al. 2023).

    Architecture:
        Encoder: x -> ReLU(W_enc @ (x - b_dec) + b_enc) -> features (sparse)
        Decoder: features -> W_dec @ features + b_dec    -> reconstruction

    Loss:
        reconstruction_loss = ||x - x_hat||^2
        sparsity_loss = lambda_l1 * ||features||_1
        total = reconstruction_loss + sparsity_loss
    """

    def __init__(self, d_input: int, d_features: int, lambda_l1: float = 1e-3):
        """
        Args:
            d_input: Dimension of input activations
            d_features: Number of sparse features (> d_input for overcomplete)
            lambda_l1: L1 sparsity penalty coefficient
        """
        self.d_input = d_input
        self.d_features = d_features
        self.lambda_l1 = lambda_l1

        # Initialize with He-style scaling
        scale = np.sqrt(2.0 / d_input)
        self.W_enc = np.random.randn(d_features, d_input) * scale
        self.W_dec = self.W_enc.T.copy()  # (d_input, d_features)
        self.b_enc = np.zeros(d_features)
        self.b_dec = np.zeros(d_input)

        self._normalize_decoder()

    def _normalize_decoder(self):
        """Normalize decoder columns to unit norm (standard SAE practice)."""
        norms = np.linalg.norm(self.W_dec, axis=0, keepdims=True)
        self.W_dec = self.W_dec / (norms + 1e-8)

    def encode(self, x: np.ndarray) -> np.ndarray:
        """Encode inputs to sparse features.

        Args:
            x: (batch, d_input) activations

        Returns:
            features: (batch, d_features) sparse activations (ReLU produces mostly zeros)
        """
        pre_relu = (x - self.b_dec) @ self.W_enc.T + self.b_enc
        return np.maximum(0, pre_relu)  # ReLU sparsity

    def decode(self, features: np.ndarray) -> np.ndarray:
        """Decode sparse features back to activation space."""
        return features @ self.W_dec.T + self.b_dec

    def forward(self, x: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Encode then decode."""
        features = self.encode(x)
        reconstruction = self.decode(features)
        return reconstruction, features

    def loss(self, x: np.ndarray) -> dict:
        """Compute SAE loss components."""
        reconstruction, features = self.forward(x)

        # Reconstruction loss: MSE
        recon_loss = float(np.mean((x - reconstruction) ** 2))

        # Sparsity loss: L1 norm of features
        sparsity_loss = float(
            self.lambda_l1 * np.mean(np.sum(np.abs(features), axis=-1))
        )

        # Metrics
        n_active = float(np.mean(np.sum(features > 0, axis=-1)))

        return {
            "total_loss": recon_loss + sparsity_loss,
            "reconstruction_loss": recon_loss,
            "sparsity_loss": sparsity_loss,
            "mean_active_features": n_active,
            "sparsity_ratio": n_active / self.d_features,
        }

    def train_step(self, x: np.ndarray, lr: float = 1e-3) -> dict:
        """One gradient descent step using closed-form gradients."""
        reconstruction, features = self.forward(x)

        # Gradient of MSE wrt decoder
        residual = reconstruction - x  # (batch, d_input)
        grad_W_dec = (residual.T @ features) / len(x)  # (d_input, d_features)
        grad_b_dec = np.mean(residual, axis=0)  # (d_input,)

        # L1 gradient for encoder bias
        sign_features = np.sign(features)  # (batch, d_features)
        grad_b_enc = self.lambda_l1 * np.mean(sign_features, axis=0)

        # Update
        self.W_dec -= lr * grad_W_dec
        self.b_dec -= lr * grad_b_dec
        self.b_enc -= lr * grad_b_enc
        self._normalize_decoder()

        return self.loss(x)


def train_sae(
    activations: np.ndarray,
    d_features: int = None,
    n_steps: int = 100,
    lr: float = 1e-3,
    lambda_l1: float = 1e-3,
    seed: int = None,
) -> SparseAutoencoder:
    """Train a sparse autoencoder on neural network activations."""
    if seed is not None:
        np.random.seed(seed)

    d_input = activations.shape[-1]
    d_features = d_features or d_input * 4  # Overcomplete by 4x

    sae = SparseAutoencoder(d_input, d_features, lambda_l1)

    for _step in range(n_steps):
        batch_size = min(32, len(activations))
        idx = np.random.choice(len(activations), batch_size, replace=False)
        batch = activations[idx]
        sae.train_step(batch, lr)

    return sae


def analyze_features(sae: SparseAutoencoder, activations: np.ndarray) -> dict:
    """Analyze learned features: find most active, compute correlations."""
    features = sae.encode(activations)

    # Feature activation statistics
    activation_freq = np.mean(features > 0, axis=0)
    mean_activation = np.mean(features, axis=0)

    # Top features by frequency
    top_k = min(10, sae.d_features)
    top_feature_ids = np.argsort(activation_freq)[-top_k:][::-1]

    return {
        "d_features": sae.d_features,
        "mean_active_features": float(np.mean(np.sum(features > 0, axis=-1))),
        "sparsity_ratio": float(np.mean(features > 0)),
        "top_features": [
            {
                "feature_id": int(i),
                "activation_freq": float(activation_freq[i]),
                "mean_activation": float(mean_activation[i]),
            }
            for i in top_feature_ids
        ],
    }
