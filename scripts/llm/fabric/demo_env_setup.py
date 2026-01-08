#!/usr/bin/env python3
"""
Demo script showing how to use the interactive Fabric environment setup.

This demonstrates the setup process and shows the created files.
"""

import sys
from pathlib import Path
try:
    import codomyrmex
except ImportError:
    # Add project root to sys.path
    project_root = Path(__file__).resolve().parent.parent.parent
    src_path = project_root / "src"
    sys.path.insert(0, str(src_path))
import os
import sys
from pathlib import Path

def show_demo_info():
    """Show information about the interactive environment setup."""
    print("🎯 FABRIC ENVIRONMENT SETUP DEMO")
    print("=" * 40)
    print()
    print("The setup_fabric_env.py script provides interactive configuration for:")
    print("  🔑 API Keys (OpenAI, Anthropic, OpenRouter, Google)")
    print("  🤖 Model selection and vendor preferences") 
    print("  ⚙️ Fabric configuration settings")
    print("  🌐 OpenRouter integration (multi-model access)")
    print("  🧪 Automatic testing with real API calls")
    print()
    print("Features:")
    print("  • Interactive prompts with sensible defaults")
    print("  • Secure password masking for API keys")
    print("  • Automatic .env file creation in correct location")
    print("  • Real-time testing and validation")
    print("  • OpenRouter integration for cost-effective access")
    print()

def check_existing_env():
    """Check if Fabric environment already exists."""
    fabric_config_dir = Path.home() / ".config" / "fabric"
    env_file = fabric_config_dir / ".env"
    
    if env_file.exists():
        print(f"📄 Existing Fabric environment found: {env_file}")
        with open(env_file, 'r') as f:
            content = f.read()
            lines = [line for line in content.split('\n') if '=' in line and not line.startswith('#')]
            print(f"   Contains {len(lines)} configuration variables")
        print("   (Will be backed up during setup)")
        return True
    else:
        print("📭 No existing Fabric environment found")
        print(f"   Will create: {env_file}")
        return False

def show_usage_examples():
    """Show usage examples after setup."""
    print("\n📖 USAGE EXAMPLES AFTER SETUP")
    print("-" * 35)
    print()
    print("1. 🚀 Run the interactive setup:")
    print("   python3 setup_fabric_env.py")
    print()
    print("2. 🧪 Test Fabric with simple commands:")
    print("   echo 'Hello world' | fabric --pattern summarize")
    print("   echo 'Python is great' | fabric --pattern extract_wisdom")
    print()
    print("3. 📋 List available patterns:")
    print("   fabric --listpatterns")
    print()
    print("4. 🤖 Use with orchestrator:")
    print("   python3 fabric_orchestrator.py")
    print("   python3 content_analysis_workflow.py")
    print()
    print("5. 💡 Advanced usage with OpenRouter:")
    print("   # Access multiple models through OpenRouter")
    print("   fabric --model openai/gpt-4o-mini --pattern analyze_code < myfile.py")
    print("   fabric --model anthropic/claude-3-haiku --pattern summarize < article.txt")
    print()

def show_openrouter_benefits():
    """Show benefits of OpenRouter integration."""
    print("🌐 OPENROUTER INTEGRATION BENEFITS")
    print("-" * 35)
    print()
    print("OpenRouter provides unified access to multiple AI providers:")
    print("  • 💰 Cost-effective access to premium models")
    print("  • 🔄 Automatic fallback between providers")
    print("  • 📊 Usage tracking and cost monitoring")
    print("  • 🚀 Access to latest models from multiple providers")
    print("  • 🔑 Single API key for multiple AI services")
    print()
    print("Popular OpenRouter models for code analysis:")
    print("  • openai/gpt-4o-mini (fast, cost-effective)")
    print("  • anthropic/claude-3-haiku (excellent for code)")
    print("  • google/gemini-1.5-flash (multimodal capabilities)")
    print("  • meta-llama/llama-3.1-8b-instruct (open source)")
    print()

def main():
    """Main demo function."""
    show_demo_info()
    check_existing_env()
    show_openrouter_benefits()
    show_usage_examples()
    
    print("🎬 DEMO SUMMARY")
    print("-" * 15)
    print("✅ Interactive environment setup script created")
    print("✅ OpenRouter integration included")
    print("✅ Automatic testing and validation")
    print("✅ Secure API key handling")
    print("✅ Integration with existing Fabric orchestrators")
    print()
    print("🚀 Ready to run: python3 setup_fabric_env.py")
    print()

if __name__ == "__main__":
    main()