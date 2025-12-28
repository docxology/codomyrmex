# Codomyrmex Agents — scripts/ai_code_editing

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: December 2025

## Purpose

AI Code Editing automation scripts providing CLI access to AI-powered code assistance capabilities. This script module offers command-line interfaces for code generation, refactoring, analysis, and AI provider management, enabling seamless integration into development workflows and automation pipelines.

The ai_code_editing scripts serve as the primary interface for developers and automated systems to leverage AI capabilities for code-related tasks.

## Module Overview

### Key Capabilities
- **Code Generation**: Generate code snippets from natural language descriptions
- **Code Refactoring**: AI-assisted code improvement and optimization
- **Code Analysis**: Quality assessment and improvement suggestions
- **Provider Management**: API key validation and model availability checking
- **Multi-Language Support**: Support for multiple programming languages
- **Batch Operations**: Process multiple files or prompts efficiently

### Key Features
- Command-line interface with argument parsing
- Integration with all supported AI providers (OpenAI, Anthropic, Google AI)
- Structured output formatting (JSON, text, verbose)
- Error handling and validation
- Dry-run capabilities for safe testing
- Logging integration for operation tracking

## Function Signatures

### Core CLI Functions

```python
def main() -> None
```

Main CLI entry point for the AI code editing orchestrator.

**Command-line Usage:**
```bash
python orchestrate.py [command] [options]
```

**Available Commands:**
- `generate` - Generate code from natural language prompts
- `refactor` - Refactor existing code with AI assistance
- `analyze` - Analyze code quality and provide suggestions
- `validate-api-keys` - Validate API keys for all providers
- `list-providers` - List available AI providers
- `list-languages` - List supported programming languages
- `list-models` - List available models for a provider

**Global Options:**
- `--verbose, -v` - Enable verbose output
- `--dry-run` - Dry run mode (no actual changes)

```python
def handle_generate(args: argparse.Namespace) -> None
```

Handle code generation commands from CLI arguments.

**Parameters:**
- `args` (argparse.Namespace): Parsed command-line arguments containing:
  - `prompt` (str): Natural language description of desired code
  - `language` (str): Target programming language
  - `provider` (str, optional): AI provider to use (default: "openai")
  - `model` (str, optional): Specific model to use
  - `output` (str, optional): Output file path
  - `context` (str, optional): Additional context for generation

**Returns:** None (outputs generated code to stdout or file)

```python
def handle_refactor(args: argparse.Namespace) -> None
```

Handle code refactoring commands from CLI arguments.

**Parameters:**
- `args` (argparse.Namespace): Parsed command-line arguments containing:
  - `file` (str): Path to file to refactor
  - `instructions` (str): Refactoring instructions
  - `language` (str, optional): Programming language (auto-detected if not provided)
  - `provider` (str, optional): AI provider to use (default: "openai")
  - `output` (str, optional): Output file path (default: overwrite input file)

**Returns:** None (outputs refactored code to stdout or file)

```python
def handle_analyze(args: argparse.Namespace) -> None
```

Handle code analysis commands from CLI arguments.

**Parameters:**
- `args` (argparse.Namespace): Parsed command-line arguments containing:
  - `file` (str): Path to file to analyze
  - `language` (str, optional): Programming language (auto-detected if not provided)
  - `provider` (str, optional): AI provider to use (default: "openai")

**Returns:** None (outputs analysis results to stdout)

```python
def handle_validate_api_keys(args: argparse.Namespace) -> None
```

Validate API keys for all configured AI providers.

**Parameters:**
- `args` (argparse.Namespace): Parsed command-line arguments

**Returns:** None (outputs validation results to stdout)

```python
def handle_list_providers(args: argparse.Namespace) -> None
```

List all available AI providers and their status.

**Parameters:**
- `args` (argparse.Namespace): Parsed command-line arguments

**Returns:** None (outputs provider list to stdout)

```python
def handle_list_languages(args: argparse.Namespace) -> None
```

List all supported programming languages.

**Parameters:**
- `args` (argparse.Namespace): Parsed command-line arguments

**Returns:** None (outputs language list to stdout)

```python
def handle_list_models(args: argparse.Namespace) -> None
```

List available models for a specific AI provider.

**Parameters:**
- `args` (argparse.Namespace): Parsed command-line arguments containing:
  - `provider` (str): AI provider name

**Returns:** None (outputs model list to stdout)

## Active Components

### Core Implementation
- `__init__.py` – Module initialization and public API exports
- `orchestrate.py` – Main CLI orchestrator script

### Documentation
- `README.md` – Script usage and overview
- `AGENTS.md` – This coordination document

### Supporting Files
- Integration with `_orchestrator_utils.py` for shared utilities

## Operating Contracts

### Universal Script Protocols

All scripts in this module must:

1. **CLI Standards**: Follow consistent command-line argument patterns
2. **Error Handling**: Provide clear error messages and exit codes
3. **Logging Integration**: Use centralized logging for all operations
4. **Dry-Run Support**: Support safe testing without side effects
5. **Output Formatting**: Provide structured output options (JSON, text)

### Module-Specific Guidelines

#### Code Generation Scripts
- Validate input prompts for safety and appropriateness
- Provide clear success/failure feedback
- Support output to files or stdout
- Include timing information for performance tracking

#### Code Refactoring Scripts
- Preserve code functionality unless explicitly requested otherwise
- Create backups before modifying files
- Provide diff output for review before applying changes
- Support partial refactoring of specific functions

#### Analysis Scripts
- Provide actionable feedback with specific recommendations
- Include severity levels for identified issues
- Support multiple output formats for different consumers
- Integrate with CI/CD pipelines for automated quality gates

## Navigation Links

### Module Documentation
- **Script Overview**: [README.md](README.md) - Complete script documentation

### Related Scripts

### Platform Navigation
- **Scripts Directory**: [../README.md](../README.md) - Scripts directory overview

## Agent Coordination

### Integration Points

When integrating with other scripts:

1. **Shared Utilities**: Use `_orchestrator_utils.py` for common CLI patterns
2. **Configuration Sharing**: Coordinate API key and provider settings
3. **Output Consistency**: Maintain consistent output formats across scripts
4. **Error Propagation**: Handle and propagate errors appropriately

### Quality Gates

Before script changes are accepted:

1. **CLI Testing**: All command-line options work correctly
2. **Error Handling**: Scripts handle edge cases gracefully
3. **Documentation**: Help text and examples are current and accurate
4. **Integration**: Scripts work correctly with the core modules

## Version History

- **v0.1.0** (December 2025) - Initial AI code editing automation scripts with CLI interface

## Usage Examples

### Code Generation
```bash
# Generate a Python function
python orchestrate.py generate "create a function to calculate fibonacci numbers" --language python

# Generate with specific provider and model
python orchestrate.py generate "sort a list using quicksort" --language javascript --provider anthropic --model claude-3-sonnet
```

### Code Refactoring
```bash
# Refactor a Python file for performance
python orchestrate.py refactor my_code.py "optimize for better performance"

# Refactor with output to new file
python orchestrate.py refactor old_code.py "simplify the logic" --output new_code.py
```

### Code Analysis
```bash
# Analyze code quality
python orchestrate.py analyze my_script.py

# Analyze with verbose output
python orchestrate.py analyze complex_module.py --verbose
```

### Provider Management
```bash
# Validate all API keys
python orchestrate.py validate-api-keys

# List available providers
python orchestrate.py list-providers

# List models for a specific provider
python orchestrate.py list-models --provider openai
```
