#!/usr/bin/env python3
"""Run test_project demonstration.

This script demonstrates the full capabilities of test_project,
showcasing integration with codomyrmex modules.

Usage:
    python run_demo.py [target_path]
    
Examples:
    python run_demo.py           # Analyze src/ directory
    python run_demo.py .         # Analyze current directory
    python run_demo.py ../..     # Analyze parent directories
"""

from pathlib import Path
import sys

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent))

from src.main import run_analysis
from src.visualizer import DataVisualizer
from src.reporter import ReportGenerator, ReportConfig
from src.pipeline import AnalysisPipeline


def print_header(text: str) -> None:
    """Print formatted header."""
    print()
    print("=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_section(text: str) -> None:
    """Print section header."""
    print()
    print(f"▸ {text}")
    print("-" * 40)


def demo_analysis(target: Path) -> dict:
    """Demonstrate the analysis functionality."""
    print_section("Running Analysis")
    
    results = run_analysis(target)
    
    summary = results.get("summary", {})
    print(f"  Files analyzed:    {summary.get('total_files', 0)}")
    print(f"  Total lines:       {summary.get('total_lines', 0):,}")
    print(f"  Non-empty lines:   {summary.get('total_non_empty_lines', 0):,}")
    print(f"  Functions:         {summary.get('total_functions', 0)}")
    print(f"  Classes:           {summary.get('total_classes', 0)}")
    print(f"  Issues found:      {summary.get('total_issues', 0)}")
    
    # Show patterns
    patterns = summary.get("patterns_found", {})
    if patterns:
        print()
        print("  Patterns detected:")
        for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    • {pattern.replace('_', ' ').title()}: {count}")
    
    return results


def demo_visualization(results: dict) -> Path:
    """Demonstrate the visualization functionality."""
    print_section("Generating Visualization")
    
    output_dir = Path(__file__).parent / "reports" / "visualizations"
    visualizer = DataVisualizer(output_dir=output_dir)
    
    dashboard_path = visualizer.create_dashboard(results)
    print(f"  Dashboard: {dashboard_path.relative_to(Path(__file__).parent)}")
    
    return dashboard_path


def demo_reporting(results: dict) -> dict:
    """Demonstrate the reporting functionality."""
    print_section("Generating Reports")
    
    output_dir = Path(__file__).parent / "reports" / "output"
    generator = ReportGenerator(output_dir=output_dir)
    
    # Generate all formats
    paths = {}
    for fmt in ["html", "json", "markdown"]:
        config = ReportConfig(
            title="Test Project Analysis Report",
            format=fmt,
            author="Codomyrmex Demo"
        )
        path = generator.generate(results, config)
        paths[fmt] = path
        rel_path = path.relative_to(Path(__file__).parent)
        print(f"  {fmt.upper():10} {rel_path}")
    
    return paths


def demo_pipeline(target: Path) -> None:
    """Demonstrate the pipeline functionality."""
    print_section("Running Full Pipeline")
    
    config_path = Path(__file__).parent / "config" / "workflows.yaml"
    pipeline = AnalysisPipeline(config_path if config_path.exists() else None)
    
    print(f"  Steps: {len(pipeline.steps)}")
    for name, step in pipeline.steps.items():
        deps = f" (after: {', '.join(step.dependencies)})" if step.dependencies else ""
        print(f"    {name}{deps}")
    
    print()
    print("  Executing...")
    result = pipeline.execute(target)
    
    print()
    status_emoji = "✅" if result.is_success else "❌"
    print(f"  Status: {status_emoji} {result.status.value}")
    print(f"  Duration: {result.duration_seconds:.2f} seconds")
    print(f"  Steps completed: {result.steps_completed}/{result.total_steps}")
    
    if result.step_durations:
        print()
        print("  Step timings:")
        for step, duration in result.step_durations.items():
            print(f"    • {step}: {duration:.2f}s")
    
    if result.errors:
        print()
        print("  Errors:")
        for error in result.errors:
            print(f"    ⚠ {error}")


def main() -> int:
    """Run the demonstration."""
    print_header("🚀 Test Project - Codomyrmex Reference Implementation")
    
    # Determine target path
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
    else:
        target = Path(__file__).parent / "src"
    
    print(f"\nTarget: {target.absolute()}")
    
    try:
        # 1. Run analysis
        results = demo_analysis(target)
        
        # 2. Generate visualizations
        dashboard_path = demo_visualization(results)
        
        # 3. Generate reports
        report_paths = demo_reporting(results)
        
        # 4. Run full pipeline
        demo_pipeline(target)
        
        # Summary
        print_header("📁 Generated Outputs")
        print()
        print("  Visualizations:")
        print(f"    • {dashboard_path.relative_to(Path(__file__).parent)}")
        print()
        print("  Reports:")
        for fmt, path in report_paths.items():
            print(f"    • {path.relative_to(Path(__file__).parent)}")
        print()
        print("  Open the HTML files in your browser to view!")
        print()
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
