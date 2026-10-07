#!/usr/bin/env python3
"""
Build Synthesis - Real Usage Examples

Demonstrates actual build capabilities (the former ``build_synthesis`` module
now lives in ``codomyrmex.ci_cd_automation.build``):
- Supported build language enumeration
- Build configuration validation and manifest creation
- Build environment check
"""

import sys
from pathlib import Path

# Ensure codomyrmex is in path
try:
    import codomyrmex
except ImportError:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))

from codomyrmex.ci_cd_automation.build import (
    check_build_environment,
    create_build_manifest,
    get_supported_languages,
    validate_build_config,
)
from codomyrmex.utils.cli_helpers import (
    print_error,
    print_info,
    print_success,
    setup_logging,
)


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml

    config_path = (
        Path(__file__).resolve().parent.parent.parent
        / "config"
        / "build_synthesis"
        / "config.yaml"
    )
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/build_synthesis/config.yaml")

    setup_logging()
    print_info("Running Build Synthesis Examples...")

    # 1. Supported languages
    print_info("Enumerating supported build languages...")
    try:
        languages = get_supported_languages()
        print_success(f"  Supported build languages: {', '.join(languages)}")
    except Exception as e:
        print_error(f"  Failed to get build languages: {e}")

    # 2. Build configuration and manifest
    print_info("Validating Python build configuration...")
    try:
        config = {
            "name": "codomyrmex-dist",
            "source_path": "src",
            "output_path": "dist/codomyrmex",
        }
        valid, errors = validate_build_config(config)
        if valid:
            manifest = create_build_manifest(config)
            print_success(
                f"  Build config '{config['name']}' valid; manifest "
                f"v{manifest['manifest_version']} created."
            )
        else:
            print_error(f"  Build config invalid: {errors}")
    except Exception as e:
        print_error(f"  Failed to create build manifest: {e}")

    # 3. Environment Check
    print_info("Checking build environment...")
    try:
        env = check_build_environment()
        tools = [
            name.removesuffix("_available")
            for name, available in env.items()
            if name.endswith("_available") and available
        ]
        print_success(
            f"  Python {env['python_version']}; available tools: {', '.join(tools)}"
        )
    except Exception as e:
        print_error(f"  Build environment check failed: {e}")

    print_success("Build synthesis examples completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
