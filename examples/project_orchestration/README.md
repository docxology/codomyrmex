# Project Orchestration Example

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Module**: `project_orchestration` - Workflow Management and Task Orchestration

## Overview

This example demonstrates comprehensive project orchestration capabilities using the Codomyrmex `project_orchestration` module. It showcases workflow creation, DAG-based task execution, parallel processing, and resource management through a complete project automation scenario.

## What This Example Demonstrates

### Core Orchestration Features
- **Workflow Management**: Creating, configuring, and executing complex workflows
- **DAG Processing**: Directed Acyclic Graph creation and execution order determination
- **Parallel Execution**: Concurrent task processing with dependency management
- **Dependency Validation**: Ensuring workflow integrity and proper task ordering
- **Resource Management**: Managing computational resources and constraints
- **Session Management**: Orchestration context and state management

### Workflow Lifecycle
1. **Workflow Definition**: Creating workflows with interdependent steps
2. **Dependency Analysis**: Validating task relationships and execution order
3. **DAG Construction**: Building execution graphs from task dependencies
4. **Parallel Execution**: Running independent tasks concurrently
5. **Result Aggregation**: Collecting and reporting execution outcomes

## Tested Methods

This example references methods verified in the following test files:

- **`test_project_orchestration.py`** - Comprehensive orchestration testing

### Specific Methods Demonstrated

| Method | Test Reference | Description |
|--------|----------------|-------------|
| `WorkflowManager.create_workflow()` | `TestWorkflowManager::test_create_workflow` | Create workflow with steps |
| `WorkflowManager.list_workflows()` | `TestWorkflowManager::test_list_workflows` | List available workflows |
| `create_workflow_dag()` | `TestWorkflowManager::test_create_workflow_dag` | Build task dependency graph |
| `execute_parallel_workflow()` | `TestWorkflowManager::test_execute_parallel_workflow` | Execute tasks in parallel |
| `validate_workflow_dependencies()` | `TestWorkflowManager::test_validate_workflow_dependencies` | Check dependency validity |
| `get_workflow_execution_order()` | `TestWorkflowManager::test_get_workflow_execution_order` | Determine execution sequence |

## Configuration

### YAML Configuration (`config.yaml`)

```yaml
# Workflow manager settings
workflow:
  manager:
    enable_performance_monitoring: true
    max_parallel_tasks: 4

  # Sample workflow definition
  sample_workflow:
    name: "analysis_and_reporting"
    steps:
      - name: "data_collection"
        module: "data_visualization"
        action: "create_bar_chart"
        parameters:
          data: {"Python": 85, "JavaScript": 75}
        dependencies: []

      - name: "security_audit"
        module: "security_audit"
        action: "scan_codebase"
        dependencies: ["data_collection"]

# DAG configuration
dag:
  tasks:
    - name: "init"
      module: "environment_setup"
      dependencies: []
    - name: "build"
      dependencies: ["init"]
  execution:
    max_parallel: 3
    timeout_seconds: 300

# Resource management
resources:
  cpu_limit: 4
  memory_limit_gb: 8
```

### JSON Configuration (`config.json`)

The JSON configuration provides the same options in JSON format with nested object structures for complex workflow definitions.

## Running the Example

### Basic Execution

```bash
cd examples/project_orchestration

# Run with YAML config (default)
python example_basic.py

# Run with JSON config
python example_basic.py --config config.json
```

### Environment Variables

- `LOG_LEVEL`: Override logging level (DEBUG, INFO, WARNING, ERROR)
- `MAX_PARALLEL_TASKS`: Override maximum parallel tasks (default: 4)
- `WORKFLOW_TIMEOUT`: Set workflow execution timeout in seconds

## Expected Output

### Console Output

```
================================================================================
 Project Orchestration Example
================================================================================

🏗️  Initializing Workflow Manager...
✓ Workflow manager initialized

📋 Creating sample workflow...
✓ Workflow 'sample_analysis_workflow' created successfully

📋 Listing available workflows...

================================================================================
 Available Workflows
================================================================================

workflows:
  [
  "sample_analysis_workflow"
]

🔗 Creating workflow DAG...

================================================================================
 DAG Creation Results
================================================================================

tasks_count: 4
dag_created: true

✅ Validating workflow dependencies...

================================================================================
 Dependency Validation
================================================================================

valid: true
errors: []

📊 Determining execution order...

================================================================================
 Execution Order Analysis
================================================================================

stages: 3
total_tasks: 4
execution_order:
  [
    [
      "task1"
    ],
    [
      "task2",
      "task3"
    ],
    [
      "task4"
    ]
  ]

⚡ Executing parallel workflow...
✓ Parallel execution completed

🚀 Executing workflow (simulated)...

================================================================================
 Workflow Execution Summary
================================================================================

workflow_name: "sample_analysis_workflow"
status: "completed"
steps_executed: 4
execution_time: "2.5s"

================================================================================
 Operations Summary
================================================================================

workflow_manager_initialized: true
workflow_created: true
workflows_listed: true
dag_created: true
dependencies_validated: true
execution_order_determined: true
parallel_execution_attempted: true
workflow_execution_simulated: true

✅ Project Orchestration example completed successfully!
```

### Generated Files

- **`output/project_orchestration_results.json`**: Complete execution results and workflow metadata
- **`logs/project_orchestration_example.log`**: Detailed execution logs with performance metrics

### Results Structure

```json
{
  "workflow_manager_initialized": true,
  "workflow_created": true,
  "workflows_listed": true,
  "dag_created": true,
  "dependencies_validated": true,
  "execution_order_determined": true,
  "parallel_execution_attempted": true,
  "workflow_execution_simulated": true
}
```

## Workflow Demonstration

The example demonstrates a complete orchestration scenario:

### 1. Workflow Creation
- Define complex workflows with multiple interdependent steps
- Configure parameters and dependencies for each task
- Validate workflow structure and requirements

### 2. Dependency Analysis
- Parse task dependencies to build execution graph
- Identify independent tasks for parallel execution
- Determine optimal execution order

### 3. DAG Construction
- Create Directed Acyclic Graph from task relationships
- Identify execution stages and parallel opportunities
- Validate graph structure and constraints

### 4. Parallel Execution
- Execute independent tasks concurrently
- Respect dependency constraints
- Aggregate results from parallel operations

### 5. Resource Management
- Monitor resource usage during execution
- Respect CPU and memory limits
- Track execution performance metrics

## Configuration Options

### Workflow Manager Settings

| Option | Description | Default |
|--------|-------------|---------|
| `workflow.manager.enable_performance_monitoring` | Track execution metrics | `true` |
| `workflow.manager.max_parallel_tasks` | Maximum concurrent tasks | `4` |
| `workflow.manager.config_dir` | Workflow storage directory | `"./workflows"` |

### DAG Execution Settings

| Option | Description | Default |
|--------|-------------|---------|
| `dag.execution.max_parallel` | Maximum parallel tasks | `3` |
| `dag.execution.timeout_seconds` | Execution timeout | `300` |
| `dag.execution.retry_failed` | Retry failed tasks | `true` |
| `dag.execution.retry_attempts` | Number of retries | `2` |

### Resource Limits

| Option | Description | Default |
|--------|-------------|---------|
| `resources.cpu_limit` | CPU core limit | `4` |
| `resources.memory_limit_gb` | Memory limit in GB | `8` |
| `resources.disk_space_gb` | Disk space limit | `10` |

## Task Definition Format

Tasks are defined with the following structure:

```yaml
- name: "task_name"
  module: "module_name"
  action: "function_name"
  parameters:
    param1: value1
    param2: value2
  dependencies:
    - "parent_task1"
    - "parent_task2"
```

## Dependency Resolution

The orchestration engine automatically:

- **Topological Sorting**: Orders tasks based on dependencies
- **Cycle Detection**: Prevents circular dependencies
- **Parallel Grouping**: Identifies tasks that can run concurrently
- **Resource Allocation**: Manages resource constraints across tasks

## Error Handling

The example includes comprehensive error handling for:

- **Workflow Creation**: Invalid workflow definitions
- **Dependency Validation**: Circular or invalid dependencies
- **Resource Limits**: Insufficient resources for execution
- **Task Failures**: Individual task execution errors
- **Timeout Handling**: Long-running workflow termination

## Performance Monitoring

When enabled, the orchestration system tracks:

- **Execution Time**: Total and per-task timing
- **Resource Usage**: CPU, memory, and disk utilization
- **Parallel Efficiency**: Task concurrency metrics
- **Failure Rates**: Task success/failure statistics

## Integration with Other Modules

This example demonstrates orchestration integration with:

- **`logging_monitoring`**: Workflow execution logging
- **`performance`**: Execution performance tracking
- **`events`**: Workflow event broadcasting
- **`config_management`**: Workflow configuration management

## Session Management

The orchestration engine supports:

- **Session Creation**: Isolated execution contexts
- **State Persistence**: Workflow state across executions
- **Resource Tracking**: Session-level resource management
- **Event Logging**: Session activity monitoring

## Scaling Considerations

For large-scale orchestration:

- **Horizontal Scaling**: Distribute tasks across multiple workers
- **Resource Pooling**: Shared resource management
- **Load Balancing**: Optimal task distribution
- **Fault Tolerance**: Handle worker failures gracefully

## Troubleshooting

### Common Issues

**"Workflow creation failed"**
- Check workflow definition syntax
- Verify module and action names
- Ensure parameter types are correct

**"Dependency validation failed"**
- Check for circular dependencies
- Verify parent task names exist
- Ensure dependency chains are valid

**"Resource limits exceeded"**
- Reduce concurrent task count
- Increase resource allocations
- Optimize task resource requirements

**"Task execution timeout"**
- Increase timeout values
- Optimize task performance
- Break large tasks into smaller units

### Debug Mode

Enable detailed debugging:

```bash
LOG_LEVEL=DEBUG python example_basic.py
```

This provides verbose logging for workflow execution, dependency resolution, and performance metrics.

## Related Examples

- **CI/CD Automation**: Shows orchestration in deployment pipelines
- **Build Synthesis**: Demonstrates build orchestration workflows
- **Events System**: Integration with event-driven workflows

---

**Module**: `project_orchestration` | **Status**: ✅ Complete | **Test Coverage**: Comprehensive

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [examples](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)