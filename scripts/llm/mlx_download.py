#!/usr/bin/env python3
"""
MLX Download — Download, list, and manage MLX models.

Usage:
    python mlx_download.py                           # download default model
    python mlx_download.py --model ORG/MODEL         # download specific model
    python mlx_download.py --list                    # list cached models
    python mlx_download.py --delete ORG/MODEL        # delete a cached model
    python mlx_download.py --recommend               # show model recommendations
    python mlx_download.py --info ORG/MODEL          # show model details

Thin orchestration script delegating to codomyrmex.llm.mlx.
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import importlib.util


def cmd_download(model: str, cache_dir: str | None) -> int:
    """Download a model from HuggingFace Hub."""
    from codomyrmex.llm.mlx.config import MLXConfig
    from codomyrmex.llm.mlx.model_manager import MLXModelManager

    config_kwargs = {}
    if cache_dir:
        config_kwargs["cache_dir"] = cache_dir

    config = MLXConfig(**config_kwargs)
    mgr = MLXModelManager(config)

    if mgr.is_model_cached(model):
        print(f"✅ Model already cached: {model}")
        info = mgr.get_model_info(model)
        if info:
            size_gb = info.size_bytes / (1024**3)
            print(f"   Size: {size_gb:.2f} GB")
            print(f"   Path: {info.local_path}")
        return 0

    print(f"⬇️  Downloading: {model}")
    try:
        path = mgr.download_model(model)
        print(f"✅ Downloaded to: {path}")

        info = mgr.get_model_info(model)
        if info:
            size_gb = info.size_bytes / (1024**3)
            print(f"   Size: {size_gb:.2f} GB")
        return 0
    except Exception as exc:
        print(f"❌ Download failed: {exc}", file=sys.stderr)
        return 1


def cmd_list(cache_dir: str | None) -> int:
    """List all cached models."""
    from codomyrmex.llm.mlx.config import MLXConfig
    from codomyrmex.llm.mlx.model_manager import MLXModelManager

    config_kwargs = {}
    if cache_dir:
        config_kwargs["cache_dir"] = cache_dir

    config = MLXConfig(**config_kwargs)
    mgr = MLXModelManager(config)
    models = mgr.list_cached_models()

    print(f"📁 Cache directory: {config.cache_dir}")
    print()

    if not models:
        print("  No models cached.")
        return 0

    total_size = 0
    for m in models:
        size_gb = m.size_bytes / (1024**3)
        total_size += m.size_bytes
        quant = m.quantization or "unknown quant"
        model_type = m.model_type or "unknown type"
        print(f"  📦 {m.repo_id}")
        print(f"     {size_gb:.2f} GB | {quant} | {model_type}")
        if m.vocab_size:
            print(
                f"     vocab={m.vocab_size} hidden={m.hidden_size} layers={m.num_layers}"
            )
        print()

    total_gb = total_size / (1024**3)
    print(f"  Total: {len(models)} model(s), {total_gb:.2f} GB")
    return 0


def cmd_delete(model: str, cache_dir: str | None) -> int:
    """Delete a cached model."""
    from codomyrmex.llm.mlx.config import MLXConfig
    from codomyrmex.llm.mlx.model_manager import MLXModelManager

    config_kwargs = {}
    if cache_dir:
        config_kwargs["cache_dir"] = cache_dir

    config = MLXConfig(**config_kwargs)
    mgr = MLXModelManager(config)

    info = mgr.get_model_info(model)
    if not info:
        print(f"❌ Model not found in cache: {model}")
        return 1

    size_gb = info.size_bytes / (1024**3)
    print(f"🗑️  Deleting {model} ({size_gb:.2f} GB)...")

    if mgr.delete_model(model):
        print("✅ Deleted successfully.")
        return 0
    print("❌ Deletion failed.")
    return 1


def cmd_info(model: str, cache_dir: str | None) -> int:
    """Show detailed info for a cached model."""
    from codomyrmex.llm.mlx.config import MLXConfig
    from codomyrmex.llm.mlx.model_manager import MLXModelManager

    config_kwargs = {}
    if cache_dir:
        config_kwargs["cache_dir"] = cache_dir

    config = MLXConfig(**config_kwargs)
    mgr = MLXModelManager(config)

    info = mgr.get_model_info(model)
    if not info:
        print(f"❌ Model not found in cache: {model}")
        print("   Use --list to see cached models, or --download to fetch it.")
        return 1

    size_gb = info.size_bytes / (1024**3)
    print(f"📦 {info.repo_id}")
    print(f"   Path:            {info.local_path}")
    print(f"   Size:            {size_gb:.2f} GB ({info.size_bytes:,} bytes)")
    print(f"   Quantization:    {info.quantization or 'unknown'}")
    print(f"   Model type:      {info.model_type or 'unknown'}")
    print(f"   Vocab size:      {info.vocab_size or 'unknown'}")
    print(f"   Hidden size:     {info.hidden_size or 'unknown'}")
    print(f"   Layers:          {info.num_layers or 'unknown'}")
    print(f"   Max positions:   {info.max_position_embeddings or 'unknown'}")

    # Memory estimation
    est_ram = MLXModelManager.estimate_memory_gb(
        total_params_billions=size_gb * 2,  # rough: 4-bit ≈ 0.5 bytes/param
        bits=4,
    )
    print(f"   Est. RAM (4-bit): ~{est_ram:.1f} GB")
    return 0


def cmd_recommend(ram_gb: int | None) -> int:
    """Show model recommendations for given RAM."""
    import platform
    import subprocess

    if ram_gb is None:
        try:
            result = subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                ram_gb = int(int(result.stdout.strip()) / (1024**3))
        except Exception:
            pass
        if ram_gb is None:
            ram_gb = 16

    from codomyrmex.llm.mlx.config import get_models_for_ram
    from codomyrmex.llm.mlx.model_manager import MLXModelManager

    recs = get_models_for_ram(ram_gb)

    print(f"💡 Recommended models for {ram_gb} GB RAM:")
    print()

    for rec in recs:
        est_ram = MLXModelManager.estimate_memory_gb(rec.approx_size_gb * 2, bits=4)
        print(f"  🏷️  {rec.label}")
        print(f"     {rec.repo_id}")
        print(
            f"     Download: ~{rec.approx_size_gb} GB | Runtime RAM: ~{est_ram:.1f} GB"
        )
        print(f"     {rec.notes}")
        print()

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="MLX model management — download, list, inspect, delete"
    )
    parser.add_argument(
        "--model",
        default="mlx-community/Llama-3.2-3B-Instruct-4bit",
        help="Model repo id (default: Llama-3.2-3B-Instruct-4bit)",
    )
    parser.add_argument("--cache-dir", default=None, help="Override cache directory")
    parser.add_argument("--list", action="store_true", help="List all cached models")
    parser.add_argument("--delete", metavar="MODEL", help="Delete a cached model")
    parser.add_argument("--info", metavar="MODEL", help="Show model details")
    parser.add_argument(
        "--recommend", action="store_true", help="Show model recommendations"
    )
    parser.add_argument(
        "--ram", type=int, default=None, help="RAM in GB for recommendations"
    )

    args = parser.parse_args()

    if not importlib.util.find_spec("mlx"):
        print("❌ MLX is not installed. Install: pip install mlx-lm", file=sys.stderr)
        return 1

    if args.list:
        return cmd_list(args.cache_dir)
    if args.delete:
        return cmd_delete(args.delete, args.cache_dir)
    if args.info:
        return cmd_info(args.info, args.cache_dir)
    if args.recommend:
        return cmd_recommend(args.ram)
    return cmd_download(args.model, args.cache_dir)


if __name__ == "__main__":
    sys.exit(main())
