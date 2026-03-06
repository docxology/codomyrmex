# RLHF (Reinforcement Learning from Human Feedback) Tests

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Unit tests for the `rlhf` module. Covers GAE computation, actor/critic/reward models, PPO step mechanics (clipping, entropy, value loss), PPO trainer, and MCP tool integration.

## Test Coverage

| Test Class | What It Tests |
|-----------|---------------|
| `TestComputeGAE` | GAE output shapes, advantages + values, discount, zero rewards, single step |
| `TestActor` | Actor output shape, log-prob non-positivity, sum-to-one, determinism |
| `TestCritic` | Critic output shape, single state evaluation |
| `TestRewardModel` | Reward score shape, preference loss scalar, loss direction |
| `TestPPOStep` | PPO keys, clip fraction bounds, entropy positivity, mean ratio, value/total loss |
| `TestPPOTrainer` | Trainer loss tracking, custom config |
| `TestMCPTools` | rlhf_ppo_step MCP tool |

## Test Structure

```
tests/unit/rlhf/
    __init__.py
    test_rlhf.py
```

## Running Tests

```bash
# Run all tests for this module
uv run pytest src/codomyrmex/tests/unit/rlhf/ -v

# Run with coverage
uv run pytest src/codomyrmex/tests/unit/rlhf/ --cov=src/codomyrmex/rlhf -v
```

## Test Policy

All tests follow the zero-mock policy: no `unittest.mock`, `MagicMock`, or `monkeypatch`.
External dependencies use `@pytest.mark.skipif` guards.

## Related

- [Source Module](../../../../rlhf/README.md)
- [All Tests](../README.md)
