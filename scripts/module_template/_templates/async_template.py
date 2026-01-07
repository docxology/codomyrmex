#!/usr/bin/env python3
"""
Example: {Module Name} Async - {Brief Description} with Async/Await Patterns

Demonstrates:
- Asynchronous operations using async/await
- Concurrent task execution
- Async error handling and recovery
- Performance benefits of async patterns
- Integration with async Codomyrmex modules

Tested Methods:
- {async_method_name}() - Verified in test_{module}.py::{TestClass}::{test_async_method}
- {another_async_method}() - Verified in test_{module}.py::{TestClass}::{test_another_async}
"""

import sys
import os
import asyncio
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Coroutine, Union
from concurrent.futures import ThreadPoolExecutor
from functools import partial

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Import the module to demonstrate (async version)
from codomyrmex.{module} import (
    {AsyncTestedFunction},
    {AnotherAsyncFunction}
)

# Import common utilities
from examples._common.config_loader import load_config
from examples._common.example_runner import ExampleRunner
from examples._common.utils import print_section, print_results, print_success, print_error

# Import logging
from codomyrmex.logging_monitoring import setup_logging, get_logger

logger = get_logger(__name__)


class {ModuleName}AsyncExample:
    """Async example class demonstrating {module} asynchronous functionality."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the async example with configuration."""
        self.config = config
        self.start_time = time.time()
        self.executor = ThreadPoolExecutor(max_workers=config.get('async', {}).get('max_workers', 4))
        self.semaphore = asyncio.Semaphore(config.get('async', {}).get('max_concurrent', 10))

        self.results = {
            "module": "{module}",
            "async_operations_completed": 0,
            "concurrent_tasks_executed": 0,
            "errors_encountered": 0,
            "execution_time": 0,
            "performance_metrics": {}
        }

    async def setup_async(self) -> bool:
        """Async setup of the example environment."""
        try:
            logger.info(f"Setting up async {self.config.get('module', {}).get('name', '{module}')} example")

            # Add any async setup logic here
            # For example: initialize async connections, setup async pools, etc.
            await asyncio.sleep(0.1)  # Simulate async setup

            logger.info("Async setup completed successfully")
            return True

        except Exception as e:
            logger.error(f"Async setup failed: {e}")
            return False

    async def demonstrate_async_core_functionality(self) -> Dict[str, Any]:
        """Demonstrate the core async functionality of the module."""
        print_section("Async Core Functionality Demonstration")

        results = {}

        try:
            # Example 1: Basic async operations
            print("1. Basic async functionality...")
            basic_result = await self._run_basic_async_example()
            results["basic_async_example"] = basic_result
            print_success("Basic async example completed")

            # Example 2: Concurrent async operations
            print("2. Concurrent async operations...")
            concurrent_result = await self._run_concurrent_async_example()
            results["concurrent_async_example"] = concurrent_result
            print_success("Concurrent async example completed")

            # Example 3: Async integration scenario
            print("3. Async integration scenario...")
            integration_result = await self._run_async_integration_example()
            results["async_integration_example"] = integration_result
            print_success("Async integration example completed")

        except Exception as e:
            logger.error(f"Async core functionality demonstration failed: {e}")
            results["error"] = str(e)
            print_error(f"Async core functionality failed: {e}")

        return results

    async def _run_basic_async_example(self) -> Dict[str, Any]:
        """Run basic async functionality example."""
        async with self.semaphore:
            # Simulate async operation
            await asyncio.sleep(0.1)

            # Replace with actual async module functionality
            # result = await {module}.async_basic_function(self.config)

            return {
                "operation": "basic_async_functionality",
                "status": "success",
                "async_execution": True,
                "data": "async_example_result"
            }

    async def _run_concurrent_async_example(self) -> Dict[str, Any]:
        """Run concurrent async operations example."""
        print("   Executing multiple async operations concurrently...")

        # Create multiple concurrent tasks
        tasks = []
        for i in range(self.config.get('async', {}).get('concurrent_tasks', 5)):
            task = self._single_async_operation(i)
            tasks.append(task)

        # Execute all tasks concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        execution_time = time.time() - start_time

        # Process results
        successful = sum(1 for r in results if not isinstance(r, Exception))
        failed = sum(1 for r in results if isinstance(r, Exception))

        return {
            "operation": "concurrent_async_operations",
            "status": "completed",
            "total_tasks": len(tasks),
            "successful_tasks": successful,
            "failed_tasks": failed,
            "execution_time": execution_time,
            "tasks_per_second": len(tasks) / execution_time if execution_time > 0 else 0
        }

    async def _single_async_operation(self, task_id: int) -> Dict[str, Any]:
        """Execute a single async operation."""
        async with self.semaphore:
            # Simulate variable execution time
            execution_time = 0.1 + (task_id * 0.05)
            await asyncio.sleep(execution_time)

            # Replace with actual async operation
            # result = await {module}.async_operation(task_id, self.config)

            return {
                "task_id": task_id,
                "status": "success",
                "execution_time": execution_time,
                "data": f"task_{task_id}_result"
            }

    async def _run_async_integration_example(self) -> Dict[str, Any]:
        """Run async integration scenario example."""
        print("   Running async integration workflow...")

        # Phase 1: Initialize async resources
        await asyncio.sleep(0.05)

        # Phase 2: Execute async operations with dependencies
        phase2_results = await self._execute_async_workflow_phase()

        # Phase 3: Cleanup and aggregation
        await asyncio.sleep(0.05)

        return {
            "operation": "async_integration_scenario",
            "status": "success",
            "phases_completed": 3,
            "phase2_results": phase2_results,
            "integration_complete": True
        }

    async def _execute_async_workflow_phase(self) -> List[Dict[str, Any]]:
        """Execute a phase of the async workflow."""
        # Simulate dependent async operations
        results = []

        # First set of independent operations
        first_phase_tasks = [
            self._async_workflow_step(1, "data_ingestion"),
            self._async_workflow_step(2, "data_validation"),
            self._async_workflow_step(3, "data_transformation")
        ]

        first_results = await asyncio.gather(*first_phase_tasks, return_exceptions=True)
        results.extend([r for r in first_results if not isinstance(r, Exception)])

        # Second set dependent on first
        await asyncio.sleep(0.1)  # Simulate processing time

        second_phase_tasks = [
            self._async_workflow_step(4, "data_analysis", depends_on=first_results),
            self._async_workflow_step(5, "data_persistence", depends_on=first_results)
        ]

        second_results = await asyncio.gather(*second_phase_tasks, return_exceptions=True)
        results.extend([r for r in second_results if not isinstance(r, Exception)])

        return results

    async def _async_workflow_step(self, step_id: int, step_name: str, depends_on: Optional[List] = None) -> Dict[str, Any]:
        """Execute a single workflow step asynchronously."""
        async with self.semaphore:
            execution_time = 0.05 + (step_id * 0.02)
            await asyncio.sleep(execution_time)

            return {
                "step_id": step_id,
                "step_name": step_name,
                "status": "success",
                "execution_time": execution_time,
                "dependencies_satisfied": depends_on is not None
            }

    async def demonstrate_async_error_handling(self) -> Dict[str, Any]:
        """Demonstrate async error handling and recovery."""
        print_section("Async Error Handling Demonstration")

        error_results = {
            "timeout_handled": False,
            "exception_recovery_handled": False,
            "circuit_breaker_handled": False,
            "concurrent_error_handled": False
        }

        try:
            # Test timeout handling
            print("Testing async timeout handling...")
            await self._test_async_timeout()
            error_results["timeout_handled"] = True
            print_success("Async timeout handled correctly")

        except Exception as e:
            logger.warning(f"Async timeout test failed: {e}")

        try:
            # Test exception recovery
            print("Testing async exception recovery...")
            await self._test_async_exception_recovery()
            error_results["exception_recovery_handled"] = True
            print_success("Async exception recovery handled correctly")

        except Exception as e:
            logger.warning(f"Async exception recovery test failed: {e}")

        try:
            # Test concurrent error handling
            print("Testing concurrent async error handling...")
            await self._test_concurrent_async_errors()
            error_results["concurrent_error_handled"] = True
            print_success("Concurrent async errors handled correctly")

        except Exception as e:
            logger.warning(f"Concurrent async error test failed: {e}")

        return error_results

    async def _test_async_timeout(self):
        """Test async timeout handling."""
        try:
            await asyncio.wait_for(self._long_running_async_operation(), timeout=0.1)
        except asyncio.TimeoutError:
            logger.info("Async timeout handled correctly")
            return True
        raise Exception("Timeout should have occurred")

    async def _long_running_async_operation(self):
        """Simulate a long-running async operation."""
        await asyncio.sleep(1.0)  # Longer than timeout

    async def _test_async_exception_recovery(self):
        """Test async exception recovery."""
        try:
            await self._failing_async_operation()
        except ValueError as e:
            if "simulated failure" in str(e):
                logger.info("Async exception recovery handled correctly")
                return True
        raise Exception("Expected exception was not caught properly")

    async def _failing_async_operation(self):
        """Simulate a failing async operation."""
        await asyncio.sleep(0.05)
        raise ValueError("Simulated async failure")

    async def _test_concurrent_async_errors(self):
        """Test handling errors in concurrent async operations."""
        tasks = []
        for i in range(3):
            if i == 1:  # Make one task fail
                task = self._failing_async_operation()
            else:
                task = self._single_async_operation(i)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Check that we handled both successes and failures
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        failure_count = sum(1 for r in results if isinstance(r, Exception))

        if success_count >= 2 and failure_count >= 1:
            logger.info("Concurrent async errors handled correctly")
            return True

        raise Exception(f"Expected mixed results, got {success_count} successes, {failure_count} failures")

    async def generate_async_performance_metrics(self) -> Dict[str, Any]:
        """Generate performance metrics for async operations."""
        execution_time = time.time() - self.start_time

        metrics = {
            "total_execution_time": execution_time,
            "async_operations_per_second": self.results.get("async_operations_completed", 0) / max(execution_time, 0.001),
            "concurrent_tasks_per_second": self.results.get("concurrent_tasks_executed", 0) / max(execution_time, 0.001),
            "error_rate": self.results.get("errors_encountered", 0) / max(self.results.get("async_operations_completed", 1), 1),
            "memory_usage": "N/A",  # Could be enhanced with psutil
            "cpu_usage": "N/A",     # Could be enhanced with psutil
            "async_efficiency": "N/A"  # Could measure async vs sync performance
        }

        return metrics

    async def cleanup_async(self) -> bool:
        """Async cleanup of resources."""
        try:
            logger.info("Cleaning up async example resources")

            # Shutdown executor
            self.executor.shutdown(wait=True)

            # Add other async cleanup logic here
            await asyncio.sleep(0.05)  # Simulate async cleanup

            logger.info("Async cleanup completed successfully")
            return True

        except Exception as e:
            logger.error(f"Async cleanup failed: {e}")
            return False

    async def run_complete_async_example(self) -> Dict[str, Any]:
        """Run the complete async example workflow."""
        print_section("{Module Name} Complete Async Example")

        # Setup
        if not await self.setup_async():
            return {"status": "failed", "stage": "setup"}

        # Core async functionality
        core_results = await self.demonstrate_async_core_functionality()

        # Async error handling
        error_results = await self.demonstrate_async_error_handling()

        # Performance metrics
        performance_metrics = await self.generate_async_performance_metrics()

        # Cleanup
        cleanup_success = await self.cleanup_async()

        # Compile final results
        final_results = {
            "status": "completed" if cleanup_success else "completed_with_cleanup_issues",
            "module": "{module}",
            "execution_mode": "async",
            "core_functionality": core_results,
            "error_handling": error_results,
            "performance": performance_metrics,
            "cleanup_success": cleanup_success,
            "execution_summary": {
                "total_async_operations": self.results.get("async_operations_completed", 0),
                "concurrent_tasks_executed": self.results.get("concurrent_tasks_executed", 0),
                "errors_encountered": self.results.get("errors_encountered", 0),
                "success_rate": (self.results.get("async_operations_completed", 0) -
                               self.results.get("errors_encountered", 0)) /
                              max(self.results.get("async_operations_completed", 1), 1),
                "async_efficiency_gain": "calculated_vs_sync"  # Placeholder
            }
        }

        return final_results


async def main_async():
    """Async main function to run the {module} example."""
    # Load configuration
    config_path = Path(__file__).parent / "async_template_config.yaml"
    if not config_path.exists():
        # Fallback to default async config
        config = {
            "output": {
                "format": "json",
                "file": "output/async_template_results.json"
            },
            "logging": {
                "level": "INFO",
                "file": "logs/async_template.log"
            },
            "async": {
                "max_workers": 4,
                "max_concurrent": 10,
                "concurrent_tasks": 5,
                "timeout": 30
            },
            "module": {
                "name": "async_template",
                "debug": True,
                "max_operations": 10
            }
        }
    else:
        config = load_config(config_path)

    # Initialize example runner
    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        # Create and run async example
        example = {ModuleName}AsyncExample(config)
        results = await example.run_complete_async_example()

        # Validate and save results
        runner.validate_results(results)
        runner.save_results(results)
        runner.complete()

        print_success("{Module Name} async example completed successfully!")
        print(f"Executed {results.get('execution_summary', {}).get('total_async_operations', 0)} async operations")
        print(f"Concurrent tasks: {results.get('execution_summary', {}).get('concurrent_tasks_executed', 0)}")
        print(f"Success rate: {results.get('execution_summary', {}).get('success_rate', 0):.1%}")

    except Exception as e:
        runner.error("{Module Name} async example failed", e)
        print_error(f"{Module Name} async example failed: {e}")
        sys.exit(1)


def main():
    """Main entry point for the async example."""
    # Run the async main function
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
