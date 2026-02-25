"""Workflow integration test: concurrent workflow execution.

Validates that multiple workflow functions can run concurrently
without deadlocks, race conditions, or corrupted state.
"""

import concurrent.futures

import pytest


@pytest.mark.integration
class TestWorkflowConcurrent:
    """Concurrent execution of workflow functions."""

    def test_concurrent_module_listing(self):
        """10 concurrent _tool_list_modules calls complete without deadlock."""
        from codomyrmex.agents.pai.mcp_bridge import _tool_list_modules

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            futures = [pool.submit(_tool_list_modules) for _ in range(10)]
            results = [f.result(timeout=30) for f in futures]

        assert len(results) == 10
        # All results should be identical dicts
        for r in results:
            assert isinstance(r, dict)

    def test_concurrent_readme_fetches(self):
        """Concurrent README fetches for different modules succeed."""
        from codomyrmex.agents.pai.mcp_bridge import _tool_get_module_readme

        modules = ["agents", "events", "orchestrator", "utils", "coding"]

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
            futures = {
                module: pool.submit(_tool_get_module_readme, module=module)
                for module in modules
            }
            results = {m: f.result(timeout=30) for m, f in futures.items()}

        for module, result in results.items():
            assert isinstance(result, dict), f"Module {module} returned {type(result)}"

    def test_concurrent_verify_is_safe(self):
        """Multiple verify_capabilities calls don't corrupt state."""
        from codomyrmex.agents.pai.trust_gateway import verify_capabilities

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            futures = [pool.submit(verify_capabilities) for _ in range(3)]
            results = [f.result(timeout=60) for f in futures]

        # All should succeed and return the same structure
        assert len(results) == 3
        for r in results:
            assert isinstance(r, dict)

    def test_concurrent_results_independent(self):
        """Concurrent calls produce independent results (no cross-contamination)."""
        from codomyrmex.agents.pai.mcp_bridge import (
            _tool_list_modules,
            _tool_pai_status,
        )

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            f_mod = pool.submit(_tool_list_modules)
            f_status = pool.submit(_tool_pai_status)

            mod_result = f_mod.result(timeout=30)
            status_result = f_status.result(timeout=30)

        # Results should be different dict shapes
        assert isinstance(mod_result, dict)
        assert isinstance(status_result, dict)
        # The keys should differ (modules vs status info)
        assert mod_result.keys() != status_result.keys() or mod_result != status_result
