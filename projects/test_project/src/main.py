"""Main entry point for test_project.

Demonstrates integration with codomyrmex logging_monitoring and
config_management modules for structured logging and configuration.

Example:
    >>> from pathlib import Path
    >>> from src.main import run_analysis, run_pipeline
    >>> 
    >>> # Run analysis on a directory
    >>> results = run_analysis(Path("src"))
    >>> print(f"Files: {results['summary']['total_files']}")
    >>> 
    >>> # Run full pipeline
    >>> pipeline_result = run_pipeline()
    >>> print(f"Status: {pipeline_result.status.value}")
"""

from pathlib import Path
from typing import Optional, Dict, Any
import sys
import logging

# Configure basic logging if codomyrmex is not available
try:
    from codomyrmex.logging_monitoring import setup_logging, get_logger
    HAS_CODOMYRMEX_LOGGING = True
except ImportError:
    HAS_CODOMYRMEX_LOGGING = False
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)
    def setup_logging() -> None:
        pass

logger = get_logger(__name__)


def run_analysis(
    target_path: Path,
    config_path: Optional[Path] = None
) -> Dict[str, Any]:
    """Run project analysis using codomyrmex static_analysis.
    
    Demonstrates integration with:
    - codomyrmex.logging_monitoring for structured logging
    - codomyrmex.config_management for configuration loading
    - codomyrmex.static_analysis for code analysis
    
    Args:
        target_path: Path to file or directory to analyze.
        config_path: Optional path to configuration YAML file.
        
    Returns:
        Dictionary containing analysis results with keys:
        - target: str - Target path analyzed
        - files: List[dict] - Per-file analysis results
        - summary: dict - Aggregate statistics
        
    Example:
        >>> results = run_analysis(Path("src"))
        >>> print(f"Total lines: {results['summary']['total_lines']}")
    """
    setup_logging()
    logger.info(f"Starting analysis of {target_path}")
    
    # Import here to avoid circular imports
    from .analyzer import ProjectAnalyzer
    
    # Resolve config path
    if config_path is None:
        default_config = Path(__file__).parent.parent / "config" / "settings.yaml"
        if default_config.exists():
            config_path = default_config
            logger.debug(f"Using default config: {config_path}")
    
    # Create analyzer and run analysis
    analyzer = ProjectAnalyzer(config_path)
    results = analyzer.analyze(target_path)
    
    # Log summary
    summary = results.get("summary", {})
    logger.info(
        f"Analysis complete: {summary.get('total_files', 0)} files, "
        f"{summary.get('total_lines', 0)} lines, "
        f"{summary.get('total_functions', 0)} functions"
    )
    
    return results


def run_pipeline(
    target_path: Optional[Path] = None,
    config_path: Optional[Path] = None
) -> "PipelineResult":
    """Run the full analysis pipeline.
    
    Demonstrates orchestrator module integration with DAG-based
    workflow execution. The pipeline executes these steps:
    
    1. load_config - Load project configuration
    2. validate - Validate inputs and settings
    3. analyze - Run code analysis
    4. visualize - Generate visualizations
    5. report - Create final reports
    
    Args:
        target_path: Optional target path to analyze. Defaults to current directory.
        config_path: Optional path to configuration file.
        
    Returns:
        PipelineResult with execution status, duration, and step results.
        
    Example:
        >>> result = run_pipeline(Path("src"))
        >>> print(f"Status: {result.status.value}")
        >>> print(f"Duration: {result.duration_seconds:.2f}s")
    """
    setup_logging()
    logger.info("Starting full analysis pipeline")
    
    # Import here to avoid circular imports
    from .pipeline import AnalysisPipeline
    
    # Resolve target path
    if target_path is None:
        target_path = Path(__file__).parent
        logger.debug(f"Using default target: {target_path}")
    
    # Resolve config path
    if config_path is None:
        default_config = Path(__file__).parent.parent / "config" / "workflows.yaml"
        if default_config.exists():
            config_path = default_config
    
    # Create and execute pipeline
    pipeline = AnalysisPipeline(config_path)
    result = pipeline.execute(target_path)
    
    # Log completion
    logger.info(
        f"Pipeline {result.status.value} in {result.duration_seconds:.2f}s "
        f"({result.steps_completed}/{result.total_steps} steps)"
    )
    
    return result


def main() -> int:
    """Command-line entry point.
    
    Usage:
        python -m src.main [target_path]
        
    Args:
        target_path: Optional path to analyze (default: current directory)
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test Project - Codomyrmex Reference Implementation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main                    # Analyze current directory
  python -m src.main src/               # Analyze src directory
  python -m src.main --pipeline src/    # Run full pipeline
        """
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="Path to analyze (default: current directory)"
    )
    parser.add_argument(
        "--pipeline",
        action="store_true",
        help="Run full pipeline instead of just analysis"
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to configuration file"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        target = Path(args.target)
        
        if args.pipeline:
            result = run_pipeline(target, args.config)
            print(f"\n{'='*60}")
            print(f"Pipeline Status: {result.status.value}")
            print(f"Duration: {result.duration_seconds:.2f} seconds")
            print(f"Steps Completed: {result.steps_completed}/{result.total_steps}")
            if result.errors:
                print(f"Errors: {', '.join(result.errors)}")
            print(f"{'='*60}")
            return 0 if result.status.value == "completed" else 1
        else:
            results = run_analysis(target, args.config)
            summary = results.get("summary", {})
            print(f"\n{'='*60}")
            print(f"Analysis Results for: {results.get('target', 'Unknown')}")
            print(f"{'='*60}")
            print(f"Files Analyzed:   {summary.get('total_files', 0)}")
            print(f"Total Lines:      {summary.get('total_lines', 0)}")
            print(f"Total Functions:  {summary.get('total_functions', 0)}")
            print(f"Total Classes:    {summary.get('total_classes', 0)}")
            print(f"{'='*60}")
            return 0
            
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
