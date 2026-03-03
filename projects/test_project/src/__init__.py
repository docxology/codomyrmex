"""Test Project - Reference implementation for Codomyrmex.

This package demonstrates comprehensive usage of codomyrmex modules
including logging, analysis, visualization, and reporting capabilities.

Modules:
    main: Entry point with run_analysis() and run_pipeline() functions
    analyzer: Code analysis using static_analysis and pattern_matching
    visualizer: Data visualization and dashboard generation
    reporter: Multi-format report generation
    pipeline: DAG-based workflow orchestration

Example:
    >>> from src.main import run_analysis
    >>> from pathlib import Path
    >>> results = run_analysis(Path("src"))
    >>> print(f"Analyzed {results['summary']['total_files']} files")
"""

__version__ = "1.0.0"
__author__ = "Codomyrmex Team"

from .main import run_analysis, run_pipeline
from .analyzer import ProjectAnalyzer, AnalysisResult
from .visualizer import DataVisualizer, ChartConfig
from .reporter import ReportGenerator, ReportConfig
from .pipeline import AnalysisPipeline, PipelineResult, PipelineStatus

__all__ = [
    # Entry points
    "run_analysis",
    "run_pipeline",
    # Analyzer
    "ProjectAnalyzer",
    "AnalysisResult",
    # Visualizer
    "DataVisualizer",
    "ChartConfig",
    # Reporter
    "ReportGenerator",
    "ReportConfig",
    # Pipeline
    "AnalysisPipeline",
    "PipelineResult",
    "PipelineStatus",
]
