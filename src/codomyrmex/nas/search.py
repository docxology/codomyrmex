"""
Neural Architecture Search with random and evolutionary strategies.

Defines a search space over transformer-like architectures and provides
random search + evolutionary search with mutation. The evaluation function
is pluggable, making this a general NAS framework.
"""

import random
from dataclasses import dataclass, field
from typing import Callable

import numpy as np


@dataclass
class ArchConfig:
    """Architecture configuration sampled from search space."""

    n_layers: int
    d_model: int
    n_heads: int
    d_ff: int
    dropout: float
    activation: str
    params: dict = field(default_factory=dict)

    @property
    def total_params_estimate(self) -> int:
        """Rough parameter count estimate for a transformer-like model."""
        per_layer = (
            4 * self.d_model * self.d_model  # Q, K, V, O matrices
            + 2 * self.d_model * self.d_ff  # FFN weights
        )
        return self.n_layers * per_layer + self.d_model * 32000  # embedding


@dataclass
class NASSearchSpace:
    """Defines the searchable architecture dimensions."""

    n_layers: list[int] = field(default_factory=lambda: [1, 2, 4, 6, 8])
    d_model: list[int] = field(default_factory=lambda: [64, 128, 256, 512])
    n_heads: list[int] = field(default_factory=lambda: [2, 4, 8])
    d_ff_multiplier: list[int] = field(default_factory=lambda: [2, 4, 8])
    dropout: list[float] = field(default_factory=lambda: [0.0, 0.1, 0.3])
    activation: list[str] = field(default_factory=lambda: ["relu", "gelu", "swish"])

    def sample(self, seed: int = None) -> ArchConfig:
        """Sample a random architecture from the search space."""
        if seed is not None:
            random.seed(seed)

        d_model = random.choice(self.d_model)
        n_heads = random.choice([h for h in self.n_heads if d_model % h == 0])
        d_ff_mult = random.choice(self.d_ff_multiplier)

        return ArchConfig(
            n_layers=random.choice(self.n_layers),
            d_model=d_model,
            n_heads=n_heads,
            d_ff=d_model * d_ff_mult,
            dropout=random.choice(self.dropout),
            activation=random.choice(self.activation),
        )

    def validate(self, config: ArchConfig) -> bool:
        """Check if an architecture config is valid."""
        return (
            config.n_layers in self.n_layers
            and config.d_model in self.d_model
            and config.n_heads in self.n_heads
            and config.d_model % config.n_heads == 0
            and 0 <= config.dropout < 1.0
        )


class NASSearcher:
    """Neural Architecture Search with pluggable evaluation function."""

    def __init__(
        self,
        search_space: NASSearchSpace,
        eval_fn: Callable[[ArchConfig], float],
    ):
        self.search_space = search_space
        self.eval_fn = eval_fn  # Returns score (higher = better)
        self.history: list[tuple[ArchConfig, float]] = []

    def random_search(self, n_trials: int = 20, seed: int = None) -> ArchConfig:
        """Random architecture search."""
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        best_config = None
        best_score = float("-inf")

        for i in range(n_trials):
            config = self.search_space.sample()
            score = self.eval_fn(config)
            self.history.append((config, score))

            if score > best_score:
                best_score = score
                best_config = config

        return best_config

    def evolutionary_search(
        self,
        n_generations: int = 5,
        population_size: int = 10,
        n_mutations: int = 3,
        seed: int = None,
    ) -> ArchConfig:
        """Evolutionary architecture search with mutation."""
        if seed is not None:
            random.seed(seed)

        # Initialize population
        population = [self.search_space.sample() for _ in range(population_size)]
        scores = [self.eval_fn(c) for c in population]
        self.history.extend(zip(population, scores))

        for gen in range(n_generations):
            # Select top half
            ranked = sorted(
                zip(scores, population), key=lambda x: x[0], reverse=True
            )
            top_configs = [c for _, c in ranked[: population_size // 2]]

            # Mutate to fill population
            new_population = list(top_configs)
            while len(new_population) < population_size:
                parent = random.choice(top_configs)
                child = self._mutate(parent)
                new_population.append(child)

            population = new_population
            scores = [self.eval_fn(c) for c in population]
            self.history.extend(zip(population, scores))

        best_idx = int(np.argmax(scores))
        return population[best_idx]

    def _mutate(self, config: ArchConfig) -> ArchConfig:
        """Randomly modify one dimension of an architecture config."""
        space = self.search_space

        mutation = random.choice(["n_layers", "d_model", "dropout", "activation"])

        if mutation == "n_layers":
            n_layers = random.choice(space.n_layers)
        else:
            n_layers = config.n_layers

        if mutation == "d_model":
            d_model = random.choice(space.d_model)
            n_heads = random.choice([h for h in space.n_heads if d_model % h == 0])
        else:
            d_model = config.d_model
            n_heads = config.n_heads

        dropout = random.choice(space.dropout) if mutation == "dropout" else config.dropout
        activation = (
            random.choice(space.activation) if mutation == "activation" else config.activation
        )

        return ArchConfig(
            n_layers=n_layers,
            d_model=d_model,
            n_heads=n_heads,
            d_ff=d_model * 4,
            dropout=dropout,
            activation=activation,
        )

    def best(self) -> tuple[ArchConfig, float]:
        """Return the best architecture and score found so far."""
        if not self.history:
            raise RuntimeError(
                "No search history. Call random_search or evolutionary_search first."
            )
        return max(self.history, key=lambda x: x[1])


def random_search(
    search_space: NASSearchSpace,
    eval_fn: Callable,
    n_trials: int = 20,
) -> ArchConfig:
    """Convenience function for random architecture search."""
    searcher = NASSearcher(search_space, eval_fn)
    return searcher.random_search(n_trials)


def evolutionary_search(
    search_space: NASSearchSpace,
    eval_fn: Callable,
    n_generations: int = 5,
    population_size: int = 10,
) -> ArchConfig:
    """Convenience function for evolutionary architecture search."""
    searcher = NASSearcher(search_space, eval_fn)
    return searcher.evolutionary_search(n_generations, population_size)
