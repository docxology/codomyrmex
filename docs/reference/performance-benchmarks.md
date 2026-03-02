# Performance Benchmarks

Detailed benchmark results and testing framework for Codomyrmex modules.

## 📊 Module Performance Benchmarks

### **Data Visualization Module**
```python
# Benchmark: data_visualization performance
import time
import numpy as np
from codomyrmex.data_visualization import create_line_plot, create_bar_chart

def benchmark_data_visualization():
    """Performance benchmarks for visualization module (ACTUAL IMPLEMENTATION)."""
    from codomyrmex.data_visualization.line_plot import create_line_plot
    import numpy as np
    import time

    # Small dataset (1K points) - Interactive tier
    small_x_data = list(np.linspace(0, 10, 1000))
    small_y_data = list(np.sin(np.array(small_x_data)))

    start_time = time.time()
    result = create_line_plot(
        x_data=small_x_data,
        y_data=small_y_data,
        title="Small Dataset Performance Test",
        output_path="perf_test_small.png"
    )
    small_duration = time.time() - start_time

    # Medium dataset (100K points) - Should remain interactive
    medium_x = np.linspace(0, 100, 100000)
    medium_y = np.sin(medium_x) * np.cos(medium_x / 10)

    start_time = time.time()
    result = create_line_plot(medium_x, medium_y, title="Medium Dataset")
    medium_duration = time.time() - start_time

    # Large dataset (1M points) - Batch processing acceptable
    large_x = np.linspace(0, 1000, 1000000)
    large_y = np.sin(large_x) + np.random.normal(0, 0.1, 1000000)

    start_time = time.time()
    result = create_line_plot(large_x, large_y, title="Large Dataset", optimize_large=True)
    large_duration = time.time() - start_time

    return {
        'small_dataset': {'points': 1000, 'duration': small_duration, 'target': '<0.1s'},
        'medium_dataset': {'points': 100000, 'duration': medium_duration, 'target': '<2s'},
        'large_dataset': {'points': 1000000, 'duration': large_duration, 'target': '<10s'}
    }
```

**Expected Performance**:
| Dataset Size | Target Time | Typical Memory | Notes |
|-------------|-------------|----------------|--------|
| 1K points   | < 100ms     | ~10MB         | Interactive response |
| 100K points | < 2s        | ~50MB         | Smooth user experience |
| 1M points   | < 10s       | ~200MB        | Batch processing acceptable |
| 10M+ points | < 60s       | ~1GB          | Background processing + streaming |

### **Static Analysis Module**
```python
# Benchmark: static_analysis performance
from codomyrmex.coding.static_analysis import analyze_codebase, analyze_file
from pathlib import Path

def benchmark_static_analysis():
    """Performance benchmarks for static analysis (ACTUAL IMPLEMENTATION)."""
    from codomyrmex.coding.static_analysis.pyrefly_runner import run_pyrefly_analysis, parse_pyrefly_output
    import time
    import tempfile
    from pathlib import Path

    # Single file analysis
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "sample_module.py"
        test_file.write_text("def sample_function():
    return True
" * 250)  # ~500 lines

        start_time = time.time()
        # Test with actual function signature
        result = run_pyrefly_analysis(
            target_paths=[str(test_file)],
            project_root=temp_dir
        )
        single_duration = time.time() - start_time

    # Small codebase (10-50 files)
    small_codebase = Path("test_data/small_project/")
    start_time = time.time()
    result = analyze_codebase(small_codebase, parallel=True)
    small_duration = time.time() - start_time

    # Medium codebase (100-500 files)
    medium_codebase = Path("test_data/medium_project/")
    start_time = time.time()
    result = analyze_codebase(medium_codebase, parallel=True, cache=True)
    medium_duration = time.time() - start_time

    # Large codebase (1000+ files)
    large_codebase = Path("test_data/large_project/")
    start_time = time.time()
    result = analyze_codebase(
        large_codebase,
        parallel=True,
        cache=True,
        incremental=True
    )
    large_duration = time.time() - start_time

    return {
        'single_file': {'lines': 500, 'duration': single_duration, 'target': '<1s'},
        'small_codebase': {'files': 25, 'duration': small_duration, 'target': '<5s'},
        'medium_codebase': {'files': 250, 'duration': medium_duration, 'target': '<30s'},
        'large_codebase': {'files': 2500, 'duration': large_duration, 'target': '<300s'}
    }
```

**Expected Performance**:
| Codebase Size | Files | Target Time | Memory Usage | Parallelization |
|--------------|-------|-------------|--------------|----------------|
| Single File | 1 | < 1s | ~20MB | N/A |
| Small Project | 10-50 | < 5s | ~50MB | 4 workers |
| Medium Project | 100-500 | < 30s | ~200MB | 8 workers |
| Large Project | 1000+ | < 5min | ~500MB | 16 workers |

### **AI Code Editing Module**
```python
# Benchmark: agents performance
from codomyrmex.agents import enhance_code, generate_code
import asyncio

async def benchmark_agents():
    """Performance benchmarks for AI code editing (async)."""

    # Simple code enhancement
    simple_code = """
def add_numbers(a, b):
    return a + b
"""

    start_time = time.time()
    result = await enhance_code(simple_code, enhancement_type="documentation")
    simple_duration = time.time() - start_time

    # Complex code enhancement
    complex_code = open("test_data/complex_module.py").read()  # ~200 lines

    start_time = time.time()
    result = await enhance_code(
        complex_code,
        enhancement_type="full_optimization",
        include_tests=True
    )
    complex_duration = time.time() - start_time

    # Batch code generation
    specifications = [
        "Create a function to sort a list of dictionaries by a key",
        "Implement a binary search algorithm",
        "Create a class for managing database connections"
    ]

    start_time = time.time()
    results = await asyncio.gather(*[
        generate_code(spec, include_tests=True)
        for spec in specifications
    ])
    batch_duration = time.time() - start_time

    return {
        'simple_enhancement': {'lines': 3, 'duration': simple_duration, 'target': '<5s'},
        'complex_enhancement': {'lines': 200, 'duration': complex_duration, 'target': '<30s'},
        'batch_generation': {'tasks': 3, 'duration': batch_duration, 'target': '<45s'}
    }
```

**Expected Performance** (varies by AI provider):
| Operation Type | Input Size | Target Time | API Calls | Notes |
|----------------|------------|-------------|-----------|--------|
| Simple Enhancement | < 50 lines | < 5s | 1-2 | Documentation, formatting |
| Complex Enhancement | 100-500 lines | < 30s | 3-5 | Optimization, refactoring |
| Code Generation | Per function | < 15s | 1-2 | With tests and docs |
| Batch Operations | 5-10 tasks | < 60s | 5-20 | Parallel processing |

## 🎯 Performance Testing Framework

### **Benchmark Suite**
```python
# benchmark_suite.py - Comprehensive performance testing
import pytest
import time
import numpy as np
from pathlib import Path
import tempfile
import shutil

class PerformanceBenchmark:
    """Base class for performance benchmarks."""

    def __init__(self, name: str, target_time: float, max_memory_mb: int = None):
        self.name = name
        self.target_time = target_time
        self.max_memory_mb = max_memory_mb
        self.results = []

    def run_benchmark(self, iterations: int = 5):
        """Run benchmark multiple times and collect results."""
        for i in range(iterations):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss

            try:
                self.execute_benchmark()
                success = True
            except Exception as e:
                logger.error(f"Benchmark {self.name} failed: {e}")
                success = False

            end_time = time.time()
            end_memory = psutil.Process().memory_info().rss

            self.results.append({
                'iteration': i + 1,
                'duration': end_time - start_time,
                'memory_used': end_memory - start_memory,
                'success': success
            })

        return self.analyze_results()

    def execute_benchmark(self):
        """Override this method in subclasses."""
        raise NotImplementedError

    def analyze_results(self):
        """Analyze benchmark results."""
        successful_runs = [r for r in self.results if r['success']]

        if not successful_runs:
            return {'status': 'failed', 'reason': 'No successful runs'}

        durations = [r['duration'] for r in successful_runs]
        memory_usage = [r['memory_used'] / 1024**2 for r in successful_runs]  # Convert to MB

        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        avg_memory = sum(memory_usage) / len(memory_usage)
        max_memory = max(memory_usage)

        # Performance evaluation
        time_ok = avg_duration <= self.target_time
        memory_ok = self.max_memory_mb is None or max_memory <= self.max_memory_mb

        return {
            'status': 'passed' if time_ok and memory_ok else 'failed',
            'avg_duration': avg_duration,
            'max_duration': max_duration,
            'target_duration': self.target_time,
            'avg_memory_mb': avg_memory,
            'max_memory_mb': max_memory,
            'memory_limit_mb': self.max_memory_mb,
            'success_rate': len(successful_runs) / len(self.results),
            'iterations': len(self.results)
        }

class DataVisualizationBenchmark(PerformanceBenchmark):
    """Benchmark for data visualization performance."""

    def __init__(self, dataset_size: int):
        self.dataset_size = dataset_size

        # Set targets based on dataset size
        if dataset_size <= 1000:
            target_time, max_memory = 0.1, 20
        elif dataset_size <= 100000:
            target_time, max_memory = 2.0, 100
        else:
            target_time, max_memory = 10.0, 500

        super().__init__(
            f"DataVisualization_{dataset_size}_points",
            target_time,
            max_memory
        )

    def execute_benchmark(self):
        """Execute data visualization benchmark."""
        from codomyrmex.data_visualization import create_line_plot

        x = np.linspace(0, 10, self.dataset_size)
        y = np.sin(x) * np.random.random(self.dataset_size)

        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / f"benchmark_{self.dataset_size}.png"
            result = create_line_plot(x, y, f"Benchmark {self.dataset_size}", str(output_path))

            # Verify output
            assert output_path.exists()
            assert result.success

# Run all benchmarks
def run_performance_benchmarks():
    """Run comprehensive performance benchmark suite."""
    benchmarks = [
        # Data visualization benchmarks
        DataVisualizationBenchmark(1000),
        DataVisualizationBenchmark(100000),
        DataVisualizationBenchmark(1000000),

        # Add more benchmark classes...
    ]

    results = {}
    for benchmark in benchmarks:
        logger.info(f"Running benchmark: {benchmark.name}")
        result = benchmark.run_benchmark()
        results[benchmark.name] = result

        status_symbol = "✅" if result['status'] == 'passed' else "❌"
        logger.info(f"{status_symbol} {benchmark.name}: {result['avg_duration']:.2f}s avg")

    return results

# Pytest integration
@pytest.mark.performance
def test_performance_benchmarks():
    """Run performance benchmarks as tests."""
    results = run_performance_benchmarks()

    failed_benchmarks = [
        name for name, result in results.items()
        if result['status'] == 'failed'
    ]

    if failed_benchmarks:
        pytest.fail(f"Performance benchmarks failed: {failed_benchmarks}")
```

## 🔗 Related Documentation

### **Performance Resources**
- **[Production Deployment](../deployment/production.md)**: Production performance optimization
- **[Testing Strategy](../development/testing-strategy.md)**: Performance testing integration
- **[Architecture Overview](../project/architecture.md)**: System design for performance

### **Development Resources**
- **[Development Environment](../development/environment-setup.md)**: Development performance setup
- **[Module System](../modules/overview.md)**: Module architecture and performance considerations

---

**Performance Monitoring Checklist** ✅:
- [ ] Benchmarks established for all critical operations
- [ ] Performance monitoring integrated into CI/CD
- [ ] Production performance dashboards configured
- [ ] Performance regression testing automated
- [ ] Memory leak detection enabled
- [ ] Performance budgets defined and enforced
- [ ] Optimization strategies documented and tested

**Need Performance Help?** Check our [Performance Troubleshooting Guide](../reference/troubleshooting.md#performance-issues) or review module-specific performance documentation.
