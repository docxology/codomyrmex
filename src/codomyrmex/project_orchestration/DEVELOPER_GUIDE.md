# Developer Guide - Project Orchestration

This guide provides comprehensive information for developers working with the Codomyrmex Project Orchestration system.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Architecture Overview](#architecture-overview)
3. [Development Setup](#development-setup)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Performance Considerations](#performance-considerations)
7. [Error Handling](#error-handling)
8. [Logging and Monitoring](#logging-and-monitoring)
9. [Contributing](#contributing)
10. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Prerequisites

- Python 3.8+
- pip or conda for package management
- Git for version control
- IDE with Python support (VS Code, PyCharm, etc.)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/codomyrmex.git
cd codomyrmex

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

### Quick Start

```python
from codomyrmex.project_orchestration import get_orchestration_engine

# Get the orchestration engine
engine = get_orchestration_engine()

# Create a session
session = engine.create_session("My First Session")

# Create a simple workflow
from codomyrmex.project_orchestration import WorkflowStep
steps = [
    WorkflowStep(name="setup", module="environment_setup", action="check_environment"),
    WorkflowStep(name="analyze", module="static_analysis", action="analyze_code", dependencies=["setup"])
]

engine.workflow_manager.create_workflow("my_workflow", steps)

# Execute the workflow
result = engine.execute_workflow_in_session(session.session_id, "my_workflow")
print(f"Workflow result: {result}")
```

---

## Architecture Overview

### Core Components

The Project Orchestration system consists of five main components:

1. **WorkflowManager**: Manages workflow definitions and execution
2. **TaskOrchestrator**: Handles individual task execution with dependencies
3. **ProjectManager**: Manages project lifecycle and templates
4. **ResourceManager**: Handles resource allocation and monitoring
5. **OrchestrationEngine**: Coordinates all components

### Component Relationships

```
OrchestrationEngine
├── WorkflowManager
│   ├── WorkflowStep
│   └── WorkflowExecution
├── TaskOrchestrator
│   ├── Task
│   ├── TaskResult
│   └── ResourceManager
├── ProjectManager
│   ├── Project
│   └── ProjectTemplate
└── ResourceManager
    ├── Resource
    ├── ResourceAllocation
    └── ResourceUsage
```

### Data Flow

1. **Workflow Creation**: Define workflow steps and dependencies
2. **Task Generation**: Convert workflow steps to executable tasks
3. **Resource Allocation**: Allocate required resources for tasks
4. **Execution**: Execute tasks in dependency order
5. **Monitoring**: Track execution status and performance
6. **Cleanup**: Release resources and update project status

---

## Development Setup

### Project Structure

```
src/codomyrmex/project_orchestration/
├── __init__.py
├── workflow_manager.py
├── task_orchestrator.py
├── project_manager.py
├── resource_manager.py
├── orchestration_engine.py
├── mcp_tools.py
├── tests/
│   ├── test_workflow_manager.py
│   ├── test_task_orchestrator.py
│   ├── test_project_manager.py
│   ├── test_resource_manager.py
│   ├── test_orchestration_engine.py
│   └── test_integration.py
├── examples/
│   ├── basic_workflow.py
│   ├── complex_workflow.py
│   └── resource_management.py
└── docs/
    ├── API_SPECIFICATION.md
    ├── COMPREHENSIVE_API_DOCUMENTATION.md
    └── DEVELOPER_GUIDE.md
```

### Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linting
flake8 src/codomyrmex/project_orchestration/
black src/codomyrmex/project_orchestration/

# Generate documentation
sphinx-build docs/ docs/_build/
```

### IDE Configuration

#### VS Code

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

#### PyCharm

1. Configure Python interpreter to use virtual environment
2. Enable pytest as test runner
3. Configure code style to use Black formatter
4. Enable flake8 inspection

---

## Coding Standards

### Python Style Guide

Follow PEP 8 with these additional guidelines:

#### Naming Conventions

```python
# Classes: PascalCase
class WorkflowManager:
    pass

# Functions and variables: snake_case
def create_workflow(name: str) -> bool:
    workflow_id = generate_id()
    return True

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 300

# Private methods: leading underscore
def _validate_workflow(self, workflow: Workflow) -> bool:
    pass
```

#### Type Hints

Always use type hints for function parameters and return values:

```python
from typing import Dict, List, Optional, Any, Union

def process_tasks(
    tasks: List[Task],
    timeout: Optional[int] = None,
    metadata: Dict[str, Any] = None
) -> Dict[str, TaskResult]:
    """Process a list of tasks with optional timeout and metadata."""
    if metadata is None:
        metadata = {}
    
    results = {}
    for task in tasks:
        result = self._execute_task(task, timeout)
        results[task.id] = result
    
    return results
```

#### Docstrings

Use Google-style docstrings:

```python
def create_workflow(self, name: str, steps: List[WorkflowStep], save: bool = True) -> bool:
    """
    Create a new workflow with the specified steps.
    
    This method creates a new workflow definition and optionally persists it to disk.
    The workflow can then be executed using the execute_workflow method.
    
    Args:
        name: Unique name for the workflow. Must be a valid identifier.
        steps: List of workflow steps to execute in order.
            Dependencies between steps are resolved automatically.
        save: Whether to persist the workflow to disk. Defaults to True.
            
    Returns:
        True if workflow was created successfully, False otherwise.
        
    Raises:
        ValueError: If workflow name is empty or invalid.
        OSError: If workflow cannot be saved to disk (when save=True).
        
    Example:
        steps = [
            WorkflowStep(
                name="setup",
                module="environment_setup",
                action="check_environment"
            ),
            WorkflowStep(
                name="analyze",
                module="static_analysis",
                action="analyze_code_quality",
                parameters={"path": "."},
                dependencies=["setup"]
            )
        ]
        
        success = manager.create_workflow("code_analysis", steps)
        if success:
            print("Workflow created successfully")
        else:
            print("Failed to create workflow")
            
    Note:
        - Workflow names must be unique within the manager instance
        - Steps are validated for proper dependency chains
        - Existing workflows with the same name will be overwritten
        - Performance metrics are collected if monitoring is enabled
    """
    # Implementation here
    pass
```

### Error Handling

#### Exception Hierarchy

```python
class OrchestrationError(Exception):
    """Base exception for orchestration errors."""
    pass

class WorkflowError(OrchestrationError):
    """Exception raised for workflow-related errors."""
    pass

class TaskError(OrchestrationError):
    """Exception raised for task-related errors."""
    pass

class ResourceError(OrchestrationError):
    """Exception raised for resource-related errors."""
    pass
```

#### Error Handling Patterns

```python
def execute_workflow(self, name: str) -> WorkflowExecution:
    """Execute a workflow with proper error handling."""
    try:
        if name not in self.workflows:
            raise WorkflowError(f"Workflow '{name}' not found")
        
        execution = WorkflowExecution(workflow_name=name)
        execution.start_time = datetime.now()
        execution.status = WorkflowStatus.RUNNING
        
        # Execute workflow steps
        for step in self.workflows[name]:
            try:
                result = self._execute_step(step)
                execution.results[step.name] = result
            except TaskError as e:
                execution.errors.append(f"Step {step.name} failed: {e}")
                self.logger.error(f"Step {step.name} execution failed: {e}")
        
        execution.end_time = datetime.now()
        execution.status = WorkflowStatus.COMPLETED if not execution.errors else WorkflowStatus.FAILED
        
        return execution
        
    except Exception as e:
        self.logger.error(f"Workflow execution failed: {e}")
        raise WorkflowError(f"Failed to execute workflow '{name}': {e}")
```

### Logging

#### Logger Configuration

```python
import logging
from codomyrmex.logging_monitoring import get_logger

class WorkflowManager:
    def __init__(self):
        self.logger = get_logger(__name__)
    
    def create_workflow(self, name: str, steps: List[WorkflowStep]) -> bool:
        """Create a workflow with proper logging."""
        self.logger.info(f"Creating workflow: {name} with {len(steps)} steps")
        
        try:
            # Validation
            if not name or not name.strip():
                self.logger.error("Workflow name cannot be empty")
                return False
            
            if not steps:
                self.logger.error("Workflow must have at least one step")
                return False
            
            # Create workflow
            self.workflows[name] = steps
            self.logger.info(f"Successfully created workflow: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create workflow {name}: {e}")
            return False
```

#### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General information about program execution
- **WARNING**: Something unexpected happened but program continues
- **ERROR**: A serious problem occurred
- **CRITICAL**: A very serious problem occurred

---

## Testing Guidelines

### Test Structure

```
tests/
├── unit/
│   ├── test_workflow_manager.py
│   ├── test_task_orchestrator.py
│   ├── test_project_manager.py
│   ├── test_resource_manager.py
│   └── test_orchestration_engine.py
├── integration/
│   ├── test_workflow_task_integration.py
│   ├── test_project_workflow_integration.py
│   └── test_resource_task_integration.py
├── performance/
│   ├── test_workflow_performance.py
│   └── test_resource_performance.py
└── fixtures/
    ├── workflow_fixtures.py
    ├── task_fixtures.py
    └── resource_fixtures.py
```

### Unit Testing

#### Test Naming

```python
class TestWorkflowManager:
    """Test cases for WorkflowManager class."""
    
    def test_create_workflow_success(self):
        """Test successful workflow creation."""
        pass
    
    def test_create_workflow_empty_name(self):
        """Test workflow creation with empty name."""
        pass
    
    def test_create_workflow_invalid_dependencies(self):
        """Test workflow creation with invalid dependencies."""
        pass
```

#### Test Fixtures

```python
@pytest.fixture
def workflow_manager():
    """Create a WorkflowManager instance for testing."""
    return WorkflowManager(enable_performance_monitoring=False)

@pytest.fixture
def sample_steps():
    """Create sample workflow steps for testing."""
    return [
        WorkflowStep(
            name="step1",
            module="module1",
            action="action1"
        ),
        WorkflowStep(
            name="step2",
            module="module2",
            action="action2",
            dependencies=["step1"]
        )
    ]
```

#### Test Assertions

```python
def test_workflow_creation(workflow_manager, sample_steps):
    """Test workflow creation with valid steps."""
    result = workflow_manager.create_workflow("test_workflow", sample_steps)
    
    assert result is True
    assert "test_workflow" in workflow_manager.workflows
    assert workflow_manager.workflows["test_workflow"] == sample_steps
```

### Integration Testing

```python
class TestWorkflowTaskIntegration:
    """Integration tests between WorkflowManager and TaskOrchestrator."""
    
    def test_workflow_creates_tasks(self):
        """Test that workflow execution creates and manages tasks."""
        workflow_manager = get_workflow_manager()
        task_orchestrator = get_task_orchestrator()
        
        # Create workflow
        steps = [
            WorkflowStep(name="setup", module="environment_setup", action="check_environment"),
            WorkflowStep(name="analyze", module="static_analysis", action="analyze_code", dependencies=["setup"])
        ]
        
        workflow_manager.create_workflow("integration_test", steps)
        
        # Execute workflow
        async def run_workflow():
            execution = await workflow_manager.execute_workflow("integration_test")
            return execution
        
        execution = asyncio.run(run_workflow())
        
        # Verify execution
        assert execution.status.value in ["completed", "failed"]
        assert len(execution.results) == 2
```

### Performance Testing

```python
@pytest.mark.performance
def test_workflow_performance():
    """Test workflow execution performance."""
    workflow_manager = get_workflow_manager()
    
    # Create large workflow
    steps = [
        WorkflowStep(name=f"step_{i}", module="module", action="action")
        for i in range(100)
    ]
    
    workflow_manager.create_workflow("performance_test", steps)
    
    # Measure execution time
    start_time = time.time()
    execution = asyncio.run(workflow_manager.execute_workflow("performance_test"))
    execution_time = time.time() - start_time
    
    # Assert performance requirements
    assert execution_time < 10.0  # Should complete within 10 seconds
    assert execution.status == WorkflowStatus.COMPLETED
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_workflow_manager.py

# Run with coverage
pytest --cov=src/codomyrmex.project_orchestration --cov-report=html

# Run performance tests
pytest -m performance

# Run integration tests
pytest tests/integration/
```

---

## Performance Considerations

### Memory Management

```python
class WorkflowManager:
    def __init__(self):
        # Use weak references for large objects
        self._workflow_cache = weakref.WeakValueDictionary()
        
    def _cleanup_old_executions(self):
        """Clean up old execution records to prevent memory leaks."""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=24)
        
        executions_to_remove = [
            exec_id for exec_id, execution in self.executions.items()
            if execution.start_time and execution.start_time < cutoff_time
        ]
        
        for exec_id in executions_to_remove:
            del self.executions[exec_id]
```

### Async Operations

```python
async def execute_workflow(self, name: str) -> WorkflowExecution:
    """Execute workflow asynchronously for better performance."""
    execution = WorkflowExecution(workflow_name=name)
    execution.start_time = datetime.now()
    execution.status = WorkflowStatus.RUNNING
    
    try:
        steps = self.workflows[name]
        
        # Execute steps concurrently where possible
        tasks = []
        for step in steps:
            if not step.dependencies:
                task = asyncio.create_task(self._execute_step(step))
                tasks.append((step, task))
        
        # Wait for independent steps to complete
        for step, task in tasks:
            result = await task
            execution.results[step.name] = result
        
        execution.end_time = datetime.now()
        execution.status = WorkflowStatus.COMPLETED
        
    except Exception as e:
        execution.status = WorkflowStatus.FAILED
        execution.errors.append(str(e))
    
    return execution
```

### Resource Optimization

```python
class ResourceManager:
    def __init__(self):
        # Use efficient data structures
        self._resource_locks = {}
        self._allocation_cache = {}
        
    def _optimize_allocations(self):
        """Optimize resource allocations for better performance."""
        # Implement allocation optimization logic
        pass
```

---

## Error Handling

### Custom Exceptions

```python
class OrchestrationError(Exception):
    """Base exception for orchestration errors."""
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.error_code = error_code
        self.timestamp = datetime.now()

class WorkflowError(OrchestrationError):
    """Exception raised for workflow-related errors."""
    pass

class TaskError(OrchestrationError):
    """Exception raised for task-related errors."""
    pass

class ResourceError(OrchestrationError):
    """Exception raised for resource-related errors."""
    pass
```

### Error Recovery

```python
def execute_workflow_with_retry(self, name: str, max_retries: int = 3) -> WorkflowExecution:
    """Execute workflow with automatic retry on failure."""
    for attempt in range(max_retries):
        try:
            return self.execute_workflow(name)
        except WorkflowError as e:
            if attempt == max_retries - 1:
                raise
            self.logger.warning(f"Workflow execution failed (attempt {attempt + 1}): {e}")
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

---

## Logging and Monitoring

### Structured Logging

```python
import structlog

logger = structlog.get_logger(__name__)

def create_workflow(self, name: str, steps: List[WorkflowStep]) -> bool:
    """Create workflow with structured logging."""
    logger.info(
        "Creating workflow",
        workflow_name=name,
        step_count=len(steps),
        step_names=[step.name for step in steps]
    )
    
    try:
        # Implementation
        logger.info("Workflow created successfully", workflow_name=name)
        return True
    except Exception as e:
        logger.error(
            "Failed to create workflow",
            workflow_name=name,
            error=str(e),
            error_type=type(e).__name__
        )
        return False
```

### Performance Monitoring

```python
from codomyrmex.performance import monitor_performance

class WorkflowManager:
    @monitor_performance("workflow_create")
    def create_workflow(self, name: str, steps: List[WorkflowStep]) -> bool:
        """Create workflow with performance monitoring."""
        # Implementation
        pass
    
    @monitor_performance("workflow_execute")
    async def execute_workflow(self, name: str) -> WorkflowExecution:
        """Execute workflow with performance monitoring."""
        # Implementation
        pass
```

---

## Contributing

### Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass: `pytest`
6. Run linting: `flake8` and `black`
7. Commit your changes: `git commit -m "Add amazing feature"`
8. Push to the branch: `git push origin feature/amazing-feature`
9. Open a Pull Request

### Code Review Checklist

- [ ] Code follows PEP 8 style guidelines
- [ ] All functions have proper type hints
- [ ] All functions have comprehensive docstrings
- [ ] All tests pass
- [ ] New code has appropriate test coverage
- [ ] No hardcoded values or magic numbers
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate
- [ ] Performance considerations are addressed

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build process or auxiliary tool changes

Examples:
```
feat(workflow): add workflow retry mechanism
fix(task): resolve task dependency circular reference
docs(api): update API documentation
test(integration): add workflow-task integration tests
```

---

## Troubleshooting

### Common Issues

#### Import Errors

```python
# Problem: ModuleNotFoundError
from codomyrmex.project_orchestration import WorkflowManager

# Solution: Ensure proper Python path
import sys
sys.path.insert(0, '/path/to/codomyrmex/src')
```

#### Async/Await Issues

```python
# Problem: RuntimeError: This event loop is already running
async def main():
    execution = await workflow_manager.execute_workflow("test")

# Solution: Use asyncio.run() in main thread
def main():
    asyncio.run(workflow_manager.execute_workflow("test"))
```

#### Resource Allocation Issues

```python
# Problem: Resource allocation fails
allocation = resource_manager.allocate_resource("cpu_1", "task_1", 150.0)

# Solution: Check available capacity first
available = resource_manager.get_available_capacity("cpu_1")
if available >= 150.0:
    allocation = resource_manager.allocate_resource("cpu_1", "task_1", 150.0)
else:
    print(f"Insufficient capacity. Available: {available}")
```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or use the Codomyrmex logger
from codomyrmex.logging_monitoring import get_logger
logger = get_logger(__name__)
logger.setLevel(logging.DEBUG)
```

### Performance Profiling

```python
import cProfile
import pstats

def profile_workflow_execution():
    """Profile workflow execution performance."""
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Execute workflow
    execution = asyncio.run(workflow_manager.execute_workflow("test"))
    
    profiler.disable()
    
    # Print profiling results
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions
```

### Memory Profiling

```python
from memory_profiler import profile

@profile
def create_large_workflow():
    """Profile memory usage for large workflow creation."""
    steps = [WorkflowStep(name=f"step_{i}", module="module", action="action") for i in range(1000)]
    workflow_manager.create_workflow("large_workflow", steps)
```

This developer guide provides comprehensive information for working with the Codomyrmex Project Orchestration system. For additional help, refer to the API documentation or create an issue in the repository.

## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../docs/README.md)
- **Home**: [Root README](../../../README.md)
