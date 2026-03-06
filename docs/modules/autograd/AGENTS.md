# Autograd Engine -- Agent Coordination

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides from-scratch automatic differentiation (Micrograd-style) with Value and Tensor types. Supports forward computation and backward pass gradient computation for neural network training.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `autograd_compute` | Evaluate a simple expression and compute its gradient via backward pass | Standard | autograd |
| `autograd_gradient_check` | Numerically verify analytic gradients match finite differences | Standard | autograd |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| BUILD | Engineer Agent | Construct differentiable computation graphs |
| VERIFY | QA Agent | Validate gradient correctness via numerical gradient checking |


## Agent Instructions

1. Expressions support +, -, *, ** operators with named variables
2. Call autograd_gradient_check with func_name from: relu, tanh, sigmoid, square, sum


## Navigation

- [Source README](../../src/codomyrmex/autograd/README.md) | [SPEC.md](SPEC.md)
