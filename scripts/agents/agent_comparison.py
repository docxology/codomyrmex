#!/usr/bin/env python3
"""
Agent Comparison Example

Compares outputs from different agents for the same task.
Useful for evaluating agent capabilities and consistency.
"""
import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents import AgentRequest
from codomyrmex.agents.exceptions import AgentConfigurationError
from codomyrmex.utils.cli_helpers import (
    setup_logging, print_success, print_error, print_info, 
    print_section, print_warning
)


def test_agent(agent_class, agent_name: str, prompt: str) -> dict:
    """Test an agent and return results."""
    try:
        agent = agent_class()
        if hasattr(agent, 'test_connection') and not agent.test_connection():
            return {"status": "skipped", "reason": f"{agent_name} not configured"}
        
        request = AgentRequest(prompt=prompt, context={"language": "python"})
        response = agent.execute(request)
        
        if response.is_success():
            return {
                "status": "success",
                "content": response.content[:200],
                "tokens": response.tokens_used,
            }
        return {"status": "error", "reason": response.error}
    except AgentConfigurationError as e:
        return {"status": "skipped", "reason": str(e)}
    except Exception as e:
        return {"status": "error", "reason": str(e)}


def main():
    setup_logging()
    print_section("Agent Comparison")
    
    prompt = "Write a Python function to check if a number is prime. Include docstring."
    print_info(f"Prompt: {prompt[:50]}...")
    
    # Import agents dynamically
    agents_to_test = []
    
    try:
        from codomyrmex.agents.claude import ClaudeClient
        agents_to_test.append(("Claude", ClaudeClient))
    except ImportError:
        pass
    
    try:
        from codomyrmex.agents import GeminiClient
        agents_to_test.append(("Gemini", GeminiClient))
    except ImportError:
        pass
    
    try:
        from codomyrmex.agents import CodeEditor
        agents_to_test.append(("CodeEditor", CodeEditor))
    except ImportError:
        pass
    
    if not agents_to_test:
        print_warning("No agents available for comparison")
        return 0
    
    results = {}
    for name, agent_class in agents_to_test:
        print_section(f"Testing {name}")
        result = test_agent(agent_class, name, prompt)
        results[name] = result
        
        if result["status"] == "success":
            print_success(f"{name}: Success ({result.get('tokens', '?')} tokens)")
            print_info(f"  Preview: {result['content'][:80]}...")
        elif result["status"] == "skipped":
            print_warning(f"{name}: Skipped - {result['reason']}")
        else:
            print_error(f"{name}: Error - {result['reason']}")
    
    # Summary
    print_section("Comparison Summary")
    success_count = sum(1 for r in results.values() if r["status"] == "success")
    skip_count = sum(1 for r in results.values() if r["status"] == "skipped")
    error_count = sum(1 for r in results.values() if r["status"] == "error")
    
    print_info(f"Total Agents: {len(results)}")
    print_info(f"  Success: {success_count}")
    print_info(f"  Skipped: {skip_count}")
    print_info(f"  Errors: {error_count}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
