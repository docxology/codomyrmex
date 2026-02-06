# Personal AI Infrastructure — Feature Flags Module

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Feature Flags module provides PAI integration for progressive rollouts and A/B testing.

## PAI Capabilities

### Feature Toggle

Control features dynamically:

```python
from codomyrmex.feature_flags import FeatureFlags

flags = FeatureFlags()

if flags.is_enabled("new_llm_model"):
    response = new_model.complete(prompt)
else:
    response = old_model.complete(prompt)
```

### A/B Testing

Run experiments:

```python
from codomyrmex.feature_flags import ABTest

test = ABTest("prompt_style")
variant = test.get_variant(user_id)

if variant == "concise":
    prompt = short_prompt
else:
    prompt = detailed_prompt
```

## PAI Integration Points

| Component | PAI Use Case |
|-----------|-------------|
| `FeatureFlags` | Toggle features |
| `ABTest` | Run experiments |
| `Rollout` | Progressive rollouts |

## Navigation

- [README](README.md) | [AGENTS](AGENTS.md) | [SPEC](SPEC.md)
