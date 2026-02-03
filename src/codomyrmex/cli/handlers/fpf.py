from typing import Optional
from pathlib import Path
import json
import traceback
from ..utils import get_logger

logger = get_logger(__name__)

def handle_fpf_fetch(repo: str, branch: str, output: Optional[str]) -> bool:
    """Handle FPF fetch command."""
    try:
        from codomyrmex.fpf import FPFFetcher
        fetcher = FPFFetcher()
        content = fetcher.fetch_latest(repo, branch)

        if output:
            Path(output).write_text(content, encoding="utf-8")
            print(f"✅ FPF specification fetched and saved to {output}")
        else:
            print(content)

        return True
    except Exception as e:
        logger.error(f"Error fetching FPF specification: {e}", exc_info=True)
        print(f"❌ Error fetching FPF specification: {str(e)}")
        return False


def handle_fpf_parse(file: str, output: Optional[str]) -> bool:
    """Handle FPF parse command."""
    try:
        from codomyrmex.fpf import FPFClient
        client = FPFClient()
        spec = client.load_from_file(file)

        print(f"✅ Parsed FPF specification: {len(spec.patterns)} patterns, {len(spec.concepts)} concepts")

        if output:
            client.export_json(output)
            print(f"✅ Exported to {output}")

        return True
    except Exception as e:
        logger.error(f"Error parsing FPF specification: {e}", exc_info=True)
        print(f"❌ Error parsing FPF specification: {str(e)}")
        return False


def handle_fpf_export(file: str, output: str, format: str) -> bool:
    """Handle FPF export command."""
    try:
        from codomyrmex.fpf import FPFClient
        client = FPFClient()
        client.load_from_file(file)
        client.export_json(output)

        print(f"✅ Exported FPF specification to {output}")
        return True
    except Exception as e:
        logger.error(f"Error exporting FPF specification: {e}", exc_info=True)
        print(f"❌ Error exporting FPF specification: {str(e)}")
        return False


def handle_fpf_search(query: str, file: Optional[str], filters: dict) -> bool:
    """Handle FPF search command."""
    try:
        if not file:
            # Try default location
            # Note: adjusted relative path logic for CLI location
            # src/codomyrmex/cli/handlers/fpf.py -> ../../../..
            # But simpler to assume src logic is consistent
            default_path = Path(__file__).parent.parent.parent / "fpf" / "FPF-Spec.md"
            if default_path.exists():
                file = str(default_path)
            else:
                print("❌ No file specified and default not found")
                return False

        from codomyrmex.fpf import FPFClient
        client = FPFClient()
        client.load_from_file(file)
        results = client.search(query, filters)

        print(f"Found {len(results)} matching patterns:")
        for pattern in results:
            print(f"  - {pattern.id}: {pattern.title}")

        return True
    except Exception as e:
        logger.error(f"Error searching FPF: {e}", exc_info=True)
        print(f"❌ Error searching FPF: {str(e)}")
        return False


def handle_fpf_visualize(file: str, viz_type: str, output: str, format: str, layout: str, chart_type: str) -> bool:
    """Handle FPF visualize command."""
    try:
        from codomyrmex.fpf import FPFClient, FPFVisualizer
        from codomyrmex.fpf.visualizer_png import FPFVisualizerPNG

        client = FPFClient()
        client.load_from_file(file)

        if format == "png":
            # Use PNG visualizer
            png_visualizer = FPFVisualizerPNG()
            output_path = Path(output)

            if viz_type == "shared-terms":
                png_visualizer.visualize_shared_terms_network(client.spec, output_path)
            elif viz_type == "dependencies":
                png_visualizer.visualize_pattern_dependencies(client.spec, output_path, layout=layout)
            elif viz_type == "concept-map":
                png_visualizer.visualize_concept_map(client.spec, output_path, layout=layout)
            elif viz_type == "part-hierarchy":
                png_visualizer.visualize_part_hierarchy(client.spec, output_path)
            elif viz_type == "status-distribution":
                png_visualizer.visualize_status_distribution(client.spec, output_path, chart_type=chart_type)
            else:
                # Default to hierarchy
                png_visualizer.visualize_pattern_dependencies(client.spec, output_path, layout="hierarchical")

            print(f"✅ PNG visualization saved to {output}")
        else:
            # Use Mermaid visualizer
            visualizer = FPFVisualizer()
            if viz_type == "hierarchy":
                diagram = visualizer.visualize_pattern_hierarchy(client.spec.patterns)
            else:
                diagram = visualizer.visualize_dependencies(client.spec.patterns)

            Path(output).write_text(diagram, encoding="utf-8")
            print(f"✅ Mermaid diagram saved to {output}")

        return True
    except Exception as e:
        logger.error(f"Error generating visualization: {e}", exc_info=True)
        print(f"❌ Error generating visualization: {str(e)}")
        return False


def handle_fpf_context(file: str, pattern: Optional[str], output: Optional[str], depth: int) -> bool:
    """Handle FPF context command."""
    try:
        from codomyrmex.fpf import FPFClient
        client = FPFClient()
        client.load_from_file(file)

        if pattern:
            context = client.build_context(pattern_id=pattern)
        else:
            context = client.build_context()

        if output:
            Path(output).write_text(context, encoding="utf-8")
            print(f"✅ Context saved to {output}")
        else:
            print(context)

        return True
    except Exception as e:
        logger.error(f"Error building context: {e}", exc_info=True)
        print(f"❌ Error building context: {str(e)}")
        return False


def handle_fpf_export_section(file: str, part: Optional[str], pattern: Optional[str], output: str, include_dependencies: bool) -> bool:
    """Handle FPF export-section command."""
    try:
        from codomyrmex.fpf import FPFClient
        from codomyrmex.fpf.section_manager import SectionManager
        from codomyrmex.fpf.section_exporter import SectionExporter

        client = FPFClient()
        client.load_from_file(file)

        section_manager = SectionManager(client.spec)
        exporter = SectionExporter(section_manager)

        if part:
            exporter.export_part(part, Path(output))
            print(f"✅ Part {part} exported to {output}")
        elif pattern:
            exporter.export_single_pattern(pattern, Path(output), include_related=include_dependencies)
            print(f"✅ Pattern {pattern} exported to {output}")
        else:
            print("❌ Must specify either --part or --pattern")
            return False

        return True
    except Exception as e:
        logger.error(f"Error exporting section: {e}", exc_info=True)
        print(f"❌ Error exporting section: {str(e)}")
        return False


def handle_fpf_analyze(file: str, output: Optional[str]) -> bool:
    """Handle FPF analyze command."""
    try:
        from codomyrmex.fpf import FPFClient
        from codomyrmex.fpf.analyzer import FPFAnalyzer

        client = FPFClient()
        client.load_from_file(file)

        analyzer = FPFAnalyzer(client.spec)
        analysis = analyzer.get_analysis_summary()

        if output:
            with open(output, "w", encoding="utf-8") as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
            print(f"✅ Analysis saved to {output}")
        else:
            print(json.dumps(analysis, indent=2, default=str))

        return True
    except Exception as e:
        logger.error(f"Error analyzing FPF: {e}", exc_info=True)
        print(f"❌ Error analyzing FPF: {str(e)}")
        return False


def handle_fpf_report(file: str, output: str, include_analysis: bool) -> bool:
    """Handle FPF report command."""
    try:
        from codomyrmex.fpf import FPFClient
        from codomyrmex.fpf.report_generator import ReportGenerator

        client = FPFClient()
        client.load_from_file(file)

        generator = ReportGenerator(client.spec)
        generator.generate_html_report(Path(output), include_analysis=include_analysis)

        print(f"✅ Report generated at {output}")
        return True
    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        print(f"❌ Error generating report: {str(e)}")
        return False
