# 🤖 Codomyrmex Droid TODO System

## Overview

The Codomyrmex Droid TODO System is an intelligent task automation system that allows you to define, execute, and manage complex development tasks using AI-powered agents. This system integrates with the broader Codomyrmex platform to provide seamless task execution with comprehensive monitoring and statistics.

## Architecture

### Core Components

1. **TODO List** (`todo_list.txt`) - Defines tasks to be executed
2. **Task Handlers** (`tasks.py`) - Contains the actual implementation of tasks
3. **Droid Controller** (`controller.py`) - Manages task execution and system state
4. **TODO Manager** (`todo.py`) - Handles TODO list parsing and management
5. **Execution Engine** (`run_todo_droid.py`) - Main execution script with enhanced features
6. **System Manager** (`droid_manager.py`) - High-level system management and monitoring

### Data Flow

```
User Request → TODO List → Task Parser → Handler Resolution → Controller Execution → Results
     ↓              ↓            ↓              ↓                  ↓              ↓
  Documentation   Format      Validation    Import Check      AI Processing   Statistics
  Interface       Validation   Error Check   Module Loading    Task Completion  Monitoring
```

## How to Add New Tasks

### 1. Define the Task in TODO List

Add your task to `todo_list.txt` using the following format:

```text
# TODO Format Example: operation_id | handler_path | description
[TODO]
your_operation_id | tasks:your_handler_function | Your detailed task description here.
```

### 2. Implement the Task Handler

Add your task handler function to `tasks.py`:

```python
def your_handler_function(*, prompt: str, description: str) -> str:
    """Your task handler implementation."""
    # Your implementation here
    logger.info(f"Executing task: {description}", extra={"description": description})
    return f"Task completed: {description}"
```

### 3. Register the Handler

Add your function to the `__all__` list in `tasks.py`:

```python
__all__ = [
    # ... existing handlers ...
    "your_handler_function",
]
```

### 4. Execute the Task

Run the droid system:

```bash
# Execute all TODOs
python run_todo_droid.py --count -1

# Execute specific number
python run_todo_droid.py --count 3

# Dry run to preview
python run_todo_droid.py --dry-run
```

## Task Handler Guidelines

### Function Signature

All task handlers must follow this signature:

```python
def handler_name(*, prompt: str, description: str) -> str:
    """Handler description."""
    # Implementation
    return "result message"
```

### Required Components

1. **Prompt Parameter**: Enhanced Codomyrmex-specific prompt with project context
2. **Description Parameter**: Task description from TODO list
3. **Return Value**: Success message or result description
4. **Logging**: Use the provided logger for status updates
5. **Error Handling**: Handle exceptions gracefully

### Best Practices

- **Modularity**: Keep handlers focused on single responsibilities
- **Idempotency**: Handlers should be safe to run multiple times
- **Documentation**: Include comprehensive docstrings
- **Testing**: Add tests for complex logic
- **Performance**: Consider execution time and resource usage
- **Security**: Follow Codomyrmex security guidelines

## TODO List Format Specification

### Structure

```text
# TODO Format Example: operation_id | handler_path | description
[TODO]
operation_id | module:function | Task description here.

[COMPLETED]
```

### Field Definitions

- **operation_id**: Unique identifier for the task (used in logging)
- **handler_path**: Module and function reference (`module:function_name`)
- **description**: Human-readable task description

### Examples

```text
# Simple task
update_readme | tasks:update_readme_handler | Update the main README with latest changes.

# Complex task
generate_api_docs | tasks:generate_api_documentation | Generate comprehensive API documentation for all modules.

# Maintenance task
cleanup_temp_files | tasks:cleanup_temp_handler | Remove temporary files and clean up workspace.
```

## System Monitoring

### Real-time Statistics

The system provides comprehensive real-time monitoring:

```bash
# Show system status
python -c "from droid_manager import show_droid_status; show_droid_status()"

# Get detailed status
python -c "from droid_manager import get_droid_manager; manager = get_droid_manager(); print(manager.get_system_status())"
```

### Metrics Tracked

- **System Information**: Uptime, directory paths, controller status
- **TODO Statistics**: Total, completed, completion rate
- **Session Statistics**: Tasks executed, failed, execution times
- **Controller Metrics**: Internal performance metrics

### Performance Reports

Generate detailed performance reports:

```python
from droid_manager import get_droid_manager

manager = get_droid_manager()
report = manager.get_performance_report()
print(report)
```

## Error Handling and Debugging

### Common Issues

1. **Import Errors**: Ensure proper module structure and paths
2. **Handler Not Found**: Check handler_path format and function existence
3. **Syntax Errors**: Validate TODO format and Python syntax
4. **Permission Errors**: Check file permissions and access rights

### Debugging Steps

1. **Validate TODO Format**:
   ```bash
   python run_todo_droid.py --list
   ```

2. **Check Handler Resolution**:
   ```python
   from run_todo_droid import resolve_handler
   handler = resolve_handler("tasks:your_function")
   ```

3. **Test Individual Components**:
   ```bash
   python -c "from todo import TodoManager; manager = TodoManager('todo_list.txt'); print(manager.load())"
   ```

4. **Enable Debug Logging**:
   ```python
   import logging
   logging.getLogger().setLevel(logging.DEBUG)
   ```

## Integration with Codomyrmex

### Module Integration

Tasks can interact with other Codomyrmex modules:

```python
def integrated_task_handler(*, prompt: str, description: str) -> str:
    """Task that integrates with other Codomyrmex modules."""
    # Import other modules
    from codomyrmex.documentation import generate_quality_report
    from codomyrmex.data_visualization import create_dashboard

    # Execute cross-module operations
    report = generate_quality_report(Path("."))
    dashboard = create_dashboard(report)

    return f"Integrated task completed: {len(dashboard)} charts generated"
```

### Configuration Management

Use Codomyrmex configuration system:

```python
def config_aware_task(*, prompt: str, description: str) -> str:
    """Task that uses Codomyrmex configuration."""
    from codomyrmex.config_management import get_config

    config = get_config()
    api_key = config.get("api_keys", {}).get("openai")

    # Use configuration in task
    return f"Task completed using API key: {bool(api_key)}"
```

## Advanced Features

### Custom Configuration

Create `droid_config.json` for custom settings:

```json
{
  "max_parallel_tasks": 2,
  "safe_mode": true,
  "log_level": "INFO",
  "statistics_enabled": true,
  "auto_save": true
}
```

### Batch Operations

Execute multiple related tasks:

```text
# Documentation update batch
update_all_docs | tasks:update_documentation | Update all module documentation.
generate_api_spec | tasks:generate_api_specs | Generate API specifications.
validate_docs | tasks:validate_documentation | Validate documentation quality.
```

### Conditional Tasks

Use task dependencies:

```python
def dependent_task_handler(*, prompt: str, description: str) -> str:
    """Task that depends on other tasks being completed."""
    # Check if prerequisite tasks are done
    todo_items, completed_items = TodoManager("todo_list.txt").load()

    if "prerequisite_task" not in [item.operation_id for item in completed_items]:
        raise RuntimeError("Prerequisite task not completed")

    # Execute main task
    return "Dependent task completed"
```

## API Reference

### DroidSystemManager

```python
class DroidSystemManager:
    def __init__(droid_dir: Optional[str | Path] = None)
    def get_system_status() -> Dict[str, Any]
    def display_system_status() -> None
    def execute_todos(count: Optional[int] = None, dry_run: bool = False) -> List[TodoItem]
    def validate_todo_format() -> Tuple[bool, List[str]]
    def add_todo(operation_id: str, handler_path: str, description: str) -> bool
    def list_todos(show_completed: bool = False) -> None
    def get_performance_report() -> str
```

### Convenience Functions

```python
def get_droid_manager(droid_dir: Optional[str | Path] = None) -> DroidSystemManager
def show_droid_status(droid_dir: Optional[str | Path] = None) -> None
```

## Troubleshooting

### Task Execution Issues

**Problem**: Handler not found
**Solution**: Check `handler_path` format and function existence in `tasks.py`

**Problem**: Import errors
**Solution**: Ensure proper module structure and relative imports

**Problem**: Permission errors
**Solution**: Check file permissions and directory access

### Performance Issues

**Problem**: Slow task execution
**Solution**: Optimize handler implementations and reduce external dependencies

**Problem**: Memory usage
**Solution**: Implement proper cleanup and resource management

**Problem**: Timeout errors
**Solution**: Break large tasks into smaller chunks or increase timeout limits

## Contributing

### Adding New Task Types

1. Define task handler in `tasks.py`
2. Add comprehensive documentation
3. Include error handling and logging
4. Add tests for the handler
5. Update this documentation

### Improving the System

1. Follow existing code patterns
2. Add comprehensive tests
3. Update documentation
4. Consider backward compatibility
5. Test across different environments

## Examples

### Simple Task

```text
# TODO List Entry
simple_task | tasks:simple_example | Print a hello world message.

# Handler Implementation
def simple_example(*, prompt: str, description: str) -> str:
    """Simple example task."""
    print("Hello, World!")
    return "Simple task completed"
```

### Complex Task

```text
# TODO List Entry
complex_analysis | tasks:complex_analysis_handler | Perform comprehensive code analysis.

# Handler Implementation
def complex_analysis_handler(*, prompt: str, description: str) -> str:
    """Complex analysis task with multiple steps."""
    # Step 1: Analyze codebase
    files = list(Path(".").rglob("*.py"))
    total_lines = sum(len(f.read_text().splitlines()) for f in files)

    # Step 2: Generate report
    report = f"Analysis complete: {len(files)} files, {total_lines} lines"

    # Step 3: Log results
    logger.info(f"Code analysis: {report}", extra={"description": description})

    return report
```

This TODO system provides a powerful, flexible way to automate complex development tasks while maintaining comprehensive monitoring and integration with the broader Codomyrmex ecosystem.
