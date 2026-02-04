# src/ - Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Core implementation of test_project analysis capabilities. Provides a complete, working example of codomyrmex module integration.

## Module Specifications

### main.py

- **Function**: `run_analysis(target_path, config_path)` → `Dict[str, Any]`
- **Function**: `run_pipeline(target_path, config_path)` → `PipelineResult`
- **Function**: `main()` → `int` (CLI entry point)

### analyzer.py

- **Class**: `AnalysisResult` (dataclass)
  - `file_path: Path`, `metrics: Dict`, `issues: List`, `patterns: List`
- **Class**: `ProjectAnalyzer`
  - `analyze(target_path: Path)` → `Dict[str, Any]`

### visualizer.py

- **Class**: `ChartConfig` (dataclass)
- **Class**: `DataVisualizer`
  - `create_dashboard(results)` → `Path`
  - `visualize_metrics(metrics, config)` → `Path`

### reporter.py

- **Class**: `ReportConfig` (dataclass)
- **Class**: `ReportGenerator`
  - `generate(results, config)` → `Path`
  - `generate_all_formats(results)` → `Dict[str, Path]`

### pipeline.py

- **Enum**: `PipelineStatus` (PENDING, RUNNING, COMPLETED, FAILED, CANCELLED)
- **Class**: `PipelineStep` (dataclass)
- **Class**: `PipelineResult` (dataclass)
- **Class**: `AnalysisPipeline`
  - `add_step(name, handler, dependencies)` → `None`
  - `execute(target_path)` → `PipelineResult`

## Navigation

- **Human Documentation**: [README.md](README.md)
- **Agent Coordination**: [AGENTS.md](AGENTS.md)
- **Parent**: [../README.md](../README.md)
