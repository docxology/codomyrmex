# LLM Eval Harness -- Agent Coordination

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides a standardized evaluation framework for language models. Defines evaluation tasks with input-target pairs and supports exact match and F1 scoring metrics for systematic model benchmarking.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `eval_harness_run` | Run evaluation tasks against a model and return aggregated metrics | Standard | eval_harness |
| `eval_harness_score` | Score predictions against targets using exact match or F1 metric | Standard | eval_harness |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| VERIFY | QA Agent | Benchmark language model performance on standardized evaluation tasks |
| OBSERVE | Monitoring Agent | Track model performance regressions across evaluation runs |


## Agent Instructions

1. Define tasks as dicts with 'name' and 'examples' (list of input/target pairs)
2. Supported metrics: 'exact_match' (strict string equality) and 'f1' (token-level F1 score)


## Navigation

- [Source README](../../src/codomyrmex/eval_harness/README.md) | [SPEC.md](SPEC.md)
