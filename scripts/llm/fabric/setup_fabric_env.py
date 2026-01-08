#!/usr/bin/env python3
"""
Interactive Fabric Environment Configuration Script

Sets up Fabric .env file with user-provided API keys and configuration,
then demonstrates functionality with an OpenRouter API call.
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
import subprocess
from pathlib import Path
from datetime import datetime
import tempfile

def show_header():
    print("\n" + "="*60)
    print("🔧 FABRIC ENVIRONMENT INTERACTIVE SETUP")
    print("="*60)
    print("This script will help you configure Fabric with your API keys")
    print("and demonstrate functionality with a real API call.\n")

def get_input_with_default(prompt, default_value="", mask_input=False):
    """Get user input with default value option."""
    display_default = "[hidden]" if mask_input and default_value else f"[{default_value}]" if default_value else "[none]"
    
    if mask_input:
        import getpass
        user_input = getpass.getpass(f"{prompt} {display_default}: ")
    else:
        user_input = input(f"{prompt} {display_default}: ")
    
    return user_input.strip() if user_input.strip() else default_value

def create_fabric_env_interactively():
    """Interactive .env file creation."""
    print("📝 Configure Fabric Environment Variables")
    print("-" * 40)
    print("Enter values for each configuration option.")
    print("Press Enter to use default values or skip optional fields.\n")
    
    # API Keys
    print("🔑 API Keys Configuration:")
    openai_key = get_input_with_default(
        "OpenAI API Key (for GPT models)",
        "",
        mask_input=True
    )
    
    anthropic_key = get_input_with_default(
        "Anthropic API Key (for Claude models)",
        "",
        mask_input=True
    )
    
    openrouter_key = get_input_with_default(
        "OpenRouter API Key (for multiple models)",
        "",
        mask_input=True
    )
    
    google_key = get_input_with_default(
        "Google API Key (for Gemini models)",
        "",
        mask_input=True
    )
    
    # Model Configuration
    print("\n🤖 Model Configuration:")
    available_vendors = ["OpenAI", "Anthropic", "OpenRouter", "Google"]
    print(f"Available vendors: {', '.join(available_vendors)}")
    
    default_vendor = get_input_with_default(
        "Default Vendor",
        "OpenRouter" if openrouter_key else "OpenAI"
    )
    
    # Suggest model based on vendor
    model_suggestions = {
        "OpenAI": "gpt-4o-mini",
        "Anthropic": "claude-3-haiku-20240307",
        "OpenRouter": "openai/gpt-4o-mini",
        "Google": "gemini-1.5-flash"
    }
    
    suggested_model = model_suggestions.get(default_vendor, "gpt-4o-mini")
    default_model = get_input_with_default(
        f"Default Model (for {default_vendor})",
        suggested_model
    )
    
    # Fabric Configuration
    print("\n⚙️ Fabric Configuration:")
    output_path = get_input_with_default(
        "Output Path",
        "./fabric_outputs"
    )
    
    repo_url = get_input_with_default(
        "Patterns Repository URL",
        "https://github.com/danielmiessler/fabric.git"
    )
    
    patterns_folder = get_input_with_default(
        "Patterns Folder Path",
        "data/patterns"
    )
    
    # Additional OpenRouter Configuration
    openrouter_config = {}
    if openrouter_key:
        print("\n🌐 OpenRouter Configuration:")
        openrouter_config['base_url'] = get_input_with_default(
            "OpenRouter Base URL",
            "https://openrouter.ai/api/v1"
        )
        
        openrouter_config['site_url'] = get_input_with_default(
            "Site URL (for OpenRouter headers)",
            "https://github.com/danielmiessler/fabric"
        )
        
        openrouter_config['app_name'] = get_input_with_default(
            "App Name (for OpenRouter headers)",
            "Fabric-Codomyrmex-Integration"
        )
    
    return {
        'openai_key': openai_key,
        'anthropic_key': anthropic_key,
        'openrouter_key': openrouter_key,
        'google_key': google_key,
        'default_vendor': default_vendor,
        'default_model': default_model,
        'output_path': output_path,
        'repo_url': repo_url,
        'patterns_folder': patterns_folder,
        'openrouter_config': openrouter_config
    }

def write_env_file(config):
    """Write the .env file to the correct Fabric location."""
    fabric_config_dir = Path.home() / ".config" / "fabric"
    fabric_config_dir.mkdir(parents=True, exist_ok=True)
    
    env_file = fabric_config_dir / ".env"
    
    print(f"\n📄 Writing environment configuration to: {env_file}")
    
    with open(env_file, 'w') as f:
        f.write("# Fabric Environment Configuration\n")
        f.write(f"# Generated on {datetime.now().isoformat()}\n")
        f.write("# By Fabric-Codomyrmex Interactive Setup\n\n")
        
        # API Keys
        f.write("# API Keys\n")
        if config['openai_key']:
            f.write(f"OPENAI_API_KEY={config['openai_key']}\n")
        if config['anthropic_key']:
            f.write(f"ANTHROPIC_API_KEY={config['anthropic_key']}\n")
        if config['openrouter_key']:
            f.write(f"OPENROUTER_API_KEY={config['openrouter_key']}\n")
        if config['google_key']:
            f.write(f"GOOGLE_API_KEY={config['google_key']}\n")
        
        f.write("\n# Model Configuration\n")
        f.write(f"DEFAULT_VENDOR={config['default_vendor']}\n")
        f.write(f"DEFAULT_MODEL={config['default_model']}\n")
        
        f.write("\n# Fabric Configuration\n")
        f.write(f"FABRIC_OUTPUT_PATH={config['output_path']}\n")
        f.write(f"PATTERNS_LOADER_GIT_REPO_URL={config['repo_url']}\n")
        f.write(f"PATTERNS_LOADER_GIT_REPO_PATTERNS_FOLDER={config['patterns_folder']}\n")
        
        # OpenRouter specific configuration
        if config['openrouter_config']:
            f.write("\n# OpenRouter Configuration\n")
            f.write(f"OPENROUTER_BASE_URL={config['openrouter_config']['base_url']}\n")
            f.write(f"OPENROUTER_SITE_URL={config['openrouter_config']['site_url']}\n")
            f.write(f"OPENROUTER_APP_NAME={config['openrouter_config']['app_name']}\n")
    
    print("✅ Environment file created successfully!")
    return env_file

def test_fabric_setup():
    """Test Fabric setup with a simple call."""
    print("\n🧪 Testing Fabric Setup")
    print("-" * 25)
    
    # Check if fabric binary is available
    try:
        result = subprocess.run(['fabric', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("❌ Fabric binary not available")
            return False
        print(f"✅ Fabric binary available: {result.stdout.strip()}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("❌ Fabric binary not found or not responding")
        return False
    
    # Test pattern listing
    try:
        result = subprocess.run(['fabric', '--listpatterns'], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            patterns = [line.strip() for line in result.stdout.split('\n') if line.strip() and not line.startswith('Available')]
            print(f"✅ Found {len(patterns)} Fabric patterns")
            print(f"   Sample patterns: {', '.join(patterns[:5])}")
            return True
        else:
            print("⚠️  Pattern listing failed, but binary is available")
            return True
    except subprocess.TimeoutExpired:
        print("⚠️  Pattern listing timeout, but binary is available")
        return True

def run_example_fabric_call(config):
    """Run an example Fabric call to demonstrate functionality."""
    print("\n🚀 Running Example Fabric Call")
    print("-" * 30)
    
    # Sample text for analysis
    sample_text = """
    Artificial intelligence is transforming software development by automating repetitive tasks,
    enhancing code quality through intelligent analysis, and enabling new forms of human-AI collaboration.
    Modern AI tools like large language models can understand code context, suggest improvements,
    and even generate entire functions based on natural language descriptions.
    """
    
    print("📝 Sample text to analyze:")
    print(sample_text.strip())
    print()
    
    # Try different patterns based on what's available
    patterns_to_try = ['summarize', 'extract_wisdom', 'analyze_prose', 'ai']
    
    for pattern in patterns_to_try:
        print(f"🔍 Trying Fabric pattern: {pattern}")
        
        try:
            # Create temporary file with sample text
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tmp:
                tmp.write(sample_text)
                tmp.flush()
                
                # Run fabric command
                with open(tmp.name, 'r') as input_file:
                    result = subprocess.run(
                        ['fabric', '--pattern', pattern],
                        stdin=input_file,
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                
                os.unlink(tmp.name)
                
                if result.returncode == 0 and result.stdout.strip():
                    print(f"✅ Success! Pattern '{pattern}' response:")
                    print("-" * 40)
                    # Show first 300 characters of response
                    response = result.stdout.strip()
                    if len(response) > 300:
                        print(f"{response[:300]}...")
                        print(f"\n[Response truncated - full length: {len(response)} characters]")
                    else:
                        print(response)
                    print("-" * 40)
                    print("🎉 Fabric integration working successfully!")
                    return True
                else:
                    print(f"❌ Pattern '{pattern}' failed: {result.stderr.strip() if result.stderr else 'No output'}")
                    
        except subprocess.TimeoutExpired:
            print(f"⏰ Pattern '{pattern}' timed out")
        except Exception as e:
            print(f"❌ Error with pattern '{pattern}': {e}")
    
    print("⚠️  All test patterns failed. This might be due to:")
    print("   • Missing or invalid API keys")
    print("   • Network connectivity issues") 
    print("   • API rate limits")
    print("   • Pattern configuration issues")
    print("\n💡 Try running: fabric --pattern summarize < some_text_file.txt")
    return False

def main():
    """Main interactive setup function."""
    show_header()
    
    # Check for non-interactive environment
    if not sys.stdin.isatty() and not os.environ.get("FABRIC_FORCE_INTERACTIVE"):
        print("⚠️  Non-interactive environment detected. Skipping interactive setup.")
        print("   Set FABRIC_FORCE_INTERACTIVE=1 to force interactive mode.")
        return
    
    try:
        # Interactive configuration
        config = create_fabric_env_interactively()
        
        # Write .env file
        env_file = write_env_file(config)
        
        print(f"\n📋 Configuration Summary:")
        print(f"   Environment file: {env_file}")
        print(f"   Default vendor: {config['default_vendor']}")
        print(f"   Default model: {config['default_model']}")
        print(f"   API keys configured: {sum(1 for key in [config['openai_key'], config['anthropic_key'], config['openrouter_key'], config['google_key']] if key)}")
        
        # Test setup
        if test_fabric_setup():
            print("\n" + "="*50)
            
            # Ask user if they want to run example
            run_example = input("\n🎯 Would you like to run an example Fabric call? (Y/n): ").strip()
            if run_example.lower() != 'n':
                success = run_example_fabric_call(config)
                if success:
                    print("\n🎊 Setup and testing completed successfully!")
                else:
                    print("\n⚠️  Setup completed, but example call failed.")
                    print("   You can troubleshoot by checking your API keys and trying manual calls.")
            else:
                print("\n✅ Setup completed! You can now use Fabric with your configured environment.")
        else:
            print("\n⚠️  Setup completed, but Fabric binary test failed.")
            
        # Final usage instructions
        print(f"\n📖 Usage Instructions:")
        print(f"   • Environment file: {env_file}")
        print(f"   • Test manually: echo 'Hello world' | fabric --pattern summarize")
        print(f"   • List patterns: fabric --listpatterns")
        print(f"   • Use in orchestrator: python3 fabric_orchestrator.py")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()