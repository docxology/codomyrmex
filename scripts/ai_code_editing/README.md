# AI Code Editing Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.ai_code_editing` module.

## Purpose

This orchestrator provides command-line interface for AI-powered code generation, refactoring, and analysis operations.

## Usage

```bash
# Generate code
python scripts/ai_code_editing/orchestrate.py generate "create a fibonacci function" --language python

# Refactor code
python scripts/ai_code_editing/orchestrate.py refactor file.py "optimize for performance"

# Analyze code quality
python scripts/ai_code_editing/orchestrate.py analyze file.py

# Validate API keys
python scripts/ai_code_editing/orchestrate.py validate-api-keys

# List supported providers
python scripts/ai_code_editing/orchestrate.py list-providers

# List supported languages
python scripts/ai_code_editing/orchestrate.py list-languages

# List available models for a provider
python scripts/ai_code_editing/orchestrate.py list-models --provider openai
```

## Commands

- `generate` - Generate code snippets using LLMs
- `refactor` - Refactor existing code using LLMs
- `analyze` - Analyze code quality and provide suggestions
- `validate-api-keys` - Validate API keys for all providers
- `list-providers` - List supported LLM providers
- `list-languages` - List supported programming languages
- `list-models` - List available models for a provider

## Related Documentation

- **[Module README](../../src/codomyrmex/ai_code_editing/README.md)**: Complete module documentation
- **[API Specification](../../src/codomyrmex/ai_code_editing/API_SPECIFICATION.md)**: Detailed API reference
- **[MCP Tools](../../src/codomyrmex/ai_code_editing/MCP_TOOL_SPECIFICATION.md)**: AI integration tools
- **[Usage Examples](../../src/codomyrmex/ai_code_editing/USAGE_EXAMPLES.md)**: Practical examples
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.ai_code_editing.generate_code_snippet`
- `codomyrmex.ai_code_editing.refactor_code_snippet`
- `codomyrmex.ai_code_editing.analyze_code_quality`
- `codomyrmex.ai_code_editing.validate_api_keys`
- `codomyrmex.ai_code_editing.get_supported_providers`
- `codomyrmex.ai_code_editing.get_supported_languages`
- `codomyrmex.ai_code_editing.get_available_models`

See `codomyrmex.cli.py` for main CLI integration.

