# Codomyrmex Agents — projects/test_project/src

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: January 2026

## Signposting

- **Parent**: [test_project/AGENTS.md](../AGENTS.md)
- **Self**: [src/AGENTS.md](AGENTS.md)
- **Key Artifacts**: `main.py`, `analyzer.py`, `visualizer.py`, `reporter.py`, `pipeline.py`

## Purpose

Core Python source modules implementing the test_project analysis capabilities. Demonstrates comprehensive codomyrmex integration patterns.

## Active Components

| Module | Codomyrmex Integration | Key Classes |
| :--- | :--- | :--- |
| `main.py` | `logging_monitoring`, `config_management` | `run_analysis()`, `run_pipeline()` |
| `analyzer.py` | `static_analysis`, `pattern_matching`, `validation` | `ProjectAnalyzer`, `AnalysisResult` |
| `visualizer.py` | `data_visualization` | `DataVisualizer`, `ChartConfig` |
| `reporter.py` | `documentation` | `ReportGenerator`, `ReportConfig` |
| `pipeline.py` | `orchestrator`, `events` | `AnalysisPipeline`, `PipelineResult`, `PipelineStep` |

## Operating Contracts

### Code Standards

- Python 3.10+ with full type hints
- `@dataclass` for all data structures
- Comprehensive docstrings (Google style)
- Graceful fallback if codomyrmex not available

### Import Pattern

```python
try:
    from codomyrmex.logging_monitoring import get_logger
except ImportError:
    def get_logger(name): return logging.getLogger(name)
```

### Testing Requirements

- Unit tests for all public functions
- No mocking - use real implementations
- Minimum 80% coverage target

## Navigation Links

- **📁 Parent**: [../AGENTS.md](../AGENTS.md)
- **🏠 Project Root**: [../../README.md](../../README.md)
