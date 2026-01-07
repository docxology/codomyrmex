#!/usr/bin/env python3
"""
FPF Orchestration Script

Main orchestrator for First Principles Framework (FPF) processing.
Provides CLI access to FPF specification processing, analysis, visualization, and export.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List

# Add project root and src to path for imports
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import shared utilities
try:
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_info,
        print_section,
        print_success,
        save_json_file,
    )
except ImportError:
    # Fallback if running from different directory
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_info,
        print_section,
        print_success,
        save_json_file,
    )

# Import FPF modules
from codomyrmex.fpf import (
    FPFClient,
    FPFAnalyzer,
    FPFExporter,
    FPFVisualizerPNG,
    ReportGenerator,
    SectionExporter,
    SectionManager,
)

logger = get_logger(__name__)


class FPFOrchestrator:
    """Orchestrates FPF specification processing pipeline."""

    def __init__(self, output_dir: Path, log_dir: Optional[Path] = None, dry_run: bool = False):
        """
        Initialize FPF orchestrator.

        Args:
            output_dir: Output directory for all generated files
            log_dir: Log directory (defaults to output_dir/logs)
            dry_run: If True, preview without writing files
        """
        self.output_dir = Path(output_dir)
        self.log_dir = log_dir if log_dir else self.output_dir / "logs"
        self.dry_run = dry_run
        self.client = FPFClient()
        self.spec = None

        # Create output directories
        if not dry_run:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            self.log_dir.mkdir(parents=True, exist_ok=True)

        # Subdirectories
        self.analysis_dir = self.output_dir / "analysis"
        self.json_dir = self.output_dir / "json"
        self.sections_dir = self.output_dir / "sections"
        self.viz_png_dir = self.output_dir / "visualizations" / "png"
        self.viz_mermaid_dir = self.output_dir / "visualizations" / "mermaid"
        self.reports_dir = self.output_dir / "reports"
        self.context_dir = self.output_dir / "context"

        if not dry_run:
            for dir_path in [
                self.analysis_dir,
                self.json_dir,
                self.sections_dir,
                self.viz_png_dir,
                self.viz_mermaid_dir,
                self.reports_dir,
                self.context_dir,
            ]:
                dir_path.mkdir(parents=True, exist_ok=True)

    def load_spec(self, source: str, fetch: bool = False) -> bool:
        """
        Load FPF specification from file or GitHub.

        Args:
            source: Path to local file or GitHub repo
            fetch: If True, fetch from GitHub

        Returns:
            True if successful
        """
        try:
            if fetch:
                repo, branch = source.split("/") if "/" in source else (source, "main")
                self.spec = self.client.fetch_and_load(repo=repo, branch=branch)
                logger.info(f"Fetched FPF specification from {repo}/{branch}")
            else:
                self.spec = self.client.load_from_file(source)
                logger.info(f"Loaded FPF specification from {source}")

            return True
        except Exception as e:
            logger.error(f"Failed to load FPF specification: {e}")
            return False

    def run_analysis(self) -> bool:
        """Run FPF specification analysis."""
        if not self.spec:
            logger.error("No specification loaded")
            return False

        try:
            analyzer = FPFAnalyzer(self.spec)
            
            # Run various analyses
            pattern_importance = analyzer.calculate_pattern_importance()
            concept_centrality = analyzer.calculate_concept_centrality()
            relationship_strength = analyzer.calculate_relationship_strength()
            dependency_depth = analyzer.analyze_dependency_depth()
            part_cohesion = analyzer.analyze_part_cohesion()
            
            analysis_results = {
                "pattern_importance": pattern_importance,
                "concept_centrality": concept_centrality,
                "relationship_strength": {str(k): v for k, v in relationship_strength.items()},
                "dependency_depth": dependency_depth,
                "part_cohesion": part_cohesion,
            }

            if not self.dry_run:
                import json
                analysis_file = self.analysis_dir / "analysis_results.json"
                with open(analysis_file, 'w') as f:
                    json.dump(analysis_results, f, indent=2, default=str)
                logger.info(f"Analysis results saved to {analysis_file}")

            return True
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            import traceback
            logger.exception("Analysis error details")
            return False

    def generate_visualizations(self, formats: List[str] = None) -> bool:
        """
        Generate visualizations.

        Args:
            formats: List of formats (png, mermaid)

        Returns:
            True if successful
        """
        if not self.spec:
            logger.error("No specification loaded")
            return False

        if formats is None:
            formats = ["png", "mermaid"]

        try:
            if "png" in formats:
                # Initialize visualizer with defaults (figsize, dpi)
                visualizer = FPFVisualizerPNG()
                # Generate various visualizations
                visualizer.visualize_pattern_dependencies(
                    self.spec,
                    Path(self.viz_png_dir / "dependencies.png")
                )
                visualizer.visualize_concept_map(
                    self.spec,
                    Path(self.viz_png_dir / "concept_map.png")
                )
                visualizer.visualize_part_hierarchy(
                    self.spec,
                    Path(self.viz_png_dir / "hierarchy.png")
                )
                logger.info("Generated PNG visualizations")

            if "mermaid" in formats:
                # Mermaid diagram generation would go here
                logger.info("Mermaid visualization generation not yet implemented")

            return True
        except Exception as e:
            logger.error(f"Visualization generation failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def export_sections(self) -> bool:
        """Export sections to separate files."""
        if not self.spec:
            logger.error("No specification loaded")
            return False

        try:
            from codomyrmex.fpf import SectionManager
            section_manager = SectionManager(self.spec)
            exporter = SectionExporter(section_manager)
            exporter.export_all_parts(Path(self.sections_dir))
            logger.info(f"Sections exported to {self.sections_dir}")
            return True
        except Exception as e:
            logger.error(f"Section export failed: {e}")
            import traceback
            logger.exception("Section export error details")
            return False

    def export_data(self) -> bool:
        """Export data to JSON and context strings."""
        if not self.spec:
            logger.error("No specification loaded")
            return False

        try:
            exporter = FPFExporter()
            exporter.export_json(self.spec, Path(self.json_dir / "fpf_spec.json"))
            logger.info("Data exported to JSON")
            return True
        except Exception as e:
            logger.error(f"Data export failed: {e}")
            import traceback
            logger.exception("Data export error details")
            return False

    def generate_report(self) -> bool:
        """Generate comprehensive HTML report."""
        if not self.spec:
            logger.error("No specification loaded")
            return False

        try:
            report_gen = ReportGenerator(self.spec)
            report_path = self.reports_dir / "fpf_report.html"
            report_gen.generate_report(report_path)
            logger.info(f"Report generated at {report_path}")
            return True
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return False

    def run_full_pipeline(
        self,
        source: str,
        fetch: bool = False,
        skip_analysis: bool = False,
        skip_viz: bool = False,
        skip_sections: bool = False,
        skip_data: bool = False,
        skip_report: bool = False,
        viz_formats: List[str] = None,
    ) -> bool:
        """
        Run full FPF processing pipeline.

        Args:
            source: Source path or GitHub repo
            fetch: Fetch from GitHub
            skip_analysis: Skip analysis step
            skip_viz: Skip visualization step
            skip_sections: Skip section export
            skip_data: Skip data export
            skip_report: Skip report generation
            viz_formats: Visualization formats (png, mermaid)

        Returns:
            True if all steps successful
        """
        logger.info("Starting FPF processing pipeline")

        # Load specification
        if not self.load_spec(source, fetch):
            return False

        success = True

        # Run analysis
        if not skip_analysis:
            if not self.run_analysis():
                success = False

        # Generate visualizations
        if not skip_viz:
            if not self.generate_visualizations(viz_formats):
                success = False

        # Export sections
        if not skip_sections:
            if not self.export_sections():
                success = False

        # Export data
        if not skip_data:
            if not self.export_data():
                success = False

        # Generate report
        if not skip_report:
            if not self.generate_report():
                success = False

        return success


def handle_pipeline(args):
    """Handle pipeline command."""
    output_dir = Path(args.output_dir) if args.output_dir else Path("./fpf_output")
    log_dir = Path(args.log_dir) if args.log_dir else output_dir / "logs"

    orchestrator = FPFOrchestrator(
        output_dir=output_dir,
        log_dir=log_dir,
        dry_run=args.dry_run
    )

    viz_formats = args.viz_formats.split(',') if args.viz_formats else None

    success = orchestrator.run_full_pipeline(
        source=args.source,
        fetch=args.fetch,
        skip_analysis=args.skip_analysis,
        skip_viz=args.skip_viz,
        skip_sections=args.skip_sections,
        skip_data=args.skip_data,
        skip_report=args.skip_report,
        viz_formats=viz_formats,
    )

    if success:
        print_success(f"FPF pipeline completed successfully!")
        print_info(f"Output directory: {output_dir}")
    else:
        print_error("FPF pipeline completed with errors")

    return success


def handle_info(args):
    """Handle info command."""
    try:
        verbose = getattr(args, "verbose", False)
        if verbose:
            logger.info("Retrieving FPF integration information")

        info = {
            "module": "fpf",
            "description": "First Principles Framework (FPF) processing and analysis",
            "setup_instructions": [
                "Use FPFClient to load specifications from file or GitHub",
                "Run pipeline: python scripts/fpf/orchestrate.py pipeline SOURCE",
            ],
            "location": "scripts/fpf/",
            "core_module": "src/codomyrmex/fpf/",
        }

        print_section("FPF Orchestrator")
        print("Main orchestrator for First Principles Framework processing.")
        print("")
        print("To process an FPF specification, run:")
        print(f"  python scripts/fpf/orchestrate.py pipeline SOURCE")
        print("")
        print(f"Location: {info['location']}")
        print(f"Core Module: {info['core_module']}")
        print_section("", separator="")

        output = getattr(args, "output", None)
        if output:
            output_path = save_json_file(info, output)
            if verbose:
                logger.info(f"Information saved to {output_path}")
            print_success(f"Information saved to {output_path}")

        return True

    except Exception as e:
        logger.exception("Unexpected error retrieving FPF information")
        print_error("Unexpected error retrieving FPF information", exception=e)
        return False


def main():
    """Main CLI entry point."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="FPF Orchestration operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s info
  %(prog)s pipeline FPF-Spec.md
  %(prog)s pipeline ailev/FPF --fetch --output-dir ./fpf_output
        """,
    )

    # Global options
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "--output", "-o", help="Output file path for JSON results"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show FPF integration information")

    # Pipeline command
    pipeline_parser = subparsers.add_parser("pipeline", help="Run FPF processing pipeline")
    pipeline_parser.add_argument("source", help="Path to FPF-Spec.md or GitHub repo")
    pipeline_parser.add_argument("--fetch", action="store_true", help="Fetch from GitHub")
    pipeline_parser.add_argument("--output-dir", default="./fpf_output", help="Output directory")
    pipeline_parser.add_argument("--log-dir", help="Log directory (default: output_dir/logs)")
    pipeline_parser.add_argument("--skip-analysis", action="store_true", help="Skip analysis step")
    pipeline_parser.add_argument("--skip-viz", action="store_true", help="Skip visualization step")
    pipeline_parser.add_argument("--skip-sections", action="store_true", help="Skip section export")
    pipeline_parser.add_argument("--skip-data", action="store_true", help="Skip data export")
    pipeline_parser.add_argument("--skip-report", action="store_true", help="Skip report generation")
    pipeline_parser.add_argument("--viz-formats", default="png,mermaid", help="Comma-separated formats (png,mermaid)")
    pipeline_parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")

    args = parser.parse_args()

    if not args.command:
        # Default to info command if no arguments provided
        args.command = "info"


    # Route to appropriate handler
    handlers = {
        "info": handle_info,
        "pipeline": handle_pipeline,
    }

    handler = handlers.get(args.command)
    if handler:
        success = handler(args)
        return 0 if success else 1
    else:
        print_error(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
