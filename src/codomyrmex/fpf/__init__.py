"""First Principles Framework (FPF) module.

This module provides functionality to fetch, parse, analyze, and export
the First Principles Framework specification for use in prompt/context engineering.
"""

from pathlib import Path

from .analysis.analyzer import FPFAnalyzer
from .analysis.indexer import FPFIndexer
from .analysis.report_generator import ReportGenerator
from .analysis.term_analyzer import TermAnalyzer
from .core.context_builder import ContextBuilder
from .core.extractor import FPFExtractor
from .core.models import (
    Concept,
    ConceptType,
    FPFIndex,
    FPFSpec,
    Pattern,
    PatternStatus,
    Relationship,
    RelationshipType,
)
from .core.parser import FPFParser
from .io.exporter import FPFExporter
from .io.fetcher import FPFFetcher
from .io.section_exporter import SectionExporter
from .io.section_importer import SectionImporter
from .io.section_manager import SectionManager
from .visualization.graph_generator import GraphGenerator
from .visualization.visualizer import FPFVisualizer
from .visualization.visualizer_png import FPFVisualizerPNG

__all__ = [
    # Main classes
    "FPFParser",
    "FPFExtractor",
    "FPFIndexer",
    "FPFFetcher",
    "FPFExporter",
    "FPFVisualizer",
    "FPFVisualizerPNG",
    "ContextBuilder",
    "TermAnalyzer",
    "GraphGenerator",
    "SectionManager",
    "SectionExporter",
    "SectionImporter",
    "FPFAnalyzer",
    "ReportGenerator",
    # Models
    "FPFSpec",
    "Pattern",
    "Concept",
    "Relationship",
    "FPFIndex",
    # Enums
    "PatternStatus",
    "ConceptType",
    "RelationshipType",
]


class FPFClient:
    """High-level client for working with FPF specifications.

    This class provides a convenient interface for common FPF operations.
    """

    def __init__(self, spec_path: str = None):
        """Initialize the FPF client.

        Args:
            spec_path: Optional path to local FPF-Spec.md file
        """
        self.parser = FPFParser()
        self.extractor = FPFExtractor()
        self.indexer = FPFIndexer()
        self.fetcher = FPFFetcher()
        self.exporter = FPFExporter()
        self.visualizer = FPFVisualizer()
        self.spec: FPFSpec = None
        self.spec_path = spec_path

    def load_from_file(self, file_path: str) -> FPFSpec:
        """Load and parse FPF specification from a local file.

        Args:
            file_path: Path to FPF-Spec.md file

        Returns:
            Parsed FPFSpec object
        """
        content = Path(file_path).read_text(encoding="utf-8")
        self.spec = self.parser.parse_spec(content, source_path=file_path)

        # Extract concepts and relationships
        self.spec.concepts = self.extractor.extract_concepts(self.spec)
        self.spec.relationships = self.extractor.extract_relationships(self.spec)

        # Build index
        self.indexer.build_index(self.spec)

        return self.spec

    def fetch_and_load(self, repo: str = "ailev/FPF", branch: str = "main") -> FPFSpec:
        """Fetch latest FPF specification from GitHub and load it.

        Args:
            repo: GitHub repository in format "owner/repo"
            branch: Branch name (default: "main")

        Returns:
            Parsed FPFSpec object
        """
        content = self.fetcher.fetch_latest(repo, branch)
        self.spec = self.parser.parse_spec(content, source_path=f"{repo}/{branch}")

        # Extract concepts and relationships
        self.spec.concepts = self.extractor.extract_concepts(self.spec)
        self.spec.relationships = self.extractor.extract_relationships(self.spec)

        # Build index
        self.indexer.build_index(self.spec)

        return self.spec

    def search(self, query: str, filters: dict = None) -> list[Pattern]:
        """Search for patterns.

        Args:
            query: Search query string
            filters: Optional filters

        Returns:
            List of matching Pattern objects
        """
        if not self.spec:
            raise ValueError("No specification loaded. Call load_from_file() or fetch_and_load() first.")

        return self.indexer.search_patterns(query, filters)

    def get_pattern(self, pattern_id: str) -> Pattern:
        """Get a pattern by ID.

        Args:
            pattern_id: Pattern identifier

        Returns:
            Pattern object
        """
        if not self.spec:
            raise ValueError("No specification loaded. Call load_from_file() or fetch_and_load() first.")

        pattern = self.indexer.get_pattern_by_id(pattern_id)
        if not pattern:
            raise ValueError(f"Pattern {pattern_id} not found.")

        return pattern

    def export_json(self, output_path: str) -> None:
        """Export the specification to JSON.

        Args:
            output_path: Path to output JSON file
        """
        if not self.spec:
            raise ValueError("No specification loaded. Call load_from_file() or fetch_and_load() first.")

        self.exporter.export_json(self.spec, Path(output_path))

    def build_context(self, pattern_id: str = None, filters: dict = None) -> str:
        """Build context string for prompt engineering.

        Args:
            pattern_id: Optional pattern ID to build context for
            filters: Optional filters for context building

        Returns:
            Context string
        """
        if not self.spec:
            raise ValueError("No specification loaded. Call load_from_file() or fetch_and_load() first.")

        builder = ContextBuilder(self.spec)
        if pattern_id:
            return builder.build_context_for_pattern(pattern_id)
        elif filters:
            return builder.build_minimal_context(filters)
        else:
            return builder.build_full_context()
