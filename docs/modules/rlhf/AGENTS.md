# RLHF Pipeline -- Agent Coordination

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

Implements Proximal Policy Optimization (PPO) for Reinforcement Learning from Human Feedback. Includes Actor-Critic networks, reward model with preference learning, and GAE advantage estimation for language model alignment.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `rlhf_ppo_step` | Run a single PPO step on synthetic data and return loss metrics | Standard | rlhf |
| `rlhf_reward_score` | Score synthetic states using the RLHF reward model | Standard | rlhf |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| BUILD | Engineer Agent | Train language models with PPO-based RLHF alignment |
| VERIFY | QA Agent | Validate PPO loss components and reward model preference accuracy |


## Agent Instructions

1. PPO step returns policy_loss, value_loss, entropy, total_loss, mean_ratio, and clip_fraction
2. rlhf_reward_score computes reward scores and preference loss between sample pairs


## Navigation

- [Source README](../../src/codomyrmex/rlhf/README.md) | [SPEC.md](SPEC.md)
