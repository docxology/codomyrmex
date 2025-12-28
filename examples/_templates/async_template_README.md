# Async Template Example

**Template Type**: Async Module Example
**Purpose**: Template for creating examples with async/await patterns and concurrent operations
**Complexity**: Medium to High

## Overview

This template provides a comprehensive structure for creating examples that demonstrate asynchronous functionality using Python's async/await patterns. It includes concurrent task execution, async error handling, performance monitoring, and proper resource management for async operations.

## Template Features

### Core Async Structure
- **Async/Await Patterns**: Full async/await implementation throughout
- **Concurrent Execution**: Multiple async operations running simultaneously
- **Semaphore Management**: Resource control for concurrent operations
- **ThreadPoolExecutor Integration**: CPU-bound operations in threads
- **Async Context Management**: Proper async resource cleanup

### Included Async Functionality
- **Async Setup/Cleanup**: Asynchronous environment preparation
- **Concurrent Task Execution**: Multiple async operations with gather/scatter
- **Async Error Handling**: Timeouts, exception recovery, and concurrent error management
- **Performance Monitoring**: Async-specific performance metrics
- **Resource Management**: Semaphore-based resource control

### Async Demonstration Sections
1. **Async Setup Phase**: Environment preparation with async operations
2. **Concurrent Functionality**: Multiple async operations running in parallel
3. **Async Error Handling**: Fault tolerance and recovery in async contexts
4. **Performance Metrics**: Execution statistics and async efficiency measurements
5. **Async Cleanup Phase**: Resource cleanup with async patterns

## Usage Instructions

### 1. Copy Async Template Files

```bash
# Copy template files to new async module directory
cp examples/_templates/async_template.py examples/your_async_module/example_basic.py
cp examples/_templates/async_template_config.yaml examples/your_async_module/config.yaml
cp examples/_templates/async_template_README.md examples/your_async_module/README.md
```

### 2. Customize Async Module-Specific Code

**Update async imports:**
```python
# Replace template imports with actual async functions
from codomyrmex.{async_module} import (
    {AsyncFunction},
    {AnotherAsyncFunction}
)
```

**Update async class name:**
```python
# Change class name
class {YourModuleName}AsyncExample:
```

**Implement async core methods:**
```python
async def _run_basic_async_example(self) -> Dict[str, Any]:
    """Run basic async functionality."""
    async with self.semaphore:
        # Your async implementation
        await asyncio.sleep(0.1)  # Simulate async operation
        result = await {module}.async_basic_function(self.config)
        return {
            "operation": "basic_async_functionality",
            "status": "success",
            "async_execution": True,
            "data": result
        }

async def _run_concurrent_async_example(self) -> Dict[str, Any]:
    """Run concurrent async operations."""
    # Create concurrent tasks
    tasks = [
        self._async_operation_1(),
        self._async_operation_2(),
        self._async_operation_3()
    ]

    # Execute concurrently
    start_time = time.time()
    results = await asyncio.gather(*tasks, return_exceptions=True)
    execution_time = time.time() - start_time

    return {
        "operation": "concurrent_async_operations",
        "status": "success",
        "execution_time": execution_time,
        "results": results
    }
```

### 3. Update Async Configuration

**Customize async config.yaml:**
```yaml
async:
  max_workers: 8                  # Increase for CPU-bound work
  max_concurrent: 20              # Increase for I/O-bound work
  concurrent_tasks: 10            # Number of concurrent tasks

module:
  name: "your_async_module"       # Change module name
  async_operations: true          # Mark as async module
```

### 4. Update Async Documentation

**Customize README.md:**
```markdown
# Your Async Module Example

## Overview
Demonstrates asynchronous operations in {module_name}.

## Async Features Demonstrated
- Concurrent async operations
- Async error handling and recovery
- Performance benefits of async patterns

## Tested Async Methods
- `async_function()` - Verified in `test_{module}.py::{TestClass}::{test_async_function}`
```

### 5. Update Template Placeholders

**Global search and replace:**
- `{Module Name}` → `Your Async Module Name`
- `{module}` → `your_async_module`
- `{AsyncTestedFunction}` → `actual_async_function_name`
- `{ModuleName}` → `YourAsyncModuleName`

## Async Configuration Options

### Core Async Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `async.max_workers` | integer | `4` | Maximum thread pool workers for CPU-bound tasks |
| `async.max_concurrent` | integer | `10` | Maximum concurrent async operations |
| `async.concurrent_tasks` | integer | `5` | Number of concurrent tasks for examples |
| `async.timeout` | integer | `30` | Async operation timeout in seconds |
| `async.semaphore_limit` | integer | `10` | Semaphore limit for resource control |

### Async Performance Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `performance.track_async_metrics` | boolean | `true` | Track async-specific performance metrics |
| `performance.async_efficiency_gain` | boolean | `true` | Calculate async vs sync performance gains |

### Async Error Handling Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `error_handling.async_error_recovery` | boolean | `true` | Enable async error recovery mechanisms |
| `error_handling.timeout_handling` | boolean | `true` | Handle async operation timeouts |

## Async Output Format

The async template generates a comprehensive JSON result file with async-specific metrics:

```json
{
  "status": "completed",
  "module": "your_async_module",
  "execution_mode": "async",
  "core_functionality": {
    "basic_async_example": {
      "operation": "basic_async_functionality",
      "status": "success",
      "async_execution": true,
      "data": "..."
    },
    "concurrent_async_example": {
      "operation": "concurrent_async_operations",
      "status": "completed",
      "total_tasks": 5,
      "successful_tasks": 5,
      "failed_tasks": 0,
      "execution_time": 0.234,
      "tasks_per_second": 21.37
    },
    "async_integration_example": {
      "operation": "async_integration_scenario",
      "status": "success",
      "phases_completed": 3
    }
  },
  "error_handling": {
    "timeout_handled": true,
    "exception_recovery_handled": true,
    "concurrent_error_handled": true
  },
  "performance": {
    "total_execution_time": 1.456,
    "async_operations_per_second": 15.2,
    "concurrent_tasks_per_second": 75.8,
    "error_rate": 0.0
  },
  "execution_summary": {
    "total_async_operations": 8,
    "concurrent_tasks_executed": 5,
    "errors_encountered": 0,
    "success_rate": 1.0,
    "async_efficiency_gain": "2.3x_vs_sync"
  }
}
```

## Async Extension Points

### Adding Custom Async Operations

```python
async def demonstrate_custom_async_workflow(self) -> Dict[str, Any]:
    """Demonstrate a custom async workflow."""
    print_section("Custom Async Workflow")

    try:
        # Create async tasks with dependencies
        task1 = self._custom_async_operation_1()
        task2 = self._custom_async_operation_2()

        # Execute independent tasks concurrently
        results1, results2 = await asyncio.gather(task1, task2)

        # Execute dependent task
        final_result = await self._custom_async_operation_3(results1, results2)

        print_success("Custom async workflow completed")
        return {"custom_workflow": final_result}
    except Exception as e:
        print_error(f"Custom async workflow failed: {e}")
        return {"error": str(e)}

async def _custom_async_operation_1(self):
    """Custom async operation 1."""
    async with self.semaphore:
        await asyncio.sleep(0.1)
        return {"operation": "custom_1", "result": "data"}

async def _custom_async_operation_2(self):
    """Custom async operation 2."""
    async with self.semaphore:
        await asyncio.sleep(0.15)
        return {"operation": "custom_2", "result": "data"}

async def _custom_async_operation_3(self, result1, result2):
    """Custom async operation 3 (depends on 1 and 2)."""
    async with self.semaphore:
        await asyncio.sleep(0.05)
        return {
            "operation": "custom_3",
            "combined_results": [result1, result2]
        }
```

### Implementing Async Resource Management

```python
class AsyncResourceManager:
    """Async resource manager for proper cleanup."""

    def __init__(self):
        self.resources = []
        self.lock = asyncio.Lock()

    async def acquire_resource(self, resource_type: str):
        """Acquire an async resource."""
        async with self.lock:
            resource = await self._create_async_resource(resource_type)
            self.resources.append(resource)
            return resource

    async def release_resource(self, resource):
        """Release an async resource."""
        async with self.lock:
            if resource in self.resources:
                await self._cleanup_async_resource(resource)
                self.resources.remove(resource)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup_all()

    async def cleanup_all(self):
        """Cleanup all resources asynchronously."""
        cleanup_tasks = [
            self._cleanup_async_resource(resource)
            for resource in self.resources
        ]
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        self.resources.clear()

# Usage in async example
async def demonstrate_async_resource_management(self):
    """Demonstrate async resource management."""
    async with AsyncResourceManager() as manager:
        # Acquire resources
        db_conn = await manager.acquire_resource("database")
        api_client = await manager.acquire_resource("api_client")

        # Use resources
        result = await self._perform_async_operation_with_resources(db_conn, api_client)

        return result
```

### Adding Async Performance Monitoring

```python
from contextlib import asynccontextmanager
from functools import wraps
import psutil

def async_performance_monitor(func):
    """Async decorator to monitor function performance."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss

        # Track async-specific metrics
        async_start = asyncio.get_running_loop().time()

        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss
            async_end = asyncio.get_running_loop().time()

            execution_time = end_time - start_time
            memory_used = end_memory - start_memory
            async_time = async_end - async_start

            logger.info(f"{func.__name__} async performance:", extra={
                'execution_time': execution_time,
                'async_time': async_time,
                'memory_used': memory_used,
                'cpu_percent': psutil.cpu_percent(),
                'efficiency_ratio': async_time / execution_time if execution_time > 0 else 0
            })

    return wrapper

@async_performance_monitor
async def monitored_async_operation(self):
    """Async operation with performance monitoring."""
    # Your async implementation
    await asyncio.sleep(0.1)
    return {"status": "success", "data": "monitored_result"}
```

## Async Best Practices for This Template

### 1. Proper Async/Await Usage
- Always use `async def` for async functions
- Always `await` async calls
- Don't mix sync and async code inappropriately

### 2. Resource Management
- Use semaphores to limit concurrent operations
- Always clean up resources in `finally` blocks
- Use async context managers for resource handling

### 3. Error Handling
- Handle timeouts appropriately
- Use `return_exceptions=True` in `asyncio.gather()`
- Implement proper exception propagation

### 4. Performance Considerations
- Use `asyncio.gather()` for concurrent operations
- Limit concurrent tasks with semaphores
- Monitor for async-specific performance issues

### 5. Testing Async Code
- Use `pytest-asyncio` for async tests
- Test timeout scenarios
- Test concurrent operation handling

## Common Async Patterns

### Concurrent API Calls

```python
async def concurrent_api_calls(self, urls: List[str]) -> List[Dict[str, Any]]:
    """Make concurrent API calls."""
    async def fetch_url(url: str) -> Dict[str, Any]:
        async with self.semaphore:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return {
                        "url": url,
                        "status": response.status,
                        "data": await response.json()
                    }

    # Execute all requests concurrently
    tasks = [fetch_url(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle results
    processed_results = []
    for result in results:
        if isinstance(result, Exception):
            processed_results.append({"error": str(result)})
        else:
            processed_results.append(result)

    return processed_results
```

### Async Database Operations

```python
async def concurrent_database_operations(self, queries: List[str]) -> List[Dict[str, Any]]:
    """Execute concurrent database operations."""
    async def execute_query(query: str) -> Dict[str, Any]:
        async with self.semaphore:
            # Simulate async database operation
            await asyncio.sleep(0.05)
            # result = await db.execute_async_query(query)
            return {
                "query": query,
                "status": "success",
                "rows_affected": 1
            }

    # Execute all queries concurrently
    tasks = [execute_query(query) for query in queries]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return [r for r in results if not isinstance(r, Exception)]
```

### Async File Processing

```python
async def concurrent_file_processing(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
    """Process multiple files concurrently."""
    async def process_file(file_path: Path) -> Dict[str, Any]:
        async with self.semaphore:
            # Run CPU-bound file processing in thread pool
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                self.executor,
                self._process_file_sync,
                file_path
            )

            return {
                "file": str(file_path),
                "status": "success",
                "data": result
            }

    def _process_file_sync(self, file_path: Path) -> Dict[str, Any]:
        """Synchronous file processing (runs in thread pool)."""
        # CPU-intensive file processing here
        with open(file_path, 'r') as f:
            content = f.read()
            # Process content
            return {"size": len(content), "lines": len(content.split('\n'))}

    # Execute all file processing concurrently
    tasks = [process_file(path) for path in file_paths]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    return [r for r in results if not isinstance(r, Exception)]
```

## Troubleshooting Async Template Usage

### Import Errors
```
ModuleNotFoundError: No module named 'aiohttp'
```
**Solution**: Install async dependencies:
```bash
pip install aiohttp asyncio-misc
```

### Runtime Errors
```
RuntimeError: asyncio.run() cannot be called from a running event loop
```
**Solution**: Don't call `asyncio.run()` inside async functions. Restructure your code.

### Performance Issues
```
WARNING: Async operation took longer than expected
```
**Solution**: Check semaphore limits, increase `max_concurrent`, or optimize async operations.

### Deadlock Issues
```
Task was destroyed but it is pending!
```
**Solution**: Ensure all async operations complete before program exit. Use proper cleanup.

### Memory Issues
```
Memory usage growing during async operations
```
**Solution**: Limit concurrent operations, use semaphores, implement proper cleanup.

## When to Use This Template

### Good Use Cases
- I/O-bound operations (network requests, file I/O, database queries)
- Concurrent processing requirements
- Real-time data processing
- API integrations with rate limits
- Background task processing

### When Not to Use
- CPU-bound operations (use sync template with thread pools)
- Simple sequential operations
- Modules without async support
- Single-threaded requirements

## Related Templates

- **Basic Template** (`basic_template.py`): For simple synchronous examples
- **Integration Template** (`integration_template.py`): For multi-module workflows
- **Advanced Template** (`advanced_template.py`): For complex synchronous examples

## Contributing Improvements

To improve this async template:

1. **Add Async Patterns**: Include more async design patterns
2. **Performance Monitoring**: Enhance async performance tracking
3. **Error Handling**: Improve async error recovery mechanisms
4. **Testing**: Add more comprehensive async testing examples
5. **Documentation**: Update with latest async best practices

---

**Status**: Active Async Template
**Last Updated**: December 2025
**Compatibility**: Python 3.8+ with asyncio
**Dependencies**: aiohttp (optional), asyncio-misc (optional)
