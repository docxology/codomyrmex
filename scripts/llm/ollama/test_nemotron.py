#!/usr/bin/env python3
"""
Test nemotron-3-nano:30b Model Availability and Configuration

This script verifies that nemotron-3-nano:30b is available and can be accessed.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from codomyrmex.llm.ollama import OllamaManager

def main():
    print("="*60)
    print("Testing rnj-1:8b Availability (32K context)")
    print("="*60)
    
    manager = OllamaManager(use_http_api=True)
    
    # Check if model is available
    model_name = "rnj-1:8b"
    print(f"\n📋 Checking for model: {model_name}")
    
    # List all models
    models = manager.list_models(force_refresh=True)
    print(f"   Found {len(models)} total models")
    
    # Check specifically for nemotron
    nemotron_available = manager.is_model_available(model_name)
    
    if nemotron_available:
        print(f"✅ {model_name} is available!")
        model_info = manager.get_model_by_name(model_name)
        if model_info:
            size_gb = model_info.size / (1024**3)
            print(f"   Size: {size_gb:.2f} GB")
            print(f"   ID: {model_info.id}")
            print(f"   Modified: {model_info.modified}")
        return True
    else:
        print(f"❌ {model_name} is not available")
        print(f"\n📥 Attempting to pull {model_name}...")
        success = manager.download_model(model_name)
        if success:
            print(f"✅ Successfully pulled {model_name}")
            return True
        else:
            print(f"❌ Failed to pull {model_name}")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

