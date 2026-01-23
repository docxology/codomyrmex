# Personal AI Infrastructure — Documentation

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

This document provides a guide to Personal AI Infrastructure (PAI) documentation within Codomyrmex. It serves as an index to PAI-related guides, tutorials, and reference materials.

## PAI Documentation Index

### Getting Started with PAI

| Guide | Location | Description |
| :--- | :--- | :--- |
| PAI Overview | [../PAI.md](../PAI.md) | Introduction to PAI concepts |
| Quick Start | [getting-started/quickstart.md](getting-started/quickstart.md) | Get up and running |
| Installation | [getting-started/installation.md](getting-started/installation.md) | Environment setup |

### PAI Architecture

| Guide | Location | Description |
| :--- | :--- | :--- |
| Architecture | [project/architecture.md](project/architecture.md) | System design principles |
| Module System | [modules/overview.md](modules/overview.md) | Module architecture |
| Relationships | [modules/relationships.md](modules/relationships.md) | Module dependencies |

### AI Integration Guides

| Guide | Location | Description |
| :--- | :--- | :--- |
| LLM Integration | [modules/llm/](modules/llm/) | LLM provider setup |
| Ollama | [modules/ollama_integration.md](modules/ollama_integration.md) | Local LLM setup |
| Agent Framework | [modules/agents/](modules/agents/) | AI agent usage |
| Fabric AI | [integration/fabric-ai-integration.md](integration/fabric-ai-integration.md) | Fabric integration |

### Workflow Guides

| Guide | Location | Description |
| :--- | :--- | :--- |
| Project Lifecycle | [project_orchestration/project-lifecycle-guide.md](project_orchestration/project-lifecycle-guide.md) | Workflow management |
| Task Orchestration | [project_orchestration/task-orchestration-guide.md](project_orchestration/task-orchestration-guide.md) | Task coordination |
| Workflow Config | [project_orchestration/workflow-configuration-schema.md](project_orchestration/workflow-configuration-schema.md) | Configuration |

### Security & Privacy

| Guide | Location | Description |
| :--- | :--- | :--- |
| Security Guide | [reference/security.md](reference/security.md) | Security practices |
| API Reference | [reference/api.md](reference/api.md) | API documentation |

## PAI Tutorials

### Module Tutorials

| Tutorial | Location | Description |
| :--- | :--- | :--- |
| AI Agents | [modules/agents/tutorials/](modules/agents/tutorials/) | Agent tutorials |
| Cerebrum | [modules/cerebrum/tutorials/](modules/cerebrum/tutorials/) | Reasoning tutorials |
| LLM | [modules/model_context_protocol/tutorials/](modules/model_context_protocol/tutorials/) | MCP tutorials |

### Integration Examples

| Example | Location | Description |
| :--- | :--- | :--- |
| Basic Examples | [examples/basic-examples.md](examples/basic-examples.md) | Simple PAI usage |
| Integration | [examples/integration-examples.md](examples/integration-examples.md) | Integration patterns |
| Orchestration | [examples/orchestration-examples.md](examples/orchestration-examples.md) | Workflow examples |

## PAI Concepts

### Local-First AI

Codomyrmex prioritizes local AI processing:

1. **Ollama Integration** - Run models locally for privacy and cost control
2. **Hybrid Mode** - Use local for development, cloud for production
3. **Data Privacy** - Keep sensitive code on-premises

### Agent-Oriented Design

The platform is built around AI agents:

1. **Agent Abstraction** - Consistent interface across providers
2. **Multi-Agent Coordination** - Orchestrate multiple agents
3. **MCP Compatibility** - Standard tool interfaces

### Knowledge-Augmented AI

Enhance AI with contextual knowledge:

1. **Case-Based Reasoning** - Learn from past patterns
2. **Document Retrieval** - RAG for code generation
3. **Pattern Recognition** - Leverage codebase patterns

## Signposting

### Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [README.md](README.md) - Documentation hub
- **Project Root PAI**: [../PAI.md](../PAI.md) - Main PAI documentation

### Related Documentation

- [README.md](README.md) - Documentation overview
- [AGENTS.md](AGENTS.md) - Agent coordination
- [getting-started/](getting-started/) - Getting started guides
- [modules/](modules/) - Module documentation
