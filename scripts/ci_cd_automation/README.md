# CI/CD Automation Orchestrator

Thin orchestrator script providing CLI access to the `codomyrmex.ci_cd_automation` module.

## Purpose

This orchestrator provides command-line interface for CI/CD pipeline management, deployment orchestration, and monitoring.

## Usage

```bash
# Create CI/CD pipeline
python scripts/ci_cd_automation/orchestrate.py create-pipeline --name my-pipeline

# Run CI/CD pipeline
python scripts/ci_cd_automation/orchestrate.py run-pipeline --name my-pipeline

# Monitor pipeline health
python scripts/ci_cd_automation/orchestrate.py monitor-health --name my-pipeline

# Generate pipeline reports
python scripts/ci_cd_automation/orchestrate.py generate-reports --name my-pipeline
```

## Commands

- `create-pipeline` - Create and configure CI/CD pipelines
- `run-pipeline` - Execute pipeline with full orchestration
- `monitor-health` - Real-time pipeline monitoring
- `generate-reports` - Comprehensive pipeline analytics

## Related Documentation

- **[Module README](../../src/codomyrmex/ci_cd_automation/README.md)**: Complete module documentation
- **[CLI Reference](../../docs/reference/cli.md)**: Main CLI documentation

## Integration

This orchestrator calls functions from:
- `codomyrmex.ci_cd_automation.create_pipeline`
- `codomyrmex.ci_cd_automation.run_pipeline`
- `codomyrmex.ci_cd_automation.monitor_pipeline_health`
- `codomyrmex.ci_cd_automation.generate_pipeline_reports`

See `codomyrmex.cli.py` for main CLI integration.

