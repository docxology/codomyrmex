# Language Models Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.language_models` module.

## Purpose

This orchestrator provides command-line interface for local LLM integration and Ollama management.

## Usage

```bash
# Check Ollama availability
python scripts/language_models/orchestrate.py check-availability

# List available models
python scripts/language_models/orchestrate.py list-models

# Show configuration
python scripts/language_models/orchestrate.py config
```

## Commands

- `check-availability` - Check Ollama availability
- `list-models` - List available models
- `config` - Show configuration

## Related Documentation

- **[Module README](../../src/codomyrmex/language_models/README.md)**: Complete module documentation
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.language_models.check_ollama_availability`
- `codomyrmex.language_models.get_available_models`
- `codomyrmex.language_models.get_config`

See `codomyrmex.cli.py` for main CLI integration.

