#!/usr/bin/env python3
"""
MLX Benchmark — Measure inference speed, latency, and throughput.

Usage:
    python mlx_benchmark.py                            # default benchmark
    python mlx_benchmark.py --preset coding --runs 3   # benchmark with preset
    python mlx_benchmark.py --latency                   # measure first-token latency
    python mlx_benchmark.py --compare q4 q8             # compare quantization levels
    python mlx_benchmark.py --sweep 10 50 100 200       # sweep max_tokens values

Thin orchestration script delegating to codomyrmex.llm.mlx.
"""

import sys
import time
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

import argparse
import importlib.util
import json

DEFAULT_PROMPTS = [
    "Explain quantum computing in one paragraph.",
    "Write a Python function that computes the Fibonacci sequence.",
    "What are the three laws of thermodynamics? Be concise.",
]


def run_benchmark(
    model: str,
    max_tokens: int,
    prompts: list[str],
    runs: int,
    temperature: float = 0.7,
    preset: str | None = None,
) -> dict:
    """Run inference benchmarks and return results."""
    from codomyrmex.llm.mlx.config import MLXConfig, MLXConfigPresets
    from codomyrmex.llm.mlx.runner import MLXRunner

    if preset:
        preset_fn = getattr(MLXConfigPresets, preset, None)
        if preset_fn:
            config = preset_fn()
            config.model = model
            config.max_tokens = max_tokens
        else:
            config = MLXConfig(model=model, max_tokens=max_tokens, temperature=temperature)
    else:
        config = MLXConfig(model=model, max_tokens=max_tokens, temperature=temperature)

    runner = MLXRunner(config)

    # Warmup — load model
    print(f"🔄 Loading model: {model}")
    t0 = time.perf_counter()
    runner.load_model()
    load_time = time.perf_counter() - t0
    print(f"✅ Model loaded in {load_time:.2f}s")
    print()

    results = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": config.temperature,
        "preset": preset,
        "load_time_seconds": round(load_time, 3),
        "runs": [],
    }

    for run_idx in range(runs):
        print(f"--- Run {run_idx + 1}/{runs} ---")
        run_results = []

        for i, prompt in enumerate(prompts):
            short_prompt = prompt[:50] + ("..." if len(prompt) > 50 else "")
            print(f"  [{i+1}/{len(prompts)}] {short_prompt}")

            result = runner.generate(prompt, config=config)

            entry = {
                "prompt": prompt,
                "response_length": len(result.response),
                "tokens_generated": result.tokens_generated,
                "tokens_per_second": result.tokens_per_second,
                "execution_time": round(result.execution_time, 3),
                "success": result.success,
            }
            run_results.append(entry)

            if result.success:
                print(
                    f"    ✅ {result.tokens_generated} tokens in {result.execution_time:.2f}s "
                    f"({result.tokens_per_second:.1f} tok/s)"
                )
            else:
                print(f"    ❌ {result.error_message}")

        results["runs"].append(run_results)
        print()

    # Compute aggregate stats
    all_tps = [
        r["tokens_per_second"]
        for run in results["runs"]
        for r in run
        if r["success"] and r["tokens_per_second"]
    ]
    all_times = [
        r["execution_time"]
        for run in results["runs"]
        for r in run
        if r["success"]
    ]

    if all_tps:
        results["aggregate"] = {
            "avg_tokens_per_second": round(sum(all_tps) / len(all_tps), 2),
            "max_tokens_per_second": round(max(all_tps), 2),
            "min_tokens_per_second": round(min(all_tps), 2),
            "avg_execution_time": round(sum(all_times) / len(all_times), 3),
            "total_prompts": len(all_tps),
        }

    runner.unload_model()
    return results


def measure_latency(model: str, num_trials: int = 5) -> dict:
    """Measure first-token latency (time to first token via streaming)."""
    from codomyrmex.llm.mlx.config import MLXConfig
    from codomyrmex.llm.mlx.runner import MLXRunner

    config = MLXConfig(model=model, max_tokens=1)
    runner = MLXRunner(config)

    print(f"🔄 Loading model: {model}")
    t0 = time.perf_counter()
    runner.load_model()
    load_time = time.perf_counter() - t0
    print(f"✅ Model loaded in {load_time:.2f}s\n")

    prompt = "Hello"
    latencies = []

    for i in range(num_trials):
        config_trial = MLXConfig(model=model, max_tokens=10)
        t0 = time.perf_counter()
        for chunk in runner.stream_generate(prompt, config=config_trial):
            if not chunk.done:
                first_token_time = time.perf_counter() - t0
                latencies.append(first_token_time)
                break

        print(f"  Trial {i+1}: {latencies[-1]*1000:.1f}ms")

    runner.unload_model()

    results = {
        "model": model,
        "trials": num_trials,
        "latencies_ms": [round(l * 1000, 1) for l in latencies],
        "avg_latency_ms": round(sum(latencies) / len(latencies) * 1000, 1) if latencies else None,
        "min_latency_ms": round(min(latencies) * 1000, 1) if latencies else None,
        "max_latency_ms": round(max(latencies) * 1000, 1) if latencies else None,
        "p50_latency_ms": round(sorted(latencies)[len(latencies) // 2] * 1000, 1) if latencies else None,
    }
    return results


def sweep_tokens(model: str, token_counts: list[int], prompt: str | None = None) -> dict:
    """Sweep max_tokens to find throughput at different generation lengths."""
    from codomyrmex.llm.mlx.config import MLXConfig
    from codomyrmex.llm.mlx.runner import MLXRunner

    test_prompt = prompt or "Write a detailed explanation of how computers work."

    config = MLXConfig(model=model)
    runner = MLXRunner(config)
    runner.load_model()

    results = {"model": model, "sweeps": []}

    for count in token_counts:
        cfg = MLXConfig(model=model, max_tokens=count)
        result = runner.generate(test_prompt, config=cfg)
        entry = {
            "max_tokens": count,
            "actual_tokens": result.tokens_generated,
            "tokens_per_second": result.tokens_per_second,
            "execution_time": round(result.execution_time, 3),
            "success": result.success,
        }
        results["sweeps"].append(entry)
        status = f"✅ {result.tokens_per_second:.1f} tok/s" if result.success else "❌"
        print(f"  max_tokens={count:>4d}: {status} ({result.execution_time:.2f}s)")

    runner.unload_model()
    return results


def print_summary(results: dict):
    """Print a formatted summary of benchmark results."""
    print("=" * 60)
    print("📊  RESULTS SUMMARY")
    print("=" * 60)
    print(f"  Model:       {results['model']}")
    print(f"  Load time:   {results.get('load_time_seconds', 'N/A')}s")

    if "aggregate" in results:
        agg = results["aggregate"]
        print(f"  Avg tok/s:   {agg['avg_tokens_per_second']:.1f}")
        print(f"  Max tok/s:   {agg['max_tokens_per_second']:.1f}")
        print(f"  Min tok/s:   {agg['min_tokens_per_second']:.1f}")
        print(f"  Avg time:    {agg['avg_execution_time']:.2f}s")
        print(f"  Prompts run: {agg['total_prompts']}")

    if results.get("preset"):
        print(f"  Preset:      {results['preset']}")


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark MLX model inference",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--model",
        default="mlx-community/Llama-3.2-3B-Instruct-4bit",
        help="Model to benchmark",
    )
    parser.add_argument(
        "--max-tokens", type=int, default=100, help="Max tokens per generation"
    )
    parser.add_argument(
        "--prompt", default=None, help="Custom prompt (overrides defaults)"
    )
    parser.add_argument(
        "--runs", type=int, default=1, help="Number of benchmark runs"
    )
    parser.add_argument(
        "--temperature", type=float, default=0.7, help="Temperature"
    )
    parser.add_argument(
        "--preset",
        choices=["creative", "precise", "fast", "comprehensive", "coding"],
        default=None,
        help="Use a config preset",
    )
    parser.add_argument(
        "--output", default=None, help="Save results to JSON file"
    )
    parser.add_argument(
        "--latency", action="store_true", help="Measure first-token latency"
    )
    parser.add_argument(
        "--latency-trials", type=int, default=5, help="Number of latency trials"
    )
    parser.add_argument(
        "--sweep",
        nargs="+",
        type=int,
        default=None,
        metavar="N",
        help="Sweep max_tokens values (e.g., 10 50 100 200)",
    )
    args = parser.parse_args()

    if not importlib.util.find_spec("mlx"):
        print("❌ MLX is not installed. Install with: pip install mlx-lm")
        return 1

    print("=" * 60)
    print("🏎️  MLX BENCHMARK")
    print("=" * 60)
    print(f"  Model: {args.model}")

    if args.latency:
        print(f"  Mode: First-token latency ({args.latency_trials} trials)")
        print("=" * 60)
        print()
        results = measure_latency(args.model, args.latency_trials)
        print()
        print(f"  Avg latency:  {results['avg_latency_ms']}ms")
        print(f"  P50 latency:  {results['p50_latency_ms']}ms")
        print(f"  Min latency:  {results['min_latency_ms']}ms")
        print(f"  Max latency:  {results['max_latency_ms']}ms")

    elif args.sweep:
        print(f"  Mode: Token sweep ({args.sweep})")
        print("=" * 60)
        print()
        results = sweep_tokens(args.model, args.sweep, args.prompt)

    else:
        prompts = [args.prompt] if args.prompt else DEFAULT_PROMPTS
        if args.preset:
            print(f"  Preset: {args.preset}")
        print(f"  Max tokens: {args.max_tokens}")
        print(f"  Prompts:    {len(prompts)}")
        print(f"  Runs:       {args.runs}")
        print("=" * 60)
        print()

        results = run_benchmark(
            args.model, args.max_tokens, prompts, args.runs,
            temperature=args.temperature, preset=args.preset,
        )
        print_summary(results)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n📁  Results saved to {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
