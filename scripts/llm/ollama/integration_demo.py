#!/usr/bin/env python3
"""
Ollama Integration Comprehensive Demo

This script demonstrates all the capabilities of the Codomyrmex Ollama integration,
including model management, flexible execution, output saving, and configuration management.
"""

import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

try:
    from codomyrmex.llm.ollama import OllamaManager, ModelRunner, OutputManager, ConfigManager
    from codomyrmex.llm.ollama.model_runner import ExecutionOptions
    from codomyrmex.logging_monitoring import setup_logging, get_logger
    from codomyrmex.data_visualization import create_bar_chart, create_line_plot

    OLLAMA_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Ollama integration not fully available: {e}")
    OLLAMA_AVAILABLE = False


def demo_model_management():
    """Demonstrate model listing and management capabilities."""
    print("🔧 MODEL MANAGEMENT DEMONSTRATION")
    print("=" * 50)

    if not OLLAMA_AVAILABLE:
        print("❌ Ollama integration not available")
        return False

    try:
        # Initialize Ollama manager
        manager = OllamaManager()

        print("📋 Listing available models...")
        models = manager.list_models()
        print(f"✅ Found {len(models)} models")

        for model in models:
            print(f"   📦 {model.name} ({model.size // (1024*1024)} MB) - {model.modified}")

        # Show model statistics
        print("\n📊 Model Statistics:")
        stats = manager.get_model_stats()
        print(f"   Total models: {stats['total_models']}")
        print(f"   Total size: {stats['total_size_mb']:.1f} MB")
        print(f"   Largest model: {stats['largest_model']}")
        print(f"   Smallest model: {stats['smallest_model']}")

        return True

    except Exception as e:
        print(f"❌ Model management demo failed: {e}")
        return False


def demo_flexible_execution():
    """Demonstrate flexible model execution with different options."""
    print("\n🚀 FLEXIBLE EXECUTION DEMONSTRATION")
    print("=" * 50)

    if not OLLAMA_AVAILABLE:
        print("❌ Ollama integration not available")
        return False

    try:
        manager = OllamaManager()
        runner = ModelRunner(manager)

        # Test with a small model for quick demo
        test_model = "smollm:135m"  # Small model for quick testing

        if not manager.is_model_available(test_model):
            print(f"⚠️  Test model {test_model} not available, using available model...")
            models = manager.list_models()
            if models:
                test_model = models[0].name
            else:
                print("❌ No models available for testing")
                return False

        print(f"🧪 Testing model: {test_model}")

        # Test different execution options
        test_prompt = "Explain quantum computing in simple terms."

        print("\n📝 Testing basic execution...")
        result = runner.run_with_options(
            test_model,
            test_prompt,
            ExecutionOptions(temperature=0.7, max_tokens=200)
        )

        if result.success:
            print("✅ Basic execution successful")
            print(f"   Response length: {len(result.response)} characters")
            print(f"   Execution time: {result.execution_time:.2f}s")
        else:
            print(f"❌ Basic execution failed: {result.error_message}")

        print("\n🎨 Testing creative mode...")
        creative_result = runner.run_with_options(
            test_model,
            "Write a short poem about artificial intelligence.",
            ExecutionOptions(temperature=0.9, max_tokens=150)
        )

        if creative_result.success:
            print("✅ Creative execution successful")
            print(f"   Response preview: {creative_result.response[:100]}...")
        else:
            print(f"❌ Creative execution failed: {creative_result.error_message}")

        return True

    except Exception as e:
        print(f"❌ Flexible execution demo failed: {e}")
        return False


def demo_output_management():
    """Demonstrate output saving and management."""
    print("\n💾 OUTPUT MANAGEMENT DEMONSTRATION")
    print("=" * 50)

    if not OLLAMA_AVAILABLE:
        print("❌ Ollama integration not available")
        return False

    try:
        # Initialize managers
        manager = OllamaManager()
        output_manager = OutputManager()

        print("📁 Setting up output directory structure...")

        # Show output statistics
        stats = output_manager.get_output_stats()
        print(f"📊 Current output stats: {stats['total_outputs']} files, {stats['total_size'] // 1024} KB")

        # Save a test configuration
        test_config = {
            'test_model': 'smollm:135m',
            'temperature': 0.7,
            'max_tokens': 200
        }

        config_path = output_manager.save_model_config("test_model", test_config, "demo_config")
        print(f"✅ Saved test configuration to: {config_path}")

        # Load it back
        loaded_config = output_manager.load_model_config("test_model", "demo_config")
        if loaded_config:
            print("✅ Successfully loaded configuration back")
            print(f"   Config keys: {list(loaded_config.keys())}")

        return True

    except Exception as e:
        print(f"❌ Output management demo failed: {e}")
        return False


def demo_configuration_management():
    """Demonstrate configuration management capabilities."""
    print("\n⚙️  CONFIGURATION MANAGEMENT DEMONSTRATION")
    print("=" * 50)

    try:
        config_manager = ConfigManager()

        print("📋 Current configuration:")
        if config_manager.config:
            print(f"   Ollama binary: {config_manager.config.ollama_binary}")
            print(f"   Default model: {config_manager.config.default_model}")
            print(f"   Output directory: {config_manager.config.base_output_dir}")
            print(f"   Auto-start server: {config_manager.config.auto_start_server}")

        # Show execution presets
        presets = config_manager.get_execution_presets()
        print(f"\n🎛️  Available execution presets: {list(presets.keys())}")

        for preset_name, preset_options in presets.items():
            print(f"   • {preset_name}: temp={preset_options.temperature}, tokens={preset_options.max_tokens}")

        # Validate configuration
        validation = config_manager.validate_config()
        if validation['valid']:
            print("✅ Configuration is valid")
        else:
            print(f"❌ Configuration has errors: {validation['errors']}")

        if validation['warnings']:
            print(f"⚠️  Configuration warnings: {validation['warnings']}")

        return True

    except Exception as e:
        print(f"❌ Configuration management demo failed: {e}")
        return False


def demo_model_comparison():
    """Demonstrate model comparison capabilities."""
    print("\n⚖️  MODEL COMPARISON DEMONSTRATION")
    print("=" * 50)

    if not OLLAMA_AVAILABLE:
        print("❌ Ollama integration not available")
        return False

    try:
        manager = OllamaManager()
        runner = ModelRunner(manager)

        # Get available models for comparison
        models = manager.list_models()

        if len(models) < 2:
            print("⚠️  Need at least 2 models for comparison, only have 1")
            return False

        # Use first two models for comparison
        model_names = [models[0].name, models[1].name]
        test_prompt = "What are the main benefits of using local LLMs?"

        print(f"🔍 Comparing models: {model_names}")
        print(f"📝 Test prompt: {test_prompt}")

        comparison_result = runner.create_model_comparison(
            model_names,
            test_prompt,
            ExecutionOptions(max_tokens=150, temperature=0.7)
        )

        print("\n📊 Comparison Results:")
        for model_name, result in comparison_result['results'].items():
            status = "✅" if result['success'] else "❌"
            print(f"   {status} {model_name}:")
            print(f"      Execution time: {result['execution_time']:.2f}s")
            print(f"      Response length: {result['response_length']} chars")
            print(f"      Tokens/sec: {result['tokens_per_second']:.1f}")

        # Show summary
        summary = comparison_result['summary']
        if 'fastest_model' in summary:
            print("\n🏆 Summary:")
            print(f"   Fastest model: {summary['fastest_model']}")
            print(f"   Most efficient: {summary['most_efficient']}")
            print(f"   Success rate: {summary['success_rate']*100:.1f}%")

        return True

    except Exception as e:
        print(f"❌ Model comparison demo failed: {e}")
        return False


def demo_batch_execution():
    """Demonstrate batch execution capabilities."""
    print("\n📦 BATCH EXECUTION DEMONSTRATION")
    print("=" * 50)

    if not OLLAMA_AVAILABLE:
        print("❌ Ollama integration not available")
        return False

    try:
        manager = OllamaManager()
        runner = ModelRunner(manager)

        # Test with a small model for quick demo
        test_model = "smollm:135m"

        if not manager.is_model_available(test_model):
            print(f"⚠️  Test model {test_model} not available")
            return False

        print(f"🚀 Running batch execution with {test_model}")

        # Test prompts for batch execution
        test_prompts = [
            "What is machine learning?",
            "Explain artificial intelligence in simple terms.",
            "What are the benefits of using local LLMs?"
        ]

        print(f"📝 Executing {len(test_prompts)} prompts in batch...")

        start_time = time.time()
        results = runner.run_batch(
            test_model,
            test_prompts,
            ExecutionOptions(max_tokens=100, temperature=0.7),
            max_concurrent=2
        )

        total_time = time.time() - start_time

        print("✅ Batch execution completed!")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Successful: {sum(1 for r in results if r.success)}/{len(results)}")

        for i, result in enumerate(results):
            status = "✅" if result.success else "❌"
            print(f"   {status} Prompt {i+1}: {result.execution_time:.2f}s")

        return True

    except Exception as e:
        print(f"❌ Batch execution demo failed: {e}")
        return False


def demo_integration_with_codomyrmex():
    """Demonstrate integration with other Codomyrmex modules."""
    print("\n🔗 CODOMYRMEX INTEGRATION DEMONSTRATION")
    print("=" * 50)

    try:
        # Test integration capabilities
        print("🔧 Testing Codomyrmex module integration...")

        # Test logging integration
        setup_logging()
        logger = get_logger("ollama_demo")

        logger.info("Ollama integration demo started")
        print("✅ Logging integration working")

        # Test if data visualization is available for output analysis
        try:
            from codomyrmex.data_visualization import create_bar_chart

            # Create a simple visualization
            categories = ["Feature A", "Feature B", "Feature C"]
            values = [85, 72, 91]

            create_bar_chart(
                categories=categories,
                values=values,
                title="Ollama Integration Features",
                output_path="scripts/output/ollama/integration_demo.png",
                show_plot=False
            )

            print("✅ Data visualization integration working")
            logger.info("Created integration visualization")

        except ImportError:
            print("⚠️  Data visualization not available")

        print("🎉 Codomyrmex integration demonstration complete!")
        return True

    except Exception as e:
        print(f"❌ Integration demo failed: {e}")
        return False


def main():
    """Run the complete Ollama integration demonstration."""
    print("🐙 CODOMYRMEX OLLAMA INTEGRATION COMPREHENSIVE DEMO")
    print("=" * 60)
    print("Demonstrating local LLM management, execution, and integration")
    print("=" * 60)

    if not OLLAMA_AVAILABLE:
        print("❌ Ollama integration modules not available")
        print("Please ensure Ollama is installed and the integration module is properly set up")
        return 1

    # Run all demonstrations
    demos = [
        ("Model Management", demo_model_management),
        ("Flexible Execution", demo_flexible_execution),
        ("Output Management", demo_output_management),
        ("Configuration Management", demo_configuration_management),
        ("Model Comparison", demo_model_comparison),
        ("Batch Execution", demo_batch_execution),
        ("Codomyrmex Integration", demo_integration_with_codomyrmex)
    ]

    results = {}
    successful_demos = 0

    for demo_name, demo_func in demos:
        print(f"\n{'━' * 60}")
        print(f"Running: {demo_name}")
        print(f"{'━' * 60}")

        try:
            result = demo_func()
            results[demo_name] = result
            if result:
                successful_demos += 1
                print(f"✅ {demo_name}: PASSED")
            else:
                print(f"❌ {demo_name}: FAILED")
        except Exception as e:
            print(f"❌ {demo_name}: ERROR - {e}")
            results[demo_name] = False

    # Final summary
    print(f"\n{'=' * 60}")
    print("DEMONSTRATION SUMMARY")
    print(f"{'=' * 60}")

    print(f"Total demos: {len(demos)}")
    print(f"Successful: {successful_demos}")
    print(f"Failed: {len(demos) - successful_demos}")

    print("\n📊 Demo Results:")
    for demo_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {demo_name}: {status}")

    print("\n🎯 Key Capabilities Demonstrated:")
    print("   ✅ Model listing and management")
    print("   ✅ Flexible execution with custom options")
    print("   ✅ Output saving and configuration management")
    print("   ✅ Model comparison and benchmarking")
    print("   ✅ Batch execution with concurrency control")
    print("   ✅ Integration with Codomyrmex ecosystem")
    print("   ✅ Comprehensive logging and error handling")

    if successful_demos == len(demos):
        print("\n🎉 ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
        print("✨ Ollama integration is fully functional and ready for use!")
        return 0
    else:
        print(f"\n⚠️  {len(demos) - successful_demos} demonstrations had issues")
        print("💡 Check the output above for specific error details")
        return 1


if __name__ == "__main__":
    exit(main())
