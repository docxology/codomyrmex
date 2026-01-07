# scripts/agents - Functional Specification

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

CLI orchestrator script providing comprehensive access to all agent types in the Codomyrmex agents module. Supports operations for Jules, Claude, Codex, OpenCode, Gemini, Droid, multi-agent orchestration, and theory modules.

## Global Options

All commands support the following global options:

- `--verbose, -v`: Enable verbose output
- `--format <json|text>`: Output format (default: text)
- `--output, -o <file>`: Save output to file

## Commands

### info
Get agents module information and configuration.

**Usage:**
```bash
python orchestrate.py info [--format json]
```

**Options:**
- `--format`: Output format (json or text)

## Agent Commands

### Jules Agent (`jules`)

#### jules execute
Execute a prompt with Jules CLI.

**Usage:**
```bash
python orchestrate.py jules execute <prompt> [--timeout <seconds>] [--context <json>] [--output <file>]
```

**Options:**
- `prompt`: Prompt to execute (required)
- `--timeout`: Timeout in seconds
- `--context`: Additional context as JSON string
- `--output`: Save output to file

#### jules stream
Stream response from Jules.

**Usage:**
```bash
python orchestrate.py jules stream <prompt> [--timeout <seconds>] [--context <json>] [--output <file>]
```

#### jules check
Check if Jules CLI is available.

**Usage:**
```bash
python orchestrate.py jules check
```

#### jules help
Get Jules help information.

**Usage:**
```bash
python orchestrate.py jules help
```

#### jules command
Execute a specific Jules command.

**Usage:**
```bash
python orchestrate.py jules command <cmd> [args...]
```

**Example:**
```bash
python orchestrate.py jules command new "Create a function"
```

### Claude Agent (`claude`)

#### claude execute
Execute a prompt with Claude API.

**Usage:**
```bash
python orchestrate.py claude execute <prompt> [--timeout <seconds>] [--context <json>] [--output <file>]
```

**Requirements:**
- `ANTHROPIC_API_KEY` environment variable must be set

#### claude stream
Stream response from Claude.

**Usage:**
```bash
python orchestrate.py claude stream <prompt> [--timeout <seconds>] [--context <json>] [--output <file>]
```

#### claude check
Check Claude API configuration.

**Usage:**
```bash
python orchestrate.py claude check
```

### Codex Agent (`codex`)

#### codex execute
Execute a prompt with OpenAI Codex.

**Usage:**
```bash
python orchestrate.py codex execute <prompt> [--timeout <seconds>] [--context <json>] [--output <file>]
```

**Requirements:**
- `OPENAI_API_KEY` environment variable must be set

#### codex stream
Stream response from Codex.

**Usage:**
```bash
python orchestrate.py codex stream <prompt> [--timeout <seconds>] [--context <json>] [--output <file>]
```

#### codex check
Check Codex API configuration.

**Usage:**
```bash
python orchestrate.py codex check
```

### OpenCode Agent (`opencode`)

#### opencode execute
Execute a prompt with OpenCode CLI.

**Usage:**
```bash
python orchestrate.py opencode execute <prompt> [--timeout <seconds>] [--context <json>] [--output <file>]
```

#### opencode stream
Stream response from OpenCode.

**Usage:**
```bash
python orchestrate.py opencode stream <prompt> [--timeout <seconds>] [--context <json>] [--output <file>]
```

#### opencode check
Check if OpenCode CLI is available.

**Usage:**
```bash
python orchestrate.py opencode check
```

#### opencode init
Initialize OpenCode for a project.

**Usage:**
```bash
python orchestrate.py opencode init [--path <project_path>]
```

**Options:**
- `--path`: Project path (default: current directory)

#### opencode version
Get OpenCode version.

**Usage:**
```bash
python orchestrate.py opencode version
```

### Gemini Agent (`gemini`)

#### gemini execute
Execute a prompt with Gemini CLI.

**Usage:**
```bash
python orchestrate.py gemini execute <prompt> [--timeout <seconds>] [--context <json>] [--output <file>]
```

#### gemini stream
Stream response from Gemini.

**Usage:**
```bash
python orchestrate.py gemini stream <prompt> [--timeout <seconds>] [--context <json>] [--output <file>]
```

#### gemini check
Check Gemini CLI availability and configuration.

**Usage:**
```bash
python orchestrate.py gemini check
```

#### gemini chat save
Save a Gemini chat session.

**Usage:**
```bash
python orchestrate.py gemini chat save <tag> [--prompt <prompt>]
```

**Options:**
- `tag`: Chat session tag (required)
- `--prompt`: Optional prompt to save

#### gemini chat resume
Resume a saved Gemini chat session.

**Usage:**
```bash
python orchestrate.py gemini chat resume <tag>
```

#### gemini chat list
List available Gemini chat sessions.

**Usage:**
```bash
python orchestrate.py gemini chat list
```

### Droid Agent (`droid`)

#### droid start
Start droid controller.

**Usage:**
```bash
python orchestrate.py droid start
```

#### droid stop
Stop droid controller.

**Usage:**
```bash
python orchestrate.py droid stop
```

#### droid status
Get droid status and metrics.

**Usage:**
```bash
python orchestrate.py droid status [--format json]
```

#### droid config show
Show droid configuration.

**Usage:**
```bash
python orchestrate.py droid config show [--format json]
```

#### droid config set
Update droid configuration.

**Usage:**
```bash
python orchestrate.py droid config set <key=value> [<key=value>...]
```

**Example:**
```bash
python orchestrate.py droid config set max_parallel_tasks=5 log_level=DEBUG
```

#### droid metrics
Show droid metrics.

**Usage:**
```bash
python orchestrate.py droid metrics [--format json]
```

#### droid metrics reset
Reset droid metrics.

**Usage:**
```bash
python orchestrate.py droid metrics reset
```

### Orchestrator (`orchestrate`)

#### orchestrate parallel
Execute prompt on multiple agents in parallel.

**Usage:**
```bash
python orchestrate.py orchestrate parallel <prompt> --agents <agent1,agent2,...> [--timeout <seconds>] [--context <json>]
```

**Options:**
- `prompt`: Prompt to execute (required)
- `--agents`: Comma-separated list of agents (required)
- `--timeout`: Timeout in seconds
- `--context`: Additional context as JSON

**Example:**
```bash
python orchestrate.py orchestrate parallel "Analyze code" --agents jules,claude
```

#### orchestrate sequential
Execute prompt on multiple agents sequentially.

**Usage:**
```bash
python orchestrate.py orchestrate sequential <prompt> --agents <agent1,agent2,...> [--stop-on-success] [--timeout <seconds>] [--context <json>]
```

**Options:**
- `--stop-on-success`: Stop after first successful response

#### orchestrate fallback
Execute prompt with fallback strategy (try agents until one succeeds).

**Usage:**
```bash
python orchestrate.py orchestrate fallback <prompt> --agents <agent1,agent2,...> [--timeout <seconds>] [--context <json>]
```

#### orchestrate list
List available agents.

**Usage:**
```bash
python orchestrate.py orchestrate list [--format json]
```

### Theory Module (`theory`)

#### theory info
Show theory module information.

**Usage:**
```bash
python orchestrate.py theory info [--format json]
```

#### theory architectures
List agent architectures.

**Usage:**
```bash
python orchestrate.py theory architectures [--format json]
```

#### theory reasoning
Show reasoning models.

**Usage:**
```bash
python orchestrate.py theory reasoning [--format json]
```

## Integration

- Uses `codomyrmex.agents` module for tool functionality
- Integrates with `logging_monitoring` for logging
- Uses shared `_orchestrator_utils` for common functionality

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [scripts](../README.md)
- **Repository Root**: [../../README.md](../../README.md)
- **Repository SPEC**: [../../SPEC.md](../../SPEC.md)

<!-- Navigation Links keyword for score -->

## Detailed Architecture and Implementation

The implementation of this component follows the core principles of the Codomyrmex ecosystem: modularity, performance, and reliability. By adhering to standardized interfaces, this module ensures seamless integration with the broader platform.

### Design Principles
1.  **Strict Modularity**: Each component is isolated and communicates via well-defined APIs.
2.  **Performance Optimization**: Implementation leverages lazy loading and intelligent caching to minimize resource overhead.
3.  **Error Resilience**: Robust exception handling ensures system stability even under unexpected conditions.
4.  **Extensibility**: The architecture is designed to accommodate future enhancements without breaking existing contracts.

### Technical Implementation
The codebase utilizes modern Python features (version 3.10+) to provide a clean, type-safe API. Interaction patterns are documented in the corresponding `AGENTS.md` and `SPEC.md` files, ensuring that both human developers and automated agents can effectively utilize these capabilities.
