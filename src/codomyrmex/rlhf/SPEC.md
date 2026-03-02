# RLHF Pipeline -- Technical Specification

## Architecture

### PPO Algorithm (Schulman et al. 2017)

The PPO-Clip objective:
```
L_CLIP = E[min(r_t * A_t, clip(r_t, 1-eps, 1+eps) * A_t)]
```
where `r_t = pi_new(a|s) / pi_old(a|s)` is the probability ratio.

### Actor-Critic

- **Actor**: 2-layer MLP (d_state -> 64 -> d_action), log-softmax output
- **Critic**: 2-layer MLP (d_state -> 64 -> 1), scalar value output
- Both use ReLU activation in hidden layer, Xavier initialization

### Generalized Advantage Estimation

```
delta_t = r_t + gamma * V(s_{t+1}) - V(s_t)
A_t = delta_t + (gamma * lambda) * A_{t+1}
```

GAE provides a smooth tradeoff between bias and variance via lambda parameter.

### Bradley-Terry Reward Model

Preference loss: `-log sigmoid(r_w - r_l)`

The reward model learns to score responses such that preferred responses receive higher scores.

## Loss Components

| Component | Formula | Weight |
|-----------|---------|--------|
| Policy loss | `-E[min(r*A, clip(r)*A)]` | 1.0 |
| Value loss | `E[(V - R)^2]` | 0.5 (value_loss_coef) |
| Entropy bonus | `-E[sum(p * log p)]` | -0.01 (entropy_coef) |

## Limitations

- NumPy-only: no automatic differentiation, no gradient updates
- Actor/Critic weights are randomly initialized each run
- Designed for educational/testing use, not production RL training
