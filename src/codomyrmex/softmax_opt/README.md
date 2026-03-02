# Softmax Opt Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Softmax Opt module provides numerically stable softmax implementations including the online (single-pass) algorithm used in Flash Attention. All implementations use the max-subtraction trick to prevent floating-point overflow.

This module is designed for use in attention mechanisms, language model inference, and anywhere probability distributions need to be computed from raw logits.

## PAI Integration

| Algorithm Phase | Role | Tools Used |
|----------------|------|-----------|
| **BUILD** | Compute probability distributions from logits | `compute_softmax` |
| **VERIFY** | Validate numerical stability and correctness | `compute_softmax` |

## Features

- **Standard softmax**: Max-subtraction stable with temperature scaling
- **Log-softmax**: Log-sum-exp trick for stable log probabilities (cross-entropy loss)
- **Online softmax**: Single-pass algorithm (Flash Attention style) -- computes max and sum simultaneously
- **Safe softmax**: Epsilon-guarded denominator for attention mask safety
- **Temperature scaling**: Control distribution sharpness (peaked vs uniform)

## API

### `softmax(x, axis=-1, temperature=1.0)`

Numerically stable softmax using max subtraction.

- **x**: Input array of logits
- **axis**: Axis to compute softmax over (default: last)
- **temperature**: Scaling factor (>1 = uniform, <1 = peaked)
- **Returns**: Probability distribution summing to 1 along axis

### `log_softmax(x, axis=-1)`

Log-softmax using the log-sum-exp trick. More numerically stable than `log(softmax(x))`.

### `online_softmax(x, axis=-1)`

Single-pass softmax maintaining running (max, normalizer). Key algorithm behind Flash Attention memory efficiency.

### `safe_softmax(x, axis=-1, eps=1e-8)`

Softmax with epsilon in denominator to prevent division by zero (useful with attention masks).

## MCP Tools

| Tool | Description |
|------|-------------|
| `compute_softmax` | Compute softmax probabilities with variant selection and entropy output |

## Dependencies

- `numpy` (core dependency)
