"""Unit tests for Bayesian inference."""

import pytest

from codomyrmex.cerebrum.bayesian import (
    BayesianNetwork,
    Distribution,
    InferenceEngine,
    NetworkStructureError,
    InferenceError,
)


class TestDistribution:
    """Test Distribution class."""

    def test_distribution_creation(self):
        """Test distribution creation."""
        dist = Distribution(values=["a", "b", "c"], probabilities=[0.5, 0.3, 0.2])
        assert len(dist.values) == 3
        assert abs(sum(dist.probabilities) - 1.0) < 1e-6

    def test_distribution_normalization(self):
        """Test probability normalization."""
        dist = Distribution(values=["a", "b"], probabilities=[2.0, 1.0])
        assert abs(sum(dist.probabilities) - 1.0) < 1e-6

    def test_distribution_sample(self):
        """Test sampling from distribution."""
        dist = Distribution(values=["a", "b"], probabilities=[0.7, 0.3])
        samples = dist.sample(n=100)
        assert len(samples) == 100
        assert all(s in ["a", "b"] for s in samples)

    def test_distribution_mode(self):
        """Test mode computation."""
        dist = Distribution(values=["a", "b", "c"], probabilities=[0.1, 0.7, 0.2])
        assert dist.mode() == "b"


class TestBayesianNetwork:
    """Test BayesianNetwork class."""

    def test_add_node(self):
        """Test adding nodes."""
        network = BayesianNetwork()
        network.add_node("A", values=[0, 1])
        assert "A" in network.nodes

    def test_add_node_duplicate(self):
        """Test adding duplicate node."""
        network = BayesianNetwork()
        network.add_node("A", values=[0, 1])
        with pytest.raises(NetworkStructureError):
            network.add_node("A", values=[0, 1])

    def test_add_edge(self):
        """Test adding edges."""
        network = BayesianNetwork()
        network.add_node("A", values=[0, 1])
        network.add_node("B", values=[0, 1])
        network.add_edge("A", "B")
        assert "B" in network.edges["A"]

    def test_add_edge_invalid(self):
        """Test adding edge with invalid nodes."""
        network = BayesianNetwork()
        network.add_node("A", values=[0, 1])
        with pytest.raises(NetworkStructureError):
            network.add_edge("A", "B")  # B doesn't exist

    def test_set_cpt(self):
        """Test setting conditional probability table."""
        network = BayesianNetwork()
        network.add_node("A", values=[0, 1])
        network.add_node("B", values=[0, 1])
        network.add_edge("A", "B")
        
        network.set_cpt("B", {
            (0,): {0: 0.8, 1: 0.2},
            (1,): {0: 0.3, 1: 0.7},
        })
        
        assert () in network.cpt["A"]  # Root node has empty parent config
        assert (0,) in network.cpt["B"]


class TestInferenceEngine:
    """Test InferenceEngine class."""

    def test_simple_inference(self):
        """Test simple inference."""
        network = BayesianNetwork()
        network.add_node("A", values=[0, 1], prior=[0.5, 0.5])
        network.add_node("B", values=[0, 1])
        network.add_edge("A", "B")
        network.set_cpt("B", {
            (0,): {0: 0.8, 1: 0.2},
            (1,): {0: 0.3, 1: 0.7},
        })
        
        inference = InferenceEngine(network)
        result = inference.compute_marginal("A")
        
        assert "A" in result.values
        assert abs(sum(result.probabilities) - 1.0) < 1e-6

    def test_inference_with_evidence(self):
        """Test inference with evidence."""
        network = BayesianNetwork()
        network.add_node("A", values=[0, 1], prior=[0.5, 0.5])
        network.add_node("B", values=[0, 1])
        network.add_edge("A", "B")
        network.set_cpt("B", {
            (0,): {0: 0.8, 1: 0.2},
            (1,): {0: 0.3, 1: 0.7},
        })
        
        inference = InferenceEngine(network)
        evidence = {"B": 1}
        result = inference.compute_marginal("A", evidence)
        
        assert "A" in result.values
        assert abs(sum(result.probabilities) - 1.0) < 1e-6

    def test_inference_invalid_variable(self):
        """Test inference with invalid variable."""
        network = BayesianNetwork()
        network.add_node("A", values=[0, 1])
        
        inference = InferenceEngine(network)
        with pytest.raises(InferenceError):
            inference.compute_marginal("B")  # B doesn't exist


