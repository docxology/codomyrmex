# Integration Template Example

**Template Type**: Multi-Module Integration Example
**Purpose**: Template for creating complex multi-module integration workflows
**Complexity**: High

## Overview

This template provides a comprehensive framework for creating examples that demonstrate integration between multiple Codomyrmex modules. It includes workflow orchestration, cross-module communication, event-driven patterns, error propagation, and resource coordination.

## Template Features

### Core Integration Architecture
- **Workflow Engine**: Orchestrates complex multi-step workflows
- **Module Registry**: Manages module initialization and coordination
- **Event System**: Enables cross-module communication
- **Dependency Management**: Handles step dependencies and execution order
- **Resource Coordination**: Manages shared resources across modules

### Integration Patterns Demonstrated
- **Sequential Workflows**: Step-by-step module execution
- **Parallel Processing**: Concurrent module operations
- **Event-Driven Communication**: Loose coupling between modules
- **Error Propagation**: Cross-module error handling and recovery
- **Resource Sharing**: Shared resource allocation and cleanup

### Integration Demonstration Sections
1. **Module Initialization**: Setup and registration of multiple modules
2. **Workflow Execution**: Orchestrated execution of integration scenarios
3. **Cross-Module Communication**: Event-driven inter-module communication
4. **Error Propagation**: Error handling across module boundaries
5. **Resource Management**: Shared resource coordination and cleanup

## Usage Instructions

### 1. Copy Integration Template Files

```bash
# Copy template files to new integration example directory
cp scripts/_templates/integration_template.py scripts/multi_module/examples/{integration_name}/example_basic.py
cp scripts/_templates/integration_template_config.yaml scripts/multi_module/examples/{integration_name}/config.yaml
cp scripts/_templates/integration_template_README.md scripts/multi_module/examples/{integration_name}/README.md
```

### 2. Customize Integration Modules

**Update module imports:**
```python
# Replace template imports with actual modules
from codomyrmex.{actual_module1} import (
    {ActualFunction1},
    {ActualClass1}
)

from codomyrmex.{actual_module2} import (
    {ActualFunction2},
    {ActualClass2}
)

from codomyrmex.{actual_module3} import (
    {ActualFunction3},
    {ActualClass3}
)
```

**Update integration class name:**
```python
# Change class name
class {YourIntegrationName}Example:
```

**Customize workflow engine:**
```python
# Update workflow engine configuration
def _initialize_module(self, module_name: str) -> Any:
    if module_name == "{actual_module1}":
        return {ActualClass1}(self.config.get('module1_config', {}))
    elif module_name == "{actual_module2}":
        return {ActualClass2}(self.config.get('module2_config', {}))
    elif module_name == "{actual_module3}":
        return {ActualClass3}(self.config.get('module3_config', {}))
```

### 3. Configure Integration Scenarios

**Customize workflow scenarios:**
```yaml
integration:
  scenarios:
    - name: "your_integration_scenario"
      description: "Description of your integration workflow"
      steps:
        - name: "step_1"
          module: "{actual_module1}"
          operation: "actual_operation"
          parameters:
            param1: "value1"
            param2: 42
          timeout: 60

        - name: "step_2"
          module: "{actual_module2}"
          operation: "another_operation"
          parameters:
            input: "step_1_output"
          depends_on:
            - "step_1"
```

### 4. Update Integration Documentation

**Customize README.md:**
```markdown
# Your Integration Example

## Overview
Demonstrates integration between {module1}, {module2}, and {module3}.

## Integration Scenario
Describe the real-world scenario this integration addresses.

## Modules Integrated
- **{Module1}**: Purpose and role in integration
- **{Module2}**: Purpose and role in integration
- **{Module3}**: Purpose and role in integration

## Workflow Steps
1. **Step 1**: Description of first step
2. **Step 2**: Description of second step
3. **Step 3**: Description of third step

## Communication Patterns
- Event-driven communication between modules
- Shared resource coordination
- Error propagation and recovery
```

### 5. Update Template Placeholders

**Global search and replace:**
- `{Integration Name}` → `Your Integration Name`
- `{integration_name}` → `your_integration_name`
- `{module1}` → `actual_module1`
- `{module2}` → `actual_module2`
- `{module3}` → `actual_module3`
- `{IntegrationName}` → `YourIntegrationName`

## Integration Configuration Options

### Core Integration Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `integration.workflow_id` | string | `"integration_template_workflow"` | Unique workflow identifier |
| `integration.fail_fast` | boolean | `false` | Stop execution on first failure |
| `integration.enable_events` | boolean | `true` | Enable event-driven communication |
| `integration.max_execution_time` | integer | `300` | Maximum workflow execution time |
| `integration.modules` | array | `["{module1}", "{module2}", "{module3}"]` | List of modules to integrate |

### Workflow Scenario Configuration

**Scenario Structure:**
```yaml
- name: "scenario_name"
  description: "Human-readable description"
  timeout: 120                    # Scenario timeout in seconds
  parallel_execution: false       # Enable parallel step execution
  steps:
    - name: "step_name"
      module: "module_name"
      operation: "operation_name"
      parameters:
        param1: "value1"
        param2: 42
      depends_on:                 # Optional dependencies
        - "previous_step_name"
      timeout: 60                 # Step-specific timeout
      retry_count: 2              # Retry attempts on failure
```

### Event System Configuration

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `events.enabled` | boolean | `true` | Enable event system |
| `events.event_bus_size` | integer | `1000` | Maximum events in bus |
| `events.event_retention_hours` | integer | `24` | Event retention time |
| `events.handlers` | object | `{}` | Event handler mappings |

## Integration Output Format

The integration template generates a comprehensive JSON result file:

```json
{
  "status": "completed",
  "integration_name": "your_integration_name",
  "module_initialization": {
    "modules_attempted": 3,
    "modules_successful": 3,
    "modules_failed": 0,
    "module_details": [
      {"name": "module1", "status": "success"},
      {"name": "module2", "status": "success"},
      {"name": "module3", "status": "success"}
    ]
  },
  "integration_scenarios": {
    "scenarios_executed": 2,
    "scenario_results": [
      {
        "scenario_name": "basic_integration",
        "status": "completed",
        "result": {
          "workflow_name": "basic_integration",
          "total_steps": 3,
          "completed_steps": 3,
          "failed_steps": 0,
          "execution_time": 45.2,
          "success_rate": 1.0,
          "step_results": [...]
        }
      }
    ]
  },
  "cross_module_communication": {
    "events_exchanged": 12,
    "modules_coordinated": 3,
    "shared_resources": 2,
    "communication_patterns": [
      "event_driven",
      "shared_resources",
      "module_coordination"
    ]
  },
  "error_propagation": {
    "errors_simulated": 3,
    "errors_handled": 3,
    "recovery_successful": 2,
    "error_scenarios": [...]
  },
  "integration_metrics": {
    "total_execution_time": 123.4,
    "modules_integrated": 3,
    "workflows_executed": 2,
    "total_operations": 8,
    "error_rate": 0.0,
    "integration_efficiency": 1.0,
    "event_system_active": true,
    "cross_module_communication": true
  },
  "execution_summary": {
    "modules_integrated": 3,
    "workflows_executed": 2,
    "total_operations": 8,
    "errors_encountered": 0,
    "integration_success_rate": 1.0,
    "event_driven_communication": true
  }
}
```

## Advanced Integration Patterns

### Implementing Custom Workflow Steps

```python
def execute_custom_workflow_step(self, step_config: Dict[str, Any]) -> ModuleResult:
    """Execute a custom workflow step with advanced logic."""

    step_name = step_config.get('name', 'custom_step')
    start_time = time.time()

    result = ModuleResult(
        module_name="custom_orchestrator",
        operation=step_name,
        status="pending"
    )

    try:
        # Custom step logic
        if step_config.get('type') == 'parallel':
            # Execute multiple operations in parallel
            await self._execute_parallel_operations(step_config)
        elif step_config.get('type') == 'conditional':
            # Execute based on conditions
            await self._execute_conditional_operations(step_config)
        elif step_config.get('type') == 'iterative':
            # Execute iterative operations
            await self._execute_iterative_operations(step_config)

        result.status = "success"
        result.data = {"custom_execution": True}

        # Emit custom event
        if self.workflow_engine.event_emitter:
            self.workflow_engine.event_emitter.emit("custom_step_completed", {
                "step_name": step_name,
                "custom_data": result.data
            })

    except Exception as e:
        result.status = "failed"
        result.error = str(e)

        # Emit error event
        if self.workflow_engine.event_emitter:
            self.workflow_engine.event_emitter.emit("custom_step_failed", {
                "step_name": step_name,
                "error": str(e)
            })

    result.execution_time = time.time() - start_time
    return result
```

### Dynamic Module Loading

```python
async def load_modules_dynamically(self, module_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Load modules dynamically based on configuration."""

    loaded_modules = {}
    load_results = {
        "modules_requested": len(module_configs),
        "modules_loaded": 0,
        "load_errors": []
    }

    for module_config in module_configs:
        module_name = module_config.get('name')
        module_type = module_config.get('type')
        module_params = module_config.get('parameters', {})

        try:
            # Dynamic module loading
            if module_type == 'database':
                module = await self._load_database_module(module_params)
            elif module_type == 'api':
                module = await self._load_api_module(module_params)
            elif module_type == 'processing':
                module = await self._load_processing_module(module_params)

            loaded_modules[module_name] = module
            self.workflow_engine.register_module(module_name, module)
            load_results["modules_loaded"] += 1

            # Emit module loaded event
            if self.workflow_engine.event_emitter:
                self.workflow_engine.event_emitter.emit("module_loaded", {
                    "module_name": module_name,
                    "module_type": module_type
                })

        except Exception as e:
            error_msg = f"Failed to load module {module_name}: {e}"
            load_results["load_errors"].append(error_msg)
            logger.error(error_msg)

    return load_results
```

### Event-Driven Error Recovery

```python
def setup_error_recovery_handlers(self):
    """Setup event-driven error recovery."""

    @self.workflow_engine.event_bus.subscribe("step_failed")
    def handle_step_failure(event):
        """Handle workflow step failures."""
        failed_step = event.data.get('step_name')
        error_details = event.data.get('error')

        logger.warning(f"Handling failure for step: {failed_step}")

        # Determine recovery strategy
        recovery_strategy = self._determine_recovery_strategy(failed_step, error_details)

        if recovery_strategy == 'retry':
            self._schedule_step_retry(failed_step)
        elif recovery_strategy == 'skip':
            self._mark_step_skipped(failed_step)
        elif recovery_strategy == 'compensate':
            self._execute_compensation_actions(failed_step)
        elif recovery_strategy == 'fail_workflow':
            self._fail_entire_workflow(failed_step, error_details)

    @self.workflow_engine.event_bus.subscribe("resource_exhausted")
    def handle_resource_exhaustion(event):
        """Handle resource exhaustion events."""
        resource_type = event.data.get('resource_type')

        logger.warning(f"Handling resource exhaustion: {resource_type}")

        # Implement resource cleanup and reallocation
        self._cleanup_exhausted_resources(resource_type)
        self._reallocate_resources(resource_type)

    @self.workflow_engine.event_bus.subscribe("module_unresponsive")
    def handle_module_unresponsiveness(event):
        """Handle unresponsive module events."""
        module_name = event.data.get('module_name')

        logger.warning(f"Handling unresponsive module: {module_name}")

        # Attempt module restart or replacement
        self._attempt_module_recovery(module_name)
```

### Resource Coordination Across Modules

```python
class ResourceCoordinator:
    """Coordinates resource sharing across modules."""

    def __init__(self):
        self.resources = {}
        self.resource_locks = {}
        self.waiting_modules = {}

    async def allocate_shared_resource(self, resource_name: str, requesting_module: str) -> Any:
        """Allocate a shared resource with coordination."""

        if resource_name not in self.resource_locks:
            self.resource_locks[resource_name] = asyncio.Lock()

        async with self.resource_locks[resource_name]:
            # Check if resource exists
            if resource_name not in self.resources:
                # Create resource
                self.resources[resource_name] = await self._create_resource(resource_name)

            # Check resource availability
            if not await self._is_resource_available(resource_name):
                # Add to waiting list
                if resource_name not in self.waiting_modules:
                    self.waiting_modules[resource_name] = []
                self.waiting_modules[resource_name].append(requesting_module)

                # Wait for resource availability
                await self._wait_for_resource(resource_name)

            # Allocate resource
            resource = self.resources[resource_name]
            await self._record_allocation(resource_name, requesting_module)

            return resource

    async def release_shared_resource(self, resource_name: str, releasing_module: str):
        """Release a shared resource."""

        async with self.resource_locks[resource_name]:
            await self._record_release(resource_name, releasing_module)

            # Notify waiting modules
            if resource_name in self.waiting_modules and self.waiting_modules[resource_name]:
                next_module = self.waiting_modules[resource_name].pop(0)
                # Notify next module (implementation depends on notification system)

    async def _create_resource(self, resource_name: str) -> Any:
        """Create a new shared resource."""
        # Implementation for different resource types
        if resource_name.startswith('database_'):
            return await self._create_database_connection(resource_name)
        elif resource_name.startswith('cache_'):
            return await self._create_cache_instance(resource_name)
        elif resource_name.startswith('queue_'):
            return await self._create_message_queue(resource_name)

    async def _is_resource_available(self, resource_name: str) -> bool:
        """Check if a resource is available for allocation."""
        # Implementation for resource availability checking
        resource = self.resources.get(resource_name)
        if resource is None:
            return False

        # Check resource-specific availability
        return await self._check_resource_health(resource)
```

## Integration Testing Strategies

### End-to-End Integration Testing

```python
def test_complete_integration_workflow(self):
    """Test complete integration workflow end-to-end."""

    # Setup test environment
    test_config = self._create_test_configuration()
    example = IntegrationExample(test_config)

    # Execute integration
    start_time = time.time()
    results = example.run_complete_integration_example()
    execution_time = time.time() - start_time

    # Validate results
    assert results["status"] in ["completed", "completed_with_cleanup_issues"]
    assert results["execution_summary"]["modules_integrated"] >= 2
    assert results["execution_summary"]["workflows_executed"] >= 1
    assert execution_time < 300  # Should complete within 5 minutes

    # Validate cross-module communication
    assert results["execution_summary"]["event_driven_communication"]

    # Validate error handling
    assert results["error_propagation"]["errors_simulated"] >= 1
    assert results["error_propagation"]["errors_handled"] >= 1

def test_integration_error_recovery(self):
    """Test error recovery in integration scenarios."""

    # Setup scenario with simulated failures
    test_config = self._create_error_test_configuration()
    example = IntegrationExample(test_config)

    # Execute with error injection
    results = example.run_complete_integration_example()

    # Validate error recovery
    error_results = results["error_propagation"]
    assert error_results["errors_simulated"] > 0
    assert error_results["recovery_successful"] >= error_results["errors_simulated"] * 0.8  # 80% recovery rate
```

### Performance Testing for Integration

```python
def test_integration_performance_scaling(self):
    """Test integration performance under different loads."""

    load_scenarios = [
        {"modules": 2, "workflows": 1, "expected_time": 30},
        {"modules": 3, "workflows": 2, "expected_time": 60},
        {"modules": 5, "workflows": 3, "expected_time": 120}
    ]

    for scenario in load_scenarios:
        test_config = self._create_load_test_configuration(scenario)
        example = IntegrationExample(test_config)

        start_time = time.time()
        results = example.run_complete_integration_example()
        execution_time = time.time() - start_time

        # Validate performance
        assert execution_time < scenario["expected_time"] * 1.5  # 50% tolerance
        assert results["integration_metrics"]["integration_efficiency"] > 0.8

        # Log performance metrics
        logger.info(f"Load test {scenario}: {execution_time:.2f}s, efficiency: {results['integration_metrics']['integration_efficiency']:.2%}")
```

## Integration Best Practices

### 1. Loose Coupling Between Modules
- Use event-driven communication
- Avoid direct module dependencies
- Implement abstraction layers

### 2. Robust Error Handling
- Implement circuit breakers
- Use exponential backoff for retries
- Provide graceful degradation

### 3. Resource Management
- Implement proper cleanup
- Use resource pools
- Monitor resource usage

### 4. Monitoring and Observability
- Track integration metrics
- Implement health checks
- Provide comprehensive logging

### 5. Testing Strategy
- Test individual modules first
- Test integration scenarios
- Include performance testing
- Test failure scenarios

## Troubleshooting Integration Template Usage

### Workflow Execution Issues

**Symptoms**: Workflow steps fail to execute
```
Error: Module not registered: module_name
```
**Solution**: Ensure all modules are properly initialized before workflow execution.

### Event System Problems

**Symptoms**: Events not being processed
```
Warning: Event bus not available
```
**Solution**: Check that the events module is available and properly configured.

### Dependency Resolution Issues

**Symptoms**: Steps fail due to unmet dependencies
```
Error: Dependencies not satisfied: ['step_name']
```
**Solution**: Ensure dependency steps complete successfully before dependent steps execute.

### Resource Contention Issues

**Symptoms**: Deadlocks or resource exhaustion
```
Error: Resource timeout exceeded
```
**Solution**: Implement proper resource cleanup and avoid circular dependencies.

### Performance Issues

**Symptoms**: Integration takes too long
```
Warning: Workflow execution exceeded timeout
```
**Solution**: Optimize step execution, reduce dependencies, or increase timeouts.

## Common Integration Patterns

### Data Pipeline Integration

```yaml
# Configuration for data processing pipeline
integration:
  scenarios:
    - name: "data_pipeline"
      steps:
        - name: "extract"
          module: "data_ingestion"
          operation: "extract_data"
        - name: "transform"
          module: "data_processing"
          operation: "transform_data"
          depends_on: ["extract"]
        - name: "load"
          module: "data_storage"
          operation: "load_data"
          depends_on: ["transform"]
```

### API Integration Workflow

```yaml
# Configuration for API development workflow
integration:
  scenarios:
    - name: "api_workflow"
      steps:
        - name: "design"
          module: "api_design"
          operation: "design_api"
        - name: "implement"
          module: "api_implementation"
          operation: "implement_api"
          depends_on: ["design"]
        - name: "test"
          module: "api_testing"
          operation: "test_api"
          depends_on: ["implement"]
        - name: "deploy"
          module: "api_deployment"
          operation: "deploy_api"
          depends_on: ["test"]
```

### Microservices Coordination

```yaml
# Configuration for microservices integration
integration:
  scenarios:
    - name: "microservices_workflow"
      parallel_execution: true
      steps:
        - name: "auth_service"
          module: "auth_service"
          operation: "start_service"
        - name: "user_service"
          module: "user_service"
          operation: "start_service"
        - name: "product_service"
          module: "product_service"
          operation: "start_service"
        - name: "order_service"
          module: "order_service"
          operation: "start_service"
          depends_on: ["auth_service", "user_service", "product_service"]
```

## Related Templates

- **Basic Template** (`basic_template.py`): For single module examples
- **Async Template** (`async_template.py`): For async operations
- **Advanced Template** (`advanced_template.py`): For complex single module examples

## Contributing Improvements

To improve this integration template:

1. **Add Integration Patterns**: Include more complex integration scenarios
2. **Enhance Error Recovery**: Implement more sophisticated error recovery mechanisms
3. **Improve Resource Management**: Add more advanced resource coordination
4. **Expand Monitoring**: Include more comprehensive integration monitoring
5. **Add Testing**: Create more integration testing patterns

---

**Status**: Active Integration Template
**Last Updated**: January 2026
**Compatibility**: Codomyrmex v1.0+
**Dependencies**: events (optional)
