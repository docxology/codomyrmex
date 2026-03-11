#!/usr/bin/env python3
"""
MLX Test — Unified test runner for the MLX submodule.

Usage:
    python mlx_test.py               # run all MLX tests (pure-logic only by default)
    python mlx_test.py --integration # include integration tests
    python mlx_test.py --smoke       # quick smoke test: load model + one generation
    python mlx_test.py --validate    # full validation: tests + import chain + status

Thin orchestration script delegating to pytest and codomyrmex.llm.mlx.
"""

import sys
import time
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import importlib.util
import subprocess


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TEST_DIR = PROJECT_ROOT / "src" / "codomyrmex" / "tests" / "unit" / "llm"
TEST_FILES = sorted(TEST_DIR.glob("test_mlx_*.py"))


def run_pytest(markers: str | None = None, verbose: bool = True) -> int:
    """Run pytest on the MLX test files."""
    cmd = [
        sys.executable, "-m", "pytest",
        *[str(f) for f in TEST_FILES],
        "--tb=short",
        "--no-cov",
    ]
    if verbose:
        cmd.append("-v")
    if markers:
        cmd.extend(["-m", markers])

    print(f"🧪 Running: {' '.join(cmd[-4:])}")
    print()

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    return result.returncode


def smoke_test() -> int:
    """Quick smoke test: verify import, load model, generate one response."""
    print("=" * 60)
    print("🔥 MLX SMOKE TEST")
    print("=" * 60)
    print()

    # 1. Import check
    print("1️⃣  Import check...")
    try:
        from codomyrmex.llm.mlx import (
            MLXConfig,
            MLXConfigPresets,
            MLXGenerationResult,
            MLXModelManager,
            MLXQuantizer,
            MLXRunner,
            MLXStreamChunk,
        )
        print("   ✅ All imports successful")
    except ImportError as exc:
        print(f"   ❌ Import failed: {exc}")
        return 1

    # 2. Config validation
    print("2️⃣  Config validation...")
    config = MLXConfig()
    result = config.validate()
    if result["valid"]:
        print(f"   ✅ Default config valid (model={config.model})")
    else:
        print(f"   ❌ Config invalid: {result['errors']}")
        return 1

    # 3. MLX availability
    if not importlib.util.find_spec("mlx"):
        print("3️⃣  MLX not installed — skipping model tests")
        print("\n✅ Smoke test passed (import + config only)")
        return 0

    # 4. Model check
    print("3️⃣  Model check...")
    mgr = MLXModelManager(config)
    if not mgr.is_model_cached(config.model):
        print(f"   ⚠️  Model not cached: {config.model}")
        print("   Use: python mlx_download.py to download it first")
        print("\n✅ Smoke test passed (import + config only)")
        return 0

    # 5. Load + generate
    print("4️⃣  Loading model...")
    runner = MLXRunner(config)
    t0 = time.perf_counter()
    try:
        runner.load_model()
        load_time = time.perf_counter() - t0
        print(f"   ✅ Loaded in {load_time:.2f}s")
    except Exception as exc:
        print(f"   ❌ Load failed: {exc}")
        return 1

    print("5️⃣  Generating text...")
    gen_config = MLXConfig(model=config.model, max_tokens=30, temperature=0.5)
    result = runner.generate("What is 2+2? Answer with just the number.", config=gen_config)
    if result.success:
        response_preview = result.response[:100].replace("\n", " ")
        print(f"   ✅ Response: {response_preview}")
        print(f"   ✅ {result.tokens_generated} tokens, {result.tokens_per_second:.1f} tok/s")
    else:
        print(f"   ❌ Generation failed: {result.error_message}")
        runner.unload_model()
        return 1

    print("6️⃣  Streaming test...")
    stream_config = MLXConfig(model=config.model, max_tokens=10)
    chunks = list(runner.stream_generate("Count to 3.", config=stream_config))
    if chunks and chunks[-1].done:
        text = "".join(c.content for c in chunks if not c.done)
        print(f"   ✅ Streamed: {text[:80].replace(chr(10), ' ')}")
    else:
        print("   ❌ Streaming failed")
        runner.unload_model()
        return 1

    print("7️⃣  Chat test...")
    chat_result = runner.chat(
        [{"role": "user", "content": "Say 'hello' in French."}],
        config=gen_config,
    )
    if chat_result.success:
        print(f"   ✅ Chat: {chat_result.response[:80].replace(chr(10), ' ')}")
    else:
        print(f"   ❌ Chat failed: {chat_result.error_message}")
        runner.unload_model()
        return 1

    runner.unload_model()
    print()
    print("✅ All smoke tests passed!")
    return 0


def full_validate() -> int:
    """Full validation: tests + smoke test + structural checks."""
    print("=" * 60)
    print("🔍 MLX FULL VALIDATION")
    print("=" * 60)
    print()

    errors = 0

    # 1. Structural check
    print("📂 Checking file structure...")
    required_files = [
        "src/codomyrmex/llm/mlx/__init__.py",
        "src/codomyrmex/llm/mlx/config.py",
        "src/codomyrmex/llm/mlx/model_manager.py",
        "src/codomyrmex/llm/mlx/runner.py",
        "src/codomyrmex/llm/mlx/quantization.py",
        "src/codomyrmex/llm/mlx/README.md",
        "src/codomyrmex/llm/mlx/AGENTS.md",
        "src/codomyrmex/llm/mlx/SPEC.md",
    ]
    for rel_path in required_files:
        full_path = PROJECT_ROOT / rel_path
        if full_path.exists():
            print(f"   ✅ {rel_path}")
        else:
            print(f"   ❌ Missing: {rel_path}")
            errors += 1

    print()

    # 2. Import chain
    print("🔗 Checking import chain...")
    try:
        from codomyrmex.llm import mlx as mlx_mod
        exports = dir(mlx_mod)
        expected = ["MLXConfig", "MLXRunner", "MLXModelManager", "MLXQuantizer"]
        for name in expected:
            if name in exports:
                print(f"   ✅ codomyrmex.llm.mlx.{name}")
            else:
                print(f"   ❌ Missing export: {name}")
                errors += 1
    except ImportError as exc:
        print(f"   ❌ Import chain broken: {exc}")
        errors += 1

    print()

    # 3. Pure-logic tests
    print("🧪 Running pure-logic tests...")
    rc = run_pytest(markers="unit")
    if rc != 0:
        errors += 1

    print()

    # 4. Smoke test
    rc = smoke_test()
    if rc != 0:
        errors += 1

    print()
    print("=" * 60)
    if errors == 0:
        print("✅ FULL VALIDATION PASSED")
    else:
        print(f"❌ VALIDATION FAILED ({errors} error(s))")
    print("=" * 60)
    return 1 if errors else 0


def main():
    parser = argparse.ArgumentParser(description="MLX submodule test suite runner")
    parser.add_argument("--integration", action="store_true", help="Include integration tests")
    parser.add_argument("--smoke", action="store_true", help="Quick smoke test only")
    parser.add_argument("--validate", action="store_true", help="Full validation suite")
    parser.add_argument("-v", "--verbose", action="store_true", default=True, help="Verbose output")
    args = parser.parse_args()

    if args.smoke:
        return smoke_test()

    if args.validate:
        return full_validate()

    # Default: run pytest
    markers = None if args.integration else "unit"
    return run_pytest(markers=markers, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
