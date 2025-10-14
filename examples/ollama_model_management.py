#!/usr/bin/env python3
"""
Ollama Model Management Example

This script demonstrates how to manage Ollama models within the Codomyrmex ecosystem,
including downloading, listing, and managing model configurations.
"""

import sys
import time
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from codomyrmex.ollama_integration import OllamaManager, OutputManager, ConfigManager
    from codomyrmex.logging_monitoring import get_logger

    OLLAMA_AVAILABLE = True
except ImportError as e:
    print(f"❌ Ollama integration not available: {e}")
    sys.exit(1)


def list_and_analyze_models():
    """List all available models and analyze their properties."""
    print("📋 MODEL ANALYSIS")
    print("=" * 30)

    manager = OllamaManager()

    print("🔄 Refreshing model list...")
    models = manager.list_models(force_refresh=True)

    if not models:
        print("❌ No models found")
        return

    print(f"✅ Found {len(models)} models\n")

    # Display model information
    print("📊 Model Details:")
    print("-" * 80)
    print(f"{'Model Name'"<25"} {'Size'"<10"} {'Modified'"<15"} {'Parameters'"<15"}")
    print("-" * 80)

    for model in models:
        size_mb = model.size // (1024 * 1024)
        size_str = f"{size_mb}MB"

        # Get additional info if available
        param_info = model.parameters or "N/A"
        if len(param_info) > 12:
            param_info = param_info[:9] + "..."

        print(f"{model.name:<25} {size_str:<10} {model.modified:<15} {param_info:<15}")

    # Show statistics
    print("\n📈 Statistics:")
    stats = manager.get_model_stats()

    print(f"   Total models: {stats['total_models']}")
    print(f"   Total size: {stats['total_size_mb']:.1f} MB")
    print(f"   Models by family: {len(stats['models_by_family'])} families")

    for family, model_list in stats['models_by_family'].items():
        print(f"     {family}: {len(model_list)} models")

    if stats['largest_model']:
        largest = next(m for m in models if m.name == stats['largest_model'])
        print(f"   Largest model: {stats['largest_model']} ({largest.size // (1024*1024)} MB)")

    if stats['smallest_model']:
        smallest = next(m for m in models if m.name == stats['smallest_model'])
        print(f"   Smallest model: {stats['smallest_model']} ({smallest.size // (1024*1024)} MB)")


def download_models():
    """Demonstrate model downloading capabilities."""
    print("\n\n⬇️  MODEL DOWNLOADING")
    print("=" * 30)

    manager = OllamaManager()

    # Popular models to suggest
    suggested_models = [
        "llama3.1:8b",      # Good balance of size and capability
        "codellama:7b",     # Code-focused model
        "mistral:7b",       # Fast and capable
        "gemma2:2b",        # Small but capable
        "smollm:135m"       # Very small for testing
    ]

    print("💡 Suggested models to download:")
    for model in suggested_models:
        print(f"   • {model}")

    print("\n📝 To download a model, run:")
    print("   ollama run <model_name>")
    print("   Example: ollama run llama3.1:8b")

    # Try to download a small test model if not already available
    test_model = "smollm:135m"

    if not manager.is_model_available(test_model):
        print(f"\n🔄 Attempting to download test model: {test_model}")
        success = manager.download_model(test_model)

        if success:
            print(f"✅ Successfully downloaded {test_model}")
        else:
            print(f"❌ Failed to download {test_model}")
    else:
        print(f"\n✅ Test model {test_model} already available")


def manage_model_configurations():
    """Demonstrate model configuration management."""
    print("\n\n⚙️  MODEL CONFIGURATION MANAGEMENT")
    print("=" * 40)

    config_manager = ConfigManager()
    output_manager = OutputManager()

    print("📋 Current configuration:")
    if config_manager.config:
        print(f"   Default model: {config_manager.config.default_model}")
        print(f"   Preferred models: {config_manager.config.preferred_models}")
        print(f"   Output directory: {config_manager.config.base_output_dir}")

    # Save a test model configuration
    test_model = "smollm:135m"
    test_config = {
        'temperature': 0.7,
        'max_tokens': 512,
        'timeout': 60,
        'description': 'Fast, small model for testing and quick responses'
    }

    print(f"\n💾 Saving configuration for model: {test_model}")
    config_path = output_manager.save_model_config(test_model, test_config, "test_config")

    if config_path:
        print(f"✅ Configuration saved to: {config_path}")

    # Load it back
    loaded_config = output_manager.load_model_config(test_model, "test_config")
    if loaded_config:
        print("✅ Configuration loaded successfully")
        print(f"   Keys: {list(loaded_config.keys())}")

    # Show available configurations
    print("\n📁 Available configurations:")
    configs = output_manager.list_saved_outputs(output_type="configs")
    for config in configs[:5]:  # Show first 5
        print(f"   • {config['filename']}")


def export_and_import_config():
    """Demonstrate configuration export/import."""
    print("\n\n📤📥 CONFIGURATION EXPORT/IMPORT")
    print("=" * 40)

    config_manager = ConfigManager()

    # Export current configuration
    export_path = "examples/output/ollama/configs/exported_config.json"
    print(f"📤 Exporting configuration to: {export_path}")

    success = config_manager.export_config(export_path)

    if success:
        print("✅ Configuration exported successfully")

        # Show export file size
        try:
            size = Path(export_path).stat().st_size
            print(f"   Export file size: {size} bytes")
        except:
            pass
    else:
        print("❌ Export failed")

    # Show configuration validation
    print("\n🔍 Configuration validation:")
    validation = config_manager.validate_config()

    if validation['valid']:
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration has errors:")
        for error in validation['errors']:
            print(f"   • {error}")

    if validation['warnings']:
        print("⚠️  Configuration warnings:")
        for warning in validation['warnings']:
            print(f"   • {warning}")


def main():
    """Run all model management demonstrations."""
    print("🐙 CODOMYRMEX OLLAMA MODEL MANAGEMENT")
    print("=" * 45)
    print("Comprehensive model management and configuration")
    print("=" * 45)

    # Run demonstrations
    list_and_analyze_models()
    download_models()
    manage_model_configurations()
    export_and_import_config()

    print("\n🎉 Model management demonstration completed!")
    print("💡 Use these patterns to manage your Ollama models effectively")
    print("📚 For advanced usage, see: examples/ollama_integration_demo.py")


if __name__ == "__main__":
    main()
