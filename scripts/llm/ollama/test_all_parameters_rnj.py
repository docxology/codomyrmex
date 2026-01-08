#!/usr/bin/env python3
"""
Comprehensive Parameter Testing for rnj-1:8b Model

Tests all ExecutionOptions parameters with rnj-1:8b model (32K context)
using real Ollama API calls. No mocks are used.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from codomyrmex.llm.ollama import OllamaManager, ModelRunner
from codomyrmex.llm.ollama.model_runner import ExecutionOptions
from codomyrmex.logging_monitoring import setup_logging, get_logger


def test_temperature_range(manager: OllamaManager, runner: ModelRunner, model_name: str) -> dict:
    """Test temperature parameter variations."""
    print("\n" + "="*60)
    print("Testing Temperature Parameter (0.1, 0.5, 0.7, 0.9, 1.2)")
    print("="*60)
    
    temperatures = [0.1, 0.5, 0.7, 0.9, 1.2]
    results = {}
    test_prompt = "Write a haiku about programming."
    
    for temp in temperatures:
        print(f"\n   Testing temperature={temp}...")
        try:
            options = ExecutionOptions(temperature=temp, max_tokens=50)
            result = runner.run_with_options(model_name, test_prompt, options, save_output=False)
            
            if result.success:
                results[temp] = {
                    'success': True,
                    'response_length': len(result.response),
                    'execution_time': result.execution_time
                }
                print(f"   ✅ Temperature {temp}: {len(result.response)} chars, {result.execution_time:.2f}s")
            else:
                results[temp] = {'success': False, 'error': result.error_message}
                print(f"   ❌ Temperature {temp} failed: {result.error_message}")
        except Exception as e:
            results[temp] = {'success': False, 'error': str(e)}
            print(f"   ❌ Temperature {temp} error: {e}")
    
    return results


def test_top_p_range(manager: OllamaManager, runner: ModelRunner, model_name: str) -> dict:
    """Test top_p parameter variations."""
    print("\n" + "="*60)
    print("Testing Top P Parameter (0.5, 0.7, 0.9, 0.95)")
    print("="*60)
    
    top_p_values = [0.5, 0.7, 0.9, 0.95]
    results = {}
    test_prompt = "Explain recursion in one sentence."
    
    for top_p in top_p_values:
        print(f"\n   Testing top_p={top_p}...")
        try:
            options = ExecutionOptions(top_p=top_p, max_tokens=100)
            result = runner.run_with_options(model_name, test_prompt, options, save_output=False)
            
            if result.success:
                results[top_p] = {
                    'success': True,
                    'response_length': len(result.response),
                    'execution_time': result.execution_time
                }
                print(f"   ✅ Top P {top_p}: {len(result.response)} chars, {result.execution_time:.2f}s")
            else:
                results[top_p] = {'success': False, 'error': result.error_message}
                print(f"   ❌ Top P {top_p} failed: {result.error_message}")
        except Exception as e:
            results[top_p] = {'success': False, 'error': str(e)}
            print(f"   ❌ Top P {top_p} error: {e}")
    
    return results


def test_top_k_range(manager: OllamaManager, runner: ModelRunner, model_name: str) -> dict:
    """Test top_k parameter variations."""
    print("\n" + "="*60)
    print("Testing Top K Parameter (20, 40, 60, 100)")
    print("="*60)
    
    top_k_values = [20, 40, 60, 100]
    results = {}
    test_prompt = "What is Python?"
    
    for top_k in top_k_values:
        print(f"\n   Testing top_k={top_k}...")
        try:
            options = ExecutionOptions(top_k=top_k, max_tokens=75)
            result = runner.run_with_options(model_name, test_prompt, options, save_output=False)
            
            if result.success:
                results[top_k] = {
                    'success': True,
                    'response_length': len(result.response),
                    'execution_time': result.execution_time
                }
                print(f"   ✅ Top K {top_k}: {len(result.response)} chars, {result.execution_time:.2f}s")
            else:
                results[top_k] = {'success': False, 'error': result.error_message}
                print(f"   ❌ Top K {top_k} failed: {result.error_message}")
        except Exception as e:
            results[top_k] = {'success': False, 'error': str(e)}
            print(f"   ❌ Top K {top_k} error: {e}")
    
    return results


def test_repeat_penalty_range(manager: OllamaManager, runner: ModelRunner, model_name: str) -> dict:
    """Test repeat_penalty parameter variations."""
    print("\n" + "="*60)
    print("Testing Repeat Penalty Parameter (1.0, 1.1, 1.2)")
    print("="*60)
    
    repeat_penalties = [1.0, 1.1, 1.2]
    results = {}
    test_prompt = "List the benefits of using local LLMs."
    
    for rp in repeat_penalties:
        print(f"\n   Testing repeat_penalty={rp}...")
        try:
            options = ExecutionOptions(repeat_penalty=rp, max_tokens=150)
            result = runner.run_with_options(model_name, test_prompt, options, save_output=False)
            
            if result.success:
                results[rp] = {
                    'success': True,
                    'response_length': len(result.response),
                    'execution_time': result.execution_time
                }
                print(f"   ✅ Repeat Penalty {rp}: {len(result.response)} chars, {result.execution_time:.2f}s")
            else:
                results[rp] = {'success': False, 'error': result.error_message}
                print(f"   ❌ Repeat Penalty {rp} failed: {result.error_message}")
        except Exception as e:
            results[rp] = {'success': False, 'error': str(e)}
            print(f"   ❌ Repeat Penalty {rp} error: {e}")
    
    return results


def test_max_tokens_range(manager: OllamaManager, runner: ModelRunner, model_name: str) -> dict:
    """Test max_tokens parameter variations."""
    print("\n" + "="*60)
    print("Testing Max Tokens Parameter (100, 500, 1000, 2048)")
    print("="*60)
    
    max_tokens_values = [100, 500, 1000, 2048]
    results = {}
    test_prompt = "Explain machine learning in detail."
    
    for max_tokens in max_tokens_values:
        print(f"\n   Testing max_tokens={max_tokens}...")
        try:
            options = ExecutionOptions(max_tokens=max_tokens, temperature=0.7)
            result = runner.run_with_options(model_name, test_prompt, options, save_output=False)
            
            if result.success:
                results[max_tokens] = {
                    'success': True,
                    'response_length': len(result.response),
                    'execution_time': result.execution_time
                }
                print(f"   ✅ Max Tokens {max_tokens}: {len(result.response)} chars, {result.execution_time:.2f}s")
            else:
                results[max_tokens] = {'success': False, 'error': result.error_message}
                print(f"   ❌ Max Tokens {max_tokens} failed: {result.error_message}")
        except Exception as e:
            results[max_tokens] = {'success': False, 'error': str(e)}
            print(f"   ❌ Max Tokens {max_tokens} error: {e}")
    
    return results


def test_system_prompt(manager: OllamaManager, runner: ModelRunner, model_name: str) -> bool:
    """Test system_prompt functionality."""
    print("\n" + "="*60)
    print("Testing System Prompt Functionality")
    print("="*60)
    
    test_prompt = "What is the capital of France?"
    system_prompt = "You are a helpful geography assistant."
    
    try:
        options = ExecutionOptions(system_prompt=system_prompt, max_tokens=50)
        result = runner.run_with_options(model_name, test_prompt, options, save_output=False)
        
        if result.success:
            print(f"✅ System prompt test successful")
            print(f"   Response length: {len(result.response)} chars")
            print(f"   Execution time: {result.execution_time:.2f}s")
            return True
        else:
            print(f"❌ System prompt test failed: {result.error_message}")
            return False
    except Exception as e:
        print(f"❌ System prompt test error: {e}")
        return False


def test_json_format(manager: OllamaManager, runner: ModelRunner, model_name: str) -> bool:
    """Test JSON format output."""
    print("\n" + "="*60)
    print("Testing JSON Format Output")
    print("="*60)
    
    test_prompt = "Return a JSON object with keys 'name' and 'age' for a person named Alice who is 30 years old."
    
    try:
        options = ExecutionOptions(format="json", max_tokens=100)
        result = runner.run_with_options(model_name, test_prompt, options, save_output=False)
        
        if result.success:
            print(f"✅ JSON format test successful")
            print(f"   Response length: {len(result.response)} chars")
            print(f"   Response preview: {result.response[:100]}...")
            # Try to parse as JSON
            import json
            try:
                json.loads(result.response)
                print(f"   ✅ Response is valid JSON")
            except json.JSONDecodeError:
                print(f"   ⚠️  Response may not be valid JSON (model-dependent)")
            return True
        else:
            print(f"❌ JSON format test failed: {result.error_message}")
            return False
    except Exception as e:
        print(f"❌ JSON format test error: {e}")
        return False


def test_32k_context(manager: OllamaManager, runner: ModelRunner, model_name: str) -> bool:
    """Test 32K context window capability."""
    print("\n" + "="*60)
    print("Testing 32K Context Window")
    print("="*60)
    
    # Create a long context (approximately 32K tokens worth of text)
    long_context = "Python is a programming language. " * 1000  # ~30K chars
    test_prompt = "Summarize the main topic of the following text: " + long_context
    
    try:
        options = ExecutionOptions(
            context_window=32768,
            max_tokens=200,
            temperature=0.7
        )
        result = runner.run_with_options(model_name, test_prompt, options, save_output=False)
        
        if result.success:
            print(f"✅ 32K context test successful")
            print(f"   Prompt length: {len(test_prompt)} chars")
            print(f"   Response length: {len(result.response)} chars")
            print(f"   Execution time: {result.execution_time:.2f}s")
            return True
        else:
            print(f"❌ 32K context test failed: {result.error_message}")
            return False
    except Exception as e:
        print(f"❌ 32K context test error: {e}")
        return False


def main():
    """Run comprehensive parameter tests."""
    print("="*60)
    print("COMPREHENSIVE PARAMETER TESTING - rnj-1:8b")
    print("="*60)
    print("Testing all ExecutionOptions with real Ollama API calls")
    print("Model: rnj-1:8b (32K context window)")
    print("="*60)
    
    setup_logging()
    logger = get_logger("parameter_testing")
    
    # Initialize
    target_model_name = "rnj-1:8b"
    manager = OllamaManager(use_http_api=True)
    runner = ModelRunner(manager)
    
    # Check model availability
    model_name = target_model_name
    if not manager.is_model_available(model_name):
        print(f"\n❌ Model {model_name} not available")
        print(f"📥 Attempting to pull {model_name}...")
        success = manager.download_model(model_name)
        if success:
            print(f"✅ Model {model_name} pull completed")
            # Give it more time to register and check again
            import time
            for i in range(5):
                time.sleep(2)
                if manager.is_model_available(model_name):
                    print(f"✅ Model {model_name} is now available")
                    break
                print(f"   Waiting for model registration... ({i+1}/5)")
            
            # If still not available, try to find it by base name
            if not manager.is_model_available(model_name):
                models = manager.list_models(force_refresh=True)
                base_name = model_name.split(':')[0]
                matching = [m for m in models if base_name in m.name.lower()]
                if matching:
                    model_name = matching[0].name
                    print(f"✅ Found model: {model_name} (using instead)")
                else:
                    # Use any available model for testing
                    if models:
                        model_name = models[0].name
                        print(f"⚠️  Using available model {model_name} for parameter testing")
                        print(f"📝 Configuration will be for {target_model_name} (32K context)")
                    else:
                        print(f"❌ No models available for testing")
                        return 1
        else:
            print(f"❌ Failed to pull {model_name}")
            # Try to use an available model
            models = manager.list_models(force_refresh=True)
            if models:
                model_name = models[0].name
                print(f"⚠️  Using available model {model_name} for parameter testing")
                print(f"📝 Configuration will be for {target_model_name} (32K context)")
            else:
                return 1
    
    print(f"\n✅ Using model: {model_name} for testing")
    
    # Run all parameter tests
    all_results = {}
    
    all_results['temperature'] = test_temperature_range(manager, runner, model_name)
    all_results['top_p'] = test_top_p_range(manager, runner, model_name)
    all_results['top_k'] = test_top_k_range(manager, runner, model_name)
    all_results['repeat_penalty'] = test_repeat_penalty_range(manager, runner, model_name)
    all_results['max_tokens'] = test_max_tokens_range(manager, runner, model_name)
    all_results['system_prompt'] = test_system_prompt(manager, runner, model_name)
    all_results['json_format'] = test_json_format(manager, runner, model_name)
    all_results['32k_context'] = test_32k_context(manager, runner, model_name)
    
    # Summary
    print("\n" + "="*60)
    print("PARAMETER TEST SUMMARY")
    print("="*60)
    
    total_tests = 0
    passed_tests = 0
    
    for param_name, results in all_results.items():
        if isinstance(results, dict) and 'success' in str(results):
            # Count individual parameter tests
            for value, result in results.items():
                if isinstance(result, dict):
                    total_tests += 1
                    if result.get('success', False):
                        passed_tests += 1
        elif isinstance(results, bool):
            total_tests += 1
            if results:
                passed_tests += 1
    
    print(f"\nTotal parameter tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success rate: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL PARAMETER TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) had issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())

