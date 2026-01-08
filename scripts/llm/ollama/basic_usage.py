#!/usr/bin/env python3
"""
Basic Ollama Usage Example

This script demonstrates the simplest way to use the Codomyrmex Ollama integration
for basic model execution and output management.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

try:
    from codomyrmex.llm.ollama import OllamaManager, ModelRunner
    from codomyrmex.llm.ollama.model_runner import ExecutionOptions
except ImportError as e:
    print(f"❌ Ollama integration not available: {e}")
    print("Please ensure Ollama is installed and the integration module is properly set up")
    sys.exit(1)


def basic_model_execution():
    """Demonstrate basic model execution."""
    print("🤖 Basic Ollama Model Execution")
    print("=" * 40)

    # Initialize managers
    manager = OllamaManager()
    runner = ModelRunner(manager)

    # List available models
    models = manager.list_models()
    print(f"📋 Available models: {len(models)}")

    if not models:
        print("❌ No models available. Please download some models first:")
        print("   ollama run llama3.1:8b")
        return

    # Use the first available model
    model_name = models[0].name
    print(f"🧪 Using model: {model_name}")

    # Simple prompt
    prompt = "Explain what artificial intelligence is in one sentence."

    print(f"\n📝 Prompt: {prompt}")

    # Run the model
    result = runner.run_with_options(
        model_name,
        prompt,
        ExecutionOptions(temperature=0.7, max_tokens=100)
    )

    if result.success:
        print("\n✅ Response:")
        print(result.response)
        print(f"\n⏱️  Execution time: {result.execution_time:.2f} seconds")
    else:
        print(f"\n❌ Execution failed: {result.error_message}")


def model_comparison_example():
    """Demonstrate model comparison."""
    print("\n\n⚖️  Model Comparison Example")
    print("=" * 40)

    manager = OllamaManager()
    runner = ModelRunner(manager)

    # Get available models
    models = manager.list_models()

    if len(models) < 2:
        print("⚠️  Need at least 2 models for comparison")
        return

    # Compare first two models
    model_names = [models[0].name, models[1].name]
    prompt = "What is the capital of France?"

    print(f"🔍 Comparing: {model_names}")
    print(f"📝 Prompt: {prompt}")

    comparison = runner.create_model_comparison(
        model_names,
        prompt,
        ExecutionOptions(max_tokens=50, temperature=0.1)
    )

    print("\n📊 Results:")
    for model_name, result in comparison['results'].items():
        if result['success']:
            print(f"   ✅ {model_name}: {result['response_preview']}")
        else:
            print(f"   ❌ {model_name}: {result['error']}")


def batch_processing_example():
    """Demonstrate batch processing."""
    print("\n\n📦 Batch Processing Example")
    print("=" * 40)

    manager = OllamaManager()
    runner = ModelRunner(manager)

    # Use a small model for quick demo
    test_model = "smollm:135m"

    if not manager.is_model_available(test_model):
        print(f"⚠️  Model {test_model} not available, using first available model")
        models = manager.list_models()
        if models:
            test_model = models[0].name
        else:
            print("❌ No models available")
            return

    print(f"🚀 Running batch with model: {test_model}")

    # Multiple prompts
    prompts = [
        "What is Python?",
        "Explain machine learning.",
        "What are the benefits of open source?",
        "How does the internet work?"
    ]

    print(f"📝 Processing {len(prompts)} prompts...")

    results = runner.run_batch(
        test_model,
        prompts,
        ExecutionOptions(max_tokens=75, temperature=0.7),
        max_concurrent=2
    )

    print("\n✅ Results:")
    for i, result in enumerate(results):
        if result.success:
            print(f"   {i+1}. ✅ {len(result.response)} chars in {result.execution_time:.2f}s")
        else:
            print(f"   {i+1}. ❌ {result.error_message}")


def main():
    """Run all basic usage examples."""
    print("🐙 CODOMYRMEX OLLAMA BASIC USAGE EXAMPLES")
    print("=" * 50)
    print("Simple demonstrations of Ollama integration")
    print("=" * 50)

    # Run examples
    basic_model_execution()
    model_comparison_example()
    batch_processing_example()

    print("\n🎉 Basic usage examples completed!")
    print("💡 For advanced usage, see: scripts/ollama_integration/integration_demo.py")
    print("📚 For configuration management, see the ConfigManager class")


if __name__ == "__main__":
    main()
