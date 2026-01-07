#!/usr/bin/env python3
"""
Example: {Integration Name} - {Brief Description}

Demonstrates:
- Multi-module integration and orchestration
- Cross-module communication patterns
- Event-driven workflows
- Error propagation across modules
- Resource sharing and coordination
- Complex workflow execution

Tested Methods:
- Integration orchestration - Verified across multiple module tests
- Event system integration - Verified in test_events.py
- Cross-module communication - Verified in integration tests
"""

import sys
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Import multiple modules for integration
from codomyrmex.{module1} import (
    {Module1Function},
    {Module1Class}
)

from codomyrmex.{module2} import (
    {Module2Function},
    {Module2Class}
)

from codomyrmex.{module3} import (
    {Module3Function},
    {Module3Class}
)

# Event system for cross-module communication
try:
    from codomyrmex.events import EventBus, EventEmitter, EventLogger
    EVENTS_AVAILABLE = True
except ImportError:
    EVENTS_AVAILABLE = False
    EventBus = None
    EventEmitter = None
    EventLogger = None

# Import common utilities
from examples._common.config_loader import load_config
from examples._common.example_runner import ExampleRunner
from examples._common.utils import print_section, print_results, print_success, print_error

# Import logging
from codomyrmex.logging_monitoring import setup_logging, get_logger

logger = get_logger(__name__)


@dataclass
class IntegrationContext:
    """Context for multi-module integration."""

    workflow_id: str
    start_time: float
    modules_initialized: List[str] = field(default_factory=list)
    events_emitted: int = 0
    errors_encountered: int = 0
    resources_allocated: Dict[str, Any] = field(default_factory=dict)

    def record_module_init(self, module_name: str):
        """Record module initialization."""
        self.modules_initialized.append(module_name)
        logger.info(f"Module initialized: {module_name}")

    def record_event(self, event_type: str):
        """Record event emission."""
        self.events_emitted += 1
        logger.debug(f"Event emitted: {event_type}")

    def record_error(self, error: str):
        """Record error occurrence."""
        self.errors_encountered += 1
        logger.warning(f"Integration error: {error}")

    def allocate_resource(self, resource_name: str, resource: Any):
        """Allocate a shared resource."""
        self.resources_allocated[resource_name] = resource
        logger.debug(f"Resource allocated: {resource_name}")

    def get_execution_time(self) -> float:
        """Get total execution time."""
        return time.time() - self.start_time


@dataclass
class ModuleResult:
    """Result from a module operation."""

    module_name: str
    operation: str
    status: str
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    dependencies_satisfied: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "module_name": self.module_name,
            "operation": self.operation,
            "status": self.status,
            "data": self.data,
            "error": self.error,
            "execution_time": self.execution_time,
            "dependencies_satisfied": self.dependencies_satisfied
        }


class IntegrationWorkflowEngine:
    """Engine for managing multi-module integration workflows."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the integration workflow engine."""
        self.config = config
        self.context = IntegrationContext(
            workflow_id=config.get('integration', {}).get('workflow_id', 'default_workflow'),
            start_time=time.time()
        )

        # Initialize event system if available
        if EVENTS_AVAILABLE:
            self.event_bus = EventBus()
            self.event_emitter = EventEmitter(self.event_bus)
            self.event_logger = EventLogger()
            self._setup_event_handlers()
        else:
            self.event_bus = None
            self.event_emitter = None
            self.event_logger = None

        # Module registry
        self.modules = {}
        self.module_results = []

    def _setup_event_handlers(self):
        """Setup event handlers for cross-module communication."""
        @self.event_bus.subscribe("module_initialized")
        def on_module_initialized(event):
            self.context.record_module_init(event.data.get('module_name', 'unknown'))

        @self.event_bus.subscribe("workflow_error")
        def on_workflow_error(event):
            self.context.record_error(event.data.get('error', 'unknown error'))

        @self.event_bus.subscribe("resource_allocated")
        def on_resource_allocated(event):
            self.context.allocate_resource(
                event.data.get('resource_name', 'unknown'),
                event.data.get('resource', None)
            )

    def register_module(self, module_name: str, module_instance: Any):
        """Register a module for integration."""
        self.modules[module_name] = module_instance
        logger.info(f"Module registered: {module_name}")

    def execute_workflow_step(self, step_config: Dict[str, Any]) -> ModuleResult:
        """Execute a single workflow step."""
        step_name = step_config.get('name', 'unknown_step')
        module_name = step_config.get('module', 'unknown_module')
        operation = step_config.get('operation', 'unknown_operation')

        logger.info(f"Executing workflow step: {step_name}")

        start_time = time.time()
        result = ModuleResult(
            module_name=module_name,
            operation=operation,
            status="pending"
        )

        try:
            # Check dependencies
            dependencies = step_config.get('depends_on', [])
            if not self._check_dependencies(dependencies):
                result.status = "failed"
                result.error = f"Dependencies not satisfied: {dependencies}"
                result.dependencies_satisfied = False
            else:
                # Execute the step
                step_result = self._execute_step_operation(step_config)
                result.status = "success"
                result.data = step_result

                # Emit success event
                if self.event_emitter:
                    self.event_emitter.emit("step_completed", {
                        "step_name": step_name,
                        "module_name": module_name,
                        "result": step_result
                    })

        except Exception as e:
            result.status = "failed"
            result.error = str(e)
            logger.error(f"Step execution failed: {step_name} - {e}")

            # Emit error event
            if self.event_emitter:
                self.event_emitter.emit("step_failed", {
                    "step_name": step_name,
                    "module_name": module_name,
                    "error": str(e)
                })

        result.execution_time = time.time() - start_time
        self.module_results.append(result)

        return result

    def _check_dependencies(self, dependencies: List[str]) -> bool:
        """Check if step dependencies are satisfied."""
        for dependency in dependencies:
            # Check if dependency step has completed successfully
            dependency_results = [
                r for r in self.module_results
                if r.operation == dependency and r.status == "success"
            ]
            if not dependency_results:
                return False
        return True

    def _execute_step_operation(self, step_config: Dict[str, Any]) -> Any:
        """Execute the actual step operation."""
        module_name = step_config.get('module')
        operation = step_config.get('operation')
        parameters = step_config.get('parameters', {})

        # Get module instance
        if module_name not in self.modules:
            raise ValueError(f"Module not registered: {module_name}")

        module = self.modules[module_name]

        # Get operation function
        if not hasattr(module, operation):
            raise ValueError(f"Operation not found in module {module_name}: {operation}")

        operation_func = getattr(module, operation)

        # Execute operation
        return operation_func(**parameters)

    def execute_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a complete integration workflow."""
        workflow_name = workflow_config.get('name', 'integration_workflow')
        steps = workflow_config.get('steps', [])

        logger.info(f"Starting integration workflow: {workflow_name}")
        print_section(f"Integration Workflow: {workflow_name}")

        # Emit workflow start event
        if self.event_emitter:
            self.event_emitter.emit("workflow_started", {
                "workflow_name": workflow_name,
                "total_steps": len(steps)
            })

        workflow_results = {
            "workflow_name": workflow_name,
            "total_steps": len(steps),
            "completed_steps": 0,
            "failed_steps": 0,
            "step_results": []
        }

        for i, step_config in enumerate(steps, 1):
            step_name = step_config.get('name', f'step_{i}')
            print(f"Step {i}/{len(steps)}: {step_name}")

            # Execute step
            step_result = self.execute_workflow_step(step_config)
            workflow_results["step_results"].append(step_result.to_dict())

            if step_result.status == "success":
                workflow_results["completed_steps"] += 1
                print_success(f"✓ {step_name} completed")
            else:
                workflow_results["failed_steps"] += 1
                print_error(f"✗ {step_name} failed: {step_result.error}")

                # Check if we should fail fast
                if self.config.get('integration', {}).get('fail_fast', False):
                    logger.error("Failing fast due to step failure")
                    break

        # Calculate workflow metrics
        workflow_results["execution_time"] = self.context.get_execution_time()
        workflow_results["success_rate"] = (
            workflow_results["completed_steps"] / workflow_results["total_steps"]
            if workflow_results["total_steps"] > 0 else 0
        )

        # Emit workflow completion event
        if self.event_emitter:
            self.event_emitter.emit("workflow_completed", {
                "workflow_name": workflow_name,
                "success_rate": workflow_results["success_rate"],
                "execution_time": workflow_results["execution_time"]
            })

        logger.info(f"Workflow completed: {workflow_name}")
        print_success(f"Workflow completed: {workflow_results['completed_steps']}/{workflow_results['total_steps']} steps successful")

        return workflow_results

    def get_integration_summary(self) -> Dict[str, Any]:
        """Get summary of integration execution."""
        return {
            "workflow_id": self.context.workflow_id,
            "execution_time": self.context.get_execution_time(),
            "modules_initialized": self.context.modules_initialized,
            "events_emitted": self.context.events_emitted,
            "errors_encountered": self.context.errors_encountered,
            "resources_allocated": list(self.context.resources_allocated.keys()),
            "total_steps_executed": len(self.module_results),
            "successful_steps": sum(1 for r in self.module_results if r.status == "success"),
            "failed_steps": sum(1 for r in self.module_results if r.status == "failed")
        }


class {IntegrationName}Example:
    """Example class demonstrating multi-module integration."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the integration example."""
        self.config = config
        self.start_time = time.time()
        self.workflow_engine = IntegrationWorkflowEngine(config)
        self.modules_initialized = {}

        self.results = {
            "integration_name": "{integration_name}",
            "modules_integrated": [],
            "workflows_executed": 0,
            "total_operations": 0,
            "errors_encountered": 0,
            "execution_time": 0
        }

    def initialize_modules(self) -> Dict[str, Any]:
        """Initialize all modules for integration."""
        print_section("Module Initialization")

        init_results = {
            "modules_attempted": 0,
            "modules_successful": 0,
            "modules_failed": 0,
            "module_details": []
        }

        # Define modules to initialize
        modules_to_init = self.config.get('integration', {}).get('modules', [
            "{module1}",
            "{module2}",
            "{module3}"
        ])

        for module_name in modules_to_init:
            init_results["modules_attempted"] += 1

            try:
                # Initialize module (replace with actual initialization)
                module_instance = self._initialize_module(module_name)
                self.workflow_engine.register_module(module_name, module_instance)
                self.modules_initialized[module_name] = module_instance

                init_results["modules_successful"] += 1
                init_results["module_details"].append({
                    "name": module_name,
                    "status": "success"
                })

                print_success(f"✓ Module initialized: {module_name}")

            except Exception as e:
                init_results["modules_failed"] += 1
                init_results["module_details"].append({
                    "name": module_name,
                    "status": "failed",
                    "error": str(e)
                })

                print_error(f"✗ Module initialization failed: {module_name} - {e}")

        self.results["modules_integrated"] = list(self.modules_initialized.keys())

        return init_results

    def _initialize_module(self, module_name: str) -> Any:
        """Initialize a specific module."""
        # Replace with actual module initialization logic
        if module_name == "{module1}":
            # return {Module1Class}(self.config.get('module1', {}))
            return MockModule("{module1}")
        elif module_name == "{module2}":
            # return {Module2Class}(self.config.get('module2', {}))
            return MockModule("{module2}")
        elif module_name == "{module3}":
            # return {Module3Class}(self.config.get('module3', {}))
            return MockModule("{module3}")
        else:
            raise ValueError(f"Unknown module: {module_name}")

    def execute_integration_scenarios(self) -> Dict[str, Any]:
        """Execute various integration scenarios."""
        print_section("Integration Scenarios")

        scenarios = self.config.get('integration', {}).get('scenarios', [
            {
                "name": "basic_integration",
                "description": "Basic multi-module integration workflow",
                "steps": [
                    {
                        "name": "data_ingestion",
                        "module": "{module1}",
                        "operation": "ingest_data",
                        "parameters": {"source": "sample_data"}
                    },
                    {
                        "name": "data_processing",
                        "module": "{module2}",
                        "operation": "process_data",
                        "parameters": {"input": "ingested_data"},
                        "depends_on": ["data_ingestion"]
                    },
                    {
                        "name": "result_persistence",
                        "module": "{module3}",
                        "operation": "save_results",
                        "parameters": {"data": "processed_data"},
                        "depends_on": ["data_processing"]
                    }
                ]
            },
            {
                "name": "advanced_workflow",
                "description": "Advanced workflow with error handling",
                "steps": [
                    {
                        "name": "validation_step",
                        "module": "{module1}",
                        "operation": "validate_input",
                        "parameters": {"strict": True}
                    },
                    {
                        "name": "parallel_processing",
                        "module": "{module2}",
                        "operation": "parallel_process",
                        "parameters": {"workers": 3},
                        "depends_on": ["validation_step"]
                    },
                    {
                        "name": "quality_assurance",
                        "module": "{module3}",
                        "operation": "quality_check",
                        "parameters": {"threshold": 0.95},
                        "depends_on": ["parallel_processing"]
                    }
                ]
            }
        ])

        scenario_results = []

        for scenario in scenarios:
            print(f"\nExecuting scenario: {scenario['name']}")
            print(f"Description: {scenario['description']}")

            try:
                # Execute workflow
                workflow_result = self.workflow_engine.execute_workflow(scenario)
                scenario_results.append({
                    "scenario_name": scenario["name"],
                    "status": "completed",
                    "result": workflow_result
                })

                self.results["workflows_executed"] += 1

            except Exception as e:
                scenario_results.append({
                    "scenario_name": scenario["name"],
                    "status": "failed",
                    "error": str(e)
                })

                print_error(f"Scenario failed: {scenario['name']} - {e}")

        return {"scenarios_executed": len(scenarios), "scenario_results": scenario_results}

    def demonstrate_cross_module_communication(self) -> Dict[str, Any]:
        """Demonstrate cross-module communication patterns."""
        print_section("Cross-Module Communication")

        communication_results = {
            "events_exchanged": 0,
            "modules_coordinated": 0,
            "shared_resources": 0,
            "communication_patterns": []
        }

        try:
            # Demonstrate event-driven communication
            if self.workflow_engine.event_emitter:
                print("Testing event-driven communication...")

                # Emit test events
                self.workflow_engine.event_emitter.emit("integration_test", {
                    "test_data": "cross_module_communication"
                })

                communication_results["events_exchanged"] = 1
                communication_results["communication_patterns"].append("event_driven")

                print_success("✓ Event-driven communication demonstrated")

            # Demonstrate shared resource usage
            print("Testing shared resource coordination...")

            # Simulate shared resource allocation
            shared_resource = {"type": "database_connection", "status": "active"}
            self.workflow_engine.context.allocate_resource("shared_db", shared_resource)

            communication_results["shared_resources"] = 1
            communication_results["communication_patterns"].append("shared_resources")

            print_success("✓ Shared resource coordination demonstrated")

            # Demonstrate module coordination
            print("Testing module coordination...")
            coordinated_modules = len(self.modules_initialized)
            communication_results["modules_coordinated"] = coordinated_modules
            communication_results["communication_patterns"].append("module_coordination")

            print_success(f"✓ Module coordination demonstrated: {coordinated_modules} modules")

        except Exception as e:
            print_error(f"Cross-module communication failed: {e}")
            communication_results["error"] = str(e)

        return communication_results

    def demonstrate_error_propagation(self) -> Dict[str, Any]:
        """Demonstrate error propagation across modules."""
        print_section("Error Propagation and Recovery")

        error_results = {
            "errors_simulated": 0,
            "errors_handled": 0,
            "recovery_successful": 0,
            "error_scenarios": []
        }

        # Define error scenarios
        error_scenarios = [
            {
                "name": "module_failure",
                "description": "Test failure in one module",
                "simulate_error": True,
                "recovery_expected": True
            },
            {
                "name": "communication_failure",
                "description": "Test communication breakdown",
                "simulate_error": True,
                "recovery_expected": True
            },
            {
                "name": "resource_exhaustion",
                "description": "Test resource exhaustion handling",
                "simulate_error": True,
                "recovery_expected": False
            }
        ]

        for scenario in error_scenarios:
            error_results["errors_simulated"] += 1

            try:
                print(f"Testing error scenario: {scenario['name']}")

                # Simulate error condition
                self._simulate_error_condition(scenario)

                # Test error handling
                if self._test_error_recovery(scenario):
                    error_results["errors_handled"] += 1
                    error_results["recovery_successful"] += 1
                    print_success(f"✓ Error scenario handled: {scenario['name']}")
                else:
                    print_error(f"✗ Error scenario not properly handled: {scenario['name']}")

            except Exception as e:
                print_error(f"Error scenario failed: {scenario['name']} - {e}")

            error_results["error_scenarios"].append({
                "name": scenario["name"],
                "handled": scenario.get("recovery_successful", False)
            })

        return error_results

    def _simulate_error_condition(self, scenario: Dict[str, Any]):
        """Simulate an error condition."""
        if scenario.get("simulate_error", False):
            # Simulate different types of errors
            error_type = scenario.get("name", "unknown")

            if error_type == "module_failure":
                # Simulate module operation failure
                raise RuntimeError(f"Simulated {error_type}")
            elif error_type == "communication_failure":
                # Simulate communication error
                raise ConnectionError(f"Simulated {error_type}")
            elif error_type == "resource_exhaustion":
                # Simulate resource exhaustion
                raise MemoryError(f"Simulated {error_type}")

    def _test_error_recovery(self, scenario: Dict[str, Any]) -> bool:
        """Test error recovery mechanisms."""
        # Implement error recovery testing
        # Return True if error was handled properly
        return scenario.get("recovery_expected", False)

    def generate_integration_metrics(self) -> Dict[str, Any]:
        """Generate comprehensive integration metrics."""
        execution_time = time.time() - self.start_time

        integration_summary = self.workflow_engine.get_integration_summary()

        metrics = {
            "total_execution_time": execution_time,
            "modules_integrated": len(self.modules_initialized),
            "workflows_executed": self.results.get("workflows_executed", 0),
            "total_operations": sum(len(r.get("step_results", [])) for r in integration_summary.get("scenario_results", [])),
            "error_rate": self.results.get("errors_encountered", 0) / max(self.results.get("total_operations", 1), 1),
            "integration_efficiency": integration_summary.get("successful_steps", 0) / max(integration_summary.get("total_steps_executed", 1), 1),
            "event_system_active": self.workflow_engine.event_bus is not None,
            "cross_module_communication": integration_summary.get("events_emitted", 0) > 0
        }

        return metrics

    def cleanup_integration(self) -> bool:
        """Clean up integration resources."""
        try:
            logger.info("Cleaning up integration resources")

            # Clean up modules
            for module_name, module in self.modules_initialized.items():
                try:
                    if hasattr(module, 'cleanup'):
                        module.cleanup()
                    elif hasattr(module, 'close'):
                        module.close()
                except Exception as e:
                    logger.warning(f"Module cleanup failed: {module_name} - {e}")

            # Clean up workflow engine
            if hasattr(self.workflow_engine, 'cleanup'):
                self.workflow_engine.cleanup()

            logger.info("Integration cleanup completed successfully")
            return True

        except Exception as e:
            logger.error(f"Integration cleanup failed: {e}")
            return False

    def run_complete_integration_example(self) -> Dict[str, Any]:
        """Run the complete integration example workflow."""
        print_section("{Integration Name} Complete Integration Example")

        # Phase 1: Module Initialization
        init_results = self.initialize_modules()

        # Phase 2: Integration Scenarios
        scenario_results = self.execute_integration_scenarios()

        # Phase 3: Cross-Module Communication
        communication_results = self.demonstrate_cross_module_communication()

        # Phase 4: Error Propagation
        error_results = self.demonstrate_error_propagation()

        # Phase 5: Integration Metrics
        integration_metrics = self.generate_integration_metrics()

        # Phase 6: Cleanup
        cleanup_success = self.cleanup_integration()

        # Compile final results
        final_results = {
            "status": "completed" if cleanup_success else "completed_with_cleanup_issues",
            "integration_name": "{integration_name}",
            "module_initialization": init_results,
            "integration_scenarios": scenario_results,
            "cross_module_communication": communication_results,
            "error_propagation": error_results,
            "integration_metrics": integration_metrics,
            "cleanup_success": cleanup_success,
            "execution_summary": {
                "modules_integrated": len(self.modules_initialized),
                "workflows_executed": self.results.get("workflows_executed", 0),
                "total_operations": self.results.get("total_operations", 0),
                "errors_encountered": self.results.get("errors_encountered", 0),
                "integration_success_rate": integration_metrics.get("integration_efficiency", 0),
                "event_driven_communication": integration_metrics.get("cross_module_communication", False)
            }
        }

        return final_results


class MockModule:
    """Mock module for demonstration when real modules are not available."""

    def __init__(self, name: str):
        self.name = name
        self.data = {}

    def ingest_data(self, source: str) -> Dict[str, Any]:
        """Mock data ingestion."""
        return {"operation": "ingest_data", "source": source, "status": "success"}

    def process_data(self, input: str) -> Dict[str, Any]:
        """Mock data processing."""
        return {"operation": "process_data", "input": input, "status": "success"}

    def save_results(self, data: str) -> Dict[str, Any]:
        """Mock result saving."""
        return {"operation": "save_results", "data": data, "status": "success"}

    def validate_input(self, strict: bool = False) -> Dict[str, Any]:
        """Mock input validation."""
        return {"operation": "validate_input", "strict": strict, "status": "success"}

    def parallel_process(self, workers: int = 1) -> Dict[str, Any]:
        """Mock parallel processing."""
        return {"operation": "parallel_process", "workers": workers, "status": "success"}

    def quality_check(self, threshold: float = 0.8) -> Dict[str, Any]:
        """Mock quality checking."""
        return {"operation": "quality_check", "threshold": threshold, "status": "success"}


def main():
    """Main function to run the integration example."""
    # Load configuration
    config_path = Path(__file__).parent / "integration_template_config.yaml"
    if not config_path.exists():
        # Fallback to default integration config
        config = {
            "output": {
                "format": "json",
                "file": "output/integration_template_results.json"
            },
            "logging": {
                "level": "INFO",
                "file": "logs/integration_template.log"
            },
            "integration": {
                "workflow_id": "integration_template_workflow",
                "modules": ["{module1}", "{module2}", "{module3}"],
                "fail_fast": False,
                "enable_events": True,
                "scenarios": [
                    {
                        "name": "basic_integration",
                        "description": "Basic multi-module integration workflow",
                        "steps": [
                            {
                                "name": "data_ingestion",
                                "module": "{module1}",
                                "operation": "ingest_data",
                                "parameters": {"source": "sample_data"}
                            },
                            {
                                "name": "data_processing",
                                "module": "{module2}",
                                "operation": "process_data",
                                "parameters": {"input": "ingested_data"},
                                "depends_on": ["data_ingestion"]
                            },
                            {
                                "name": "result_persistence",
                                "module": "{module3}",
                                "operation": "save_results",
                                "parameters": {"data": "processed_data"},
                                "depends_on": ["data_processing"]
                            }
                        ]
                    }
                ]
            }
        }
    else:
        config = load_config(config_path)

    # Initialize example runner
    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        # Create and run integration example
        example = {IntegrationName}Example(config)
        results = example.run_complete_integration_example()

        # Validate and save results
        runner.validate_results(results)
        runner.save_results(results)
        runner.complete()

        print_success("{Integration Name} integration example completed successfully!")
        print(f"Modules integrated: {results.get('execution_summary', {}).get('modules_integrated', 0)}")
        print(f"Workflows executed: {results.get('execution_summary', {}).get('workflows_executed', 0)}")
        print(".1%")

    except Exception as e:
        runner.error("{Integration Name} integration example failed", e)
        print_error(f"{Integration Name} integration example failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
