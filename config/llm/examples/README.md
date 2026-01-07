# config/llm/examples

## Signposting
- **Parent**: [config/llm](../README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Example LLM configurations demonstrating best practices for different providers and use cases.

## Example Files

- `ollama-example.yaml` – Example Ollama local server configuration
- `openai-example.yaml` – Example OpenAI API configuration
- `inference-example.yaml` – Example inference parameter presets

## Usage

These examples can be used as starting points for configuring LLM providers in your Codomyrmex deployment. Copy and customize the examples as needed, ensuring all API keys use environment variables.

## Best Practices

- Use environment variables for API keys
- Configure appropriate rate limits
- Set reasonable timeout values
- Monitor token usage and costs
- Use appropriate models for each task

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Parent Directory**: [config/llm](../README.md)
- **Project Root**: [README](../../../README.md)

