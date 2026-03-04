# Direct Preference Optimization -- Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Implements DPO (Direct Preference Optimization) loss function for aligning language models with human preferences without explicit reward modeling. Computes the implicit reward margin between preferred and dispreferred completions.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `dpo_compute_loss` | Compute DPO loss on synthetic preference data with configurable beta | Standard | dpo |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| BUILD | Engineer Agent | Implement preference-based alignment training for language models |
| VERIFY | QA Agent | Validate DPO loss and preference accuracy metrics |


## Agent Instructions

1. Beta parameter controls KL penalty strength (typical range 0.01-0.5; lower = more deviation from reference)
2. Provide policy and reference log probabilities for both winning and losing completions


## Navigation

- [Source README](../../src/codomyrmex/dpo/README.md) | [SPEC.md](SPEC.md)
