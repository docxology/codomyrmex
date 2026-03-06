# RNA Scripts

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Bioinformatics utility scripts for RNA-seq analysis workflows, specifically for identifying missing samples in Amalgkit processing pipelines.

## Purpose

These scripts support RNA-seq data processing by cross-referencing metadata files against Amalgkit work directories to identify samples that failed to process or are missing from the pipeline output.

## Contents

| File | Description |
|------|-------------|
| `find_missing_samples.py` | Cross-references metadata.tsv against Amalgkit work directory to identify missing sample IDs |

## Usage

**Prerequisites:**
```bash
uv sync
# Reads config from config/rna/config.yaml if present
```

**Run:**
```bash
uv run python scripts/rna/find_missing_samples.py \
  --metadata /path/to/metadata.tsv \
  --work-dir /path/to/amalgkit/work \
  --output missing_samples.txt
```

## Agent Usage

Agents working with RNA-seq data should use this script to audit pipeline completeness before downstream analysis. The script auto-loads configuration from `config/rna/config.yaml`.

## Navigation

- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- [Parent: scripts/](../README.md)
