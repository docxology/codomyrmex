# Code Review Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.code_review` module.

## Purpose

This orchestrator provides command-line interface for automated code review and quality analysis.

## Usage

```bash
# Analyze a single file
python scripts/code_review/orchestrate.py analyze-file file.py

# Analyze a project
python scripts/code_review/orchestrate.py analyze-project --path src/

# Generate review report
python scripts/code_review/orchestrate.py generate-report --path src/ --output report.json
```

## Commands

- `analyze-file` - Analyze a single file
- `analyze-project` - Analyze an entire project
- `generate-report` - Generate code review report

## Related Documentation

- **[Module README](../../src/codomyrmex/code_review/README.md)**: Complete module documentation
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.code_review.analyze_file`
- `codomyrmex.code_review.analyze_project`
- `codomyrmex.code_review.generate_report`

See `codomyrmex.cli.py` for main CLI integration.

