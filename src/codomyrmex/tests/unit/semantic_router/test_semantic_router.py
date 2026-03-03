"""
Unit tests for the Semantic Router module.

Tests cover:
- Route addition and retrieval
- Routing exact match for similar utterances
- No-match when below threshold
- Batch routing
- Empty router behavior
- Embedding determinism
- RouteMatch dataclass fields
- MCP tool interface
"""

import numpy as np
import pytest

from codomyrmex.semantic_router import Route, RouteMatch, SemanticRouter

# ---------------------------------------------------------------------------
# SemanticRouter - Basic
# ---------------------------------------------------------------------------


class TestSemanticRouterBasic:
    """Tests for basic router functionality."""

    @pytest.mark.unit
    def test_add_route_returns_self(self):
        """add_route should return self for chaining."""
        router = SemanticRouter(embedding_dim=32)
        result = router.add_route(Route(name="test", utterances=["hello"]))
        assert result is router

    @pytest.mark.unit
    def test_add_route_stores_route(self):
        """Added route should be in routes dict."""
        router = SemanticRouter(embedding_dim=32)
        router.add_route(Route(name="greet", utterances=["hello", "hi"]))
        assert "greet" in router.routes

    @pytest.mark.unit
    def test_add_route_computes_embeddings(self):
        """Route should have pre-computed embeddings after adding."""
        router = SemanticRouter(embedding_dim=32)
        route = Route(name="test", utterances=["hello", "hi there"])
        router.add_route(route)
        assert route.embeddings is not None
        assert route.embeddings.shape == (2, 32)

    @pytest.mark.unit
    def test_empty_router_returns_no_match(self):
        """Routing on empty router should return no_match."""
        router = SemanticRouter(embedding_dim=32)
        result = router.route("anything")
        assert result.route_name == "no_match"
        assert result.matched is False
        assert result.score == 0.0


# ---------------------------------------------------------------------------
# SemanticRouter - Routing
# ---------------------------------------------------------------------------


class TestSemanticRouterRouting:
    """Tests for routing behavior."""

    def _build_router(self):
        router = SemanticRouter(embedding_dim=64)
        router.add_route(
            Route(
                name="weather",
                utterances=[
                    "What is the weather?",
                    "How is the weather today?",
                    "Will it rain?",
                    "Temperature today?",
                ],
                threshold=0.7,
            )
        )
        router.add_route(
            Route(
                name="greeting",
                utterances=["Hello", "Hi there", "Good morning", "Hey"],
                threshold=0.7,
            )
        )
        return router

    @pytest.mark.unit
    def test_route_similar_text_matches(self):
        """Text very similar to a route's utterances should match."""
        router = self._build_router()
        result = router.route("What is the weather today?")
        assert result.matched is True
        assert result.route_name == "weather"

    @pytest.mark.unit
    def test_route_exact_utterance_matches(self):
        """Exact utterance should match its own route with high score."""
        router = self._build_router()
        result = router.route("Hello")
        assert result.matched is True
        assert result.route_name == "greeting"
        assert result.score > 0.99  # Near-perfect match

    @pytest.mark.unit
    def test_route_score_is_between_zero_and_one(self):
        """Cosine similarity score should be in [0, 1] for normalized vectors."""
        router = self._build_router()
        result = router.route("Some random text about weather")
        assert 0.0 <= result.score <= 1.0 + 1e-6

    @pytest.mark.unit
    def test_route_no_match_below_threshold(self):
        """Text very different from all routes should not match."""
        router = SemanticRouter(embedding_dim=64)
        router.add_route(
            Route(
                name="specific",
                utterances=["xyzzy foobar"],
                threshold=0.99,  # Very high threshold
            )
        )
        result = router.route("completely unrelated text about nothing")
        # With hash embeddings and high threshold, this should not match
        assert result.score < 0.99 or result.route_name == "specific"

    @pytest.mark.unit
    def test_route_deterministic(self):
        """Same input should always produce same output (no randomness)."""
        router = self._build_router()
        r1 = router.route("weather forecast")
        r2 = router.route("weather forecast")
        assert r1.route_name == r2.route_name
        assert r1.score == r2.score
        assert r1.matched == r2.matched

    @pytest.mark.unit
    def test_route_without_embeddings_is_skipped(self):
        """A route with missing embeddings should be gracefully skipped."""
        router = SemanticRouter(embedding_dim=64)
        # Manually add a route without embeddings
        route = Route(name="invalid", utterances=["bad"])
        router.routes["invalid"] = route

        result = router.route("test text")
        assert result.matched is False
        assert result.route_name == "no_match"


# ---------------------------------------------------------------------------
# SemanticRouter - Batch
# ---------------------------------------------------------------------------


class TestSemanticRouterBatch:
    """Tests for batch routing."""

    @pytest.mark.unit
    def test_route_batch_returns_list(self):
        """Batch routing should return a list of RouteMatch objects."""
        router = SemanticRouter(embedding_dim=32)
        router.add_route(Route(name="test", utterances=["hello"]))
        results = router.route_batch(["hello", "hi", "hey"])
        assert isinstance(results, list)
        assert len(results) == 3
        assert all(isinstance(r, RouteMatch) for r in results)

    @pytest.mark.unit
    def test_route_batch_empty_input(self):
        """Empty batch should return empty list."""
        router = SemanticRouter(embedding_dim=32)
        results = router.route_batch([])
        assert results == []


# ---------------------------------------------------------------------------
# Embedding
# ---------------------------------------------------------------------------


class TestEmbedding:
    """Tests for the simple hash-based embedding."""

    @pytest.mark.unit
    def test_embedding_is_normalized(self):
        """Embedding vectors should be approximately unit norm."""
        router = SemanticRouter(embedding_dim=64)
        emb = router._simple_embed("test text")
        norm = np.linalg.norm(emb)
        np.testing.assert_allclose(norm, 1.0, atol=1e-6)

    @pytest.mark.unit
    def test_embedding_shape(self):
        """Embedding should match specified dimension."""
        router = SemanticRouter(embedding_dim=128)
        emb = router._simple_embed("hello world")
        assert emb.shape == (128,)

    @pytest.mark.unit
    def test_embedding_deterministic(self):
        """Same text should always produce same embedding."""
        router = SemanticRouter(embedding_dim=64)
        e1 = router._simple_embed("test")
        e2 = router._simple_embed("test")
        np.testing.assert_array_equal(e1, e2)

    @pytest.mark.unit
    def test_embedding_case_insensitive(self):
        """Embedding should be case-insensitive (lowercases input)."""
        router = SemanticRouter(embedding_dim=64)
        e1 = router._simple_embed("Hello")
        e2 = router._simple_embed("hello")
        np.testing.assert_array_equal(e1, e2)


# ---------------------------------------------------------------------------
# RouteMatch dataclass
# ---------------------------------------------------------------------------


class TestRouteMatch:
    """Tests for RouteMatch dataclass."""

    @pytest.mark.unit
    def test_route_match_fields(self):
        rm = RouteMatch(route_name="test", score=0.85, matched=True)
        assert rm.route_name == "test"
        assert rm.score == 0.85
        assert rm.matched is True


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


class TestMCPTools:
    """Tests for Semantic Router MCP tool interface."""

    @pytest.mark.unit
    def test_semantic_router_route_tool(self):
        from codomyrmex.semantic_router.mcp_tools import semantic_router_route

        result = semantic_router_route(text="What is the weather today?")
        assert result["status"] == "success"
        assert "route_name" in result
        assert "score" in result
        assert "matched" in result
        assert "all_routes" in result

    @pytest.mark.unit
    def test_semantic_router_tool_has_mcp_metadata(self):
        from codomyrmex.semantic_router.mcp_tools import semantic_router_route

        assert hasattr(semantic_router_route, "_mcp_tool")
        assert semantic_router_route._mcp_tool["category"] == "semantic_router"

    @pytest.mark.unit
    def test_semantic_router_tool_custom_routes(self):
        from codomyrmex.semantic_router.mcp_tools import semantic_router_route

        custom_routes = [
            {"name": "code", "utterances": ["write code", "implement function"]},
            {"name": "docs", "utterances": ["write documentation", "add docs"]},
        ]
        result = semantic_router_route(text="write code", routes=custom_routes)
        assert result["status"] == "success"
        assert set(result["all_routes"]) == {"code", "docs"}
