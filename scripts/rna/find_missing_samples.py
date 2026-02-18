#!/usr/bin/env python3
import pathlib
import argparse
import csv

def main():
    parser = argparse.ArgumentParser(description="Find missing Amalgkit samples")
    parser.add_argument("--metadata", required=True, help="Path to metadata.tsv")
    parser.add_argument("--work-dir", required=True, help="Amalgkit work directory")
    parser.add_argument("--output", required=True, help="Output file for missing IDs")
    args = parser.parse_args()

    work_dir = pathlib.Path(args.work_dir)
    missing = []

    with open(args.metadata, "r") as f:
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
