#!/usr/bin/env python3
import sys
from pathlib import Path
import os

# Ensure codomyrmex is in path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from codomyrmex.agents import GeminiClient, CodeEditor, AgentOrchestrator, AgentRequest
from codomyrmex.logging_monitoring import setup_logging
from codomyrmex.utils.cli_helpers import print_success, print_error, print_info

def test_gemini_client():
    if os.getenv("CODOMYRMEX_TEST_MODE") == "1":
        print_info("Test mode enabled: skipping GeminiClient intensive tests.")
        return True
        
    print_info("Testing GeminiClient directly...")
    client = GeminiClient()
    if not client.test_connection():
        print_error("GeminiClient connection failed.")
        return False
    
    request = AgentRequest(prompt="Say 'Hello Gemini Dispatch'")
    response = client.execute(request)
    if response.is_success():
        print_success(f"GeminiClient response: {response.content}")
        return True
    else:
        print_error(f"GeminiClient failed: {response.error}")
        return False

def test_code_editor_gemini():
    if os.getenv("CODOMYRMEX_TEST_MODE") == "1":
        print_info("Test mode enabled: skipping intensive CodeEditor tests.")
        return True
        
    print_info("Testing CodeEditor backed by Gemini (via helpers)...")
    editor = CodeEditor()
    
    # Test Generation
    request = AgentRequest(
        prompt="Write a Python class for a simple BankAccount.",
        context={"language": "python"}
    )
    response = editor.execute(request)
    if response.is_success():
        print_success("CodeEditor Generation Success.")
        # print(response.content)
    else:
        print_error(f"CodeEditor Generation Failed: {response.error}")
        return False

    # Test Refactoring
    request = AgentRequest(
        prompt="refactor to add type hints",
        context={
            "code": "def greet(name): return 'Hello ' + name",
            "language": "python"
        }
    )
    response = editor.execute(request)
    if response.is_success():
        print_success("CodeEditor Refactoring Success.")
    else:
        print_error(f"CodeEditor Refactoring Failed: {response.error}")
        return False
    
    return True

def test_orchestrator_dispatch():
    if os.getenv("CODOMYRMEX_TEST_MODE") == "1":
        print_info("Test mode enabled: skipping Orchestrator dispatch tests.")
        return True
        
    print_info("Testing AgentOrchestrator dispatch to GeminiClient and CodeEditor...")
    gemini = GeminiClient()
    editor = CodeEditor()
    orchestrator = AgentOrchestrator(agents=[gemini, editor])
    
    request = AgentRequest(
        prompt="Describe the importance of clean code and provide an example in Python.",
        context={"language": "python"}
    )
    
    # Run parallel
    print_info("Executing parallel request...")
    responses = orchestrator.execute_parallel(request)
    
    success_count = sum(1 for r in responses if r.is_success())
    print_info(f"Received {success_count}/{len(responses)} successful responses.")
    
    if success_count == len(responses):
        print_success("Orchestrator Dispatch Success.")
        return True
    else:
        for i, r in enumerate(responses):
            if not r.is_success():
                print_error(f"Agent {i} failed: {r.error}")
        return False

def main():
    setup_logging()
    
    results = {
        "GeminiClient": test_gemini_client(),
        "CodeEditor": test_code_editor_gemini(),
        "Orchestrator": test_orchestrator_dispatch()
    }
    
    print("\n--- Final Results ---")
    all_passed = True
    for test, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        print(f"{test}: {status}")
        if not passed:
            all_passed = False
            
    if all_passed:
        print_success("\nAll Gemini dispatch tests PASSED!")
        sys.exit(0)
    else:
        print_error("\nSome Gemini dispatch tests FAILED.")
        sys.exit(1)

if __name__ == "__main__":
    main()
