# Project Orchestration Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.project_orchestration` module.

## Purpose

This orchestrator provides command-line interface for workflow management, project management, and orchestration system operations.

## Usage

```bash
# List available workflows
python scripts/project_orchestration/orchestrate.py list-workflows

# Run a workflow
python scripts/project_orchestration/orchestrate.py run-workflow my-workflow

# List available projects
python scripts/project_orchestration/orchestrate.py list-projects

# Show orchestration system status
python scripts/project_orchestration/orchestrate.py status

# Check orchestration system health
python scripts/project_orchestration/orchestrate.py health
```

## Commands

- `list-workflows` - List available workflows
- `run-workflow` - Run a specific workflow
- `list-projects` - List available projects
- `status` - Show orchestration system status
- `health` - Check orchestration system health

## Related Documentation

- **[Module README](../../src/codomyrmex/project_orchestration/README.md)**: Complete module documentation
- **[API Specification](../../src/codomyrmex/project_orchestration/API_SPECIFICATION.md)**: Detailed API reference
- **[Usage Examples](../../src/codomyrmex/project_orchestration/USAGE_EXAMPLES.md)**: Practical examples
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.project_orchestration.get_workflow_manager`
- `codomyrmex.project_orchestration.get_project_manager`
- `codomyrmex.project_orchestration.get_orchestration_engine`

See `codomyrmex.cli.py` for main CLI integration.

