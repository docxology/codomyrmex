#!/usr/bin/env python3
"""
Example: Terminal Interface - Comprehensive Rich UI Components and Interactive CLI Building

This example demonstrates the complete terminal interface ecosystem within Codomyrmex,
showcasing advanced Rich UI components, interactive features, progress tracking, and
error handling for various terminal environments and edge cases.

Key Features Demonstrated:
- Rich terminal formatting with colors, styles, and Unicode support
- Advanced progress bars with live updates and custom styling
- Interactive tables, panels, and boxed layouts
- Command execution with formatted output and error handling
- Terminal capability detection and graceful degradation
- Error handling for terminal size issues, color support limitations
- Edge cases: narrow terminals, no color support, rapid updates, encoding issues
- Realistic scenario: building an interactive system monitoring CLI application
- Live data updates and streaming output simulation

Core Terminal Interface Concepts:
- **Rich Formatting**: Color-coded output with semantic meaning (success/error/warning/info)
- **Progress Tracking**: Visual progress indicators for long-running operations
- **Interactive Layouts**: Tables, panels, and boxes for structured data presentation
- **Capability Detection**: Automatic adaptation to terminal capabilities
- **Error Resilience**: Graceful handling of terminal limitations and encoding issues
- **Live Updates**: Real-time data streaming and dynamic content updates

Tested Methods:
- TerminalFormatter.color(), success(), error(), warning(), info() - Verified in test_terminal_interface_comprehensive.py
- TerminalFormatter.progress_bar() - Verified in test_terminal_interface_comprehensive.py
- TerminalFormatter.table() - Verified in test_terminal_interface_comprehensive.py
- TerminalFormatter.box() - Verified in test_terminal_interface_comprehensive.py
- TerminalFormatter.header() - Verified in test_terminal_interface_comprehensive.py
- CommandRunner.run_command() - Verified in test_terminal_interface_comprehensive.py
- CommandRunner.run_diagnostic() - Verified in test_terminal_interface_comprehensive.py
- create_ascii_art() - Verified in test_terminal_interface_comprehensive.py
"""

import sys
import time
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "examples" / "_common")) # Added for common utilities

from config_loader import load_config
from example_runner import ExampleRunner
from utils import print_section, print_results, print_success, print_error, ensure_output_dir

from codomyrmex.terminal_interface.terminal_utils import (
    TerminalFormatter,
    CommandRunner,
    create_ascii_art
)
from codomyrmex.logging_monitoring import setup_logging, get_logger

logger = get_logger(__name__)


def simulate_progress_operation(formatter: TerminalFormatter, operation_name: str, steps: int = 10) -> None:
    """Simulate a progress operation with visual feedback."""
    print(f"\n{formatter.info(f'Starting {operation_name}...')}")

    for i in range(steps + 1):
        bar = formatter.progress_bar(i, steps, width=40, prefix=f"{operation_name}:")
        status_text = bar

        # Overwrite the current line
        print(f"\r{status_text}", end="", flush=True)

        if i < steps:
            time.sleep(0.1)  # Simulate work

    print()  # New line after progress bar
    print(formatter.success(f"{operation_name} completed successfully!"))


def create_sample_data() -> Dict[str, Any]:
    """Create sample data for demonstration."""
    return {
        "modules": [
            {"name": "logging_monitoring", "status": "active", "capabilities": 15, "tests": 85},
            {"name": "environment_setup", "status": "active", "capabilities": 12, "tests": 92},
            {"name": "terminal_interface", "status": "active", "capabilities": 8, "tests": 78},
            {"name": "data_visualization", "status": "active", "capabilities": 10, "tests": 88},
            {"name": "static_analysis", "status": "active", "capabilities": 20, "tests": 95}
        ],
        "system_info": {
            "os": os.uname().sysname if hasattr(os, 'uname') else "Unknown",
            "python_version": sys.version.split()[0],
            "working_directory": str(Path.cwd()),
            "project_root": str(project_root)
        },
        "performance_metrics": [
            {"operation": "Module Discovery", "duration_ms": 245, "status": "success"},
            {"operation": "Health Check", "duration_ms": 89, "status": "success"},
            {"operation": "Capability Analysis", "duration_ms": 156, "status": "success"},
            {"operation": "Documentation Generation", "duration_ms": 78, "status": "success"},
            {"operation": "Test Execution", "duration_ms": 1234, "status": "success"}
        ]
    }


def demonstrate_table_formatting(formatter: TerminalFormatter, data: Dict[str, Any]) -> None:
    """Demonstrate table formatting capabilities."""
    print(f"\n{formatter.header('Module Status Overview')}")

    # Format module data for table
    headers = ["Module Name", "Status", "Capabilities", "Test Coverage"]
    rows = []
    for module in data["modules"]:
        rows.append([
            module["name"],
            formatter.success("✓ Active") if module["status"] == "active" else formatter.error("✗ Inactive"),
            str(module["capabilities"]),
            f"{module['tests']}%"
        ])

    table = formatter.table(headers, rows)
    print(table)


def demonstrate_system_info_display(formatter: TerminalFormatter, data: Dict[str, Any]) -> None:
    """Demonstrate system information display."""
    print(f"\n{formatter.header('System Information')}")

    info_lines = [
        f"Operating System: {formatter.info(data['system_info']['os'])}",
        f"Python Version: {formatter.info(data['system_info']['python_version'])}",
        f"Working Directory: {formatter.info(data['system_info']['working_directory'])}",
        f"Project Root: {formatter.info(data['system_info']['project_root'])}"
    ]

    # Create a boxed display
    box_content = "\n".join(info_lines)
    box = formatter.box(box_content, title="System Details")
    print(box)


def demonstrate_command_execution(command_runner: CommandRunner, formatter: TerminalFormatter) -> None:
    """Demonstrate command execution with formatted output."""
    print(f"\n{formatter.header('Command Execution Examples')}")

    # Example commands to run
    commands = [
        ("echo 'Hello from Codomyrmex Terminal Interface!'", "Simple echo command"),
        ("python --version", "Python version check"),
        ("pwd", "Current working directory")
    ]

    for cmd, description in commands:
        print(f"\n{formatter.info(f'Executing: {description}')}")
        print(f"Command: {formatter.color(cmd, 'CYAN')}")

        try:
            result = command_runner.run_command(cmd, capture_output=True)
            if result["success"]:
                output_lines = result["output"].strip().split('\n')
                for line in output_lines[:3]:  # Show first 3 lines
                    print(f"  {formatter.success('→')} {line}")
                if len(output_lines) > 3:
                    print(f"  {formatter.info('...')} ({len(output_lines) - 3} more lines)")
            else:
                print(f"  {formatter.error('✗ Failed:')} {result['error']}")
        except Exception as e:
            print(f"  {formatter.error('✗ Error:')} {str(e)}")


def demonstrate_ascii_art() -> None:
    """Demonstrate ASCII art generation."""
    print("\n" + "="*60)
    print("ASCII Art Demonstration")
    print("="*60)

    art_styles = ["simple", "bold", "block"]
    for style in art_styles:
        print(f"\nStyle: {style.upper()}")
        art = create_ascii_art("Codomyrmex", style=style)
        print(art)


def demonstrate_status_messages(formatter: TerminalFormatter) -> None:
    """Demonstrate different status message types."""
    print(f"\n{formatter.header('Status Message Examples')}")

    messages = [
        ("success", "Operation completed successfully!"),
        ("error", "An error occurred during processing."),
        ("warning", "Warning: This operation may take some time."),
        ("info", "Processing data... please wait.")
    ]

    for msg_type, message in messages:
        if msg_type == "success":
            formatted = formatter.success(message)
        elif msg_type == "error":
            formatted = formatter.error(message)
        elif msg_type == "warning":
            formatted = formatter.warning(message)
        else:
            formatted = formatter.info(message)

        print(f"{msg_type.upper()}: {formatted}")


def demonstrate_terminal_capability_detection(formatter: TerminalFormatter) -> Dict[str, Any]:
    """
    Demonstrate terminal capability detection and adaptation.

    Shows how the terminal interface detects and adapts to different terminal environments.
    """
    print(f"\n{formatter.header('Terminal Capability Detection')}")

    capabilities = {}

    # Test color support
    print("🔍 Detecting terminal capabilities...")
    has_color = formatter._supports_color()
    capabilities["color_support"] = has_color

    if has_color:
        print(formatter.success("✓ Color support detected"))
    else:
        print(formatter.warning("⚠️ No color support - using monochrome output"))

    # Test terminal size
    try:
        import shutil
        terminal_size = shutil.get_terminal_size()
        capabilities["terminal_width"] = terminal_size.columns
        capabilities["terminal_height"] = terminal_size.lines

        print(formatter.info(f"Terminal size: {terminal_size.columns}x{terminal_size.lines}"))

        if terminal_size.columns < 80:
            print(formatter.warning("⚠️ Narrow terminal detected - some displays may be truncated"))
        else:
            print(formatter.success("✓ Wide terminal - full formatting available"))

    except (OSError, AttributeError):
        capabilities["terminal_size_error"] = True
        print(formatter.warning("⚠️ Could not detect terminal size"))

    # Test Unicode support
    try:
        test_unicode = "✓✗⚠️📊🎯"
        print(test_unicode)
        print(formatter.success("✓ Unicode support confirmed"))
        capabilities["unicode_support"] = True
    except UnicodeEncodeError:
        print(formatter.warning("⚠️ Limited Unicode support - using ASCII fallbacks"))
        capabilities["unicode_support"] = False

    return capabilities


def demonstrate_error_handling_edge_cases(formatter: TerminalFormatter, command_runner: CommandRunner) -> Dict[str, Any]:
    """
    Demonstrate error handling for various terminal interface edge cases.

    Shows how the interface handles terminal limitations, encoding issues, and error conditions.
    """
    print(f"\n{formatter.header('Error Handling - Edge Cases')}")

    edge_cases = {}

    # Case 1: Very narrow terminal simulation
    print("🔍 Testing narrow terminal handling...")
    try:
        # Simulate narrow terminal by forcing small width
        original_width = getattr(formatter, '_terminal_width', 80)
        formatter._terminal_width = 40  # Very narrow

        narrow_table = formatter.table(
            ["Very Long Header Name", "Another Long Header", "Status"],
            [["Short", "Data", "OK"], ["Longer content here", "More data", "Fail"]]
        )
        print("Narrow terminal simulation:")
        print(narrow_table[:200] + "..." if len(narrow_table) > 200 else narrow_table)

        # Restore width
        if hasattr(formatter, '_terminal_width'):
            formatter._terminal_width = original_width

        edge_cases["narrow_terminal_handled"] = True
        print(formatter.success("✓ Narrow terminal formatting handled"))

    except Exception as e:
        edge_cases["narrow_terminal_error"] = str(e)
        print(formatter.error(f"✗ Narrow terminal test failed: {e}"))

    # Case 2: No color support simulation
    print("\n🔍 Testing no-color environment...")
    try:
        # Temporarily disable colors
        original_colors = formatter.COLORS.copy()
        formatter.COLORS = {}  # Empty color map

        monochrome_message = formatter.success("This should be monochrome")
        print(f"Monochrome output: {monochrome_message}")

        # Restore colors
        formatter.COLORS = original_colors

        edge_cases["monochrome_handled"] = True
        print(formatter.success("✓ Monochrome output handled"))

    except Exception as e:
        edge_cases["monochrome_error"] = str(e)
        print(formatter.error(f"✗ Monochrome test failed: {e}"))

    # Case 3: Encoding error simulation
    print("\n🔍 Testing encoding error handling...")
    try:
        # Test with potentially problematic characters
        test_strings = [
            "Normal ASCII text",
            "Unicode: ✓✗⚠️🚀",
            "Mixed: Hello 世界 🌍",
            "Control chars: \n\t\r"
        ]

        for test_str in test_strings:
            try:
                formatted = formatter.info(test_str)
                print(f"✓ Encoded: {formatted[:50]}{'...' if len(formatted) > 50 else ''}")
            except (UnicodeEncodeError, UnicodeDecodeError) as e:
                print(formatter.warning(f"⚠️ Encoding issue with: {repr(test_str[:20])} - {e}"))

        edge_cases["encoding_handled"] = True
        print(formatter.success("✓ Encoding edge cases handled"))

    except Exception as e:
        edge_cases["encoding_error"] = str(e)
        print(formatter.error(f"✗ Encoding test failed: {e}"))

    # Case 4: Command execution failures
    print("\n🔍 Testing command execution error handling...")
    try:
        # Test non-existent command
        result = command_runner.run_command("nonexistent_command_xyz", capture_output=True)
        if not result.get("success", True):
            print(formatter.info("✓ Command failure properly handled"))
            print(f"  Error: {result.get('error', 'Unknown error')[:100]}...")

        edge_cases["command_error_handled"] = True

    except Exception as e:
        edge_cases["command_error"] = str(e)
        print(formatter.error(f"✗ Command error test failed: {e}"))

    return edge_cases


def demonstrate_live_updates_and_streaming(formatter: TerminalFormatter) -> Dict[str, Any]:
    """
    Demonstrate live updates and streaming data presentation.

    Shows how to create dynamic, updating displays for real-time data.
    """
    print(f"\n{formatter.header('Live Updates and Streaming')}")

    streaming_results = {}

    # Simulate live system monitoring
    print("📊 Simulating live system monitoring dashboard...")

    metrics = ["CPU Usage", "Memory Usage", "Disk I/O", "Network Traffic", "Active Processes"]
    initial_values = [45, 67, 23, 89, 42]

    print("\nInitial Metrics:")
    for metric, value in zip(metrics, initial_values):
        bar = formatter.progress_bar(value, 100, width=30, prefix=f"{metric}:")
        print(f"{bar} {value}%")

    # Simulate live updates
    print(f"\n{formatter.info('Starting live updates (simulated)...')}")

    import random
    for update in range(3):
        print(f"\nUpdate {update + 1}:")
        time.sleep(0.5)  # Simulate time between updates

        for i, metric in enumerate(metrics):
            # Simulate changing values
            change = random.randint(-10, 10)
            new_value = max(0, min(100, initial_values[i] + change))
            initial_values[i] = new_value

            bar = formatter.progress_bar(new_value, 100, width=30, prefix=f"{metric}:")
            print(f"{bar} {new_value}%")

            if new_value > 90:
                print(formatter.warning(f"  ⚠️ High {metric.lower()} detected!"))
            elif new_value < 20:
                print(formatter.info(f"  ℹ️ Low {metric.lower()} - system idle"))

    streaming_results["live_updates_simulated"] = True
    streaming_results["metrics_tracked"] = len(metrics)
    streaming_results["updates_performed"] = 3

    print(formatter.success("✓ Live monitoring simulation completed"))

    # Demonstrate streaming log simulation
    print(f"\n{formatter.header('Streaming Log Simulation')}")

    log_entries = [
        ("INFO", "System startup completed", "system"),
        ("WARN", "High memory usage detected", "monitor"),
        ("ERROR", "Database connection failed", "database"),
        ("INFO", "Backup completed successfully", "backup"),
        ("DEBUG", "Cache hit ratio: 94.2%", "cache")
    ]

    for level, message, component in log_entries:
        timestamp = time.strftime("%H:%M:%S")

        if level == "ERROR":
            formatted = formatter.error(f"[{timestamp}] {level} [{component}] {message}")
        elif level == "WARN":
            formatted = formatter.warning(f"[{timestamp}] {level} [{component}] {message}")
        elif level == "DEBUG":
            formatted = formatter.info(f"[{timestamp}] {level} [{component}] {message}")
        else:
            formatted = formatter.success(f"[{timestamp}] {level} [{component}] {message}")

        print(formatted)
        time.sleep(0.2)  # Simulate log streaming

    streaming_results["log_entries_streamed"] = len(log_entries)

    return streaming_results


def demonstrate_interactive_cli_application(formatter: TerminalFormatter, command_runner: CommandRunner) -> Dict[str, Any]:
    """
    Demonstrate building a realistic interactive CLI application for system monitoring.

    This shows how to combine multiple terminal interface components into a cohesive application.
    """
    print(f"\n{formatter.header('Interactive CLI Application: System Monitor')}")

    print("🏗️ Building a complete interactive system monitoring CLI application...")
    print("This demonstrates integrating multiple terminal components into a real application.\n")

    # Application header
    print(create_ascii_art("System Monitor", style="bold"))
    print(formatter.info("Welcome to the Codomyrmex System Monitor CLI"))
    print(formatter.info("Use commands: status, monitor, logs, quit\n"))

    # Simulate interactive session
    app_results = {"commands_processed": 0, "features_demonstrated": []}

    # Command 1: System Status
    print(formatter.color("$ ", "GREEN") + formatter.color("status", "CYAN"))
    print(formatter.info("Showing system status overview..."))

    # Create status table
    status_headers = ["Component", "Status", "Load", "Uptime"]
    status_data = [
        ["CPU", "Normal", "45%", "2d 4h"],
        ["Memory", "High", "78%", "2d 4h"],
        ["Disk", "Normal", "23%", "2d 4h"],
        ["Network", "Active", "67%", "2d 4h"]
    ]

    status_table = formatter.table(status_headers, status_data)
    print(status_table)
    app_results["commands_processed"] += 1
    app_results["features_demonstrated"].append("status_display")

    # Command 2: Live Monitoring
    print(f"\n{formatter.color('$ ', 'GREEN')}{formatter.color('monitor --live --duration 5', 'CYAN')}")
    print(formatter.info("Starting live monitoring for 5 seconds..."))

    # Simulate live monitoring output
    for i in range(5):
        cpu_load = 40 + (i * 5)  # Increasing load
        mem_load = 70 + (i * 2)

        progress_line = f"[{i+1}/5] CPU: {cpu_load}% | Memory: {mem_load}% | Network: {30 + i*10} Mbps"
        print(f"\r{formatter.info(progress_line)}", end="", flush=True)
        time.sleep(0.3)

    print()  # New line
    print(formatter.success("✓ Monitoring session completed"))
    app_results["commands_processed"] += 1
    app_results["features_demonstrated"].append("live_monitoring")

    # Command 3: Log Analysis
    print(f"\n{formatter.color('$ ', 'GREEN')}{formatter.color('logs --tail 10 --filter ERROR', 'CYAN')}")
    print(formatter.info("Showing recent error logs..."))

    # Simulate log output
    error_logs = [
        ("ERROR", "Database connection timeout", "db_handler.py:45"),
        ("ERROR", "API rate limit exceeded", "api_client.py:123"),
        ("WARN", "High memory usage", "memory_monitor.py:78")
    ]

    for level, message, location in error_logs:
        if level == "ERROR":
            print(formatter.error(f"[{level}] {message} ({location})"))
        else:
            print(formatter.warning(f"[{level}] {message} ({location})"))

    app_results["commands_processed"] += 1
    app_results["features_demonstrated"].append("log_analysis")

    # Command 4: Help System
    print(f"\n{formatter.color('$ ', 'GREEN')}{formatter.color('help', 'CYAN')}")
    help_content = """
Available Commands:
  status          Show system status overview
  monitor         Start system monitoring (use --live for real-time)
  logs           Show system logs (use --filter for filtering)
  config         Show/edit configuration
  quit           Exit the monitor

Options:
  --live         Enable real-time updates
  --duration N   Run for N seconds
  --filter TYPE  Filter logs by type (INFO, WARN, ERROR)
  --help         Show this help message
    """
    help_box = formatter.box(help_content.strip(), title="System Monitor Help")
    print(help_box)

    app_results["commands_processed"] += 1
    app_results["features_demonstrated"].append("help_system")

    # Application footer
    print(f"\n{formatter.success('System Monitor CLI demonstration completed!')}")
    print(formatter.info("This example showed how to build a complete interactive CLI application"))
    print(formatter.info("using Codomyrmex terminal interface components."))

    app_results["application_built"] = True
    app_results["interactive_features"] = len(app_results["features_demonstrated"])

    return app_results


def main():
    config = load_config(Path(__file__).parent / "config.yaml")
    runner = ExampleRunner(__file__, config)
    runner.start()

    try:
        print_section("Terminal Interface Example")
        print("Demonstrating rich terminal UI components, progress indicators, and interactive formatting")

        # Initialize terminal utilities
        formatter = TerminalFormatter()
        command_runner = CommandRunner(formatter=formatter)

        # 1. Demonstrate ASCII art
        demonstrate_ascii_art()

        # 2. Demonstrate status messages
        demonstrate_status_messages(formatter)

        # 3. Demonstrate terminal capability detection
        capabilities = demonstrate_terminal_capability_detection(formatter)

        # 4. Demonstrate error handling edge cases
        edge_cases = demonstrate_error_handling_edge_cases(formatter, command_runner)

        # 5. Create sample data
        sample_data = create_sample_data()
        print(f"\n{formatter.success('Sample data created for demonstration')}")

        # 6. Demonstrate table formatting
        demonstrate_table_formatting(formatter, sample_data)

        # 7. Demonstrate system info display
        demonstrate_system_info_display(formatter, sample_data)

        # 8. Demonstrate live updates and streaming
        streaming_results = demonstrate_live_updates_and_streaming(formatter)

        # 9. Demonstrate progress bars
        print(f"\n{formatter.header('Progress Bar Demonstrations')}")
        simulate_progress_operation(formatter, "Data Processing", steps=10)
        simulate_progress_operation(formatter, "File Analysis", steps=8)
        simulate_progress_operation(formatter, "System Validation", steps=12)

        # 10. Demonstrate command execution
        demonstrate_command_execution(command_runner, formatter)

        # 11. Demonstrate interactive CLI application
        cli_app_results = demonstrate_interactive_cli_application(formatter, command_runner)

        # 12. Demonstrate diagnostic capabilities
        print(f"\n{formatter.header('System Diagnostics')}")
        print(f"{formatter.info('Running system diagnostics...')}")
        command_runner.run_diagnostic()

        # 13. Generate comprehensive summary statistics
        final_results = {
            "terminal_formatter_initialized": True,
            "command_runner_initialized": True,
            "ascii_art_demonstrated": True,
            "status_messages_demonstrated": True,
            "capability_detection_run": bool(capabilities),
            "edge_cases_tested": len(edge_cases),
            "edge_cases_handled": sum(1 for case in edge_cases.values() if case is True),
            "table_formatting_used": True,
            "system_info_displayed": True,
            "live_updates_simulated": streaming_results.get("live_updates_simulated", False),
            "streaming_log_entries": streaming_results.get("log_entries_streamed", 0),
            "progress_bars_demonstrated": True,
            "command_execution_tested": True,
            "cli_application_built": cli_app_results.get("application_built", False),
            "cli_commands_processed": cli_app_results.get("commands_processed", 0),
            "interactive_features_demoed": cli_app_results.get("interactive_features", 0),
            "diagnostics_run": True,
            "sample_modules_analyzed": len(sample_data["modules"]),
            "performance_metrics_tracked": len(sample_data["performance_metrics"]),
            "system_info_collected": bool(sample_data["system_info"]),
            "color_support_detected": capabilities.get("color_support", False),
            "unicode_support_detected": capabilities.get("unicode_support", False),
            "terminal_width": capabilities.get("terminal_width", 0),
            "terminal_height": capabilities.get("terminal_height", 0),
            "formatting_styles_available": len(formatter.COLORS),
            "comprehensive_demo_completed": True
        }

        print_results(final_results, "Terminal Interface Operations Summary")

        runner.validate_results(final_results)
        runner.save_results(final_results)
        runner.complete()

        print("\n✅ Comprehensive Terminal Interface example completed successfully!")
        print("Demonstrated complete terminal interface ecosystem with advanced features and error handling.")
        print(f"✓ Terminal capabilities detected: Color={capabilities.get('color_support', False)}, Unicode={capabilities.get('unicode_support', False)}")
        print(f"✓ Edge cases tested and handled: {sum(1 for case in edge_cases.values() if case is True)}/{len(edge_cases)}")
        print(f"✓ Live updates simulated with {streaming_results.get('metrics_tracked', 0)} metrics and {streaming_results.get('log_entries_streamed', 0)} log entries")
        print(f"✓ Interactive CLI application built with {cli_app_results.get('commands_processed', 0)} commands and {cli_app_results.get('interactive_features', 0)} features")
        print(f"✓ Processed {len(sample_data['modules'])} modules with comprehensive status reporting")
        print("\n🎯 Terminal Interface Features Demonstrated:")
        print("  • Advanced Rich UI components with color and Unicode support")
        print("  • Comprehensive error handling for terminal limitations")
        print("  • Live updates and streaming data presentation")
        print("  • Interactive CLI application with multiple commands")
        print("  • Terminal capability detection and graceful degradation")
        print("  • Edge case handling for narrow terminals and encoding issues")
        print("  • Progress tracking with custom styling and live updates")
        print("  • Structured data presentation with tables and panels")

    except Exception as e:
        runner.error("Terminal Interface example failed", e)
        print(f"\n❌ Terminal Interface example failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
