#!/usr/bin/env python3
"""
Codomyrmex Example Usage Script

This script demonstrates the working modules of Codomyrmex.
Run this after setting up your environment to see it in action!
"""

import sys
from pathlib import Path

# Add the code directory to Python path
code_dir = Path(__file__).parent / "code"
if str(code_dir) not in sys.path:
    sys.path.insert(0, str(code_dir))

def demo_data_visualization():
    """Demonstrate the data visualization module."""
    print("📊 Demonstrating Data Visualization Module...")

    try:
        from data_visualization import create_line_plot, create_bar_chart, create_scatter_plot
        import numpy as np

        # Create sample data
        x = np.linspace(0, 10, 50)
        y1 = np.sin(x)
        y2 = np.cos(x)

        # Create a line plot
        print("Creating line plot...")
        create_line_plot(
            x, y1,
            title="Sine Wave",
            x_label="X Values",
            y_label="sin(x)",
            output_path="example_sine_plot.png",
            show_plot=False
        )
        print("✅ Line plot saved as 'example_sine_plot.png'")

        # Create a bar chart
        categories = ['Python', 'JavaScript', 'Java', 'C++', 'Go']
        values = [85, 72, 65, 58, 45]

        print("Creating bar chart...")
        create_bar_chart(
            categories, values,
            title="Programming Language Popularity",
            x_label="Language",
            y_label="Popularity Score",
            output_path="example_bar_chart.png",
            show_plot=False
        )
        print("✅ Bar chart saved as 'example_bar_chart.png'")

        # Create a scatter plot
        x_scatter = np.random.randn(100)
        y_scatter = np.random.randn(100)

        print("Creating scatter plot...")
        create_scatter_plot(
            x_scatter, y_scatter,
            title="Random Scatter Plot",
            x_label="X Values",
            y_label="Y Values",
            output_path="example_scatter_plot.png",
            show_plot=False
        )
        print("✅ Scatter plot saved as 'example_scatter_plot.png'")

        return True

    except ImportError as e:
        print(f"❌ Data visualization module not available: {e}")
        return False

def demo_logging():
    """Demonstrate the logging and monitoring module."""
    print("📋 Demonstrating Logging & Monitoring Module...")

    try:
        from logging_monitoring.logger_config import setup_logging, get_logger

        # Setup logging
        setup_logging()

        # Get a logger
        logger = get_logger(__name__)

        # Log some messages
        logger.info("This is an info message from the example script")
        logger.warning("This is a warning message")
        logger.error("This is an error message")
        logger.debug("This is a debug message")

        print("✅ Logging system is working! Check console output above.")
        return True

    except ImportError as e:
        print(f"❌ Logging module not available: {e}")
        return False

def demo_static_analysis():
    """Demonstrate static analysis capabilities."""
    print("🔍 Demonstrating Static Analysis Module...")

    try:
        # Test pylint
        import subprocess
        result = subprocess.run([sys.executable, '-m', 'pylint', '--version'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Pylint available: {result.stdout.strip()}")
        else:
            print("❌ Pylint not working properly")

        # Test flake8
        result = subprocess.run([sys.executable, '-m', 'flake8', '--version'],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Flake8 available: {result.stdout.strip()}")
        else:
            print("❌ Flake8 not working properly")

        return True

    except Exception as e:
        print(f"❌ Static analysis tools not available: {e}")
        return False

def main():
    """Run all demonstrations."""
    print("🐜 Codomyrmex Example Usage")
    print("=" * 50)

    demos = [
        ("Logging System", demo_logging),
        ("Data Visualization", demo_data_visualization),
        ("Static Analysis", demo_static_analysis),
    ]

    successful_demos = 0

    for demo_name, demo_func in demos:
        print(f"\n🔬 Running {demo_name} Demo:")
        print("-" * 30)
        if demo_func():
            successful_demos += 1
        print()

    print("=" * 50)
    print(f"Demo Results: {successful_demos}/{len(demos)} modules working")

    if successful_demos == len(demos):
        print("🎉 All demonstrations completed successfully!")
        print("Your Codomyrmex setup is working perfectly!")
    else:
        print("⚠️  Some modules need attention. Check the error messages above.")

    print("\nNext Steps:")
    print("1. Explore the individual module documentation")
    print("2. Check out the CLI: python codomyrmex_cli.py --help")
    print("3. Run tests: pytest testing/")
    print("4. Start building with the working modules!")

if __name__ == '__main__':
    main()




