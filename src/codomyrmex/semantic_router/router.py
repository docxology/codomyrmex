"""Semantic Router -- embedding-based intent classification and routing.

Routes user inputs to named routes by comparing embedding similarity.
Each route is defined by example utterances. During routing, the input
is embedded and compared to all route examples via cosine similarity.
The route with highest similarity (above threshold) is selected.
"""
import numpy as np
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Route:
    """A named route with example utterances."""

    name: str
    utterances: list[str]  # Example phrases for this route
    embeddings: np.ndarray = None  # Pre-computed embeddings (set during fit)
    threshold: float = 0.7  # Cosine similarity threshold


@dataclass
class RouteMatch:
    """Result of routing an utterance."""

    route_name: str
    score: float
    matched: bool


class SemanticRouter:
    """Semantic router that classifies inputs to named routes using embedding similarity.

    Routes are defined by example utterances. During routing, the input is embedded
    and compared to all route examples via cosine similarity.
    The route with highest mean similarity (above threshold) is selected.
    """

    def __init__(self, embedding_dim: int = 64):
        self.embedding_dim = embedding_dim
        self.routes: dict[str, Route] = {}
        self._embed_fn = self._simple_embed

    def _simple_embed(self, text: str) -> np.ndarray:
        """Simple hash-based embedding (deterministic, for testing).

        Args:
            text: Input text string

        Returns:
            Normalized embedding vector of shape (embedding_dim,)
        """
        vec = np.zeros(self.embedding_dim)
        for i, char in enumerate(text.lower()):
            vec[i % self.embedding_dim] += ord(char) / 100.0
        norm = np.linalg.norm(vec)
        return vec / (norm + 1e-9)

    def add_route(self, route: Route) -> "SemanticRouter":
        """Add a route and pre-compute embeddings for its utterances.

        Args:
            route: Route with name and example utterances

        Returns:
            self (for chaining)
        """
        embeddings = np.stack([self._embed_fn(u) for u in route.utterances])
        route.embeddings = embeddings
        self.routes[route.name] = route
        return self

    def route(self, text: str) -> RouteMatch:
        """Route input text to best matching route.

        Args:
            text: Input text to classify

        Returns:
            RouteMatch with route_name, score, and matched flag
        """
        if not self.routes:
            return RouteMatch(route_name="no_match", score=0.0, matched=False)

        query_emb = self._embed_fn(text)

        best_route = None
        best_score = -1.0

        for name, route in self.routes.items():
            if route.embeddings is None:
                continue
            # Cosine similarity to each example, take max
            dots = route.embeddings @ query_emb
            norms = np.linalg.norm(route.embeddings, axis=1) * np.linalg.norm(
                query_emb
            )
            sims = np.where(norms > 1e-9, dots / norms, 0.0)
            score = float(np.max(sims))

            if score > best_score:
                best_score = score
                best_route = route

        if best_route and best_score >= best_route.threshold:
            return RouteMatch(
                route_name=best_route.name, score=best_score, matched=True
            )

        return RouteMatch(route_name="no_match", score=best_score, matched=False)

    def route_batch(self, texts: list[str]) -> list[RouteMatch]:
        """Route a batch of texts.

        Args:
            texts: List of input texts

        Returns:
            List of RouteMatch results
        """
        return [self.route(t) for t in texts]
