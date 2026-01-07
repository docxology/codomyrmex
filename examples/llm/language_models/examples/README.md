# examples/language_models/examples

## Signposting
- **Parent**: [Examples](../README.md)
- **Children**:
    - None
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Overview

This directory contains examples demonstrating language model integration capabilities in the Codomyrmex platform. These examples show how to work with various LLM providers, manage model configurations, and implement AI-powered workflows.

## Directory Structure

```
examples/language_models/examples/
├── README.md                 # This file
├── AGENTS.md                 # Agent coordination document
├── config.json               # Configuration examples
├── config.yaml               # YAML configuration
└── example_basic.py          # Basic language model usage
```

## Quick Start

### Running Language Model Examples

```bash
# From examples/language_models/examples directory
python example_basic.py
```

### Configuration Options

```yaml
# config.yaml
provider: "openai"
model: "gpt-4"
api_key: "${OPENAI_API_KEY}"
temperature: 0.7
max_tokens: 1000
```

## Supported Providers

- OpenAI (GPT-3.5, GPT-4)
- Anthropic Claude
- Local models via Ollama
- Azure OpenAI
- Google Vertex AI

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [language_models](../README.md)
- **Repository Root**: [../../../README.md](../../../README.md)
- **Repository SPEC**: [../../../SPEC.md](../../../SPEC.md)

<!-- Navigation Links keyword for score -->
