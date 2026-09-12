"""Zero-mock unit tests for demos module MCP tools."""

import pytest

from codomyrmex.demos.mcp_tools import demos_list_demos, demos_run_demo
from codomyrmex.demos.registry import get_registry


@pytest.fixture
def clean_registry():
    """Fixture to ensure the registry is clean before and after tests."""
    registry = get_registry()
    # Save the original state
    original_demos = registry._demos.copy()
    yield registry
    # Restore the original state
    registry._demos = original_demos


def test_demos_list_demos(clean_registry):
    # Register a temporary demo to ensure the list is not empty
    def dummy_demo():
        return True

    clean_registry.register(
        "dummy_test_demo",
        "Dummy description",
        dummy_demo,
        module="dummy_module",
        category="dummy_category",
    )

    results = demos_list_demos()
    assert isinstance(results, list)

    # Check if our dummy is in the results
    dummy_found = False
    for res in results:
        if res["name"] == "dummy_test_demo":
            dummy_found = True
            assert res["description"] == "Dummy description"
            assert res["module"] == "dummy_module"
            assert res["category"] == "dummy_category"

    assert dummy_found, "The registered dummy demo was not found by demos_list_demos"

    # Test filtering
    filtered_results = demos_list_demos(module="dummy_module")
    assert all(r["module"] == "dummy_module" for r in filtered_results)
    assert len(filtered_results) > 0


def test_demos_run_demo(clean_registry):
    # Register a successful temporary demo
    def success_demo():
        return "Success Output"

    clean_registry.register("success_test_demo", "A successful demo", success_demo)

    res = demos_run_demo("success_test_demo")
    assert res["name"] == "success_test_demo"
    assert res["success"] is True
    assert res["output"] == "Success Output"
    assert res["error"] is None
    assert "execution_time" in res

    # Register a failing temporary demo
    def fail_demo():
        raise ValueError("Intentional Failure")

    clean_registry.register("fail_test_demo", "A failing demo", fail_demo)

    res2 = demos_run_demo("fail_test_demo")
    assert res2["name"] == "fail_test_demo"
    assert res2["success"] is False
    assert "Intentional Failure" in res2["error"]

    # Test non-existent demo
    res3 = demos_run_demo("nonexistent_demo_xyz")
    assert res3["name"] == "nonexistent_demo_xyz"
    assert res3["success"] is False
    assert "not found" in res3["error"]
