# PEFT -- Agent Integration Guide

## Module Purpose

Provides parameter-efficient fine-tuning adapters (LoRA, Prefix Tuning, IA3) for AI agents that need to understand, compare, or demonstrate PEFT methods without requiring PyTorch.

## MCP Tools

| Tool | Description | Inputs | Output |
|------|-------------|--------|--------|
| `peft_create_adapter` | Create a PEFT adapter and return parameter stats | `method: str`, `d_model: int`, `rank: int`, `alpha: float` | `{method, trainable_params, full_finetune_params, reduction_factor}` |
| `peft_compare_methods` | Compare all PEFT methods for a given dimension | `d_model: int`, `rank: int` | `{full_finetune, lora, prefix, ia3}` |

## Agent Use Cases

### Method Selection
An agent can use `peft_compare_methods` to recommend the most parameter-efficient method for a given model size.

### Cost Estimation
Use `peft_create_adapter` to estimate training cost reduction from PEFT vs full fine-tuning.

### Educational Demonstrations
Agents can explain PEFT concepts with concrete numbers by creating adapters and showing parameter counts.

## Example Agent Workflow

```
1. Agent receives: "What's the most efficient way to fine-tune a 512-dim model?"
2. Agent calls: peft_compare_methods(d_model=512, rank=4)
3. Response: {"full_finetune": 262144, "lora": 4096, "prefix": 20480, "ia3": 3072}
4. Agent explains: "IA3 is most efficient at 3072 params (85x reduction)"
```
