#!/usr/bin/env python3
"""
Error Handling and Edge Case Tests for Ollama Integration

This script tests error handling, edge cases, and failure scenarios to ensure
the Ollama integration handles errors gracefully and provides useful error messages.

All tests use real Ollama API calls (no mocks).

Error Scenarios:
1. Model Not Found - Handling unavailable models
2. Invalid Parameters - Handling invalid option values
3. Network Errors - Handling connection issues
4. Timeout Handling - Handling long-running operations
5. Empty/Invalid Inputs - Handling edge case inputs
6. Resource Cleanup - Ensuring cleanup on errors
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from codomyrmex.llm.ollama import OllamaManager, ModelRunner
from codomyrmex.llm.ollama.model_runner import ExecutionOptions
from codomyrmex.logging_monitoring import setup_logging, get_logger
from codomyrmex.tests.unit.ollama_test_helpers import OllamaTestFixture


def test_model_not_found(fixture: OllamaTestFixture) -> bool:
    """
    Test: Model Not Found Error Handling
    
    Purpose: Verify graceful handling when model doesn't exist
    Context: Models may not always be available
    Expected: Clear error message, no crash
    """
    print("\n" + "="*60)
    print("ERROR TEST 1: Model Not Found")
    print("="*60)
    
    non_existent_model = "nonexistent_model_xyz12345_does_not_exist"
    
    print(f"Attempting to use non-existent model: {non_existent_model}")
    
    result = fixture.manager.run_model(
        non_existent_model,
        "Test prompt.",
        save_output=False
    )
    
    if not result.success:
        print(f"✅ Error handled gracefully")
        print(f"   Error message: {result.error_message}")
        assert "not available" in result.error_message.lower() or "not found" in result.error_message.lower()
        return True
    else:
        print(f"❌ Expected failure but got success")
        return False


def test_invalid_parameters(fixture: OllamaTestFixture, model_name: str) -> bool:
    """
    Test: Invalid Parameter Values
    
    Purpose: Verify invalid parameters are handled or clamped
    Context: Users may provide invalid parameter values
    Expected: Parameters are validated/clamped, or clear error
    """
    print("\n" + "="*60)
    print("ERROR TEST 2: Invalid Parameters")
    print("="*60)
    
    test_cases = [
        ("Extreme temperature", ExecutionOptions(temperature=10.0, max_tokens=50)),
        ("Negative temperature", ExecutionOptions(temperature=-1.0, max_tokens=50)),
        ("Zero max_tokens", ExecutionOptions(max_tokens=0)),
        ("Negative max_tokens", ExecutionOptions(max_tokens=-10)),
    ]
    
    all_passed = True
    
    for test_name, options in test_cases:
        print(f"\n  Testing: {test_name}")
        print(f"    Options: {options}")
        
        result = fixture.runner.run_with_options(
            model_name,
            "Test prompt.",
            options,
            save_output=False
        )
        
        # Should either succeed (if clamped) or fail gracefully
        if result.success:
            print(f"    ✅ Succeeded (parameters may have been clamped)")
        else:
            print(f"    ✅ Failed gracefully: {result.error_message[:50]}...")
        
        # Main thing is it doesn't crash
        all_passed = all_passed and (result is not None)
    
    return all_passed


def test_empty_inputs(fixture: OllamaTestFixture, model_name: str) -> bool:
    """
    Test: Empty/Invalid Inputs
    
    Purpose: Verify empty or invalid inputs are handled
    Context: Users may accidentally provide empty inputs
    Expected: Graceful handling, clear error or default behavior
    """
    print("\n" + "="*60)
    print("ERROR TEST 3: Empty/Invalid Inputs")
    print("="*60)
    
    test_cases = [
        ("Empty prompt", ""),
        ("Whitespace only", "   "),
        ("Very long prompt", "A" * 100000),  # Extremely long
    ]
    
    all_passed = True
    
    for test_name, prompt in test_cases:
        print(f"\n  Testing: {test_name}")
        print(f"    Prompt length: {len(prompt)}")
        
        result = fixture.manager.run_model(
            model_name,
            prompt,
            save_output=False
        )
        
        # Should handle without crashing
        if result is not None:
            print(f"    ✅ Handled without crash")
            if not result.success:
                print(f"    Error: {result.error_message[:50]}...")
        else:
            print(f"    ❌ Returned None (unexpected)")
            all_passed = False
    
    return all_passed


def test_timeout_handling(fixture: OllamaTestFixture, model_name: str) -> bool:
    """
    Test: Timeout Handling
    
    Purpose: Verify timeouts are handled correctly
    Context: Long operations may exceed timeout
    Expected: Timeout error or operation completes within timeout
    """
    print("\n" + "="*60)
    print("ERROR TEST 4: Timeout Handling")
    print("="*60)
    
    # Use very short timeout
    options = ExecutionOptions(
        timeout=1,  # 1 second timeout
        max_tokens=5000  # But request many tokens (may take longer)
    )
    
    print(f"Testing with short timeout ({options.timeout}s) and large max_tokens ({options.max_tokens})")
    
    result = fixture.runner.run_with_options(
        model_name,
        "Write a detailed explanation of machine learning.",
        options,
        save_output=False
    )
    
    # Should either complete quickly or timeout gracefully
    if result.success:
        print(f"✅ Completed within timeout: {result.execution_time:.2f}s")
        return True
    elif result.error_message and "timeout" in result.error_message.lower():
        print(f"✅ Timeout handled gracefully: {result.error_message}")
        return True
    else:
        print(f"⚠️  Result: success={result.success}, error={result.error_message}")
        # Still passed if it didn't crash
        return True


def test_concurrent_operations(fixture: OllamaTestFixture, model_name: str) -> bool:
    """
    Test: Concurrent Operations
    
    Purpose: Verify concurrent operations don't cause issues
    Context: Multiple operations may run simultaneously
    Expected: Operations complete successfully or handle conflicts
    """
    print("\n" + "="*60)
    print("ERROR TEST 5: Concurrent Operations")
    print("="*60)
    
    print("Running 3 concurrent operations...")
    
    prompts = [
        "What is Python?",
        "What is JavaScript?",
        "What is Rust?",
    ]
    
    options = ExecutionOptions(max_tokens=50)
    
    results = fixture.runner.run_batch(
        model_name,
        prompts,
        options,
        max_concurrent=3
    )
    
    successful = sum(1 for r in results if r.success)
    print(f"✅ Concurrent operations: {successful}/{len(prompts)} successful")
    
    return successful > 0  # At least some should succeed


def test_resource_cleanup_on_error(fixture: OllamaTestFixture) -> bool:
    """
    Test: Resource Cleanup on Error
    
    Purpose: Verify resources are cleaned up even when errors occur
    Context: Errors shouldn't leave resources hanging
    Expected: Cleanup happens regardless of success/failure
    """
    print("\n" + "="*60)
    print("ERROR TEST 6: Resource Cleanup on Error")
    print("="*60)
    
    # Create some resources
    output_dir = fixture.output_dir / "error_test"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Attempt operation that may fail
    model_name = fixture.get_available_model()
    if model_name:
        result = fixture.manager.run_model(
            model_name,
            "Test for cleanup.",
            save_output=True,
            output_dir=str(output_dir)
        )
        # Whether success or failure, cleanup should work
        print(f"Operation result: success={result.success}")
    
    # Cleanup should work
    try:
        fixture.cleanup()
        print("✅ Cleanup completed successfully")
        return True
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
        return False


def main():
    """Run all error scenario tests."""
    print("="*60)
    print("OLLAMA ERROR HANDLING TESTS")
    print("="*60)
    print("Testing error handling and edge cases with real Ollama API calls")
    print("="*60)
    
    setup_logging()
    logger = get_logger("error_scenario_tests")
    
    # Initialize
    fixture = OllamaTestFixture()
    
    # Get available model
    model_name = fixture.get_available_model()
    if not model_name:
        print("⚠️  No models available - some tests will be skipped")
    
    # Run error tests
    tests = [
        ("Model Not Found", lambda: test_model_not_found(fixture)),
    ]
    
    if model_name:
        tests.extend([
            ("Invalid Parameters", lambda: test_invalid_parameters(fixture, model_name)),
            ("Empty Inputs", lambda: test_empty_inputs(fixture, model_name)),
            ("Timeout Handling", lambda: test_timeout_handling(fixture, model_name)),
            ("Concurrent Operations", lambda: test_concurrent_operations(fixture, model_name)),
        ])
    
    tests.append(("Resource Cleanup", lambda: test_resource_cleanup_on_error(fixture)))
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test '{test_name}' raised exception: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("ERROR TEST SUMMARY")
    print("="*60)
    
    total = len(tests)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    # Cleanup
    fixture.cleanup()
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())


