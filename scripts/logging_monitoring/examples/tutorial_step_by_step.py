#!/usr/bin/env python3
"""
Tutorial: Logging Monitoring - Step-by-Step Guide

This tutorial walks through Codomyrmex logging and monitoring functionality step by step,
explaining concepts and best practices along the way.

Learning Objectives:
- Understand centralized logging architecture
- Learn how to create and configure loggers
- Master different log levels and their use cases
- Implement structured logging with contextual data
- Handle logging errors and edge cases
- Apply performance logging techniques

Prerequisites:
- Basic Python knowledge
- Understanding of logging concepts
- Familiarity with JSON data structures
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Import common utilities
sys.path.insert(0, str(project_root / "examples" / "_common"))
from config_loader import load_config
from example_runner import ExampleRunner
from utils import print_section, print_results, print_success, print_error

from codomyrmex.logging_monitoring import setup_logging, get_logger

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
            # Execute code (using exec since these are statements, not expressions)
            exec(self.code)
            print(f"\n✅ Code executed successfully")

            # For tutorial steps, we focus on successful execution rather than exact output matching
            print_success("✓ Step completed successfully!")

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


class LoggingMonitoringTutorial:
    """Interactive tutorial for logging and monitoring functionality."""

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
                title="Basic Logging Setup",
                explanation="First, let's set up the basic logging system. This step covers importing the logging module and initializing the logging system with default configuration.",
                code="""# Import and setup basic logging
from codomyrmex.logging_monitoring import setup_logging, get_logger

# Setup logging with default configuration
setup_logging()

# Verify setup by creating a test logger
test_logger = get_logger('tutorial.test')
test_logger.info("Logging system initialized successfully")

print("Basic logging setup completed")""",
                expected_output="Basic logging setup completed",
                hints=[
                    "Make sure the codomyrmex.logging_monitoring module is available",
                    "Check that all dependencies are installed",
                    "The setup_logging() function configures the root logger"
                ]
            ),

            TutorialStep(
                number=2,
                title="Creating Loggers",
                explanation="Now let's create loggers for different parts of your application. Each logger can have its own configuration and log to different destinations.",
                code="""# Create loggers for different application components
logger_main = get_logger('myapp.main')
logger_database = get_logger('myapp.database')
logger_api = get_logger('myapp.api')

# Test each logger
logger_main.info("Main application started")
logger_database.info("Database connection established")
logger_api.info("API server listening on port 8080")

print(f"Created {3} hierarchical loggers")""",
                expected_output="Created 3 hierarchical loggers",
                hints=[
                    "Logger names use dot notation for hierarchy",
                    "Each logger inherits configuration from its parent",
                    "Use descriptive names that match your application structure"
                ]
            ),

            TutorialStep(
                number=3,
                title="Log Levels and Their Use Cases",
                explanation="Understanding log levels is crucial for effective logging. Each level serves a different purpose in monitoring and debugging your application.",
                code="""# Demonstrate different log levels
logger = get_logger('tutorial.levels')

# DEBUG: Detailed diagnostic information
logger.debug("Processing user request with ID: 12345")

# INFO: General operational information
logger.info("User authentication successful")

# WARNING: Something unexpected but not critical
logger.warning("High memory usage detected: 85%")

# ERROR: Something went wrong that needs attention
logger.error("Failed to connect to external service")

# CRITICAL: System-threatening errors
logger.critical("System out of memory, initiating shutdown")

print("Demonstrated all 5 standard log levels")""",
                expected_output="Demonstrated all 5 standard log levels",
                hints=[
                    "DEBUG: For developers during development",
                    "INFO: Normal operational events",
                    "WARNING: Potential issues that don't stop operation",
                    "ERROR: Failures that need attention",
                    "CRITICAL: System-threatening problems"
                ]
            ),

            TutorialStep(
                number=4,
                title="Structured Logging with Context",
                explanation="Structured logging adds contextual information to your log messages, making them easier to search, filter, and analyze.",
                code="""# Structured logging with contextual data
logger = get_logger('tutorial.structured')

# User action logging
logger.info("User login successful", extra={
    'user_id': 'user_12345',
    'ip_address': '192.168.1.100',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'session_id': 'sess_abc123',
    'login_method': 'email'
})

# API request logging
logger.info("API request processed", extra={
    'method': 'POST',
    'endpoint': '/api/users',
    'status_code': 201,
    'response_time_ms': 245.67,
    'request_size_bytes': 1024,
    'user_id': 'user_12345'
})

# Performance logging
logger.info("Database query completed", extra={
    'operation': 'SELECT',
    'table': 'users',
    'records_returned': 150,
    'query_time_ms': 45.2,
    'index_used': True
})

print("Logged 3 structured events with contextual data")""",
                expected_output="Logged 3 structured events with contextual data",
                hints=[
                    "Use the 'extra' parameter to add structured data",
                    "Include relevant IDs, timestamps, and metrics",
                    "Structure data for easy querying and filtering",
                    "Avoid putting sensitive information in logs"
                ]
            ),

            TutorialStep(
                number=5,
                title="Error Handling and Exception Logging",
                explanation="Proper error handling and exception logging is essential for debugging and monitoring application health.",
                code="""# Error handling and exception logging
logger = get_logger('tutorial.errors')

def risky_operation():
    \"\"\"Simulate an operation that might fail.\"\"\"
    if time.time() % 2 > 1:  # Random failure
        raise ValueError("Simulated operation failure")
    return "Operation successful"

try:
    result = risky_operation()
    logger.info("Risky operation completed", extra={'result': result})
except ValueError as e:
    logger.error("Risky operation failed", extra={
        'error_type': 'ValueError',
        'error_message': str(e),
        'operation': 'risky_operation',
        'timestamp': time.time()
    })
except Exception as e:
    logger.critical("Unexpected error in risky operation", exc_info=True, extra={
        'error_type': type(e).__name__,
        'unexpected_error': True
    })

print("Demonstrated error handling and exception logging")""",
                expected_output="Demonstrated error handling and exception logging",
                hints=[
                    "Always catch specific exceptions first",
                    "Use exc_info=True for full stack traces",
                    "Include error context in structured data",
                    "Log at appropriate levels based on severity"
                ]
            ),

            TutorialStep(
                number=6,
                title="Performance Logging and Monitoring",
                explanation="Performance logging helps you monitor application performance and identify bottlenecks.",
                code="""# Performance logging and monitoring
logger = get_logger('tutorial.performance')

# Function to monitor
def process_data_batch(batch_size):
    \"\"\"Simulate data processing with timing.\"\"\"
    start_time = time.time()
    # Simulate processing
    time.sleep(0.01)  # 10ms processing time
    processed_records = batch_size
    end_time = time.time()

    return processed_records, end_time - start_time

# Monitor performance
batch_sizes = [100, 500, 1000]
for batch_size in batch_sizes:
    records, duration = process_data_batch(batch_size)

    logger.info("Batch processing completed", extra={
        'operation': 'process_data_batch',
        'batch_size': batch_size,
        'records_processed': records,
        'duration_seconds': duration,
        'throughput_per_second': records / duration if duration > 0 else 0,
        'memory_usage_mb': 45.2,  # Simulated
        'cpu_usage_percent': 67.8  # Simulated
    })

print("Demonstrated performance logging with metrics")""",
                expected_output="Demonstrated performance logging with metrics",
                hints=[
                    "Measure operation start and end times",
                    "Calculate throughput and efficiency metrics",
                    "Include system resource usage when available",
                    "Use consistent metric names across your application"
                ]
            )
        ]

    def run_tutorial(self, interactive: bool = True) -> Dict[str, Any]:
        """Run the complete tutorial."""
        print_section("Logging Monitoring Tutorial")
        print("This interactive tutorial will guide you through logging and monitoring step by step.")
        print("Each step includes explanations, code examples, and expected results.")
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
    """Main function to run the logging monitoring tutorial."""
    # Load configuration
    config_path = Path(__file__).parent / "tutorial_config.yaml"
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
                "file": "output/tutorial_logging_results.json"
            },
            "logging": {
                "level": "INFO",
                "file": "logs/tutorial_logging.log"
            }
        }
    else:
        config = load_config(config_path)

    # Initialize example runner
    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        # Create and run tutorial
        tutorial = LoggingMonitoringTutorial(config)
        results = tutorial.run_tutorial(
            interactive=config.get('tutorial', {}).get('interactive', True)
        )

        # Validate and save results
        runner.validate_results(results)
        runner.save_results(results)
        runner.complete()

        if results['tutorial_completed']:
            print_success("Logging Monitoring tutorial completed successfully!")
        else:
            print(f"⚠️  Logging Monitoring tutorial completed with {results['failed_steps']} failed steps.")

        print(f"Total duration: {results['total_duration']:.2f} seconds")
        print(f"Completion rate: {results['completion_rate']:.1%}")

    except Exception as e:
        runner.error("Logging Monitoring tutorial failed", e)
        print_error(f"Logging Monitoring tutorial failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
