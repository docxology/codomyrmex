#!/usr/bin/env python3
"""
Context-Aware Usage Pattern Tests for Ollama Integration

This script demonstrates and tests real-world usage patterns for the Ollama
integration. Each pattern shows a common use case with clear documentation
explaining when and why to use that pattern.

All tests use real Ollama API calls (no mocks).

Usage Patterns:
1. Simple Query Pattern - Basic single question/answer
2. Code Generation Pattern - Generating code with specific requirements
3. Analysis with JSON Output Pattern - Structured analysis results
4. Conversation with System Prompt Pattern - Role-based interactions
5. Batch Processing Pattern - Processing multiple items efficiently
6. Configuration-Driven Execution Pattern - Using presets and configs
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from codomyrmex.llm.ollama import OllamaManager, ModelRunner, OutputManager, ConfigManager
from codomyrmex.llm.ollama.model_runner import ExecutionOptions
from codomyrmex.logging_monitoring import setup_logging, get_logger
from codomyrmex.tests.unit.ollama_test_helpers import (
    OllamaTestFixture,
    TestDataGenerator,
    AssertionHelpers,
    ModelAvailabilityChecker
)


def pattern_simple_query(fixture: OllamaTestFixture, model_name: str) -> bool:
    """
    Pattern 1: Simple Query
    
    Purpose: Answer a single question quickly
    Context: Most common use case - asking a question and getting an answer
    When to use: Quick information retrieval, simple Q&A
    Setup: Model and prompt
    Execution: Single execution with default options
    Expected: Quick response with answer
    """
    print("\n" + "="*60)
    print("PATTERN 1: Simple Query")
    print("="*60)
    print("Purpose: Answer a single question quickly")
    print("Context: Most common use case - asking a question and getting an answer")
    print("-"*60)
    
    prompt = "What is machine learning?"
    
    print(f"Prompt: {prompt}")
    print("Executing with default options...")
    
    start_time = time.time()
    result = fixture.runner.run_with_options(
        model_name,
        prompt,
        ExecutionOptions(max_tokens=100),
        save_output=False
    )
    elapsed = time.time() - start_time
    
    if result.success:
        print(f"✅ Success: {len(result.response)} chars in {elapsed:.2f}s")
        print(f"Response preview: {result.response[:100]}...")
        return True
    else:
        print(f"❌ Failed: {result.error_message}")
        return False


def pattern_code_generation(fixture: OllamaTestFixture, model_name: str) -> bool:
    """
    Pattern 2: Code Generation
    
    Purpose: Generate code with specific requirements
    Context: Common for developers - need code snippets or functions
    When to use: Code generation, function implementation, code examples
    Setup: Model with code-focused prompt
    Execution: Lower temperature for more deterministic code
    Expected: Valid code or code-like response
    """
    print("\n" + "="*60)
    print("PATTERN 2: Code Generation")
    print("="*60)
    print("Purpose: Generate code with specific requirements")
    print("Context: Common for developers - need code snippets or functions")
    print("-"*60)
    
    prompt = "Write a Python function to reverse a string without using built-in reverse methods."
    
    # Lower temperature for more deterministic code
    options = ExecutionOptions(
        temperature=0.2,  # Lower for more deterministic code
        max_tokens=200,
        top_p=0.8
    )
    
    print(f"Prompt: {prompt}")
    print(f"Options: temperature={options.temperature}, max_tokens={options.max_tokens}")
    print("Executing...")
    
    result = fixture.runner.run_with_options(
        model_name,
        prompt,
        options,
        save_output=False
    )
    
    if result.success:
        print(f"✅ Success: {len(result.response)} chars")
        print(f"Code preview: {result.response[:150]}...")
        # Check if response looks like code
        if "def" in result.response or "function" in result.response.lower():
            print("✅ Response appears to contain code")
        return True
    else:
        print(f"❌ Failed: {result.error_message}")
        return False


def pattern_analysis_json(fixture: OllamaTestFixture, model_name: str) -> bool:
    """
    Pattern 3: Analysis with JSON Output
    
    Purpose: Get structured analysis results in JSON format
    Context: When you need parseable, structured data
    When to use: Data analysis, structured responses, API integration
    Setup: Model with JSON format requirement
    Execution: format="json" option
    Expected: JSON-formatted response
    """
    print("\n" + "="*60)
    print("PATTERN 3: Analysis with JSON Output")
    print("="*60)
    print("Purpose: Get structured analysis results in JSON format")
    print("Context: When you need parseable, structured data")
    print("-"*60)
    
    prompt = """Analyze the following programming languages and return a JSON object with:
- name: language name
- strengths: array of strengths
- weaknesses: array of weaknesses
- best_use_case: primary use case

Languages: Python, JavaScript, Rust"""
    
    options = ExecutionOptions(
        format="json",
        max_tokens=300,
        temperature=0.5
    )
    
    print("Prompt: Analyze programming languages (JSON output)")
    print(f"Options: format={options.format}, temperature={options.temperature}")
    print("Executing...")
    
    result = fixture.runner.run_with_options(
        model_name,
        prompt,
        options,
        save_output=False
    )
    
    if result.success:
        print(f"✅ Success: {len(result.response)} chars")
        print(f"JSON preview: {result.response[:200]}...")
        
        # Try to parse as JSON
        import json
        try:
            json.loads(result.response)
            print("✅ Response is valid JSON")
        except json.JSONDecodeError:
            print("⚠️  Response may not be valid JSON (model-dependent)")
        
        return True
    else:
        print(f"❌ Failed: {result.error_message}")
        return False


def pattern_conversation_system_prompt(fixture: OllamaTestFixture, model_name: str) -> bool:
    """
    Pattern 4: Conversation with System Prompt
    
    Purpose: Role-based conversation with consistent behavior
    Context: When you need the model to maintain a specific role or persona
    When to use: Chatbots, specialized assistants, role-playing
    Setup: System prompt defining role
    Execution: system_prompt option
    Expected: Response consistent with defined role
    """
    print("\n" + "="*60)
    print("PATTERN 4: Conversation with System Prompt")
    print("="*60)
    print("Purpose: Role-based conversation with consistent behavior")
    print("Context: When you need the model to maintain a specific role or persona")
    print("-"*60)
    
    system_prompt = "You are a helpful coding assistant. Always provide clear, concise explanations with code examples when relevant."
    user_prompt = "How do I iterate over a dictionary in Python?"
    
    options = ExecutionOptions(
        system_prompt=system_prompt,
        max_tokens=200,
        temperature=0.7
    )
    
    print(f"System Prompt: {system_prompt[:50]}...")
    print(f"User Prompt: {user_prompt}")
    print("Executing...")
    
    result = fixture.runner.run_with_options(
        model_name,
        user_prompt,
        options,
        save_output=False
    )
    
    if result.success:
        print(f"✅ Success: {len(result.response)} chars")
        print(f"Response preview: {result.response[:150]}...")
        # Check if response seems helpful/assistant-like
        if any(word in result.response.lower() for word in ["python", "dict", "for", "in"]):
            print("✅ Response appears to address the question")
        return True
    else:
        print(f"❌ Failed: {result.error_message}")
        return False


def pattern_batch_processing(fixture: OllamaTestFixture, model_name: str) -> bool:
    """
    Pattern 5: Batch Processing
    
    Purpose: Process multiple items efficiently
    Context: When you have many similar queries to process
    When to use: Bulk processing, data transformation, batch analysis
    Setup: Multiple prompts
    Execution: Batch execution with concurrency
    Expected: All prompts processed successfully
    """
    print("\n" + "="*60)
    print("PATTERN 5: Batch Processing")
    print("="*60)
    print("Purpose: Process multiple items efficiently")
    print("Context: When you have many similar queries to process")
    print("-"*60)
    
    prompts = [
        "What is Python?",
        "What is JavaScript?",
        "What is Rust?",
    ]
    
    options = ExecutionOptions(
        max_tokens=100,
        temperature=0.7
    )
    
    print(f"Processing {len(prompts)} prompts in batch...")
    print(f"Prompts: {', '.join(prompts)}")
    
    start_time = time.time()
    results = fixture.runner.run_batch(
        model_name,
        prompts,
        options,
        max_concurrent=2
    )
    elapsed = time.time() - start_time
    
    successful = sum(1 for r in results if r.success)
    print(f"✅ Batch complete: {successful}/{len(prompts)} successful in {elapsed:.2f}s")
    
    for i, result in enumerate(results):
        if result.success:
            print(f"  [{i+1}] ✅ {len(result.response)} chars")
        else:
            print(f"  [{i+1}] ❌ {result.error_message}")
    
    return successful == len(prompts)


def pattern_configuration_driven(fixture: OllamaTestFixture, model_name: str) -> bool:
    """
    Pattern 6: Configuration-Driven Execution
    
    Purpose: Use presets and configurations for consistent behavior
    Context: When you want standardized execution settings
    When to use: Production systems, consistent quality, preset workflows
    Setup: ConfigManager with presets
    Execution: Use preset options
    Expected: Execution with preset configuration
    """
    print("\n" + "="*60)
    print("PATTERN 6: Configuration-Driven Execution")
    print("="*60)
    print("Purpose: Use presets and configurations for consistent behavior")
    print("Context: When you want standardized execution settings")
    print("-"*60)
    
    # Get presets
    presets = fixture.config_manager.get_execution_presets()
    
    print(f"Available presets: {list(presets.keys())}")
    
    # Test with 'fast' preset
    fast_options = presets.get('fast')
    if not fast_options:
        print("❌ 'fast' preset not available")
        return False
    
    print(f"Using 'fast' preset: temperature={fast_options.temperature}, max_tokens={fast_options.max_tokens}")
    
    prompt = "Quick explanation of recursion."
    
    result = fixture.runner.run_with_options(
        model_name,
        prompt,
        fast_options,
        save_output=False
    )
    
    if result.success:
        print(f"✅ Success with preset: {len(result.response)} chars in {result.execution_time:.2f}s")
        print(f"Response preview: {result.response[:100]}...")
        return True
    else:
        print(f"❌ Failed: {result.error_message}")
        return False


def main():
    """Run all usage pattern tests."""
    print("="*60)
    print("OLLAMA USAGE PATTERN TESTS")
    print("="*60)
    print("Testing real-world usage patterns with real Ollama API calls")
    print("="*60)
    
    setup_logging()
    logger = get_logger("usage_pattern_tests")
    
    # Initialize
    fixture = OllamaTestFixture()
    model_checker = ModelAvailabilityChecker(fixture.manager)
    
    # Get available model
    model_name = fixture.get_available_model()
    if not model_name:
        print("❌ No models available for testing")
        print("Available models:", model_checker.get_available_models())
        return 1
    
    print(f"\n✅ Using model: {model_name}")
    
    # Run all patterns
    patterns = [
        ("Simple Query", lambda: pattern_simple_query(fixture, model_name)),
        ("Code Generation", lambda: pattern_code_generation(fixture, model_name)),
        ("Analysis JSON", lambda: pattern_analysis_json(fixture, model_name)),
        ("Conversation System Prompt", lambda: pattern_conversation_system_prompt(fixture, model_name)),
        ("Batch Processing", lambda: pattern_batch_processing(fixture, model_name)),
        ("Configuration Driven", lambda: pattern_configuration_driven(fixture, model_name)),
    ]
    
    results = {}
    for pattern_name, pattern_func in patterns:
        try:
            results[pattern_name] = pattern_func()
        except Exception as e:
            print(f"❌ Pattern '{pattern_name}' raised exception: {e}")
            results[pattern_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("PATTERN TEST SUMMARY")
    print("="*60)
    
    total = len(patterns)
    passed = sum(1 for v in results.values() if v)
    
    for pattern_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{pattern_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} patterns passed ({passed/total*100:.1f}%)")
    
    # Cleanup
    fixture.cleanup()
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())


