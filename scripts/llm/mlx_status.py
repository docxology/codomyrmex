#!/usr/bin/env python3
"""
MLX Status — Check MLX availability, hardware info, and cached models.

Usage:
    python mlx_status.py [--cache-dir DIR] [--ram RAM_GB]

Thin orchestration script delegating to codomyrmex.llm.mlx.
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
import importlib.util
import platform
import subprocess


def get_hardware_info() -> dict:
    """Collect Apple Silicon hardware info."""
    info = {"platform": platform.platform(), "machine": platform.machine()}
    try:
        result = subprocess.run(
            ["sysctl", "-n", "hw.memsize"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            info["total_ram_gb"] = round(int(result.stdout.strip()) / (1024**3), 1)
    except Exception:
        info["total_ram_gb"] = "unknown"

    try:
        result = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            info["chip"] = result.stdout.strip()
    except Exception:
        info["chip"] = "unknown"

    return info


def main():
    parser = argparse.ArgumentParser(description="Check MLX status and cached models")
    parser.add_argument(
        "--cache-dir",
        default=None,
        help="Model cache directory (default: ~/.cache/mlx-models)",
    )
    parser.add_argument(
        "--ram",
        type=int,
        default=None,
        help="Override RAM in GB for model recommendations",
    )
    args = parser.parse_args()

    # 1. Hardware
    print("=" * 60)
    print("🖥️  HARDWARE INFO")
    print("=" * 60)
    hw = get_hardware_info()
    for k, v in hw.items():
        print(f"  {k}: {v}")

    # 2. MLX availability
    print()
    print("=" * 60)
    print("📦  MLX PACKAGES")
    print("=" * 60)
    packages = ["mlx", "mlx_lm", "mlx_metal"]
    for pkg in packages:
        spec = importlib.util.find_spec(pkg)
        if spec:
            try:
                mod = __import__(pkg)
                ver = getattr(mod, "__version__", "installed")
                print(f"  ✅ {pkg}: {ver}")
            except Exception:
                print(f"  ✅ {pkg}: installed (version unknown)")
        else:
            print(f"  ❌ {pkg}: not installed")

    if not importlib.util.find_spec("mlx"):
        print("\n⚠️  MLX is not installed. Install with: pip install mlx-lm")
        return 1

    # 3. Cached models
    print()
    print("=" * 60)
    print("💾  CACHED MODELS")
    print("=" * 60)

    from codomyrmex.llm.mlx.config import MLXConfig
    from codomyrmex.llm.mlx.model_manager import MLXModelManager

    config_kwargs = {}
    if args.cache_dir:
        config_kwargs["cache_dir"] = args.cache_dir

    config = MLXConfig(**config_kwargs)
    mgr = MLXModelManager(config)
    models = mgr.list_cached_models()

    if not models:
        print("  No models cached.")
        print(f"  Cache dir: {config.cache_dir}")
    else:
        for m in models:
            size_gb = m.size_bytes / (1024**3)
            quant = m.quantization or "unknown"
            print(f"  📁 {m.repo_id}")
            print(f"     Size: {size_gb:.2f} GB | Quantization: {quant}")
            if m.model_type:
                print(f"     Type: {m.model_type}")
            print()

    # 4. Model recommendations
    ram_gb = args.ram or hw.get("total_ram_gb", 16)
    if isinstance(ram_gb, str):
        ram_gb = 16

    print("=" * 60)
    print(f"💡  RECOMMENDED MODELS (for {ram_gb} GB RAM)")
    print("=" * 60)

    from codomyrmex.llm.mlx.config import get_models_for_ram

    recs = get_models_for_ram(int(ram_gb))
    for rec in recs:
        cached = mgr.is_model_cached(rec.repo_id)
        status = "✅ cached" if cached else "⬇️  not cached"
        print(f"  {rec.label} [{status}]")
        print(f"    {rec.repo_id}")
        print(f"    ~{rec.approx_size_gb} GB | {rec.notes}")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
