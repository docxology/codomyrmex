import pytest
import shutil

from codomyrmex.llm.fabric.fabric_manager import FabricManager
from codomyrmex.llm.fabric.fabric_orchestrator import FabricOrchestrator


def test_fabric_manager_zero_mock_degradation():
    """
    Test that FabricManager acts naturally.
    If fabric is unavailable, it should degrade gracefully (success=False, specific error).
    """
    # Use a non-existent binary to force the fallback exactly
    manager = FabricManager(fabric_binary="non_existent_fabric_binary_12345")

    assert manager.is_available() is False
    assert manager.list_patterns() == []

    result = manager.run_pattern("analyze_code", "print('hello world')")
    assert result["success"] is False
    assert "Fabric not available" in result["error"]

    history = manager.get_results_history()
    assert len(history) == 0  # because unavailable returns early without appending history


def test_fabric_orchestrator_zero_mock_degradation():
    """
    Test FabricOrchestrator chaining degrades safely.
    """
    orchestrator = FabricOrchestrator(fabric_binary="non_existent_fabric_binary_12345")

    assert orchestrator.is_available() is False

    # Run the orchestrator
    results = orchestrator.analyze_code("print('hello')", analysis_type="quality")

    assert results["analysis_type"] == "quality"
    assert "analyze_code" in results["patterns_used"]
    assert "find_code_smells" in results["patterns_used"]

    # Verify the results dictionary contains failed states
    for pattern in results["patterns_used"]:
        assert results["results"][pattern]["success"] is False
        assert "Fabric not available" in results["results"][pattern]["error"]

    assert results["summary"]["successful_patterns"] == 0
    assert results["summary"]["success_rate"] == 0.0


def test_real_fabric_execution_if_present():
    """
    If someone running tests has `fabric` installed, we verify it runs successfully.
    Otherwise we skip this specific active test.
    """
    if not shutil.which("fabric"):
        pytest.skip("Local `fabric` command not found. Skipping live invocation.")

    manager = FabricManager()

    # At this point is_available MUST be true
    assert manager.is_available() is True

    # Let's see if we can get patterns
    patterns = manager.list_patterns()
    assert isinstance(patterns, list)

    # Note: we do not fully test run_pattern because running live pattern requires an API key which might not be configured.
    # However we can evaluate the history.
    history = manager.get_results_history()
    assert isinstance(history, list)
