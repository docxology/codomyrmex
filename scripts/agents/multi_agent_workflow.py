#!/usr/bin/env python3
"""
Multi-Agent Orchestration Example

Demonstrates coordinating multiple agents for a complex code review workflow:
1. Use CodeEditor to analyze code
2. Use Claude/Codex (if available) for suggestions
3. Aggregate results using Droid task management
"""
import sys
from pathlib import Path

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents import CodeEditor, ClaudeClient, AgentRequest
from codomyrmex.agents.droid import DroidController, DroidConfig
from codomyrmex.utils.cli_helpers import (
    setup_logging, print_success, print_error, print_info, print_section, print_warning
)


def analyze_with_code_editor(code: str) -> dict:
    """Analyze code structure using CodeEditor."""
    editor = CodeEditor()
    try:
        result = editor.generate_code(
            prompt=f"Analyze this code and provide improvement suggestions:\n{code}",
            context="Focus on code quality and best practices."
        )
        return {"status": "success", "analysis": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def get_claude_review(code: str) -> dict:
    """Get code review from Claude (if available)."""
    client = ClaudeClient()
    if not client.test_connection():
        return {"status": "skipped", "reason": "Claude not configured"}
    
    request = AgentRequest(
        prompt=f"Review this Python code for bugs and improvements:\n{code}",
        context={"task": "code_review"}
    )
    response = client.execute(request)
    
    if response.is_success():
        return {"status": "success", "review": response.content}
    return {"status": "error", "error": response.error}


def main():
    setup_logging()
    print_section("Multi-Agent Code Review Workflow")

    # Sample code to review
    sample_code = '''
def calculate_average(numbers):
    total = 0
    for n in numbers:
        total = total + n
    return total / len(numbers)
'''

    print_info("Sample Code:")
    print(sample_code)

    # Initialize Droid for task coordination
    config = DroidConfig(identifier="review_orchestrator", max_parallel_tasks=3)
    droid = DroidController(config)
    droid.start()

    results = {}

    # Task 1: CodeEditor Analysis
    print_info("\n[Task 1] Running CodeEditor Analysis...")
    try:
        results["code_editor"] = droid.execute_task(
            operation_id="code_editor_analysis",
            handler=analyze_with_code_editor,
            code=sample_code
        )
        print_success(f"CodeEditor: {results['code_editor']['status']}")
    except Exception as e:
        results["code_editor"] = {"status": "error", "error": str(e)}
        print_error(f"CodeEditor failed: {e}")

    # Task 2: Claude Review (optional)
    print_info("\n[Task 2] Running Claude Review...")
    try:
        results["claude"] = droid.execute_task(
            operation_id="claude_review",
            handler=get_claude_review,
            code=sample_code
        )
        if results["claude"]["status"] == "skipped":
            print_warning(f"Claude: {results['claude']['reason']}")
        else:
            print_success(f"Claude: {results['claude']['status']}")
    except Exception as e:
        results["claude"] = {"status": "error", "error": str(e)}
        print_error(f"Claude failed: {e}")

    # Summary
    print_section("Orchestration Summary")
    print_info(f"Droid Metrics: {droid.metrics}")
    for agent, result in results.items():
        print_info(f"  {agent}: {result.get('status', 'unknown')}")

    droid.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
