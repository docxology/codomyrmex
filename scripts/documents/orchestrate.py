#!/usr/bin/env python3
"""
Orchestrator for documents - A thin wrapper around documents capabilities.
"""

import argparse
import sys
from pathlib import Path

# Ensure codomyrmex is in path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root / "src") not in sys.path:
    sys.path.insert(0, str(project_root / "src"))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from codomyrmex.documents import (
    DocumentFormat,
    convert_document,
    read_document,
    write_document,
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
        / "documents"
        / "config.yaml"
    )
    config_data = {}
    if config_path.exists():
        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}
            print(f"Loaded config from {config_path.name}")

    parser = argparse.ArgumentParser(description="Documents Orchestrator")
    parser.add_argument(
        "action", choices=["convert", "info", "test"], help="Action to perform"
    )
    parser.add_argument("--input", "-i", help="Input file path")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--format", "-f", help="Target format for conversion")

    args = parser.parse_args()
    setup_logging()

    if args.action == "test":
        print_info("Running documents module smoke test...")
        from scripts.documents.examples.basic_usage import main as run_examples

        return run_examples()

    if not args.input:
        print_error("Input file required for this action")
        return 1

    input_path = Path(args.input)
    if not input_path.exists():
        print_error(f"Input file not found: {input_path}")
        return 1

    try:
        doc = read_document(input_path)

        if args.action == "info":
            print_info("Document Info:")
            print_info(f"  Format: {doc.format.value}")
            print_info(f"  Type: {doc.type.value}")
            print_info(f"  Metadata: {doc.metadata.to_dict()}")
            return 0

        if args.action == "convert":
            if not args.output or not args.format:
                print_error("Output path and target format required for conversion")
                return 1

            target_format = DocumentFormat(args.format.lower())
            converted = convert_document(doc, target_format)
            write_document(converted, args.output)
            print_success(
                f"Successfully converted {args.input} to {args.output} ({args.format})"
            )
            return 0

    except Exception as e:
        print_error(f"Action '{args.action}' failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
