#!/usr/bin/env python3
import argparse
import csv
import pathlib


def main():
    # Auto-injected: Load configuration
    from pathlib import Path

    import yaml
    config_path = Path(__file__).resolve().parent.parent.parent / "config" / "rna" / "config.yaml"
    if config_path.exists():
        with open(config_path) as f:
            yaml.safe_load(f) or {}
            print("Loaded config from config/rna/config.yaml")

    parser = argparse.ArgumentParser(description="Find missing Amalgkit samples")
    parser.add_argument("--metadata", required=True, help="Path to metadata.tsv")
    parser.add_argument("--work-dir", required=True, help="Amalgkit work directory")
    parser.add_argument("--output", required=True, help="Output file for missing IDs")
    args = parser.parse_args()

    work_dir = pathlib.Path(args.work_dir)
    missing = []

    with open(args.metadata) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            run_id = row["run"]
            # Check for abundance.tsv in quant directory
            quant_file = work_dir / "quant" / run_id / "abundance.tsv"
            if not quant_file.exists():
                missing.append(run_id)

    with open(args.output, "w") as f:
        for run_id in missing:
            f.write(f"{run_id}\n")

    print(f"Found {len(missing)} missing samples.")
    print(f"Written to {args.output}")

if __name__ == "__main__":
    main()
