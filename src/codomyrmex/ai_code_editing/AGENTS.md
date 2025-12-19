# Codomyrmex Agents — src/codomyrmex/ai_code_editing

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

Core module providing AI-powered code assistance and generation capabilities for the Codomyrmex platform. This module enables intelligent code creation, refactoring, and enhancement through integration with multiple Large Language Models (LLMs) including OpenAI, Anthropic, and Google AI.

The ai_code_editing module serves as the primary interface for AI-driven development workflows, supporting both programmatic usage and interactive development assistance.

## Module Overview

### Key Capabilities
- **Code Generation**: Create code snippets from natural language descriptions
- **Code Refactoring**: Improve and optimize existing code with AI assistance
- **Multi-Provider Support**: Integration with OpenAI, Anthropic (Claude), and Google AI
- **Prompt Engineering**: Sophisticated prompt composition and template management
- **Context-Aware Generation**: Support for additional context and constraints
- **Performance Monitoring**: Execution time and token usage tracking

### Key Features
- Multiple LLM provider support with unified interface
- Configurable model selection and parameters
- Prompt templates for consistent code generation
- Error handling and fallback mechanisms
- Structured response format with metadata
- Integration with droid task management system

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `ai_code_helpers.py` – Core AI code assistance utilities
- `prompt_composition.py` – Prompt engineering and composition logic
- `droid_manager.py` – Task management and orchestration

### Provider Integrations
- `openai_codex.py` – OpenAI API integration
- `claude_task_master.py` – Anthropic Claude integration

### Supporting Systems
- `droid/` – Task execution and management system
- `prompt_templates/` – Reusable prompt templates and patterns

### Documentation
- `README.md` – Module usage and overview
- `API_SPECIFICATION.md` – Complete API documentation
- `USAGE_EXAMPLES.md` – Practical usage demonstrations
- `PROMPT_ENGINEERING.md` – Prompt design and optimization
- `MCP_TOOL_SPECIFICATION.md` – AI agent tool specifications
- `SECURITY.md` – Security considerations for AI usage
- `CHANGELOG.md` – Version history and updates

### Supporting Files
- `requirements.txt` – Module dependencies
- `docs/` – Additional documentation
- `tests/` – Comprehensive test suite

## Operating Contracts

### Universal AI Code Protocols

All AI code assistance within the Codomyrmex platform must:

1. **Provider Agnostic** - Code should work with any supported LLM provider
2. **Secure API Usage** - Never expose API keys or sensitive credentials
3. **Context Preservation** - Maintain code functionality and intent during refactoring
4. **Error Resilience** - Handle API failures and rate limits gracefully
5. **Usage Transparency** - Track and report token usage and costs

### Module-Specific Guidelines

#### Code Generation
- Provide clear, descriptive prompts for better results
- Specify programming language explicitly
- Include context when available to improve accuracy
- Validate generated code for syntax and logic errors

#### Code Refactoring
- Preserve existing functionality unless explicitly requested otherwise
- Provide specific refactoring goals (optimize, simplify, add error handling)
- Include sufficient context about the codebase
- Review AI suggestions for correctness and best practices

#### Provider Management
- Support fallback to alternative providers on failure
- Implement rate limiting and usage monitoring
- Cache responses when appropriate for performance
- Handle provider-specific parameter differences

## Navigation Links

### Module Documentation
- **Module Overview**: [README.md](README.md) - Complete module documentation
- **API Reference**: [API_SPECIFICATION.md](API_SPECIFICATION.md) - Detailed API specification
- **Usage Examples**: [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) - Practical usage demonstrations
- **Prompt Engineering**: [PROMPT_ENGINEERING.md](PROMPT_ENGINEERING.md) - Prompt design guide

### Related Modules
- **Language Models**: [../language_models/](../../language_models/) - LLM infrastructure
- **Model Context Protocol**: [../model_context_protocol/](../../model_context_protocol/) - AI communication standards
- **Code Review**: [../code_review/](../../code_review/) - Code analysis integration

### Platform Navigation
- **Parent Directory**: [codomyrmex](../README.md) - Package overview
- **Project Root**: [README](../../../README.md) - Main project documentation

## Agent Coordination

### Integration Points

When integrating with other modules:

1. **Model Management** - Coordinate with language_models module for provider management
2. **Context Sharing** - Exchange codebase context for improved AI assistance
3. **Code Review Integration** - Combine AI generation with automated code review
4. **Security Validation** - Ensure AI-generated code meets security standards

### Quality Gates

Before AI code changes are accepted:

1. **API Integration Tested** - All supported providers properly tested
2. **Prompt Quality Verified** - Prompts produce consistent, high-quality results
3. **Security Validated** - No security vulnerabilities in generated code
4. **Performance Optimized** - API calls and response processing efficient
5. **Error Handling Complete** - Robust handling of API failures and edge cases

## Version History

- **v0.1.0** (December 2025) - Initial AI code editing system with multi-provider support and prompt engineering
