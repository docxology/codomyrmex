# Codomyrmex Examples Tutorials

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

This document provides step-by-step tutorials for learning Codomyrmex through practical examples. Each tutorial builds on the previous one, taking you from basic concepts to advanced integration patterns.

## Tutorial 1: Your First Example - Logging and Configuration

### Goal
Learn the basics of Codomyrmex examples: configuration loading, logging setup, and basic module usage.

### Prerequisites
- Python 3.8+
- Basic command line knowledge
- Text editor

### Step 1: Explore the Example Structure

```bash
# Navigate to the examples directory
cd examples

# See the available examples
ls -la

# Look at the common utilities
ls -la _common/

# Examine the logging_monitoring example
ls -la logging_monitoring/
```

### Step 2: Understand the Basic Template

Open `scripts/logging_monitoring/example_basic.py`:

```python
#!/usr/bin/env python3
"""
Example: Logging Monitoring - Centralized Logging System

Demonstrates:
- Logger configuration and setup
- Different log levels and formats
- Structured logging with context
- Log aggregation and monitoring

Tested Methods:
- setup_logging() - Verified in test_logging_monitoring.py::TestLoggingMonitoring::test_setup_logging
- get_logger(name) - Verified in test_logging_monitoring.py::TestLoggingMonitoring::test_get_logger
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.logging_monitoring import setup_logging, get_logger
from examples._common.config_loader import load_config
from examples._common.example_runner import ExampleRunner

def main():
    config = load_config(Path(__file__).parent / "config.yaml")
    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        # Implementation here
        results = {"status": "success"}
        runner.validate_results(results)
        runner.save_results(results)
        runner.complete()
    except Exception as e:
        runner.error("Example failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Step 3: Examine Configuration Files

Open `scripts/logging_monitoring/config.yaml`:

```yaml
output:
  format: json
  file: output/logging_monitoring_results.json

logging:
  level: INFO
  file: logs/logging_monitoring.log
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

module:
  log_level: DEBUG
  enable_structured_logging: true
  log_format: json
```

### Step 4: Run Your First Example

```bash
# Navigate to the logging example
cd scripts/logging_monitoring

# Run the example
python example_basic.py

# Check the output
ls -la output/
cat output/logging_monitoring_results.json

# Check the logs
ls -la logs/
cat logs/logging_monitoring.log
```

### Step 5: Experiment with Configuration

Try changing the log level in `config.yaml`:

```yaml
logging:
  level: DEBUG  # Change from INFO to DEBUG
```

Run the example again and notice the difference in log output.

### What You Learned
- How examples are structured
- Configuration file usage
- Basic logging setup
- Output and log file generation
- How to modify and test configurations

## Tutorial 2: Configuration Management - Environment Variables and Validation

### Goal
Master configuration management with environment variables, validation, and inheritance.

### Prerequisites
- Completed Tutorial 1
- Understanding of YAML/JSON
- Environment variable basics

### Step 1: Explore the Config Management Example

```bash
# Navigate to the config management example
cd scripts/config_management

# Examine the files
ls -la
```

### Step 2: Study Configuration Loading

Open `scripts/config_management/example_basic.py` and examine the configuration loading:

```python
from codomyrmex.config_management.config_loader import Configuration
from codomyrmex.config_management.config_validator import ConfigSchema
from codomyrmex.config_management.config_migrator import ConfigMigrator

def main():
    config = load_config(Path(__file__).parent / "config.yaml")
    runner = ExampleRunner(__file__, config)

    # Load configuration with validation
    try:
        results = {
            'configurations_loaded': 0,
            'validations_performed': 0,
            'migrations_applied': 0,
        }

        # Load configuration from multiple sources
        config_sources = config.get('config_management', {}).get('config_sources', [])
        for source in config_sources:
            # Load and validate configuration
            pass  # Implementation details

    except Exception as e:
        runner.error("Config management example failed", e)
        sys.exit(1)
```

### Step 3: Environment Variable Substitution

Create a test environment variable:

```bash
# Set an environment variable
export TEST_API_KEY="your_test_key_here"
export TEST_DEBUG="true"
```

Now examine how the config uses environment variables. Open `config.yaml`:

```yaml
config_management:
  config_sources:
    - "config.yaml"
  environment_override: true
  secret_injection: true

# Example environment variable usage
api:
  key: ${TEST_API_KEY}
  debug: ${TEST_DEBUG:false}
  timeout: ${API_TIMEOUT:30}

database:
  host: ${DB_HOST:localhost}
  port: ${DB_PORT:5432}
  name: ${DB_NAME:test_db}
```

### Step 4: Configuration Validation

Run the config management example:

```bash
# Run the example
python example_basic.py

# Check what happens with missing environment variables
unset TEST_API_KEY
python example_basic.py

# Check what happens with invalid values
export TEST_API_KEY=""
python example_basic.py
```

### Step 5: Multiple Configuration Formats

Compare the YAML and JSON configurations:

```bash
# Compare file sizes
ls -lh config.yaml config.json

# Check syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"
python -c "import json; json.load(open('config.json'))"
```

### Step 6: Configuration Overrides

Examine the `config_overrides.yaml` file:

```yaml
# Configuration overrides for testing
api:
  debug: true
  timeout: 60

logging:
  level: DEBUG
```

Learn how overrides work by modifying the example to use them.

### What You Learned
- Environment variable substitution
- Configuration validation
- Multiple config file formats
- Configuration overrides
- Error handling for config issues

## Tutorial 3: Multi-Module Workflow - Integration Patterns

### Goal
Learn how to integrate multiple Codomyrmex modules in a complete workflow.

### Prerequisites
- Completed Tutorials 1 and 2
- Understanding of at least 3 different modules

### Step 1: Choose a Workflow

Let's use the analysis workflow as our example:

```bash
# Navigate to the multi-module workflows
cd scripts/multi_module

# List available workflows
ls -la example_workflow_*.py
```

### Step 2: Examine Workflow Structure

Open `example_workflow_analysis.py`:

```python
"""
Example: Analysis Workflow - Static Analysis, Security Audit, and Data Visualization

Demonstrates:
- Integration of static analysis, security audit, and data visualization
- Event-driven communication between modules
- Comprehensive codebase analysis pipeline
- Automated report generation

Tested Methods:
- Static analysis integration - Verified in test_static_analysis.py
- Security integration - Verified in test_security.py
- Data visualization integration - Verified in test_data_visualization.py
- Event system integration - Verified in test_events.py
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, List

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Import multiple modules for integration
from codomyrmex.static_analysis import analyze_project, get_available_tools
from codomyrmex.security import scan_codebase, check_vulnerabilities
from codomyrmex.data_visualization import create_plot, save_visualization
from codomyrmex.events import EventBus, EventEmitter

# Common utilities
from examples._common.config_loader import load_config
from examples._common.example_runner import ExampleRunner
```

### Step 3: Study Integration Patterns

Examine how the workflow integrates multiple modules:

```python
def run_analysis_workflow(config):
    """Run the complete analysis workflow."""

    # Phase 1: Static Analysis
    print_section("Phase 1: Static Analysis")
    analysis_results = analyze_project(
        project_root=str(project_root),
        target_paths=config.get('analysis', {}).get('target_paths', ['src/'])
    )

    # Phase 2: Security Audit
    print_section("Phase 2: Security Audit")
    security_results = scan_codebase(
        path=str(project_root),
        scan_types=config.get('security', {}).get('scan_types', ['vulnerabilities'])
    )

    # Phase 3: Data Visualization
    print_section("Phase 3: Data Visualization")
    # Create visualizations from analysis results
    viz_results = create_analysis_visualizations(analysis_results, security_results)

    return {
        'analysis_completed': True,
        'security_completed': True,
        'visualization_completed': True,
        'total_issues_found': len(analysis_results.get('issues', [])),
        'security_alerts': len(security_results.get('alerts', [])),
        'visualizations_created': len(viz_results)
    }
```

### Step 4: Event-Driven Communication

Learn about event-driven integration:

```python
def setup_event_driven_workflow(config):
    """Setup event-driven communication between modules."""

    # Initialize event system
    event_bus = EventBus()
    emitter = EventEmitter(event_bus)

    # Subscribe to events
    @event_bus.subscribe("analysis_completed")
    def on_analysis_completed(event):
        print(f"Analysis completed: {event.data.get('issues_found', 0)} issues found")

    @event_bus.subscribe("security_scan_completed")
    def on_security_completed(event):
        print(f"Security scan completed: {event.data.get('alerts_found', 0)} alerts found")

    # Emit events during workflow
    emitter.emit("workflow_started", {"workflow": "analysis"})

    # Run analysis
    analysis_results = run_static_analysis()
    emitter.emit("analysis_completed", {
        "issues_found": len(analysis_results.get('issues', []))
    })

    # Run security scan
    security_results = run_security_scan()
    emitter.emit("security_scan_completed", {
        "alerts_found": len(security_results.get('alerts', []))
    })

    emitter.emit("workflow_completed", {"status": "success"})
```

### Step 5: Configuration for Workflows

Examine the workflow configuration:

```yaml
# config_workflow_analysis.yaml
analysis:
  target_paths:
    - "src/"
    - "scripts/"
  analysis_types:
    - "complexity"
    - "style"
    - "security"
  max_issues: 100

security:
  scan_types:
    - "vulnerabilities"
    - "secrets"
    - "compliance"
  severity_threshold: "medium"

visualization:
  chart_types:
    - "bar"
    - "pie"
    - "line"
  output_formats:
    - "png"
    - "svg"
  theme: "default"

events:
  enabled: true
  log_events: true
  event_retention_days: 7
```

### Step 6: Run and Analyze the Workflow

```bash
# Run the analysis workflow
python example_workflow_analysis.py

# Examine the comprehensive output
ls -la output/workflow_*/
cat output/workflow_*_results.json

# Check event logs if enabled
ls -la logs/
```

### Step 7: Create a Custom Workflow

Based on what you've learned, create a simple custom workflow that integrates 2-3 modules of your choice.

### What You Learned
- Multi-module integration patterns
- Event-driven communication
- Workflow configuration management
- Comprehensive result aggregation
- Error handling across modules

## Tutorial 4: Custom Example Creation - From Scratch

### Goal
Learn to create a complete Codomyrmex example from scratch.

### Prerequisites
- Completed Tutorials 1-3
- Understanding of at least one Codomyrmex module
- Familiarity with the example template

### Step 1: Choose a Module

Select a module you want to demonstrate. Let's use `pattern_matching` as an example.

### Step 2: Create the Directory Structure

```bash
# Create the example directory
mkdir -p scripts/pattern_matching

# Create the required files
touch scripts/pattern_matching/example_basic.py
touch scripts/pattern_matching/config.yaml
touch scripts/pattern_matching/config.json
touch scripts/pattern_matching/README.md
```

### Step 3: Study the Module's Tests

Find the relevant test file and examine the tested methods:

```bash
# Find the test file
find src/codomyrmex/tests/unit -name "*pattern_matching*"

# Examine the tests
head -50 src/codomyrmex/tests/unit/test_pattern_matching.py
```

### Step 4: Create the Example Script

Use the standard template to create your example:

```python
#!/usr/bin/env python3
"""
Example: Pattern Matching - Code Pattern Detection and Analysis

Demonstrates:
- AST-based pattern matching
- Code pattern extraction
- Pattern-based refactoring suggestions
- Repository exploration

Tested Methods:
- find_patterns() - Verified in test_pattern_matching.py::TestPatternMatching::test_find_patterns
- extract_dependencies() - Verified in test_pattern_matching.py::TestPatternMatching::test_extract_dependencies
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.pattern_matching import find_patterns, extract_dependencies
from examples._common.config_loader import load_config
from examples._common.example_runner import ExampleRunner

def main():
    config = load_config(Path(__file__).parent / "config.yaml")
    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        # Your implementation here
        results = {
            'patterns_found': 0,
            'dependencies_extracted': 0,
            'files_analyzed': 0
        }

        runner.validate_results(results)
        runner.save_results(results)
        runner.complete()

    except Exception as e:
        runner.error("Pattern matching example failed", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### Step 5: Create Configuration Files

Create both YAML and JSON configurations:

```yaml
# config.yaml
output:
  format: json
  file: output/pattern_matching_results.json

logging:
  level: INFO
  file: logs/pattern_matching.log

module:
  target_paths:
    - "src/codomyrmex/pattern_matching/"
    - "scripts/"
  patterns:
    - "function_calls"
    - "class_definitions"
    - "import_statements"
  max_files: 50
  analysis_depth: 3
```

### Step 6: Write Documentation

Create comprehensive README documentation:

```markdown
# Pattern Matching Example

## Overview
This example demonstrates Codomyrmex's pattern matching capabilities for analyzing codebases.

## Features Demonstrated
- AST-based pattern detection
- Code structure analysis
- Dependency extraction
- Pattern-based insights

## Configuration
### Required Settings
- `target_paths`: List of paths to analyze
- `patterns`: Types of patterns to detect

### Optional Settings
- `max_files`: Maximum number of files to process
- `analysis_depth`: Depth of AST analysis

## Usage
```bash
cd scripts/pattern_matching
python example_basic.py
```

## Output
- `pattern_matching_results.json`: Analysis results and metrics
- `logs/pattern_matching.log`: Execution logs

## Tested Methods
- `find_patterns()` - Verified in `test_pattern_matching.py::TestPatternMatching::test_find_patterns`
- `extract_dependencies()` - Verified in `test_pattern_matching.py::TestPatternMatching::test_extract_dependencies`
```

### Step 7: Test Your Example

```bash
# Run your example
python example_basic.py

# Check for errors
echo $?

# Validate output
cat output/pattern_matching_results.json

# Check logs
cat logs/pattern_matching.log
```

### Step 8: Debug and Refine

Fix any issues and improve the example based on testing.

### What You Learned
- Complete example creation process
- Module research and testing
- Configuration design
- Documentation writing
- Debugging and refinement

## Tutorial 5: Advanced Patterns - Async, Error Recovery, and Optimization

### Goal
Master advanced example patterns including async operations, error recovery, and performance optimization.

### Prerequisites
- Completed Tutorials 1-4
- Understanding of async/await (optional)
- Performance testing experience

### Step 1: Async Operations

Learn to create examples with asynchronous operations:

```python
import asyncio
from typing import List, Dict, Any

async def run_async_analysis(config):
    """Run analysis operations asynchronously."""

    async def analyze_file_async(file_path: str) -> Dict[str, Any]:
        """Analyze a single file asynchronously."""
        # Simulate async file analysis
        await asyncio.sleep(0.1)  # Simulate I/O
        return {
            'file': file_path,
            'lines': 100,
            'complexity': 5
        }

    # Run multiple analyses concurrently
    file_paths = config.get('target_files', [])
    tasks = [analyze_file_async(file_path) for file_path in file_paths]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Process results
    successful_results = []
    errors = []

    for result in results:
        if isinstance(result, Exception):
            errors.append(str(result))
        else:
            successful_results.append(result)

    return {
        'files_analyzed': len(successful_results),
        'errors': errors,
        'total_lines': sum(r['lines'] for r in successful_results)
    }

async def main_async():
    """Async main function."""
    config = load_config("config.yaml")
    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        results = await run_async_analysis(config)
        runner.validate_results(results)
        runner.save_results(results)
        runner.complete()
    except Exception as e:
        runner.error("Async example failed", e)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main_async())
```

### Step 2: Error Recovery Patterns

Implement robust error recovery:

```python
class ResilientExampleRunner:
    """Example runner with error recovery capabilities."""

    def __init__(self, config):
        self.config = config
        self.attempts = 0
        self.max_attempts = config.get('max_retries', 3)
        self.backoff_factor = config.get('backoff_factor', 2)

    def execute_with_retry(self, operation, *args, **kwargs):
        """Execute operation with exponential backoff retry."""
        last_exception = None

        for attempt in range(self.max_attempts):
            try:
                self.attempts = attempt + 1
                return operation(*args, **kwargs)
            except TemporaryError as e:
                last_exception = e
                if attempt < self.max_attempts - 1:
                    delay = self.backoff_factor ** attempt
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s: {e}")
                    time.sleep(delay)
                else:
                    logger.error(f"All {self.max_attempts} attempts failed")
                    raise last_exception
            except PermanentError as e:
                # Don't retry permanent errors
                logger.error(f"Permanent error, not retrying: {e}")
                raise

    def execute_with_fallback(self, primary_op, fallback_op, *args, **kwargs):
        """Execute with fallback operation."""
        try:
            return primary_op(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Primary operation failed, using fallback: {e}")
            return fallback_op(*args, **kwargs)

    def execute_with_circuit_breaker(self, operation, failure_threshold=3):
        """Execute with circuit breaker pattern."""
        # Implementation of circuit breaker pattern
        pass
```

### Step 3: Performance Optimization

Add performance monitoring and optimization:

```python
import time
import psutil
import tracemalloc
from functools import wraps
from typing import Callable, Any

def performance_monitor(func: Callable) -> Callable:
    """Decorator to monitor function performance."""

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        # Memory tracking
        tracemalloc.start()
        start_time = time.perf_counter()
        start_memory = psutil.Process().memory_info().rss

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.perf_counter()
            end_memory = psutil.Process().memory_info().rss

            execution_time = end_time - start_time
            memory_used = end_memory - start_memory
            peak_memory = tracemalloc.get_traced_memory()[1]

            logger.info(f"{func.__name__} performance:", extra={
                'execution_time': execution_time,
                'memory_used': memory_used,
                'peak_memory': peak_memory,
                'cpu_percent': psutil.cpu_percent()
            })

            tracemalloc.stop()

    return wrapper

@performance_monitor
def optimized_analysis_operation(data: Dict[str, Any]) -> Dict[str, Any]:
    """Optimized analysis operation with performance monitoring."""
    # Your optimized implementation
    pass

def create_performance_baseline(config):
    """Create performance baseline for the example."""
    baseline_results = []

    for test_size in config.get('performance_test_sizes', [100, 1000, 10000]):
        test_data = generate_test_data(test_size)

        start_time = time.perf_counter()
        result = optimized_analysis_operation(test_data)
        end_time = time.perf_counter()

        baseline_results.append({
            'input_size': test_size,
            'execution_time': end_time - start_time,
            'result_size': len(result)
        })

    return baseline_results
```

### Step 4: Resource Management

Implement proper resource cleanup:

```python
import atexit
import signal
from contextlib import contextmanager

class ResourceManager:
    """Manage resources with proper cleanup."""

    def __init__(self):
        self.resources = []
        self.cleanup_functions = []
        atexit.register(self.cleanup)
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)

    def add_resource(self, resource, cleanup_func=None):
        """Add a resource to be managed."""
        self.resources.append(resource)
        if cleanup_func:
            self.cleanup_functions.append(cleanup_func)

    def signal_handler(self, signum, frame):
        """Handle termination signals."""
        logger.info(f"Received signal {signum}, cleaning up...")
        self.cleanup()
        sys.exit(1)

    def cleanup(self):
        """Clean up all managed resources."""
        logger.info("Cleaning up resources...")

        for cleanup_func in reversed(self.cleanup_functions):
            try:
                cleanup_func()
            except Exception as e:
                logger.error(f"Cleanup failed: {e}")

        for resource in reversed(self.resources):
            try:
                if hasattr(resource, 'close'):
                    resource.close()
                elif hasattr(resource, 'cleanup'):
                    resource.cleanup()
                elif hasattr(resource, 'disconnect'):
                    resource.disconnect()
            except Exception as e:
                logger.error(f"Resource cleanup failed: {e}")

        self.resources.clear()
        self.cleanup_functions.clear()

@contextmanager
def managed_resources(config):
    """Context manager for resource management."""
    manager = ResourceManager()

    # Setup resources
    db_connection = create_database_connection(config)
    manager.add_resource(db_connection)

    file_handle = open(config['output_file'], 'w')
    manager.add_resource(file_handle, lambda: file_handle.close())

    try:
        yield {
            'database': db_connection,
            'output_file': file_handle,
            'manager': manager
        }
    finally:
        manager.cleanup()
```

### Step 5: Integration Testing

Create comprehensive integration tests:

```python
def run_integration_tests(config):
    """Run comprehensive integration tests."""

    test_results = {
        'unit_tests': [],
        'integration_tests': [],
        'performance_tests': [],
        'error_handling_tests': []
    }

    # Unit test each component
    test_results['unit_tests'] = run_unit_tests()

    # Integration tests
    test_results['integration_tests'] = run_integration_scenarios(config)

    # Performance tests
    test_results['performance_tests'] = run_performance_tests(config)

    # Error handling tests
    test_results['error_handling_tests'] = run_error_handling_tests(config)

    return test_results

def run_integration_scenarios(config):
    """Run end-to-end integration scenarios."""

    scenarios = [
        {
            'name': 'basic_workflow',
            'steps': ['load_config', 'initialize_modules', 'process_data', 'generate_output']
        },
        {
            'name': 'error_recovery',
            'steps': ['simulate_failure', 'trigger_recovery', 'verify_state']
        },
        {
            'name': 'concurrent_operations',
            'steps': ['start_workers', 'process_concurrent', 'aggregate_results']
        }
    ]

    results = []

    for scenario in scenarios:
        try:
            result = execute_scenario(scenario, config)
            results.append({
                'scenario': scenario['name'],
                'success': True,
                'execution_time': result.get('execution_time', 0)
            })
        except Exception as e:
            results.append({
                'scenario': scenario['name'],
                'success': False,
                'error': str(e)
            })

    return results
```

### What You Learned
- Asynchronous programming patterns
- Error recovery and resilience
- Performance monitoring and optimization
- Resource management best practices
- Comprehensive integration testing

## Tutorial 6: Contributing Examples - Code Review and Publishing

### Goal
Learn the complete process of contributing examples to the Codomyrmex project.

### Prerequisites
- Completed Tutorials 1-5
- Created at least one custom example
- Understanding of git and GitHub workflow

### Step 1: Code Review Checklist

Use this checklist before submitting your example:

```markdown
## Example Review Checklist

### Structure & Organization
- [ ] Example follows standard template
- [ ] Files are in correct locations
- [ ] Naming conventions followed
- [ ] No unnecessary files included

### Code Quality
- [ ] Imports are correct and minimal
- [ ] Error handling is comprehensive
- [ ] Code follows PEP 8 style
- [ ] Type hints used where appropriate
- [ ] Comments explain complex logic

### Configuration
- [ ] YAML configuration is valid
- [ ] JSON configuration provided
- [ ] Environment variables documented
- [ ] Sensible defaults provided

### Documentation
- [ ] README follows standard format
- [ ] All configuration options documented
- [ ] Usage examples provided
- [ ] Tested methods properly referenced

### Testing
- [ ] Example runs without errors
- [ ] Output files generated correctly
- [ ] Log files created appropriately
- [ ] Tested with different configurations

### Integration
- [ ] Follows existing patterns
- [ ] Compatible with common utilities
- [ ] No breaking changes to existing code
- [ ] Proper resource cleanup
```

### Step 2: Testing Your Example

Run comprehensive tests before submission:

```bash
# Run your example
cd scripts/your_module
python example_basic.py

# Test with different configs
python example_basic.py --config config.json

# Test error conditions
unset REQUIRED_ENV_VAR
python example_basic.py  # Should handle gracefully

# Check output validation
python -c "
import json
data = json.load(open('output/your_module_results.json'))
print('Output validation passed')
"

# Run example testing infrastructure (when available)
cd ../../../src/codomyrmex/tests/examples
python -m pytest test_example_execution.py -k your_module
```

### Step 3: Documentation Review

Ensure documentation is complete:

```bash
# Check README completeness
grep -E "(Overview|Features|Configuration|Usage|Output|Tested)" scripts/your_module/README.md

# Validate links
find scripts/your_module -name "*.md" -exec markdown-link-check {} \;

# Check for broken references
grep -r "test_" scripts/your_module/README.md
```

### Step 4: Git Workflow for Contribution

Follow the standard contribution workflow:

```bash
# Fork the repository (on GitHub)

# Clone your fork
git clone https://github.com/yourusername/codomyrmex.git
cd codomyrmex

# Create a feature branch
git checkout -b feature/add-your-module-example

# Make your changes
# ... create your example files ...

# Test your changes
./run_tests.sh

# Commit your changes
git add scripts/your_module/
git commit -m "Add comprehensive example for your_module

- Implements basic usage demonstration
- Includes YAML and JSON configurations
- Comprehensive documentation with tested method references
- Error handling and logging integration"

# Push to your fork
git push origin feature/add-your-module-example

# Create Pull Request (on GitHub)
```

### Step 5: Pull Request Process

Create an effective pull request:

**Title**: `Add comprehensive example for [module_name]`

**Description**:
```markdown
## Summary
Adds a complete example for the [module_name] module, demonstrating core functionality and integration patterns.

## Changes
- `scripts/[module_name]/example_basic.py` - Main example script
- `scripts/[module_name]/config.yaml` - YAML configuration
- `scripts/[module_name]/config.json` - JSON configuration
- `scripts/[module_name]/README.md` - Documentation

## Features Demonstrated
- [Feature 1]
- [Feature 2]
- [Feature 3]

## Tested Methods
- `method_name()` - Verified in `test_[module].py::TestClass::test_method`

## Testing
- Example runs successfully
- Output files generated correctly
- Configuration validation passes
- Error handling verified
```

### Step 6: Address Review Feedback

Be prepared to address common review feedback:

```python
# Common fixes needed

# 1. Fix import issues
from codomyrmex.your_module import correct_function_name

# 2. Add missing error handling
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise

# 3. Improve documentation
"""
Example: Your Module - Brief Description

Demonstrates:
- Key feature 1 with brief explanation
- Key feature 2 with integration details

Tested Methods:
- method_name() - Verified in test_your_module.py::TestClass::test_method
"""

# 4. Fix configuration issues
# config.yaml
output:
  format: json  # Add missing fields
  file: output/your_module_results.json
```

### Step 7: Maintenance and Updates

After your example is accepted:

```bash
# Stay updated with main branch
git checkout main
git pull upstream main

# Update your example if APIs change
# Monitor for breaking changes in module updates

# Contribute improvements
# - Add more features
# - Improve error handling
# - Update documentation
# - Add performance optimizations
```

### What You Learned
- Complete contribution workflow
- Code review best practices
- Pull request creation
- Addressing feedback
- Long-term maintenance

---

## Next Steps

Congratulations! You've completed all the Codomyrmex Examples tutorials. You now have the skills to:

- Run and understand existing examples
- Create new examples from scratch
- Integrate multiple modules in workflows
- Follow best practices for code quality
- Contribute examples to the project
- Troubleshoot and debug issues

## Additional Resources

- **[Main Documentation](../docs/)** - Complete Codomyrmex documentation
- **[API Reference](../../docs/reference/api.md)** - Detailed API specifications
- **[Module Guides](../../docs/modules)** - In-depth module documentation
- **[Troubleshooting Guide](TROUBLESHOOTING.md)** - Solutions to common issues
- **[Best Practices Guide](BEST_PRACTICES.md)** - Advanced usage patterns

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../docs/README.md)
- **Home**: [Root README](../../../README.md)
