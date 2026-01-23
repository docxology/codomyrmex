# Personal AI Infrastructure - src Context

**Directory**: `projects/test_project/src/`
**Status**: Active

## Overview

Core Python implementation demonstrating codomyrmex module integration patterns.

## AI Context

### Module Usage Patterns

| Task | Module | Function |
| :--- | :--- | :--- |
| Analyze code | `analyzer.py` | `ProjectAnalyzer.analyze()` |
| Create dashboard | `visualizer.py` | `DataVisualizer.create_dashboard()` |
| Generate report | `reporter.py` | `ReportGenerator.generate()` |
| Run pipeline | `pipeline.py` | `AnalysisPipeline.execute()` |

### Key Design Patterns

1. **Dataclasses**: All data structures use `@dataclass`
2. **Optional imports**: Graceful fallback if codomyrmex unavailable
3. **Logging**: Unified via `get_logger(__name__)`
4. **Type hints**: Complete annotations on all public APIs

## Navigation

- **Parent**: [../PAI.md](../PAI.md)
