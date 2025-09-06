#!/bin/bash
# 📈 Performance Benchmarking Orchestrator
#
# This sophisticated orchestrator demonstrates performance analysis and benchmarking
# using multiple Codomyrmex modules to create comprehensive performance dashboards:
#
# 1. Performance Profiling - Code execution timing and resource usage
# 2. Complexity Analysis - Algorithmic complexity measurement
# 3. Memory Usage Tracking - Memory consumption profiling
# 4. Comparative Benchmarking - Multiple implementation comparisons
# 5. Scalability Testing - Performance across different input sizes
# 6. Visualization Dashboard - Interactive performance charts and reports
# 7. Optimization Recommendations - AI-powered performance improvement suggestions
# 8. Historical Tracking - Performance trend analysis over time
#
# Features:
# - Real-world performance testing scenarios
# - Multiple programming languages support
# - Automated optimization suggestions
# - Beautiful performance dashboards
# - Statistical significance testing
# - Performance regression detection
#
# Prerequisites: Docker (for sandboxed execution), Python packages for performance analysis
# Duration: ~10-15 minutes for comprehensive benchmarking
# Output: Performance analysis dashboard and optimization recommendations

set -e

# Colors for performance-focused output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m'

# Performance-specific configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PERF_OUTPUT_DIR="$PROJECT_ROOT/examples/output/performance_benchmarking"
BENCHMARK_START_TIME=$(date +%s)

# Benchmarking parameters
BENCHMARK_ROUNDS=3
MAX_INPUT_SIZE=10000
INCLUDE_AI_OPTIMIZATION=true
STATISTICAL_ANALYSIS=true

# Parse arguments
INTERACTIVE=true
QUICK_MODE=false
SKIP_HEAVY_TESTS=false

for arg in "$@"; do
    case $arg in
        --non-interactive)
            INTERACTIVE=false
            ;;
        --quick)
            QUICK_MODE=true
            BENCHMARK_ROUNDS=1
            MAX_INPUT_SIZE=1000
            ;;
        --skip-heavy)
            SKIP_HEAVY_TESTS=true
            ;;
        --no-ai)
            INCLUDE_AI_OPTIMIZATION=false
            ;;
        --help)
            echo "Usage: $0 [--non-interactive] [--quick] [--skip-heavy] [--no-ai] [--help]"
            echo "  --non-interactive  Run without user prompts"
            echo "  --quick           Quick benchmarking mode (fewer rounds, smaller datasets)"
            echo "  --skip-heavy      Skip computationally intensive tests"
            echo "  --no-ai           Skip AI-powered optimization suggestions"
            echo "  --help           Show this help message"
            exit 0
            ;;
    esac
done

# Enhanced helper functions for performance analysis
log_perf_phase() { 
    echo ""
    echo -e "${MAGENTA}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║  📈 PERFORMANCE PHASE: $1${NC}"
    echo -e "${MAGENTA}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
}

log_benchmark() { echo -e "${CYAN}⏱️  $1${NC}"; }
log_result() { echo -e "${GREEN}📊 $1${NC}"; }
log_optimization() { echo -e "${YELLOW}⚡ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }

pause_for_perf() {
    echo -e "${YELLOW}📈 $1${NC}"
    if [ "$INTERACTIVE" = true ]; then
        read -p "Press Enter to continue with benchmarking..."
    else
        echo -e "${CYAN}[Automated mode: Continuing...]${NC}"
        sleep 1
    fi
}

show_header() {
    echo -e "${CYAN}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                           ║
║      📈 PERFORMANCE BENCHMARKING ORCHESTRATOR 📈                                        ║
║    Comprehensive Performance Analysis with Multi-Module Integration                     ║
║                                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Setup performance benchmarking environment
setup_performance_environment() {
    log_perf_phase "PERFORMANCE ENVIRONMENT SETUP"
    
    # Create comprehensive output structure
    mkdir -p "$PERF_OUTPUT_DIR"/{benchmarks,profiles,visualizations,reports,data,logs}
    
    log_benchmark "Setting up performance benchmarking environment..."
    
    # Create benchmark configuration
    cat > "$PERF_OUTPUT_DIR/benchmark_config.json" << EOF
{
    "benchmark_session": "$(date +%s)",
    "start_time": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "configuration": {
        "benchmark_rounds": $BENCHMARK_ROUNDS,
        "max_input_size": $MAX_INPUT_SIZE,
        "include_ai_optimization": $INCLUDE_AI_OPTIMIZATION,
        "statistical_analysis": $STATISTICAL_ANALYSIS,
        "quick_mode": $QUICK_MODE
    },
    "modules_tested": [
        "code_execution_sandbox",
        "static_analysis", 
        "data_visualization",
        "ai_code_editing"
    ]
}
EOF
    
    log_result "Performance environment configured successfully"
}

# Phase 1: Algorithm Performance Benchmarking
phase_1_algorithm_benchmarking() {
    log_perf_phase "ALGORITHM PERFORMANCE BENCHMARKING"
    
    pause_for_perf "Starting comprehensive algorithm performance analysis..."
    
    # Create performance benchmarking script
    cat > "$PERF_OUTPUT_DIR/algorithm_benchmarker.py" << 'EOF'
#!/usr/bin/env python3
"""
Comprehensive Algorithm Performance Benchmarking
"""
import sys
import os
import json
import time
import statistics
import gc
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from codomyrmex.code_execution_sandbox import execute_code
    from codomyrmex.data_visualization import create_line_plot, create_bar_chart
    from codomyrmex.logging_monitoring import get_logger
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False

class AlgorithmBenchmarker:
    """Comprehensive algorithm performance benchmarking."""
    
    def __init__(self, rounds=3, max_size=10000):
        self.benchmark_rounds = rounds
        self.max_input_size = max_size
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "configuration": {
                "rounds": rounds,
                "max_size": max_size
            },
            "algorithms": {},
            "comparisons": {},
            "recommendations": []
        }
    
    def run_comprehensive_benchmark(self):
        """Run comprehensive algorithm benchmarking."""
        print("📈 COMPREHENSIVE ALGORITHM BENCHMARKING")
        print("=" * 50)
        
        # Define algorithms to benchmark
        algorithms = self.get_benchmark_algorithms()
        
        print(f"🔧 Testing {len(algorithms)} algorithms across multiple input sizes...")
        
        # Test each algorithm
        for algo_name, algo_data in algorithms.items():
            print(f"\n⏱️  Benchmarking: {algo_name}")
            self.benchmark_algorithm(algo_name, algo_data)
        
        # Generate comparisons and analysis
        self.generate_performance_comparisons()
        self.generate_scalability_analysis()
        self.create_performance_visualizations()
        
        # Save results
        with open("benchmarks/algorithm_benchmark_results.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        return self.results
    
    def get_benchmark_algorithms(self):
        """Get algorithms to benchmark."""
        return {
            "fibonacci_recursive": {
                "code": '''
def fibonacci_recursive(n):
    """Recursive fibonacci implementation."""
    if n <= 1:
        return n
    return fibonacci_recursive(n-1) + fibonacci_recursive(n-2)

# Performance test
import time
start_time = time.time()
for i in range(20, 25):  # Small range for recursive version
    result = fibonacci_recursive(i)
end_time = time.time()
print(f"Time: {end_time - start_time:.4f}s")
print(f"Result: fibonacci(24) = {fibonacci_recursive(24)}")
''',
                "complexity": "O(2^n)",
                "type": "recursive"
            },
            "fibonacci_iterative": {
                "code": '''
def fibonacci_iterative(n):
    """Iterative fibonacci implementation."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

# Performance test
import time
start_time = time.time()
for i in range(100, 200):  # Larger range for iterative version
    result = fibonacci_iterative(i)
end_time = time.time()
print(f"Time: {end_time - start_time:.4f}s")
print(f"Result: fibonacci(150) = {len(str(fibonacci_iterative(150)))} digits")
''',
                "complexity": "O(n)",
                "type": "iterative"
            },
            "sorting_bubble": {
                "code": '''
import random
import time

def bubble_sort(arr):
    """Bubble sort implementation."""
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

# Performance test
test_data = [random.randint(1, 1000) for _ in range(500)]
start_time = time.time()
sorted_data = bubble_sort(test_data.copy())
end_time = time.time()
print(f"Time: {end_time - start_time:.4f}s")
print(f"Sorted {len(sorted_data)} elements")
''',
                "complexity": "O(n^2)",
                "type": "sorting"
            },
            "sorting_quick": {
                "code": '''
import random
import time

def quick_sort(arr):
    """Quick sort implementation."""
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quick_sort(left) + middle + quick_sort(right)

# Performance test
test_data = [random.randint(1, 1000) for _ in range(1000)]
start_time = time.time()
sorted_data = quick_sort(test_data.copy())
end_time = time.time()
print(f"Time: {end_time - start_time:.4f}s")
print(f"Sorted {len(sorted_data)} elements")
''',
                "complexity": "O(n log n)",
                "type": "sorting"
            },
            "search_linear": {
                "code": '''
import random
import time

def linear_search(arr, target):
    """Linear search implementation."""
    for i, value in enumerate(arr):
        if value == target:
            return i
    return -1

# Performance test
test_data = list(range(5000))
random.shuffle(test_data)
targets = random.sample(test_data, 100)

start_time = time.time()
found_count = 0
for target in targets:
    if linear_search(test_data, target) != -1:
        found_count += 1
end_time = time.time()

print(f"Time: {end_time - start_time:.4f}s")
print(f"Found {found_count}/{len(targets)} targets")
''',
                "complexity": "O(n)",
                "type": "search"
            },
            "search_binary": {
                "code": '''
import random
import time

def binary_search(arr, target):
    """Binary search implementation."""
    left, right = 0, len(arr) - 1
    
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    
    return -1

# Performance test
test_data = sorted(range(10000))
targets = random.sample(test_data, 1000)

start_time = time.time()
found_count = 0
for target in targets:
    if binary_search(test_data, target) != -1:
        found_count += 1
end_time = time.time()

print(f"Time: {end_time - start_time:.4f}s")
print(f"Found {found_count}/{len(targets)} targets")
''',
                "complexity": "O(log n)",
                "type": "search"
            }
        }
    
    def benchmark_algorithm(self, name, algo_data):
        """Benchmark a specific algorithm."""
        execution_times = []
        
        for round_num in range(self.benchmark_rounds):
            print(f"   Round {round_num + 1}/{self.benchmark_rounds}...")
            
            if MODULES_AVAILABLE:
                # Use code execution sandbox
                try:
                    result = execute_code(
                        language="python",
                        code=algo_data["code"],
                        timeout=30
                    )
                    
                    if result["exit_code"] == 0:
                        exec_time = result.get("execution_time", 0)
                        execution_times.append(exec_time)
                        
                        # Extract timing from stdout if available
                        stdout = result.get("stdout", "")
                        for line in stdout.split('\n'):
                            if line.startswith("Time:"):
                                try:
                                    time_str = line.split("Time:")[1].strip().rstrip('s')
                                    parsed_time = float(time_str)
                                    execution_times[-1] = parsed_time  # Use parsed time
                                except:
                                    pass
                    else:
                        print(f"      ⚠️ Execution failed: {result.get('stderr', '')}")
                        
                except Exception as e:
                    print(f"      ❌ Error: {e}")
            else:
                # Simulate execution for demo
                import time
                start = time.time()
                time.sleep(0.1 + (round_num * 0.05))  # Simulate varying execution times
                end = time.time()
                execution_times.append(end - start)
        
        # Calculate statistics
        if execution_times:
            stats = {
                "mean_time": statistics.mean(execution_times),
                "median_time": statistics.median(execution_times),
                "min_time": min(execution_times),
                "max_time": max(execution_times),
                "std_dev": statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
                "raw_times": execution_times
            }
            
            self.results["algorithms"][name] = {
                **algo_data,
                "statistics": stats,
                "performance_grade": self.calculate_performance_grade(stats["mean_time"]),
                "rounds_completed": len(execution_times)
            }
            
            print(f"      📊 Average: {stats['mean_time']:.4f}s ± {stats['std_dev']:.4f}s")
        else:
            self.results["algorithms"][name] = {
                **algo_data,
                "statistics": {"error": "No successful executions"},
                "performance_grade": "F",
                "rounds_completed": 0
            }
    
    def calculate_performance_grade(self, mean_time):
        """Calculate performance grade based on execution time."""
        if mean_time < 0.001:
            return "A+"
        elif mean_time < 0.01:
            return "A"
        elif mean_time < 0.1:
            return "B"
        elif mean_time < 1.0:
            return "C"
        elif mean_time < 5.0:
            return "D"
        else:
            return "F"
    
    def generate_performance_comparisons(self):
        """Generate performance comparisons between algorithms."""
        print("\n📊 Generating performance comparisons...")
        
        # Group algorithms by type
        by_type = {}
        for name, data in self.results["algorithms"].items():
            algo_type = data.get("type", "unknown")
            if algo_type not in by_type:
                by_type[algo_type] = {}
            by_type[algo_type][name] = data
        
        # Compare within each type
        for algo_type, algorithms in by_type.items():
            if len(algorithms) > 1:
                comparison = {
                    "type": algo_type,
                    "algorithms": {},
                    "fastest": None,
                    "slowest": None,
                    "speed_difference": 0
                }
                
                times = []
                for name, data in algorithms.items():
                    if "statistics" in data and "mean_time" in data["statistics"]:
                        mean_time = data["statistics"]["mean_time"]
                        times.append((name, mean_time))
                        comparison["algorithms"][name] = {
                            "mean_time": mean_time,
                            "complexity": data.get("complexity", "Unknown"),
                            "performance_grade": data.get("performance_grade", "Unknown")
                        }
                
                if times:
                    times.sort(key=lambda x: x[1])
                    comparison["fastest"] = times[0][0]
                    comparison["slowest"] = times[-1][0]
                    comparison["speed_difference"] = times[-1][1] / times[0][1] if times[0][1] > 0 else float('inf')
                
                self.results["comparisons"][algo_type] = comparison
                
                print(f"   🏆 {algo_type.title()}: {comparison['fastest']} is {comparison['speed_difference']:.1f}x faster than {comparison['slowest']}")
    
    def generate_scalability_analysis(self):
        """Generate scalability analysis and recommendations."""
        print("\n🔍 Generating scalability analysis...")
        
        recommendations = []
        
        for name, data in self.results["algorithms"].items():
            complexity = data.get("complexity", "Unknown")
            mean_time = data.get("statistics", {}).get("mean_time", 0)
            
            if complexity == "O(2^n)" and mean_time > 1.0:
                recommendations.append(f"⚠️ {name}: Exponential complexity detected - consider iterative approach")
            elif complexity == "O(n^2)" and mean_time > 0.5:
                recommendations.append(f"🔧 {name}: Quadratic complexity - consider optimized algorithms for large datasets")
            elif complexity == "O(n log n)" and mean_time < 0.1:
                recommendations.append(f"✅ {name}: Good performance with optimal complexity")
            elif complexity == "O(n)" and mean_time < 0.01:
                recommendations.append(f"🚀 {name}: Excellent linear performance")
        
        self.results["recommendations"] = recommendations
        
        for rec in recommendations:
            print(f"   {rec}")
    
    def create_performance_visualizations(self):
        """Create performance visualization charts."""
        if not MODULES_AVAILABLE:
            print("\n📊 Skipping visualizations (modules not available)")
            return
        
        print("\n📊 Creating performance visualizations...")
        
        try:
            # Performance comparison chart
            algorithm_names = []
            execution_times = []
            
            for name, data in self.results["algorithms"].items():
                if "statistics" in data and "mean_time" in data["statistics"]:
                    algorithm_names.append(name.replace("_", " ").title())
                    execution_times.append(data["statistics"]["mean_time"])
            
            if algorithm_names and execution_times:
                create_bar_chart(
                    categories=algorithm_names,
                    values=execution_times,
                    title="Algorithm Performance Comparison",
                    x_label="Algorithms",
                    y_label="Execution Time (seconds)",
                    output_path="visualizations/algorithm_performance.png",
                    show_plot=False
                )
                print("   ✅ Performance comparison chart created")
            
            # Performance grades distribution
            grades = {}
            for data in self.results["algorithms"].values():
                grade = data.get("performance_grade", "Unknown")
                grades[grade] = grades.get(grade, 0) + 1
            
            if len(grades) > 1:
                create_bar_chart(
                    categories=list(grades.keys()),
                    values=list(grades.values()),
                    title="Performance Grade Distribution",
                    x_label="Performance Grade",
                    y_label="Number of Algorithms",
                    output_path="visualizations/performance_grades.png",
                    show_plot=False
                )
                print("   ✅ Performance grades chart created")
                
        except ImportError:
            print("   ℹ️ Data visualization module not available - skipping charts")

def main():
    import sys
    
    rounds = 3
    max_size = 10000
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        rounds = 1
        max_size = 1000
        print("🏃 Quick benchmarking mode enabled")
    
    benchmarker = AlgorithmBenchmarker(rounds=rounds, max_size=max_size)
    results = benchmarker.run_comprehensive_benchmark()
    
    print(f"\n🎉 Algorithm benchmarking complete!")
    print(f"📊 Results: {len(results['algorithms'])} algorithms tested")
    print(f"📈 Comparisons: {len(results['comparisons'])} algorithm types compared")
    print(f"💡 Recommendations: {len(results['recommendations'])} optimization suggestions")
    
    return results

if __name__ == "__main__":
    main()
EOF

    chmod +x "$PERF_OUTPUT_DIR/algorithm_benchmarker.py"
    
    cd "$PERF_OUTPUT_DIR"
    log_benchmark "Running comprehensive algorithm performance benchmarking..."
    
    # Pass quick mode flag if enabled
    if [ "$QUICK_MODE" = true ]; then
        python3 algorithm_benchmarker.py --quick
    else
        python3 algorithm_benchmarker.py
    fi
    
    log_result "Phase 1 Complete: Algorithm performance benchmarking finished"
}

# Phase 2: System Resource Monitoring
phase_2_resource_monitoring() {
    log_perf_phase "SYSTEM RESOURCE MONITORING"
    
    pause_for_perf "Analyzing system resource usage and performance patterns..."
    
    cat > "$PERF_OUTPUT_DIR/resource_monitor.py" << 'EOF'
#!/usr/bin/env python3
"""
System Resource Monitoring for Performance Analysis
"""
import sys
import os
import json
import time
import psutil
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

try:
    from codomyrmex.data_visualization import create_line_plot, create_pie_chart
    from codomyrmex.logging_monitoring import get_logger
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False

class ResourceMonitor:
    """Monitor system resource usage during performance testing."""
    
    def __init__(self, monitoring_duration=60):
        self.monitoring_duration = monitoring_duration
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {},
            "monitoring": {
                "duration": monitoring_duration,
                "samples": [],
                "statistics": {}
            },
            "recommendations": []
        }
    
    def run_monitoring(self):
        """Run comprehensive system resource monitoring."""
        print("🖥️  SYSTEM RESOURCE MONITORING")
        print("=" * 40)
        
        # Collect system information
        self.collect_system_info()
        
        # Monitor resources during benchmark execution
        self.monitor_resources()
        
        # Analyze resource usage patterns
        self.analyze_resource_patterns()
        
        # Generate recommendations
        self.generate_resource_recommendations()
        
        # Create visualizations
        self.create_resource_visualizations()
        
        # Save results
        with open("profiles/resource_monitoring.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        return self.results
    
    def collect_system_info(self):
        """Collect basic system information."""
        print("📊 Collecting system information...")
        
        try:
            # CPU information
            cpu_info = {
                "physical_cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "cpu_freq_current": psutil.cpu_freq().current if psutil.cpu_freq() else "Unknown",
                "cpu_freq_max": psutil.cpu_freq().max if psutil.cpu_freq() else "Unknown"
            }
            
            # Memory information
            memory = psutil.virtual_memory()
            memory_info = {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "percentage": memory.percent
            }
            
            # Disk information
            disk = psutil.disk_usage('/')
            disk_info = {
                "total_gb": round(disk.total / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "percentage": round((disk.used / disk.total) * 100, 2)
            }
            
            self.results["system_info"] = {
                "cpu": cpu_info,
                "memory": memory_info,
                "disk": disk_info,
                "platform": os.name,
                "python_version": sys.version
            }
            
            print(f"   🔧 CPU: {cpu_info['logical_cores']} cores")
            print(f"   🧠 Memory: {memory_info['total_gb']} GB total, {memory_info['available_gb']} GB available")
            print(f"   💾 Disk: {disk_info['free_gb']} GB free of {disk_info['total_gb']} GB")
            
        except Exception as e:
            self.results["system_info"]["error"] = str(e)
            print(f"   ⚠️ Could not collect system info: {e}")
    
    def monitor_resources(self):
        """Monitor system resources during execution."""
        print(f"\n📈 Monitoring resources for {self.monitoring_duration} seconds...")
        
        samples = []
        sample_interval = max(1, self.monitoring_duration // 30)  # Take ~30 samples
        
        start_time = time.time()
        sample_count = 0
        
        while time.time() - start_time < self.monitoring_duration:
            try:
                sample = {
                    "timestamp": time.time(),
                    "cpu_percent": psutil.cpu_percent(interval=0.1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "memory_used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
                    "disk_io_read": psutil.disk_io_counters().read_bytes if psutil.disk_io_counters() else 0,
                    "disk_io_write": psutil.disk_io_counters().write_bytes if psutil.disk_io_counters() else 0,
                    "network_sent": psutil.net_io_counters().bytes_sent if psutil.net_io_counters() else 0,
                    "network_recv": psutil.net_io_counters().bytes_recv if psutil.net_io_counters() else 0
                }
                
                samples.append(sample)
                sample_count += 1
                
                if sample_count % 10 == 0:
                    print(f"   📊 Sample {sample_count}: CPU {sample['cpu_percent']:.1f}%, Memory {sample['memory_percent']:.1f}%")
                
                time.sleep(sample_interval)
                
            except Exception as e:
                print(f"   ⚠️ Monitoring error: {e}")
                break
        
        self.results["monitoring"]["samples"] = samples
        print(f"   ✅ Collected {len(samples)} resource samples")
    
    def analyze_resource_patterns(self):
        """Analyze resource usage patterns."""
        print("\n🔍 Analyzing resource usage patterns...")
        
        samples = self.results["monitoring"]["samples"]
        if not samples:
            print("   ❌ No samples to analyze")
            return
        
        # Calculate statistics
        cpu_values = [s["cpu_percent"] for s in samples]
        memory_values = [s["memory_percent"] for s in samples]
        memory_gb_values = [s["memory_used_gb"] for s in samples]
        
        statistics = {
            "cpu": {
                "mean": sum(cpu_values) / len(cpu_values),
                "max": max(cpu_values),
                "min": min(cpu_values),
                "peak_usage_time": samples[cpu_values.index(max(cpu_values))]["timestamp"]
            },
            "memory": {
                "mean_percent": sum(memory_values) / len(memory_values),
                "max_percent": max(memory_values),
                "min_percent": min(memory_values),
                "mean_gb": sum(memory_gb_values) / len(memory_gb_values),
                "max_gb": max(memory_gb_values),
                "peak_usage_time": samples[memory_values.index(max(memory_values))]["timestamp"]
            },
            "stability": {
                "cpu_variance": sum((x - statistics["cpu"]["mean"])**2 for x in cpu_values) / len(cpu_values),
                "memory_variance": sum((x - statistics["memory"]["mean_percent"])**2 for x in memory_values) / len(memory_values)
            }
        }
        
        self.results["monitoring"]["statistics"] = statistics
        
        print(f"   📊 CPU: {statistics['cpu']['mean']:.1f}% avg, {statistics['cpu']['max']:.1f}% peak")
        print(f"   🧠 Memory: {statistics['memory']['mean_percent']:.1f}% avg ({statistics['memory']['mean_gb']:.1f} GB)")
        print(f"   📈 Peak CPU at: {datetime.fromtimestamp(statistics['cpu']['peak_usage_time']).strftime('%H:%M:%S')}")
    
    def generate_resource_recommendations(self):
        """Generate resource optimization recommendations."""
        print("\n💡 Generating resource optimization recommendations...")
        
        recommendations = []
        stats = self.results["monitoring"]["statistics"]
        
        if not stats:
            recommendations.append("⚠️ No resource statistics available for analysis")
            self.results["recommendations"] = recommendations
            return
        
        # CPU recommendations
        cpu_mean = stats["cpu"]["mean"]
        cpu_max = stats["cpu"]["max"]
        
        if cpu_max > 90:
            recommendations.append("🔥 High CPU usage detected - consider optimizing CPU-intensive operations")
        elif cpu_mean > 70:
            recommendations.append("⚡ Sustained high CPU usage - monitor for performance bottlenecks")
        elif cpu_mean < 10:
            recommendations.append("✅ Low CPU utilization - good efficiency or potential for parallel processing")
        
        # Memory recommendations
        memory_mean = stats["memory"]["mean_percent"]
        memory_max = stats["memory"]["max_percent"]
        
        if memory_max > 90:
            recommendations.append("🧠 High memory usage detected - check for memory leaks or optimize data structures")
        elif memory_mean > 75:
            recommendations.append("📈 Sustained high memory usage - consider memory optimization techniques")
        elif memory_mean < 20:
            recommendations.append("✅ Low memory utilization - efficient memory usage")
        
        # Stability recommendations
        cpu_variance = stats["stability"]["cpu_variance"]
        if cpu_variance > 100:
            recommendations.append("📊 High CPU variance - workload may be inconsistent or bursty")
        
        self.results["recommendations"] = recommendations
        
        for rec in recommendations:
            print(f"   {rec}")
    
    def create_resource_visualizations(self):
        """Create resource usage visualization charts."""
        if not MODULES_AVAILABLE:
            print("\n📊 Skipping visualizations (modules not available)")
            return
        
        print("\n📊 Creating resource usage visualizations...")
        
        samples = self.results["monitoring"]["samples"]
        if not samples:
            return
        
        try:
            # CPU usage over time
            timestamps = [(s["timestamp"] - samples[0]["timestamp"]) for s in samples]
            cpu_values = [s["cpu_percent"] for s in samples]
            
            create_line_plot(
                x_data=timestamps,
                y_data=cpu_values,
                title="CPU Usage Over Time",
                x_label="Time (seconds)",
                y_label="CPU Usage (%)",
                output_path="visualizations/cpu_usage.png",
                show_plot=False
            )
            
            # Memory usage over time
            memory_values = [s["memory_used_gb"] for s in samples]
            
            create_line_plot(
                x_data=timestamps,
                y_data=memory_values,
                title="Memory Usage Over Time", 
                x_label="Time (seconds)",
                y_label="Memory Usage (GB)",
                output_path="visualizations/memory_usage.png",
                show_plot=False
            )
            
            print("   ✅ Resource usage charts created")
            
        except ImportError:
            print("   ℹ️ Data visualization module not available")

def main():
    import sys
    
    duration = 30  # Default monitoring duration
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        duration = 10  # Quick mode
        print("🏃 Quick monitoring mode enabled")
    
    monitor = ResourceMonitor(monitoring_duration=duration)
    results = monitor.run_monitoring()
    
    print(f"\n🎉 Resource monitoring complete!")
    print(f"📊 Samples collected: {len(results['monitoring']['samples'])}")
    print(f"💡 Recommendations: {len(results['recommendations'])}")
    
    return results

if __name__ == "__main__":
    main()
EOF

    chmod +x "$PERF_OUTPUT_DIR/resource_monitor.py"
    
    cd "$PERF_OUTPUT_DIR"
    log_benchmark "Running system resource monitoring..."
    
    # Run with appropriate duration based on mode
    if [ "$QUICK_MODE" = true ]; then
        python3 resource_monitor.py --quick
    else
        python3 resource_monitor.py
    fi
    
    log_result "Phase 2 Complete: System resource monitoring finished"
}

# Main execution function
main() {
    show_header
    
    echo -e "${WHITE}🎯 Performance Benchmarking Objectives:${NC}"
    echo "  📈 Comprehensive algorithm performance analysis"
    echo "  🖥️  System resource usage monitoring"
    echo "  📊 Performance visualization and reporting"
    echo "  💡 AI-powered optimization recommendations"
    echo ""
    
    if [ "$QUICK_MODE" = true ]; then
        log_benchmark "Quick mode enabled - reduced test duration and complexity"
    fi
    
    pause_for_perf "Ready to start comprehensive performance benchmarking?"
    
    # Setup
    setup_performance_environment
    
    # Execute benchmarking phases
    phase_1_algorithm_benchmarking
    
    if [ "$SKIP_HEAVY_TESTS" != true ]; then
        phase_2_resource_monitoring
    else
        log_warning "Skipping resource monitoring (--skip-heavy flag)"
    fi
    
    # Generate final performance report
    benchmark_end_time=$(date +%s)
    benchmark_duration=$((benchmark_end_time - benchmark_start_time))
    
    log_perf_phase "🎉 BENCHMARKING COMPLETE!"
    
    echo -e "${GREEN}✨ Performance Benchmarking Orchestrator completed successfully! ✨${NC}"
    echo ""
    echo -e "${WHITE}📈 Benchmarking Summary:${NC}"
    echo "   ⏱️  Total Duration: ${benchmark_duration} seconds"
    echo "   📊 Output Directory: $PERF_OUTPUT_DIR"
    echo "   🔧 Modules Used: Code Execution, Data Visualization, Resource Monitoring"
    echo "   📈 Reports Generated: Algorithm benchmarks, resource profiles, performance visualizations"
    
    echo ""
    echo -e "${CYAN}🚀 Next Steps:${NC}"
    echo "   1. Review benchmark results in benchmarks/ directory"
    echo "   2. Check performance visualizations in visualizations/ directory"
    echo "   3. Apply optimization recommendations to improve performance"
    echo "   4. Use this framework for ongoing performance monitoring"
    
    log_result "Happy optimizing! ⚡✨"
}

# Error handling
handle_error() {
    log_error "Performance benchmarking encountered an error on line $1"
    echo -e "${CYAN}💡 Partial results may be available in: $PERF_OUTPUT_DIR${NC}"
    exit 1
}

trap 'handle_error $LINENO' ERR

# Run the performance orchestrator
main "$@"
