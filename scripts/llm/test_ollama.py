#!/usr/bin/env python3
"""
Test Ollama LLM connectivity and list available models.

Usage:
    python test_ollama.py [--host HOST] [--port PORT] [--model MODEL]
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import json


def check_ollama_connection(host: str, port: int) -> bool:
    """Check if Ollama server is accessible."""
    import urllib.error
    import urllib.request

    try:
        url = f"http://{host}:{port}/api/tags"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200
    except (urllib.error.URLError, ConnectionRefusedError):
        return False


def list_models(host: str, port: int) -> list:
    """List available Ollama models."""
    import urllib.request

    url = f"http://{host}:{port}/api/tags"
    req = urllib.request.Request(url, method="GET")

    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode())
        return data.get("models", [])


def test_inference(host: str, port: int, model: str, prompt: str = "Hello, how are you?") -> str:
    """Run a simple inference test."""
    import urllib.request

    url = f"http://{host}:{port}/api/generate"
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False
    }).encode()

    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=60) as response:
        data = json.loads(response.read().decode())
        return data.get("response", "")


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "llm" / "config.yaml"
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print("Loaded config from config/llm/config.yaml")

    parser = argparse.ArgumentParser(description="Test Ollama LLM connectivity")
    parser.add_argument("--host", default="localhost", help="Ollama host (default: localhost)")
    parser.add_argument("--port", type=int, default=11434, help="Ollama port (default: 11434)")
    parser.add_argument("--model", default=None, help="Model to test inference with")
    parser.add_argument("--prompt", default="Say hello in one sentence.", help="Test prompt")
    args = parser.parse_args()

    print(f"🔍 Testing Ollama connection at {args.host}:{args.port}...")

    if not check_ollama_connection(args.host, args.port):
        print("❌ Failed to connect to Ollama server")
        print("   Make sure Ollama is running: ollama serve")
        return 1

    print("✅ Ollama server is accessible")

    print("\n📋 Available models:")
    models = list_models(args.host, args.port)
    if not models:
        print("   No models found. Install a model: ollama pull llama2")
    else:
        for model in models:
            name = model.get("name", "unknown")
            size = model.get("size", 0) / (1024**3)  # Convert to GB
            print(f"   - {name} ({size:.1f} GB)")

    if args.model:
        print(f"\n🧪 Testing inference with {args.model}...")
        try:
            response = test_inference(args.host, args.port, args.model, args.prompt)
            print(f"   Prompt: {args.prompt}")
            print(f"   Response: {response[:200]}{'...' if len(response) > 200 else ''}")
            print("✅ Inference test passed")
        except Exception as e:
            print(f"❌ Inference test failed: {e}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
