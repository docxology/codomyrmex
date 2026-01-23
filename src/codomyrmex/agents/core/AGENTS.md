# Codomyrmex Agents — src/codomyrmex/agents/core

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Core module providing foundational abstractions, interfaces, and utilities for all agent implementations. This module defines the base classes, configuration management, exception hierarchy, response parsers, session management, tool registry, and ReAct agent pattern.

## Active Components

- `base.py` - Base agent classes and interfaces
- `config.py` - Agent configuration management
- `exceptions.py` - Exception hierarchy for all agent types
- `parsers.py` - Response parsing utilities
- `session.py` - Session and message management
- `registry.py` - Tool registration system
- `react.py` - ReAct agent implementation
- `__init__.py` - Module exports

## Key Classes

### Base Classes and Interfaces
- **`BaseAgent`** - Abstract base class for all agent implementations
- **`AgentInterface`** - Protocol defining the agent contract
- **`AgentCapabilities`** - Describes agent capabilities
- **`AgentIntegrationAdapter`** - Adapter for integrating external agents
- **`AgentRequest`** - Standardized request structure
- **`AgentResponse`** - Standardized response structure

### Configuration
- **`AgentConfig`** - Configuration dataclass for agents
- **`get_config()`** - Retrieve current configuration
- **`set_config()`** - Update configuration
- **`reset_config()`** - Reset to default configuration

### Exceptions
- **`AgentError`** - Base exception for all agent errors
- **`ClaudeError`** - Claude-specific errors
- **`CodexError`** - Codex-specific errors
- **`GeminiError`** - Gemini-specific errors
- **`JulesError`** - Jules-specific errors
- **`OpenCodeError`** - OpenCode-specific errors
- **`ConfigError`** - Configuration errors
- **`SessionError`** - Session management errors

### Parsers
- **`parse_json_response()`** - Parse JSON from agent responses
- **`parse_code_blocks()`** - Extract code blocks from responses
- **`parse_first_code_block()`** - Extract first code block
- **`parse_structured_output()`** - Parse structured output formats
- **`clean_response()`** - Clean and normalize responses
- **`CodeBlock`** - Dataclass for code block representation
- **`ParseResult`** - Dataclass for parse results

### Session Management
- **`AgentSession`** - Manages a single agent session
- **`SessionManager`** - Manages multiple sessions
- **`Message`** - Represents a conversation message

### Tool Registry
- **`ToolRegistry`** - Registry for agent tools
- **`Tool`** - Tool definition dataclass

### ReAct Pattern
- **`ReActAgent`** - Implementation of the ReAct (Reasoning + Acting) agent pattern

## Operating Contracts

- All agent implementations must inherit from `BaseAgent` or implement `AgentInterface`.
- Configuration changes via `set_config()` affect all agents using the shared config.
- Exceptions follow the hierarchy with `AgentError` as the base.
- Parsers handle malformed responses gracefully, returning appropriate defaults.
- Session state is managed through `SessionManager` for multi-turn conversations.
- Tools must be registered with `ToolRegistry` before use.

## Signposting

- **Implementing a new agent?** Extend `BaseAgent` and implement required abstract methods.
- **Need custom configuration?** Use `AgentConfig` with `set_config()`.
- **Parsing agent output?** Use the parser functions for JSON, code blocks, or structured data.
- **Managing conversations?** Use `SessionManager` and `AgentSession`.
- **Adding tools?** Register with `ToolRegistry`.

## Navigation Links

- **Parent Directory**: [agents](../README.md) - Parent directory documentation
- **Project Root**: ../../../../README.md - Main project documentation
