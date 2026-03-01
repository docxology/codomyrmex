"""Orchestrate Relay Demo with Real Ollama Management.

This script uses the `codomyrmex` source library to:
1. Ensure the Ollama server is running (starting it if needed).
2. Ensure the required model (codellama:latest) is pulled and available.
3. Launch the `relay_chat_demo.py` scenario in a real environment.

Usage:
    uv run python scripts/agents/orchestrate_with_ollama.py
"""

import sys
import os
from pathlib import Path
import logging

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.llm.ollama import OllamaManager
from codomyrmex.utils.cli_helpers import setup_logging, print_info, print_success, print_error, print_warning

# Import the demo main function
# We need to add the current dir to path to import sibling scripts if not using package relative imports
sys.path.append(str(Path(__file__).parent))
try:
    from relay_chat_demo import main as run_relay_demo
except ImportError:
    # Fallback if running from root
    from scripts.agents.relay_chat_demo import main as run_relay_demo

def main():
    setup_logging()
    logger = logging.getLogger("orchestrator")
    
    print_info("Initializing Real Ollama Orchestration...")
    
    # 1. Initialize Manager (starts server if needed)
    try:
        manager = OllamaManager(auto_start_server=True)
    except Exception as e:
        print_error(f"Failed to initialize OllamaManager: {e}")
        sys.exit(1)
        
    # 2. Check/Pull Model
    target_model = "codellama:latest"
    print_info(f"Ensuring model '{target_model}' is available...")
    
    # Check if target is available
    if not manager.is_model_available(target_model):
        print_info(f"Model '{target_model}' not found in local registry.")
        
        # Check for alternatives BEFORE pulling
        try:
            models = manager.list_models(force_refresh=True)
            available_names = [m.name for m in models]
            alternative = None
            for name in available_names:
                if "llama3" in name or "codellama" in name:
                    alternative = name
                    break
            
            if alternative:
                print_info(f"Found compatible local model '{alternative}'. Skipping pull.")
                target_model = alternative
            else:
                print_info("Pulling model... (this may take minutes)")
                if manager.download_model(target_model):
                    print_success(f"Successfully pulled '{target_model}'")
                else:
                    print_error(f"Failed to pull '{target_model}'.")
                    print_error("Please check your internet connection or disk space.")
                    sys.exit(1)
        except Exception:
             # Fallback to pull if list fails
             pass
    else:
        print_success(f"Model '{target_model}' is ready.")

    # 2b. Set Env Var for agent_utils.py to pick it up
    os.environ["OLLAMA_MODEL"] = target_model
    
    # 2c. Debug Dump - List what Ollama sees
    print_info(f"Setting OLLAMA_MODEL={target_model}")
    print_info("Verifying model visibility...")
    try:
        models = manager.list_models(force_refresh=True)
        available_names = [m.name for m in models]
        print_info(f"Available models in Ollama: {available_names}")
        if target_model not in available_names:
             print_warning(f"⚠️  Target model '{target_model}' not found in listing despite pull attempts.")
             
             # Fallback Strategy
             fallback_model = None
             
             # 1. Try close match
             for name in available_names:
                 if target_model.split(':')[0] in name:
                     fallback_model = name
                     break
            
             # 2. Try any llama3 (common for coding)
             if not fallback_model:
                 for name in available_names:
                     if "llama3" in name:
                         fallback_model = name
                         break

             # 3. Try FIRST available
             if not fallback_model and available_names:
                 fallback_model = available_names[0]

             if fallback_model:
                 print_warning(f"⚠️  Switching to available model: {fallback_model}")
                 target_model = fallback_model
                 os.environ["OLLAMA_MODEL"] = target_model
             else:
                 print_error("❌ No models available in Ollama. Demo requires at least one model.")
                 sys.exit(1)
    except Exception as e:
        print_error(f"Failed to list models: {e}")

    # 3. Launch Demo
    print_info(f"Environment verified. Launching Relay Chat Demo with model={target_model}...")
    print("-" * 50)
    try:
        run_relay_demo()
    except KeyboardInterrupt:
        print("\nDemo interrupted.")
    except Exception as e:
        print_error(f"Demo failed: {e}")
        # We don't exit here, we let finally clean up if we added cleanup logic
        
    print("-" * 50)
    print_success("Orchestration complete.")

if __name__ == "__main__":
    main()
