"""Test Project - Reference implementation for Codomyrmex.

This package demonstrates comprehensive usage of codomyrmex modules
including logging, analysis, visualization, reporting, agents, git
workflows, search, security, MCP exploration, and LLM inference.

Modules:
    main: Entry point with run_analysis() and run_pipeline() functions
    analyzer: Code analysis using static_analysis and pattern_matching
    visualizer: Data visualization and dashboard generation
    reporter: Multi-format report generation
    pipeline: DAG-based workflow orchestration
    agent_brain: Agents + agentic memory integration
    git_workflow: Git operations + git analysis integration
    knowledge_search: Search + scrape + formal verification
    security_audit: Security + crypto + maintenance + system_discovery
    mcp_explorer: MCP protocol + skills + plugin system
    llm_inference: LLM + collaboration (swarm) integration

Example:
    >>> from src.main import run_analysis
    >>> from pathlib import Path
    >>> results = run_analysis(Path("src"))
    >>> print(f"Analyzed {results['summary']['total_files']} files")
"""

__version__ = "1.1.0"
__author__ = "Codomyrmex Team"

from .agent_brain import AgentBrain
from .analyzer import AnalysisResult, ProjectAnalyzer
from .git_workflow import GitWorkflow
from .knowledge_search import KnowledgeSearch
from .llm_inference import LLMInference
from .main import run_analysis, run_pipeline
from .mcp_explorer import MCPExplorer
from .pipeline import AnalysisPipeline, PipelineResult, PipelineStatus
from .reporter import ReportConfig, ReportGenerator
from .security_audit import SecurityAudit
from .visualizer import ChartConfig, DataVisualizer

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
    # New modules (Sprint: module expansion)
    "AgentBrain",
    "GitWorkflow",
    "KnowledgeSearch",
    "SecurityAudit",
    "MCPExplorer",
    "LLMInference",
]
