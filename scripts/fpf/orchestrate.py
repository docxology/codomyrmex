#!/usr/bin/env python3
"""
FPF Orchestration Script

Thin orchestrator script providing CLI access to FPF module functionality.
Performs end-to-end FPF processing: fetch, parse, analyze, visualize, and export.

See also: src/codomyrmex/cli.py for main CLI integration
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

# Import logging setup
from codomyrmex.logging_monitoring.logger_config import setup_logging, get_logger

# Import shared utilities
try:
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_section,
        print_success,
        ProgressReporter,
        add_common_arguments,
        validate_dry_run,
    )
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from _orchestrator_utils import (
        format_output,
        print_error,
        print_section,
        print_success,
        ProgressReporter,
        add_common_arguments,
        validate_dry_run,
    )

# Import FPF module
from codomyrmex.fpf import (
    FPFClient,
    FPFAnalyzer,
    FPFVisualizerPNG,
    FPFVisualizer,
    SectionManager,
    SectionExporter,
    ReportGenerator,
    TermAnalyzer,
)

logger = get_logger(__name__)


class FPFOrchestrator:
    """Orchestrator for end-to-end FPF processing."""

    def __init__(
        self,
        output_dir: Path,
        log_dir: Optional[Path] = None,
        dry_run: bool = False,
    ):
        """Initialize orchestrator.

        Args:
            output_dir: Base output directory for all outputs
            log_dir: Optional directory for log files
            dry_run: If True, don't write files
        """
        self.output_dir = Path(output_dir)
        self.log_dir = log_dir or self.output_dir / "logs"
        self.dry_run = dry_run

        # Create output structure
        self.dirs = {
            "json": self.output_dir / "json",
            "sections": self.output_dir / "sections",
            "visualizations": self.output_dir / "visualizations",
            "png": self.output_dir / "visualizations" / "png",
            "mermaid": self.output_dir / "visualizations" / "mermaid",
            "reports": self.output_dir / "reports",
            "context": self.output_dir / "context",
            "analysis": self.output_dir / "analysis",
            "logs": self.log_dir,
        }

        if not self.dry_run:
            for dir_path in self.dirs.values():
                dir_path.mkdir(parents=True, exist_ok=True)

        self.client: Optional[FPFClient] = None
        self.spec = None

    def load_spec(self, source: str, fetch: bool = False) -> bool:
        """Load FPF specification.

        Args:
            source: Path to FPF-Spec.md or GitHub repo (if fetch=True)
            fetch: If True, fetch from GitHub

        Returns:
            True if successful
        """
        try:
            logger.info(f"Loading FPF spec from: {source}")
            self.client = FPFClient()

            if fetch:
                repo, branch = source.split("@") if "@" in source else (source, "main")
                if "/" not in repo:
                    repo = f"ailev/FPF"
                self.spec = self.client.fetch_and_load(repo=repo, branch=branch)
            else:
                self.spec = self.client.load_from_file(source)

            logger.info(f"Loaded {len(self.spec.patterns)} patterns, {len(self.spec.concepts)} concepts")
            return True

        except Exception as e:
            logger.exception("Failed to load FPF spec")
            print_error("Failed to load FPF spec", context={"source": source}, exception=e)
            return False

    def run_analysis(self) -> bool:
        """Run all analyses.

        Returns:
            True if successful
        """
        try:
            logger.info("Running FPF analysis")
            analyzer = FPFAnalyzer(self.spec)
            analysis = analyzer.get_analysis_summary()

            output_path = self.dirs["analysis"] / "analysis.json"
            if not self.dry_run:
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
                logger.info(f"Analysis saved to {output_path}")

            print_success(f"Analysis complete: {output_path}")
            return True

        except Exception as e:
            logger.exception("Failed to run analysis")
            print_error("Failed to run analysis", exception=e)
            return False

    def generate_visualizations(self, formats: List[str] = None) -> bool:
        """Generate all visualizations.

        Args:
            formats: List of formats to generate ("png", "mermaid"). If None, generates all.

        Returns:
            True if successful
        """
        if formats is None:
            formats = ["png", "mermaid"]

        try:
            logger.info("Generating visualizations")
            progress = ProgressReporter(total=len(formats) * 5, prefix="Visualizations")

            # PNG visualizations
            if "png" in formats:
                png_viz = FPFVisualizerPNG()
                progress.update(1, "Shared terms network")
                if not self.dry_run:
                    png_viz.visualize_shared_terms_network(
                        self.spec, self.dirs["png"] / "shared_terms.png"
                    )

                progress.update(1, "Pattern dependencies")
                if not self.dry_run:
                    png_viz.visualize_pattern_dependencies(
                        self.spec, self.dirs["png"] / "dependencies.png", layout="hierarchical"
                    )

                progress.update(1, "Concept map")
                if not self.dry_run:
                    png_viz.visualize_concept_map(
                        self.spec, self.dirs["png"] / "concept_map.png", layout="circular"
                    )

                progress.update(1, "Part hierarchy")
                if not self.dry_run:
                    png_viz.visualize_part_hierarchy(
                        self.spec, self.dirs["png"] / "part_hierarchy.png"
                    )

                progress.update(1, "Status distribution")
                if not self.dry_run:
                    png_viz.visualize_status_distribution(
                        self.spec, self.dirs["png"] / "status_distribution.png", chart_type="bar"
                    )

            # Mermaid visualizations
            if "mermaid" in formats:
                mermaid_viz = FPFVisualizer()
                progress.update(1, "Mermaid hierarchy")
                if not self.dry_run:
                    diagram = mermaid_viz.visualize_pattern_hierarchy(self.spec.patterns)
                    (self.dirs["mermaid"] / "hierarchy.mmd").write_text(diagram, encoding="utf-8")

                progress.update(1, "Mermaid dependencies")
                if not self.dry_run:
                    diagram = mermaid_viz.visualize_dependencies(self.spec.patterns)
                    (self.dirs["mermaid"] / "dependencies.mmd").write_text(diagram, encoding="utf-8")

            progress.complete("Visualizations generated")
            print_success("All visualizations generated")
            return True

        except Exception as e:
            logger.exception("Failed to generate visualizations")
            print_error("Failed to generate visualizations", exception=e)
            return False

    def export_sections(self) -> bool:
        """Export all sections.

        Returns:
            True if successful
        """
        try:
            logger.info("Exporting sections")
            section_manager = SectionManager(self.spec)
            exporter = SectionExporter(section_manager)

            progress = ProgressReporter(total=len(section_manager.list_parts()) + 1, prefix="Sections")

            # Export all parts
            if not self.dry_run:
                exported = exporter.export_all_parts(self.dirs["sections"] / "parts")
                progress.update(len(exported), f"Exported {len(exported)} parts")

            # Export individual patterns
            pattern_count = 0
            for pattern in self.spec.patterns:
                if not self.dry_run:
                    exporter.export_single_pattern(
                        pattern.id,
                        self.dirs["sections"] / "patterns" / f"{pattern.id}.json",
                        include_related=False,
                    )
                pattern_count += 1

            progress.update(1, f"Exported {pattern_count} patterns")
            progress.complete("Sections exported")

            print_success(f"Exported {len(section_manager.list_parts())} parts and {pattern_count} patterns")
            return True

        except Exception as e:
            logger.exception("Failed to export sections")
            print_error("Failed to export sections", exception=e)
            return False

    def export_data(self) -> bool:
        """Export data in all formats.

        Returns:
            True if successful
        """
        try:
            logger.info("Exporting data")
            progress = ProgressReporter(total=4, prefix="Data Export")

            # Full JSON export
            progress.update(1, "Full JSON export")
            if not self.dry_run:
                self.client.export_json(str(self.dirs["json"] / "fpf_full.json"))

            # Patterns only
            progress.update(1, "Patterns JSON")
            if not self.dry_run:
                from codomyrmex.fpf.exporter import FPFExporter
                exporter = FPFExporter()
                exporter.export_patterns_json(
                    self.spec.patterns, self.dirs["json"] / "patterns.json"
                )

            # Concepts only
            progress.update(1, "Concepts JSON")
            if not self.dry_run:
                exporter.export_concepts_json(
                    self.spec.concepts, self.dirs["json"] / "concepts.json"
                )

            # Context export
            progress.update(1, "Context export")
            if not self.dry_run:
                context = self.client.build_context()
                (self.dirs["context"] / "full_context.txt").write_text(context, encoding="utf-8")

            progress.complete("Data exported")
            print_success("All data formats exported")
            return True

        except Exception as e:
            logger.exception("Failed to export data")
            print_error("Failed to export data", exception=e)
            return False

    def generate_report(self) -> bool:
        """Generate comprehensive HTML report.

        Returns:
            True if successful
        """
        try:
            logger.info("Generating HTML report")
            generator = ReportGenerator(self.spec)
            output_path = self.dirs["reports"] / "fpf_report.html"

            if not self.dry_run:
                generator.generate_html_report(output_path, include_analysis=True)

            print_success(f"Report generated: {output_path}")
            return True

        except Exception as e:
            logger.exception("Failed to generate report")
            print_error("Failed to generate report", exception=e)
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
        """Run full FPF processing pipeline.

        Args:
            source: Source file or repo
            fetch: If True, fetch from GitHub
            skip_analysis: Skip analysis step
            skip_viz: Skip visualization step
            skip_sections: Skip section export
            skip_data: Skip data export
            skip_report: Skip report generation
            viz_formats: Visualization formats to generate

        Returns:
            True if all steps successful
        """
        print_section("FPF Orchestration Pipeline")
        logger.info("Starting FPF orchestration pipeline")

        # Load spec
        if not self.load_spec(source, fetch=fetch):
            return False

        success = True

        # Run analysis
        if not skip_analysis:
            if not self.run_analysis():
                success = False

        # Generate visualizations
        if not skip_viz:
            if not self.generate_visualizations(formats=viz_formats):
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

        if success:
            print_section("Pipeline Complete")
            print_success(f"All outputs saved to: {self.output_dir}")
            logger.info("FPF orchestration pipeline completed successfully")
        else:
            print_error("Pipeline completed with errors")
            logger.warning("FPF orchestration pipeline completed with errors")

        return success


def handle_full_pipeline(args):
    """Handle full pipeline command."""
    orchestrator = FPFOrchestrator(
        output_dir=Path(args.output_dir),
        log_dir=Path(args.log_dir) if args.log_dir else None,
        dry_run=validate_dry_run(args),
    )

    viz_formats = args.viz_formats.split(",") if args.viz_formats else None

    return orchestrator.run_full_pipeline(
        source=args.source,
        fetch=args.fetch,
        skip_analysis=args.skip_analysis,
        skip_viz=args.skip_viz,
        skip_sections=args.skip_sections,
        skip_data=args.skip_data,
        skip_report=args.skip_report,
        viz_formats=viz_formats,
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="FPF Orchestration - End-to-end FPF processing pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    add_common_arguments(parser)

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Full pipeline command
    pipeline_parser = subparsers.add_parser("pipeline", help="Run full processing pipeline")
    pipeline_parser.add_argument("source", help="Path to FPF-Spec.md or GitHub repo")
    pipeline_parser.add_argument("--fetch", action="store_true", help="Fetch from GitHub")
    pipeline_parser.add_argument("--output-dir", default="./fpf_output", help="Output directory")
    pipeline_parser.add_argument("--log-dir", help="Log directory (default: output_dir/logs)")
    pipeline_parser.add_argument("--skip-analysis", action="store_true", help="Skip analysis")
    pipeline_parser.add_argument("--skip-viz", action="store_true", help="Skip visualizations")
    pipeline_parser.add_argument("--skip-sections", action="store_true", help="Skip section export")
    pipeline_parser.add_argument("--skip-data", action="store_true", help="Skip data export")
    pipeline_parser.add_argument("--skip-report", action="store_true", help="Skip report generation")
    pipeline_parser.add_argument(
        "--viz-formats", default="png,mermaid", help="Comma-separated formats (png,mermaid)"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == "pipeline":
        success = handle_full_pipeline(args)
        return 0 if success else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

