# Multimodal Scripts

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Demo and orchestrator scripts for the `multimodal` module, which provides image generation via Google AI (Imagen 3) with config-driven generation parameters.

## Purpose

These scripts demonstrate multimodal image generation workflows: config-driven image generation, prompt customization, dry-run validation, and batch processing using the `ImageGenerator` class with Google AI (Gemini) backend.

## Contents

| File | Description |
|------|-------------|
| `multimodal_demo.py` | Interactive demo of `ImageGenerator` using Google AI (Imagen 3) |
| `orchestrate.py` | Config-driven orchestrator reading from `config/multimodal/config.yaml` |
| `examples/` | Additional multimodal processing examples |

## Usage

**Prerequisites:**
```bash
uv sync
export GEMINI_API_KEY=<your-key>
```

**Run:**
```bash
# Demo mode
uv run python scripts/multimodal/multimodal_demo.py

# Orchestrator (reads config/multimodal/config.yaml)
uv run python scripts/multimodal/orchestrate.py

# Dry run (no API key needed)
uv run python scripts/multimodal/orchestrate.py --dry-run

# Custom prompt
GEMINI_API_KEY=<key> uv run python scripts/multimodal/orchestrate.py --prompt "A mountain at sunset"
```

## Agent Usage

Agents generating images should use the orchestrator with `--dry-run` for validation before live API calls. The `GEMINI_API_KEY` environment variable is required for actual generation.

## Related Module

- Source: `src/codomyrmex/multimodal/`

## Navigation

- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- [Parent: scripts/](../README.md)
