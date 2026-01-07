# config/llm

## Signposting
- **Parent**: [config](../README.md)
- **Children**:
    - [examples](examples/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

LLM and AI model configuration templates for Codomyrmex. Provides centralized configuration for model definitions, provider configurations, and inference parameters used across multiple modules.

## Directory Contents

- `README.md` – This file
- `SPEC.md` – Functional specification
- `AGENTS.md` – Agent coordination documentation
- `models.yaml` – Model definitions and parameters
- `providers.yaml` – LLM provider configurations (Ollama, OpenAI, Anthropic, etc.)
- `inference.yaml` – Inference parameter templates
- `examples/` – Example model configs

## Configuration Files

### models.yaml
Model definitions and parameters including model names, capabilities, context windows, and default parameters.

### providers.yaml
LLM provider configurations including API endpoints, authentication, rate limits, and provider-specific settings for Ollama, OpenAI, Anthropic, Google, and other providers.

### inference.yaml
Inference parameter templates including temperature, top-p, top-k, max tokens, and other generation parameters.

## Supported Providers

- **Ollama** - Local LLM server
- **OpenAI** - GPT models via API
- **Anthropic** - Claude models via API
- **Google** - Gemini models via API
- **Custom** - Custom provider configurations

## Usage

LLM configurations are loaded by the `config_management` module and used by:
- `llm/` - LLM integration and model execution
- `agents/` - Agent framework integrations
- `cerebrum/` - Case-based reasoning and inference
- `ai_code_editing/` - AI-powered code editing

## Best Practices

- Use environment variables for API keys
- Configure appropriate rate limits
- Set reasonable timeout values
- Monitor token usage and costs
- Use appropriate models for each task

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Examples**: [examples/](examples/README.md)
- **Parent Directory**: [config](../README.md)
- **Project Root**: [README](../../README.md)

