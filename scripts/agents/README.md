# agents

## Signposting
- **Parent**: [Parent](../README.md)
- **Children**:
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

CLI orchestrator script providing comprehensive access to all agent types in the Codomyrmex agents module. Supports operations for Jules, Claude, Codex, OpenCode, Gemini, Droid, multi-agent orchestration, and theory modules.

## Quick Start

```bash
# Get module information
python orchestrate.py info

# Execute a prompt with Jules
python orchestrate.py jules execute "Write a Python function"

# Check Claude configuration
python orchestrate.py claude check

# Run multiple agents in parallel
python orchestrate.py orchestrate parallel "Analyze code" --agents jules,claude

# Get droid status
python orchestrate.py droid status
```

## Usage Examples

### Jules Agent

```bash
# Execute a prompt
python orchestrate.py jules execute "Create a function to calculate factorial"

# Stream response
python orchestrate.py jules stream "Write a test"

# Check availability
python orchestrate.py jules check

# Get help
python orchestrate.py jules help

# Execute specific command
python orchestrate.py jules command new "Task description"
```

### Claude Agent

```bash
# Execute with Claude API
python orchestrate.py claude execute "Explain Python decorators"

# Stream response
python orchestrate.py claude stream "Write documentation"

# Check configuration
python orchestrate.py claude check
```

### Codex Agent

```bash
# Execute with Codex
python orchestrate.py codex execute "Generate a REST API endpoint"

# Check configuration
python orchestrate.py codex check
```

### OpenCode Agent

```bash
# Initialize OpenCode for project
python orchestrate.py opencode init --path ./my-project

# Get version
python orchestrate.py opencode version

# Check availability
python orchestrate.py opencode check
```

### Gemini Agent

```bash
# Execute prompt
python orchestrate.py gemini execute "Analyze this code"

# Save chat session
python orchestrate.py gemini chat save my-session --prompt "Initial prompt"

# Resume chat
python orchestrate.py gemini chat resume my-session

# List chats
python orchestrate.py gemini chat list
```

### Droid Controller

```bash
# Start controller
python orchestrate.py droid start

# Get status
python orchestrate.py droid status

# Show configuration
python orchestrate.py droid config show

# Update configuration
python orchestrate.py droid config set max_parallel_tasks=5 log_level=DEBUG

# Show metrics
python orchestrate.py droid metrics

# Reset metrics
python orchestrate.py droid metrics reset

# Stop controller
python orchestrate.py droid stop
```

### Multi-Agent Orchestration

```bash
# Execute in parallel
python orchestrate.py orchestrate parallel "Analyze code quality" --agents jules,claude,codex

# Execute sequentially
python orchestrate.py orchestrate sequential "Generate code" --agents jules,claude --stop-on-success

# Execute with fallback
python orchestrate.py orchestrate fallback "Process request" --agents claude,codex

# List available agents
python orchestrate.py orchestrate list
```

### Theory Module

```bash
# Get module information
python orchestrate.py theory info

# List architectures
python orchestrate.py theory architectures

# Show reasoning models
python orchestrate.py theory reasoning
```

### Configuration Management

```bash
# Show configuration
python orchestrate.py config show

# Set configuration values
python orchestrate.py config set default_timeout=60 log_level=DEBUG

# Reset to defaults
python orchestrate.py config reset

# Validate configuration
python orchestrate.py config validate
```

### Task Planner

```bash
# Create a task
python orchestrate.py task create "Process data" --dependencies task_1,task_2

# List all tasks
python orchestrate.py task list

# Get task details
python orchestrate.py task get task_1

# Update task status
python orchestrate.py task update task_1 --status completed --result "Success"

# Get ready tasks
python orchestrate.py task ready

# Get execution order
python orchestrate.py task order

# Clear all tasks
python orchestrate.py task clear
```

### Message Bus

```bash
# Subscribe to messages
python orchestrate.py message subscribe task_completed

# Publish a message
python orchestrate.py message publish task_completed "Task finished" --sender worker1

# Send message to recipient
python orchestrate.py message send worker1 worker2 request "Process this"

# Broadcast message
python orchestrate.py message broadcast system shutdown "System shutting down"

# Get message history
python orchestrate.py message history --type task_completed --limit 10
```

### Enhanced Droid Operations

```bash
# Save configuration
python orchestrate.py droid config save droid_config.json

# Load configuration
python orchestrate.py droid config load droid_config.json

# Execute a task
python orchestrate.py droid execute-task my_operation

# Load TODO list
python orchestrate.py droid todo load --file my_todos.txt

# Validate TODO file
python orchestrate.py droid todo validate

# Migrate TODO format
python orchestrate.py droid todo migrate

# List TODO items
python orchestrate.py droid todo list
```

### Enhanced Orchestration

```bash
# Select agents by capability
python orchestrate.py orchestrate select --capability streaming --agents jules,claude
```

## Global Options

All commands support:

- `--verbose, -v`: Enable verbose output
- `--format <json|text>`: Output format (default: text)
- `--output, -o <file>`: Save output to file

## Common Options for Execute/Stream Commands

- `--timeout <seconds>`: Override timeout
- `--context <json>`: Additional context as JSON string

## Directory Contents
- `README.md` – File
- `SPEC.md` – File
- `orchestrate.py` – Main orchestrator script
- `tests/` – Subdirectory

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [scripts](../README.md)
- **Project Root**: [README](../../README.md)

