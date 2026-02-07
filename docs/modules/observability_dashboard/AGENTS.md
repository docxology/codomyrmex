# Observability Dashboard Module — Agent Coordination

## Purpose

Unified monitoring dashboards for system observability.

## Key Capabilities

- **MetricType**: Types of metrics.
- **AlertSeverity**: Alert severity levels.
- **PanelType**: Dashboard panel types.
- **MetricValue**: A single metric value.
- **Alert**: An alert notification.
- `to_dict()`: Convert to dictionary.
- `is_active()`: Check if alert is still active.
- `duration()`: Get alert duration.

## Agent Usage Patterns

```python
from codomyrmex.observability_dashboard import MetricType

# Agent initializes observability dashboard
instance = MetricType()
```

## Integration Points

- **Source**: [src/codomyrmex/observability_dashboard/](../../../src/codomyrmex/observability_dashboard/)
- **Docs**: [Module Documentation](README.md)
- **Spec**: [Technical Specification](SPEC.md)

## Testing Guidelines

```bash
uv run python -m pytest src/codomyrmex/tests/ -k observability_dashboard -v
```

- Run tests before and after making changes.
- Ensure all existing tests pass before submitting.
