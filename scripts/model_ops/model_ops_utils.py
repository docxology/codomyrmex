#!/usr/bin/env python3
"""
Model operations utilities.

Usage:
    python model_ops_utils.py <command> [options]
"""

import sys
from pathlib import Path

try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import json
import os


def find_models(path: str = ".") -> list:
    """Find model files."""
    p = Path(path)
    extensions = [".pt", ".pth", ".h5", ".keras", ".onnx", ".pkl", ".joblib", ".safetensors"]
    
    found = []
    for ext in extensions:
        found.extend(p.rglob(f"*{ext}"))
    
    return found


def get_model_info(path: Path) -> dict:
    """Get model file info."""
    stat = path.stat()
    return {
        "path": str(path),
        "name": path.name,
        "size_mb": round(stat.st_size / (1024 * 1024), 2),
        "format": path.suffix,
    }


def list_model_registries() -> dict:
    """Check for common model registries."""
    registries = {
        "huggingface": {"installed": False, "cache": None},
        "ollama": {"installed": False, "models": []},
        "mlflow": {"installed": False},
    }
    
    # Check HuggingFace
    hf_cache = Path.home() / ".cache" / "huggingface"
    if hf_cache.exists():
        registries["huggingface"]["installed"] = True
        registries["huggingface"]["cache"] = str(hf_cache)
    
    # Check Ollama
    ollama_dir = Path.home() / ".ollama"
    if ollama_dir.exists():
        registries["ollama"]["installed"] = True
    
    return registries


def main():
    parser = argparse.ArgumentParser(description="Model operations utilities")
    subparsers = parser.add_subparsers(dest="command")
    
    # Find command
    find = subparsers.add_parser("find", help="Find model files")
    find.add_argument("path", nargs="?", default=".")
    
    # Registries command
    subparsers.add_parser("registries", help="List model registries")
    
    # Info command
    info = subparsers.add_parser("info", help="Get model info")
    info.add_argument("path", help="Model file path")
    
    args = parser.parse_args()
    
    if not args.command:
        print("🤖 Model Ops Utilities\n")
        print("Commands:")
        print("  find       - Find model files")
        print("  registries - List model registries")
        print("  info       - Get model info")
        return 0
    
    if args.command == "find":
        models = find_models(args.path)
        print(f"🔍 Found {len(models)} model files:\n")
        
        for m in models[:20]:
            info = get_model_info(m)
            print(f"   📦 {info['name']} ({info['size_mb']} MB)")
        
        if len(models) > 20:
            print(f"\n   ... and {len(models) - 20} more")
    
    elif args.command == "registries":
        registries = list_model_registries()
        print("📚 Model Registries:\n")
        
        for name, info in registries.items():
            status = "✅" if info["installed"] else "⚪"
            print(f"   {status} {name.title()}")
            if info.get("cache"):
                print(f"      Cache: {info['cache']}")
    
    elif args.command == "info":
        path = Path(args.path)
        if not path.exists():
            print(f"❌ File not found: {args.path}")
            return 1
        
        info = get_model_info(path)
        print(f"📦 Model: {info['name']}\n")
        print(f"   Size: {info['size_mb']} MB")
        print(f"   Format: {info['format']}")
        print(f"   Path: {info['path']}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
