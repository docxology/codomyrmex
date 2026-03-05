# Parameter-Efficient Fine-Tuning (PEFT) -- Agent Coordination

**Version**: v1.1.4 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides multiple parameter-efficient fine-tuning adapters: LoRA (Low-Rank Adaptation), Prefix Tuning, and IA3 (Infused Adapter by Inhibiting and Amplifying Inner Activations). Enables fine-tuning with dramatically fewer trainable parameters.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `peft_create_adapter` | Create a PEFT adapter and return its parameter statistics | Standard | peft |
| `peft_compare_methods` | Compare all PEFT methods for a given model dimension | Standard | peft |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| BUILD | Engineer Agent | Apply parameter-efficient adapters for model fine-tuning |
| PLAN | Architect Agent | Compare PEFT methods to select optimal adapter strategy |


## Agent Instructions

1. Supported methods: 'lora', 'prefix', 'ia3'
2. Use peft_compare_methods to see trainable parameter counts across all methods before choosing


## Navigation

- [Source README](../../src/codomyrmex/peft/README.md) | [SPEC.md](SPEC.md)
