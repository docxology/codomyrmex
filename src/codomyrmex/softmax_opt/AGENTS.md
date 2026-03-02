# Softmax Opt Module -- Agent Capabilities

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Agent Access Matrix

This document defines which PAI agent types can access softmax_opt tools and at what trust level.

### Engineer Agent

**Access**: Full access to all tools
**Trust Level**: TRUSTED

| Tool | Capabilities |
|------|-------------|
| `compute_softmax` | Compute softmax with all variants (standard, log, online) and temperature control |

**Use Cases**: Building attention mechanisms, implementing loss functions, probability calibration.

### Architect Agent

**Access**: Read-only computation
**Trust Level**: OBSERVED

| Tool | Capabilities |
|------|-------------|
| `compute_softmax` | Evaluate numerical stability properties and entropy of distributions |

**Use Cases**: Analyzing attention distributions, evaluating model confidence calibration.

### QATester Agent

**Access**: Correctness validation
**Trust Level**: OBSERVED

| Tool | Capabilities |
|------|-------------|
| `compute_softmax` | Validate sum-to-one property, numerical stability with extreme inputs |

**Use Cases**: Testing softmax implementations for edge cases (large values, all-zero, single element).

## Trust Levels

| Level | Description |
|-------|-------------|
| TRUSTED | Full read/write access to all module capabilities |
| OBSERVED | Read-only access, results logged for audit |
| UNTRUSTED | No access |
