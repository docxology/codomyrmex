# SLM -- Agent Integration Guide

## Module Purpose

Provides a tiny GPT-2 style language model for agents that need local text generation, embedding extraction, or transformer architecture exploration.

## MCP Tools

| Tool | Description | Inputs | Output |
|------|-------------|--------|--------|
| `slm_generate` | Generate tokens from a tiny LM | `prompt_tokens, max_new_tokens, vocab_size, d_model, n_heads, n_layers, seed` | `{prompt, generated, full_sequence}` |
| `slm_forward` | Run forward pass and return logit stats | `batch_size, seq_len, vocab_size, d_model, n_heads, n_layers, seed` | `{output_shape, logit_mean, logit_std}` |

## Agent Use Cases

### Token Generation
An agent can use `slm_generate` to produce token sequences for testing downstream pipelines.

### Architecture Validation
Use `slm_forward` to verify output shapes and logit distributions for different model configurations.

## Example Agent Workflow

```
1. Agent receives: "Generate 5 tokens from a small model"
2. Agent calls: slm_generate(prompt_tokens=[1,2,3], max_new_tokens=5, vocab_size=100)
3. Response: {"generated": [42, 17, 88, 3, 55], ...}
4. Agent uses generated tokens for downstream processing
```
