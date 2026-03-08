# Neural Architecture Search -- Agent Coordination

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides random and evolutionary search over neural architecture search spaces. Defines configurable architecture search spaces with sampling, evaluation, and best-architecture selection.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `nas_sample_architecture` | Sample a random architecture from the default search space | Standard | nas |
| `nas_random_search` | Run random NAS with a size-based evaluation heuristic | Standard | nas |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| PLAN | Architect Agent | Explore architecture design spaces for optimal configurations |
| BUILD | Engineer Agent | Generate and evaluate candidate architectures |


## Agent Instructions

1. Use nas_sample_architecture to inspect individual random configurations
2. nas_random_search evaluates n_trials architectures and returns the best by heuristic score


## Navigation

- [Source README](../../src/codomyrmex/nas/README.md) | [SPEC.md](SPEC.md)
