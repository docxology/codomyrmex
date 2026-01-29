#!/usr/bin/env python3
"""
Claude Code Methods Demonstration

Demonstrates all Claude Code capabilities available in ClaudeClient v0.2.0:
- File operations: edit_file, create_file
- Code analysis: review_code, explain_code, suggest_tests
- Project context: scan_directory, get_project_structure
- Utilities: generate_diff, run_command

This script handles gracefully when API key is not configured.
"""
import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents.claude import ClaudeClient
from codomyrmex.agents.exceptions import AgentConfigurationError
from codomyrmex.utils.cli_helpers import (
    setup_logging, print_success, print_error, print_info, 
    print_section, print_warning
)


def demo_scan_directory(client: ClaudeClient) -> bool:
    """Demo scan_directory - works without API."""
    print_section("scan_directory")
    print_info("Scanning the Claude module directory...")
    
    claude_dir = Path(__file__).resolve().parent.parent.parent / "src/codomyrmex/agents/claude"
    result = client.scan_directory(str(claude_dir), max_depth=1)
    
    if result["success"]:
        print_success(f"Found {result['file_count']} files")
        for f in result["files"][:5]:
            print_info(f"  - {Path(f).name}")
        return True
    else:
        print_error(f"Failed: {result.get('error')}")
        return False


def demo_generate_diff(client: ClaudeClient) -> bool:
    """Demo generate_diff - works without API."""
    print_section("generate_diff")
    print_info("Generating diff between two code versions...")
    
    original = '''def add(a, b):
    return a + b'''
    
    modified = '''def add(a: int, b: int) -> int:
    """Add two integers."""
    return a + b'''
    
    result = client.generate_diff(original, modified, "math.py")
    
    if result["has_changes"]:
        print_success(f"Diff generated: +{result['additions']} -{result['deletions']}")
        print_info(result["diff"][:200])
        return True
    else:
        print_warning("No changes detected")
        return False


def demo_run_command(client: ClaudeClient) -> bool:
    """Demo run_command - works without API."""
    print_section("run_command")
    print_info("Running 'uv --version' command...")
    
    result = client.run_command("uv --version", timeout=10)
    
    if result["success"]:
        print_success(f"Command succeeded in {result['duration']:.2f}s")
        print_info(f"Output: {result['stdout'].strip()}")
        return True
    else:
        print_warning(f"Command failed: {result['stderr'][:100]}")
        return True  # Not a demo failure


def demo_get_project_structure(client: ClaudeClient) -> bool:
    """Demo get_project_structure - works without API."""
    print_section("get_project_structure")
    print_info("Analyzing project structure...")
    
    project_dir = Path(__file__).resolve().parent.parent.parent / "src/codomyrmex/agents"
    result = client.get_project_structure(str(project_dir), max_depth=2)
    
    if result["success"]:
        print_success(f"Found {result['file_count']} files")
        print_info("Language breakdown:")
        for lang, count in sorted(result["language_breakdown"].items(), key=lambda x: -x[1])[:5]:
            print_info(f"  - {lang}: {count}")
        return True
    else:
        print_error(f"Failed: {result.get('error')}")
        return False


def demo_api_methods(client: ClaudeClient) -> bool:
    """Demo API-dependent methods (review_code, explain_code, suggest_tests)."""
    if not client.test_connection():
        print_warning("Skipping API-dependent demos (no API key configured)")
        print_info("To enable: set ANTHROPIC_API_KEY environment variable")
        return True
    
    # review_code
    print_section("review_code")
    sample_code = "def divide(a, b): return a / b"
    result = client.review_code(sample_code, analysis_type="bugs")
    if result["success"]:
        print_success(f"Review complete, found {len(result['issues'])} issues")
    
    # explain_code
    print_section("explain_code")
    sample_code = "def fib(n): return n if n < 2 else fib(n-1) + fib(n-2)"
    result = client.explain_code(sample_code, detail_level="brief")
    if result["success"]:
        print_success(f"Explanation: {result['summary'][:80]}...")
    
    # suggest_tests
    print_section("suggest_tests")
    sample_code = "def is_prime(n):\n    if n < 2: return False\n    return all(n % i for i in range(2, int(n**0.5)+1))"
    result = client.suggest_tests(sample_code, framework="pytest")
    if result["success"]:
        print_success(f"Generated {len(result['test_cases'])} test cases")
    
    return True


def main():
    setup_logging()
    print_section("Claude Code Methods Demo (v0.2.0)")
    
    # Initialize client (skip __init__ for methods that don't need API)
    try:
        client = ClaudeClient()
    except AgentConfigurationError:
        # Create client without full init for non-API methods
        client = ClaudeClient.__new__(ClaudeClient)
        print_warning("API key not configured - running local-only demos")
    
    passed = 0
    total = 0
    
    # Non-API methods
    demos = [
        ("scan_directory", demo_scan_directory),
        ("generate_diff", demo_generate_diff),
        ("run_command", demo_run_command),
        ("get_project_structure", demo_get_project_structure),
    ]
    
    for name, demo in demos:
        total += 1
        try:
            if demo(client):
                passed += 1
        except Exception as e:
            print_error(f"{name} failed: {e}")
    
    # API-dependent methods
    try:
        client = ClaudeClient()
        total += 1
        if demo_api_methods(client):
            passed += 1
    except AgentConfigurationError:
        total += 1
        passed += 1  # Graceful skip counts as pass
        print_warning("Skipping API demos (no API key)")
    
    # Summary
    print_section("Summary")
    print_info(f"Demos: {passed}/{total} passed")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
