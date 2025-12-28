#!/usr/bin/env python3
"""
Example: {Module Name} - {Brief Description}

Demonstrates:
- {Key feature 1}
- {Key feature 2}
- {Integration point}

Tested Methods:
- {method_name}() - Verified in test_{module}.py::{TestClass}::{test_method}
- {another_method}() - Verified in test_{module}.py::{TestClass}::{test_another}
"""

import sys
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Import the module to demonstrate
from codomyrmex.{module} import (
    {TestedFunction},
    {AnotherFunction}
)

# Import common utilities
from examples._common.config_loader import load_config
from examples._common.example_runner import ExampleRunner
from examples._common.utils import print_section, print_results, print_success, print_error

# Import logging
from codomyrmex.logging_monitoring import setup_logging, get_logger

logger = get_logger(__name__)


class {ModuleName}Example:
    """Example class demonstrating {module} functionality."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the example with configuration."""
        self.config = config
        self.start_time = time.time()
        self.results = {
            "module": "{module}",
            "operations_completed": 0,
            "errors_encountered": 0,
            "execution_time": 0
        }

    def setup(self) -> bool:
        """Setup the example environment."""
        try:
            logger.info(f"Setting up {self.config.get('module', {}).get('name', '{module}')} example")

            # Add any setup logic here
            # For example: create directories, initialize connections, etc.

            logger.info("Setup completed successfully")
            return True

        except Exception as e:
            logger.error(f"Setup failed: {e}")
            return False

    def demonstrate_core_functionality(self) -> Dict[str, Any]:
        """Demonstrate the core functionality of the module."""
        print_section("Core Functionality Demonstration")

        results = {}

        try:
            # Example 1: Basic usage
            print("1. Basic functionality...")
            basic_result = self._run_basic_example()
            results["basic_example"] = basic_result
            print_success("Basic example completed")

            # Example 2: Advanced features
            print("2. Advanced features...")
            advanced_result = self._run_advanced_example()
            results["advanced_example"] = advanced_result
            print_success("Advanced example completed")

            # Example 3: Integration scenario
            print("3. Integration scenario...")
            integration_result = self._run_integration_example()
            results["integration_example"] = integration_result
            print_success("Integration example completed")

        except Exception as e:
            logger.error(f"Core functionality demonstration failed: {e}")
            results["error"] = str(e)
            print_error(f"Core functionality failed: {e}")

        return results

    def _run_basic_example(self) -> Dict[str, Any]:
        """Run basic functionality example."""
        # Replace with actual basic example implementation
        return {
            "operation": "basic_functionality",
            "status": "success",
            "data": "example_result"
        }

    def _run_advanced_example(self) -> Dict[str, Any]:
        """Run advanced functionality example."""
        # Replace with actual advanced example implementation
        return {
            "operation": "advanced_functionality",
            "status": "success",
            "data": "advanced_result"
        }

    def _run_integration_example(self) -> Dict[str, Any]:
        """Run integration scenario example."""
        # Replace with actual integration example implementation
        return {
            "operation": "integration_scenario",
            "status": "success",
            "data": "integration_result"
        }

    def demonstrate_error_handling(self) -> Dict[str, Any]:
        """Demonstrate error handling capabilities."""
        print_section("Error Handling Demonstration")

        error_results = {
            "invalid_input_handled": False,
            "network_error_handled": False,
            "permission_error_handled": False
        }

        try:
            # Test invalid input handling
            print("Testing invalid input handling...")
            self._test_invalid_input()
            error_results["invalid_input_handled"] = True
            print_success("Invalid input handled correctly")

        except Exception as e:
            logger.warning(f"Invalid input test failed: {e}")

        try:
            # Test network error handling (if applicable)
            print("Testing error recovery...")
            self._test_error_recovery()
            error_results["network_error_handled"] = True
            print_success("Error recovery handled correctly")

        except Exception as e:
            logger.warning(f"Error recovery test failed: {e}")

        return error_results

    def _test_invalid_input(self):
        """Test handling of invalid input."""
        # Implement invalid input test
        pass

    def _test_error_recovery(self):
        """Test error recovery mechanisms."""
        # Implement error recovery test
        pass

    def generate_performance_metrics(self) -> Dict[str, Any]:
        """Generate performance metrics for the example."""
        execution_time = time.time() - self.start_time

        metrics = {
            "total_execution_time": execution_time,
            "operations_per_second": self.results.get("operations_completed", 0) / max(execution_time, 0.001),
            "error_rate": self.results.get("errors_encountered", 0) / max(self.results.get("operations_completed", 1), 1),
            "memory_usage": "N/A",  # Could be enhanced with psutil
            "cpu_usage": "N/A"      # Could be enhanced with psutil
        }

        return metrics

    def cleanup(self) -> bool:
        """Clean up resources used by the example."""
        try:
            logger.info("Cleaning up example resources")

            # Add cleanup logic here
            # For example: close connections, remove temp files, etc.

            logger.info("Cleanup completed successfully")
            return True

        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return False

    def run_complete_example(self) -> Dict[str, Any]:
        """Run the complete example workflow."""
        print_section("{Module Name} Complete Example")

        # Setup
        if not self.setup():
            return {"status": "failed", "stage": "setup"}

        # Core functionality
        core_results = self.demonstrate_core_functionality()

        # Error handling
        error_results = self.demonstrate_error_handling()

        # Performance metrics
        performance_metrics = self.generate_performance_metrics()

        # Cleanup
        cleanup_success = self.cleanup()

        # Compile final results
        final_results = {
            "status": "completed" if cleanup_success else "completed_with_cleanup_issues",
            "module": "{module}",
            "core_functionality": core_results,
            "error_handling": error_results,
            "performance": performance_metrics,
            "cleanup_success": cleanup_success,
            "execution_summary": {
                "total_operations": self.results.get("operations_completed", 0),
                "errors_encountered": self.results.get("errors_encountered", 0),
                "success_rate": (self.results.get("operations_completed", 0) -
                               self.results.get("errors_encountered", 0)) /
                              max(self.results.get("operations_completed", 1), 1)
            }
        }

        return final_results


def main():
    """Main function to run the {module} example."""
    # Load configuration
    config_path = Path(__file__).parent / "basic_template_config.yaml"
    if not config_path.exists():
        # Fallback to default config
        config = {
            "output": {
                "format": "json",
                "file": "output/basic_template_results.json"
            },
            "logging": {
                "level": "INFO",
                "file": "logs/basic_template.log"
            },
            "module": {
                "name": "basic_template",
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
        # Create and run example
        example = {ModuleName}Example(config)
        results = example.run_complete_example()

        # Validate and save results
        runner.validate_results(results)
        runner.save_results(results)
        runner.complete()

        print_success("{Module Name} example completed successfully!")
        print(f"Executed {results.get('execution_summary', {}).get('total_operations', 0)} operations")
        print(f"Success rate: {results.get('execution_summary', {}).get('success_rate', 0):.1%}")

    except Exception as e:
        runner.error("{Module Name} example failed", e)
        print_error(f"{Module Name} example failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
