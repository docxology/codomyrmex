#!/usr/bin/env python3
"""
Multimodal Image Generation Orchestrator

Config-driven orchestrator for generating images via Google AI (Imagen 3).
Reads all generation parameters from config/multimodal/config.yaml.

Requirements:
    uv sync
    GEMINI_API_KEY environment variable (for live generation)

Usage:
    # Dry run (no API key needed)
    uv run python scripts/multimodal/orchestrate.py

    # Live generation
    GEMINI_API_KEY=<key> uv run python scripts/multimodal/orchestrate.py

    # Override prompt
    GEMINI_API_KEY=<key> uv run python scripts/multimodal/orchestrate.py --prompt "A mountain at sunset"
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("PyYAML required: uv add pyyaml")
    sys.exit(1)

try:
    import codomyrmex  # noqa: F401
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.multimodal.image_generation import ImageGenerator
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_section,
    print_success,
    setup_logging,
)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_CONFIG_PATH = _PROJECT_ROOT / "config" / "multimodal" / "config.yaml"


def load_config() -> dict:
    with open(_CONFIG_PATH) as f:
        return yaml.safe_load(f)


def run_image_generation(
    config: dict,
    prompt_override: str | None = None,
    model_override: str | None = None,
    aspect_ratio_override: str | None = None,
    images_override: int | None = None,
) -> bool:
    """Generate images using parameters from config.

    Returns True on success, False on error or missing API key.
    """
    gen_cfg = config.get("generation", {}).get("image", {})

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print_error("GEMINI_API_KEY not set — cannot run live generation.")
        print_info("  Export GEMINI_API_KEY=<your-key> to enable generation.")
        print_info(f"  Config: {_CONFIG_PATH.relative_to(_PROJECT_ROOT)}")
        return False

    model = model_override or gen_cfg.get("model", "imagen-4.0-generate-001")
    prompts = gen_cfg.get("prompts", ["A photorealistic landscape at golden hour"])
    if prompt_override:
        prompts = [prompt_override]
    number_of_images = images_override or gen_cfg.get("number_of_images", 1)
    aspect_ratio = aspect_ratio_override or gen_cfg.get("aspect_ratio", "1:1")
    output_dir_str = config.get("output_dir_override") or gen_cfg.get(
        "output_dir", "output"
    )
    output_dir = _PROJECT_ROOT / output_dir_str
    save_format = gen_cfg.get("save_format", "png")

    print_info(f"  Model:            {model}")
    print_info(f"  Prompts to run:   {len(prompts)}")
    print_info(f"  Images per pop:   {number_of_images}")
    print_info(f"  Aspect ratio:     {aspect_ratio}")
    print_info(f"  Output dir:       {output_dir_str}")

    generator = ImageGenerator()
    output_dir.mkdir(parents=True, exist_ok=True)
    saved = 0

    for p_idx, act_prompt in enumerate(prompts):
        print_info(
            f"  [{p_idx + 1}/{len(prompts)}] Generating for: {act_prompt[:60]}..."
        )
        try:
            results = generator.generate(
                prompt=act_prompt,
                model=model,
                number_of_images=number_of_images,
                aspect_ratio=aspect_ratio,
            )
            for _i, img in enumerate(results):
                image_bytes = img.get("image_bytes") or img.get("image_data")
                if image_bytes:
                    total_idx = saved + 1
                    out_path = output_dir / f"image_{total_idx}.{save_format}"
                    out_path.write_bytes(image_bytes)
                    print_success(f"    Saved → {out_path.relative_to(_PROJECT_ROOT)}")
                    saved += 1
                else:
                    print_info(f"    Result keys: {list(img.keys())}")
        except Exception as e:
            print_error(f"  Generation failed for prompt {p_idx + 1}: {e}")

    if saved:
        print_success(f"  {saved} total file(s) written to {output_dir_str}")

    return saved > 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Multimodal image generation orchestrator"
    )
    parser.add_argument("--prompt", help="Override default prompt from config")
    parser.add_argument("--model", help="Override default model from config")
    parser.add_argument(
        "--aspect-ratio",
        choices=["1:1", "16:9", "9:16", "4:3", "3:4"],
        help="Override aspect ratio",
    )
    parser.add_argument(
        "--images", type=int, help="Override number of images to generate"
    )
    parser.add_argument("--output-dir", help="Override output directory")
    return parser.parse_args()


def main() -> int:
    setup_logging()
    args = parse_args()

    print_section("Multimodal Image Generation Orchestrator")
    print_info(f"Config: {_CONFIG_PATH.relative_to(_PROJECT_ROOT)}")

    config = load_config()
    ok = run_image_generation(
        config,
        prompt_override=args.prompt,
        model_override=args.model,
        aspect_ratio_override=args.aspect_ratio,
        images_override=args.images,
    )

    if ok:
        print_section("Orchestration Complete")
        return 0
    print_error("Orchestration failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
