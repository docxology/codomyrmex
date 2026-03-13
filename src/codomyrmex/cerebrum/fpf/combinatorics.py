"""Comprehensive combinatorics analysis using CEREBRUM on FPF.

This module generates all possible combinations and analyses of FPF patterns
using CEREBRUM methods, including:
- Pattern pair analysis
- Dependency chain analysis
- Concept co-occurrence analysis
- Cross-part relationships
- Term network analysis
"""

import json
from pathlib import Path
from typing import Any

from codomyrmex.cerebrum import CerebrumEngine
from codomyrmex.fpf import FPFAnalyzer, FPFClient, TermAnalyzer
from codomyrmex.logging_monitoring import get_logger

from ._analysis import FPFCombinatoricsAnalysisMixin
from ._visualization import FPFCombinatoricsVisualizationMixin

logger = get_logger(__name__)


class FPFCombinatoricsAnalyzer(
    FPFCombinatoricsAnalysisMixin,
    FPFCombinatoricsVisualizationMixin,
):
    """Analyzes all combinatorics of FPF patterns using CEREBRUM."""

    def __init__(
        self,
        fpf_spec_path: str | None = None,
        output_dir: str = "output/cerebrum/combinatorics",
    ):
        """Initialize combinatorics analyzer.

        Args:
            fpf_spec_path: Path to FPF-Spec.md
            output_dir: Output directory (default: output/cerebrum/combinatorics)
        """
        self.logger = get_logger(__name__)

        # Load FPF
        self.fpf_client = FPFClient()
        if fpf_spec_path:
            self.spec = self.fpf_client.load_from_file(fpf_spec_path)
        else:
            self.spec = self.fpf_client.fetch_and_load()

        # Initialize CEREBRUM
        self.cerebrum = CerebrumEngine()
        self.fpf_analyzer = FPFAnalyzer(self.spec)
        self.term_analyzer = TermAnalyzer()

        # Output
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(
            "Initialized combinatorics analyzer with %s patterns",
            len(self.spec.patterns),
        )

    def run_comprehensive_combinatorics(self) -> dict[str, Any]:
        """Run all combinatorics analyses.

        Returns:
            Complete combinatorics analysis results
        """
        self.logger.info("Running comprehensive combinatorics analysis")

        # Run analyses
        pair_analysis = self.analyze_pattern_pairs()
        chain_analysis = self.analyze_dependency_chains()
        cooccurrence_analysis = self.analyze_concept_cooccurrence()
        cross_part_analysis = self.analyze_cross_part_relationships()

        results = {
            "pattern_pairs": pair_analysis,
            "dependency_chains": chain_analysis,
            "concept_cooccurrence": cooccurrence_analysis,
            "cross_part_relationships": cross_part_analysis,
        }

        # Export results
        output_path = self.output_dir / "combinatorics_analysis.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, default=str)
        self.logger.info("Exported analysis to %s", output_path)

        # Generate visualizations
        self.generate_all_visualizations(results)

        return results
