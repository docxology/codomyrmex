"""
Download datasets for SAIR Mathematics Distillation Challenge.

Sources:
- Hugging Face: SAIRfoundation/equational-theories-selected-problems
- Full ETP implication graph (large, optional)

Features:
- Integrity verification: non-empty, valid JSONL
- Local dataset registry summary
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import requests
from huggingface_hub import hf_hub_download

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

REPO_ID = "SAIRfoundation/equational-theories-selected-problems"
FILES = ["data/normal.jsonl", "data/hard.jsonl"]

# Default output directories
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_PUBLIC_DIR = os.path.join(MODULE_DIR, "data", "public")
DEFAULT_ETP_DIR = os.path.join(MODULE_DIR, "data", "etp")


def verify_dataset_integrity(path: str) -> bool:
    """Verify that a downloaded dataset file is non-empty and valid JSONL.

    Returns True if the file exists, is non-empty, and every non-blank
    line parses as valid JSON.
    """
    if not os.path.exists(path):
        logger.error("File not found: %s", path)
        return False
    size = os.path.getsize(path)
    if size == 0:
        logger.error("File is empty: %s", path)
        return False
    try:
        valid_lines = 0
        with open(path, encoding="utf-8") as f:
            for i, line in enumerate(f):
                if line.strip():
                    json.loads(line)
                    valid_lines += 1
                    if i > 500:  # Fast-check: validate first 500+ lines only
                        break
        if valid_lines == 0:
            logger.error("No valid JSON lines found in %s", path)
            return False
        logger.info("Integrity OK: %s  (%d bytes, %d valid lines checked)", path, size, valid_lines)
        return True
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON in %s: %s", path, e)
        return False


def list_local_datasets(data_dir: str = "data/sair") -> dict[str, Any]:
    """Return a dict summarising locally cached SAIR datasets."""
    base = Path(data_dir)
    summary: dict[str, Any] = {}
    for jsonl in base.rglob("*.jsonl"):
        size = jsonl.stat().st_size
        valid = verify_dataset_integrity(str(jsonl))
        summary[str(jsonl)] = {"size_bytes": size, "valid": valid}
    return summary


def download_sair_datasets(output_dir: str = DEFAULT_PUBLIC_DIR) -> None:
    """Download the competition datasets from Hugging Face and verify integrity."""
    os.makedirs(output_dir, exist_ok=True)
    logger.info("Downloading SAIR datasets from %s → %s", REPO_ID, output_dir)

    for filename in FILES:
        logger.info("Downloading %s ...", filename)
        try:
            local_path = hf_hub_download(
                repo_id=REPO_ID,
                filename=filename,
                repo_type="dataset",
                local_dir=output_dir,
            )
            logger.info("Downloaded → %s", local_path)
            if verify_dataset_integrity(local_path):
                logger.info("✓ Integrity verified: %s", local_path)
            else:
                logger.warning("⚠ Integrity check FAILED for %s", local_path)
        except Exception as e:
            logger.error("Failed to download %s: %s", filename, e)


def download_etp_full(output_dir: str = DEFAULT_ETP_DIR) -> None:
    """Download the full Equational Theories Project implication graph.

    NOTE: This is a very large dataset. Adjust the URL as needed.
    """
    # Use stable release from GitHub. The raw CSV/Parquet is at:
    url = "https://github.com/teorth/equational_theories/releases/latest/download/implications.csv"
    os.makedirs(output_dir, exist_ok=True)
    target = os.path.join(output_dir, "etp_implications.csv")
    logger.info("Downloading full ETP implication graph → %s", target)
    try:
        with requests.get(url, stream=True, timeout=120) as resp:
            resp.raise_for_status()
            total = 0
            with open(target, "wb") as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    f.write(chunk)
                    total += len(chunk)
        logger.info("✓ Downloaded ETP graph: %d bytes → %s", total, target)
    except Exception as e:
        logger.error("Failed to download ETP data from %s: %s", url, e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download SAIR/ETP datasets.")
    parser.add_argument(
        "--type",
        choices=["public", "full", "list"],
        default="public",
        help="'public': competition files; 'full': full ETP graph; 'list': show local datasets.",
    )
    parser.add_argument("--output-dir", default=DEFAULT_PUBLIC_DIR, help="Local directory for data.")
    args = parser.parse_args()

    if args.type == "public":
        download_sair_datasets(args.output_dir)
    elif args.type == "full":
        download_etp_full(DEFAULT_ETP_DIR)
    elif args.type == "list":
        datasets = list_local_datasets()
        if not datasets:
            print("No local SAIR datasets found.")
        else:
            for path, info in datasets.items():
                status = "✓" if info["valid"] else "✗"
                print(f"  [{status}] {path}  ({info['size_bytes']:,} bytes)")
