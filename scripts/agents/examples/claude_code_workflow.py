#!/usr/bin/env python3
"""
Claude Code Workflow Example

Demonstrates a complete Claude Code agentic workflow:
1. Scan project structure
2. Generate code explanation
3. Review code for issues
4. Suggest tests
5. Generate diff for improvements

This represents a typical AI-assisted development workflow.
"""
import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents.claude import ClaudeClient
from codomyrmex.agents.exceptions import AgentConfigurationError
from codomyrmex.utils.cli_helpers import (
    setup_logging, print_success, print_error, print_info, 
    print_section, print_warning
)


def main():
    setup_logging()
    print_section("Claude Code Workflow Demo")
    
    # Sample code to work with
    sample_code = '''
def calculate_discount(price, discount_percent):
    """Calculate discounted price."""
    if discount_percent < 0 or discount_percent > 100:
        return price
    discount = price * (discount_percent / 100)
    return price - discount
'''
    
    # Step 1: Scan project context
    print_section("Step 1: Scan Project Context")
    try:
        client = ClaudeClient.__new__(ClaudeClient)  # No API needed
        project_dir = Path(__file__).resolve().parent.parent.parent.parent / "src/codomyrmex/agents"
        result = client.get_project_structure(str(project_dir), max_depth=2)
        if result["success"]:
            print_success(f"Found {result['file_count']} files in agents module")
            print_info(f"Primary language: Python ({result['language_breakdown'].get('Python', 0)} files)")
        else:
            print_warning(f"Scan failed: {result.get('error')}")
    except Exception as e:
        print_warning(f"Scan error: {e}")
    
    # Check API connection for remaining steps
    print_section("Step 2: Initialize Claude Client")
    try:
        client = ClaudeClient()
        if not client.test_connection():
            print_warning("API not available - showing workflow structure only")
            print_info("Workflow would continue with:")
            print_info("  - Step 3: explain_code() - Generate explanation")
            print_info("  - Step 4: review_code() - Find issues")
            print_info("  - Step 5: suggest_tests() - Generate test cases")
            print_info("  - Step 6: generate_diff() - Show improvements")
            return 0
        print_success("Claude client connected")
    except AgentConfigurationError:
        print_warning("API key not configured. Set ANTHROPIC_API_KEY to enable full workflow.")
        return 0
    
    # Step 3: Explain the code
    print_section("Step 3: Explain Code")
    result = client.explain_code(sample_code, language="python", detail_level="medium")
    if result["success"]:
        print_success("Explanation generated")
        print_info(f"Summary: {result['summary'][:100]}...")
        if result["concepts"]:
            print_info(f"Key concepts: {', '.join(result['concepts'][:3])}")
    else:
        print_error(f"Failed: {result.get('error')}")
    
    # Step 4: Review for issues
    print_section("Step 4: Review Code")
    result = client.review_code(sample_code, language="python", analysis_type="general")
    if result["success"]:
        print_success(f"Review complete: {len(result['issues'])} issues, {len(result['recommendations'])} recommendations")
        for issue in result["issues"][:2]:
            print_info(f"  Issue: {issue[:60]}...")
    else:
        print_error(f"Failed: {result.get('error')}")
    
    # Step 5: Suggest tests
    print_section("Step 5: Suggest Tests")
    result = client.suggest_tests(sample_code, language="python", framework="pytest")
    if result["success"]:
        print_success(f"Generated {len(result['test_cases'])} test cases")
        for case in result["test_cases"][:3]:
            print_info(f"  - {case[:50]}...")
    else:
        print_error(f"Failed: {result.get('error')}")
    
    # Step 6: Generate improvement diff
    print_section("Step 6: Generate Improvement Diff")
    improved_code = '''
def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate discounted price.
    
    Args:
        price: Original price
        discount_percent: Discount percentage (0-100)
    
    Returns:
        Discounted price, or original if invalid percentage
    
    Raises:
        ValueError: If price is negative
    """
    if price < 0:
        raise ValueError("Price cannot be negative")
    if discount_percent < 0 or discount_percent > 100:
        return price
    discount = price * (discount_percent / 100)
    return price - discount
'''
    result = client.generate_diff(sample_code, improved_code, "discount.py")
    print_success(f"Diff: +{result['additions']} lines, -{result['deletions']} lines")
    
    print_section("Workflow Complete")
    print_success("Claude Code workflow demonstrated successfully!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
