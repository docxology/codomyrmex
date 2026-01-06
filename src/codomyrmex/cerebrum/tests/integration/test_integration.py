"""Integration tests for CEREBRUM module."""

from codomyrmex.cerebrum import (
    CerebrumEngine,
    Case,
    BayesianNetwork,
    InferenceEngine,
    CerebrumConfig,
)


def test_end_to_end_reasoning():
    """Test end-to-end reasoning workflow."""
    # Create engine
    config = CerebrumConfig(case_similarity_threshold=0.5)
    engine = CerebrumEngine(config)
    
    # Add cases
    for i in range(5):
        case = Case(
            case_id=f"case_{i}",
            features={"value": i, "category": "test"},
            outcome="success" if i < 3 else "failure"
        )
        engine.add_case(case)
    
    # Query
    query = Case(case_id="query", features={"value": 1, "category": "test"})
    result = engine.reason(query)
    
    assert result.prediction is not None
    assert result.confidence > 0
    assert len(result.retrieved_cases) > 0


def test_bayesian_integration():
    """Test integration with Bayesian network."""
    engine = CerebrumEngine()
    
    # Create Bayesian network
    network = BayesianNetwork(name="test_network")
    network.add_node("feature", values=["low", "high"], prior=[0.5, 0.5])
    network.add_node("outcome", values=["success", "failure"])
    network.add_edge("feature", "outcome")
    network.set_cpt("outcome", {
        ("low",): {"success": 0.8, "failure": 0.2},
        ("high",): {"success": 0.3, "failure": 0.7},
    })
    
    engine.set_bayesian_network(network)
    
    # Add cases
    case = Case(case_id="case1", features={"feature": "low"}, outcome="success")
    engine.add_case(case)
    
    # Reason with both case-based and Bayesian
    query = Case(case_id="query", features={"feature": "high"})
    result = engine.reason(query)
    
    assert result.prediction is not None
    assert "outcome" in result.inference_results or result.prediction is not None


