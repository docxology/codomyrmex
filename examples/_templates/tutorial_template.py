#!/usr/bin/env python3
"""
Tutorial: {Module Name} - Step-by-Step Guide

This tutorial walks through {module} functionality step by step,
explaining concepts and best practices along the way.

Learning Objectives:
- Understand {concept 1}
- Learn how to {action 1}
- Master {advanced feature}

Prerequisites:
- Basic Python knowledge
- Understanding of {related concept}
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.{module} import {TestedFunction}
from examples._common.config_loader import load_config
from examples._common.example_runner import ExampleRunner
from examples._common.utils import print_section, print_results, print_success, print_error

# Import logging
from codomyrmex.logging_monitoring import setup_logging, get_logger

logger = get_logger(__name__)


class TutorialStep:
    """Represents a single tutorial step."""

    def __init__(self, number: int, title: str, explanation: str, code: str,
                 expected_output: str, hints: Optional[list] = None):
        self.number = number
        self.title = title
        self.explanation = explanation
        self.code = code
        self.expected_output = expected_output
        self.hints = hints or []

    def run(self, interactive: bool = True) -> bool:
        """Execute and explain this step."""
        print(f"\n{'='*60}")
        print(f"Step {self.number}: {self.title}")
        print(f"{'='*60}")
        print(f"\n{self.explanation}\n")

        if self.hints:
            print("💡 Hints:")
            for hint in self.hints:
                print(f"   - {hint}")
            print()

        print("Code:")
        print(f"```python\n{self.code}\n```")
        print("\nExecuting...")

        try:
            # Execute code
            result = eval(self.code)
            print(f"\n✅ Result: {result}")

            if str(result) == self.expected_output:
                print_success("✓ Correct! Step completed successfully.")
            else:
                print(f"⚠️  Expected: {self.expected_output}")
                print("   This might be normal if your environment differs.")

            if interactive:
                input("\nPress Enter to continue to next step...")
            return True

        except Exception as e:
            print_error(f"❌ Error executing step: {e}")

            if self.hints:
                print("\n🔧 Troubleshooting:")
                for hint in self.hints:
                    print(f"   - {hint}")

            if interactive:
                retry = input("\nWould you like to retry this step? (y/n): ")
                if retry.lower() == 'y':
                    return self.run(interactive)
                else:
                    input("Press Enter to continue to next step...")
            return False


class {ModuleName}Tutorial:
    """Interactive tutorial for {module} functionality."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the tutorial with configuration."""
        self.config = config
        self.start_time = time.time()
        self.completed_steps = []
        self.failed_steps = []

        # Setup logging
        setup_logging()

    def create_steps(self) -> list:
        """Create the tutorial steps."""
        return [
            TutorialStep(
                number=1,
                title="Basic Setup",
                explanation="First, let's set up the basic {module} functionality. This step covers initialization and basic configuration.",
                code="""# Initialize {module}
from codomyrmex.{module} import {TestedFunction}
print("{Module} initialized successfully")""",
                expected_output="{Module} initialized successfully",
                hints=[
                    "Make sure the codomyrmex package is properly installed",
                    "Check that all dependencies are available",
                    "Verify the import path is correct"
                ]
            ),

            TutorialStep(
                number=2,
                title="Core Functionality",
                explanation="Now let's explore the core functionality of {module}. This demonstrates the primary use cases and API methods.",
                code="""# Demonstrate core functionality
result = {TestedFunction}()
print(f"Core functionality result: {result}")""",
                expected_output="Core functionality result: expected_result",
                hints=[
                    "Check the function signature and parameters",
                    "Ensure proper error handling",
                    "Verify the return value format"
                ]
            ),

            TutorialStep(
                number=3,
                title="Advanced Features",
                explanation="Let's explore advanced features and configuration options available in {module}.",
                code="""# Advanced features demonstration
advanced_result = advanced_function_call()
print(f"Advanced feature result: {advanced_result}")""",
                expected_output="Advanced feature result: advanced_expected",
                hints=[
                    "Advanced features may require additional configuration",
                    "Check parameter documentation",
                    "Some features may have dependencies"
                ]
            ),

            TutorialStep(
                number=4,
                title="Error Handling",
                explanation="Proper error handling is crucial. Let's see how {module} handles various error conditions.",
                code="""# Error handling demonstration
try:
    error_result = function_that_might_fail()
    print(f"Success: {error_result}")
except Exception as e:
    print(f"Handled error gracefully: {e}")""",
                expected_output="Handled error gracefully: expected_error",
                hints=[
                    "Always wrap potentially failing operations in try-except",
                    "Check for specific exception types when possible",
                    "Provide meaningful error messages to users"
                ]
            ),

            TutorialStep(
                number=5,
                title="Best Practices",
                explanation="Finally, let's apply best practices for using {module} in real applications.",
                code="""# Best practices demonstration
# Proper initialization
proper_setup = setup_correctly()
# Resource management
with manage_resources() as resource:
    result = use_resource_properly(resource)
print(f"Best practices result: {result}")""",
                expected_output="Best practices result: proper_result",
                hints=[
                    "Follow the principle of least surprise",
                    "Use context managers for resource management",
                    "Document your code and configuration"
                ]
            )
        ]

    def run_tutorial(self, interactive: bool = True) -> Dict[str, Any]:
        """Run the complete tutorial."""
        print_section("{Module Name} Tutorial")
        print("This interactive tutorial will guide you through {module} step by step.")
        print("Each step includes explanations, code examples, and expected results.")
        print(f"Interactive mode: {'ON' if interactive else 'OFF'}")
        print("-" * 60)

        if interactive:
            mode = input("Choose mode - (1) Step-by-step or (2) Run all: ")
            run_all = mode == '2'
        else:
            run_all = True

        steps = self.create_steps()
        total_steps = len(steps)

        for step in steps:
            step_start = time.time()

            if run_all:
                success = step.run(interactive=False)
            else:
                success = step.run(interactive=True)

            step_duration = time.time() - step_start

            if success:
                self.completed_steps.append({
                    'step': step.number,
                    'title': step.title,
                    'duration': step_duration
                })
                logger.info(f"Step {step.number} completed in {step_duration:.2f}s")
            else:
                self.failed_steps.append({
                    'step': step.number,
                    'title': step.title,
                    'duration': step_duration
                })
                logger.warning(f"Step {step.number} failed after {step_duration:.2f}s")

        # Tutorial completion summary
        tutorial_duration = time.time() - self.start_time

        results = {
            'tutorial_completed': len(self.completed_steps) == total_steps,
            'total_steps': total_steps,
            'completed_steps': len(self.completed_steps),
            'failed_steps': len(self.failed_steps),
            'completion_rate': len(self.completed_steps) / total_steps,
            'total_duration': tutorial_duration,
            'average_step_duration': tutorial_duration / total_steps,
            'step_details': self.completed_steps + self.failed_steps
        }

        print(f"\n{'='*60}")
        print("TUTORIAL COMPLETED")
        print(f"{'='*60}")
        print(f"Steps completed: {results['completed_steps']}/{results['total_steps']}")
        print(".1%")
        print(".2f")
        print(".2f")

        if results['tutorial_completed']:
            print_success("🎉 Congratulations! You completed the entire tutorial!")
        else:
            print(f"⚠️  Tutorial partially completed. {results['failed_steps']} steps need review.")

        return results


def main():
    """Main function to run the {module} tutorial."""
    # Load configuration
    config_path = Path(__file__).parent / "tutorial_template_config.yaml"
    if not config_path.exists():
        # Fallback to default config
        config = {
            "tutorial": {
                "interactive": True,
                "verbose": True,
                "save_progress": True
            },
            "output": {
                "format": "json",
                "file": "output/tutorial_template_results.json"
            },
            "logging": {
                "level": "INFO",
                "file": "logs/tutorial_template.log"
            }
        }
    else:
        config = load_config(config_path)

    # Initialize example runner
    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        # Create and run tutorial
        tutorial = {ModuleName}Tutorial(config)
        results = tutorial.run_tutorial(
            interactive=config.get('tutorial', {}).get('interactive', True)
        )

        # Validate and save results
        runner.validate_results(results)
        runner.save_results(results)
        runner.complete()

        if results['tutorial_completed']:
            print_success("{Module Name} tutorial completed successfully!")
        else:
            print(f"⚠️  {ModuleName} tutorial completed with {results['failed_steps']} failed steps.")

        print(f"Total duration: {results['total_duration']:.2f} seconds")
        print(f"Completion rate: {results['completion_rate']:.1%}")

    except Exception as e:
        runner.error("{Module Name} tutorial failed", e)
        print_error(f"{Module Name} tutorial failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
