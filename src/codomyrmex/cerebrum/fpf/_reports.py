"""Mixin for FPF orchestrator report generation and result export."""

import json
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class FPFReportMixin:
    """Result export and markdown report generation.

    Requires ``output_dir`` and ``logger`` from the host class.
    """

    def export_results(self, analysis_results: dict[str, Any]) -> None:
        """Export all results to JSON and markdown.

        Args:
            analysis_results: Comprehensive analysis results
        """
        self.logger.info("Exporting results")

        json_path = self.output_dir / "comprehensive_analysis.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(analysis_results, f, indent=2, default=str)
        self.logger.info("Exported JSON to %s", json_path)

        md_path = self.output_dir / "comprehensive_analysis.md"
        self._generate_markdown_report(analysis_results, md_path)
        self.logger.info("Exported markdown report to %s", md_path)

    def _generate_markdown_report(
        self, results: dict[str, Any], output_path: Path
    ) -> None:
        """Generate markdown report.

        Args:
            results: Analysis results
            output_path: Output file path
        """
        lines = [
            "# CEREBRUM Analysis of First Principles Framework",
            "",
            "## Overview",
            "",
            f"- **Total Patterns**: {results['fpf_statistics']['total_patterns']}",
            f"- **Total Concepts**: {results['fpf_statistics']['total_concepts']}",
            f"- **Total Relationships**: {results['fpf_statistics']['total_relationships']}",
            "",
            "## Case-Based Reasoning Analysis",
            "",
            f"- **Total Cases**: {results['case_based_reasoning']['total_cases']}",
            f"- **Case Base Size**: {results['case_based_reasoning']['case_base_size']}",
            "",
            "### Pattern Similarity Analysis",
            "",
        ]

        for pattern_id, data in list(
            results["case_based_reasoning"]["similarity_analysis"].items()
        )[:10]:
            prediction = data.get("prediction")
            prediction_text = (
                f"{prediction:.3f}" if isinstance(prediction, int | float) else "N/A"
            )
            confidence = data.get("confidence")
            confidence_text = (
                f"{confidence:.3f}" if isinstance(confidence, int | float) else "N/A"
            )
            lines.append(f"#### Pattern {pattern_id}")
            lines.append(f"- **Predicted Importance**: {prediction_text}")
            lines.append(f"- **Confidence**: {confidence_text}")
            lines.append(
                f"- **Similar Patterns Found**: {data.get('retrieved_count', 0)}"
            )
            lines.append("")

        lines.extend(
            [
                "## Bayesian Inference Analysis",
                "",
                f"- **Network Nodes**: {results['bayesian_inference']['network_nodes']}",
                f"- **Network Edges**: {results['bayesian_inference']['network_edges']}",
                "",
                "### Inference Results",
                "",
            ]
        )

        for pattern_id, data in list(
            results["bayesian_inference"]["inference_results"].items()
        )[:10]:
            if "importance_distribution" in data:
                lines.append(f"#### Pattern {pattern_id}")
                dist = data["importance_distribution"]
                lines.append(f"- **High Importance**: {dist.get('high', 0):.3f}")
                lines.append(f"- **Medium Importance**: {dist.get('medium', 0):.3f}")
                lines.append(f"- **Low Importance**: {dist.get('low', 0):.3f}")
                lines.append(f"- **Most Likely**: {data.get('most_likely', 'N/A')}")
                lines.append("")

        lines.extend(
            [
                "## Active Inference Exploration",
                "",
                "### Exploration Path",
                "",
            ]
        )

        for step in results["active_inference"]["exploration_path"][:10]:
            lines.append(
                f"- **{step['pattern_id']}**: Action={step['action']}, "
                f"FE={step['free_energy']:.3f}, Importance={step['importance']:.3f}"
            )

        fpf_analysis = results.get("fpf_analysis", {})
        lines.extend(
            [
                "",
                "## FPF Analysis",
                "",
                "### Critical Patterns",
                "",
            ]
        )

        critical_patterns = fpf_analysis.get("critical_patterns", [])
        if critical_patterns:
            for pattern_id, score in critical_patterns:
                lines.append(f"- **Pattern {pattern_id}**: Score={score:.3f}")
        else:
            lines.append("- No critical patterns reported.")

        lines.extend(["", "### Part Cohesion", ""])
        part_cohesion = fpf_analysis.get("part_cohesion", {})
        if part_cohesion:
            for part, score in part_cohesion.items():
                part_label = str(part)
                if not part_label.lower().startswith("part "):
                    part_label = f"Part {part_label}"
                lines.append(f"- **{part_label}**: Cohesion={score:.3f}")
        else:
            lines.append("- No part-cohesion results reported.")

        lines.extend(
            [
                "",
                "## Term Analysis",
                "",
                "### Important Terms",
                "",
            ]
        )

        term_analysis = results.get("term_analysis", {})
        important_terms = term_analysis.get("important_terms", [])
        if important_terms:
            for term, frequency, score in important_terms[:15]:
                lines.append(f"- **{term}**: Frequency={frequency}, Score={score:.3f}")
        else:
            lines.append("- No ranked terms reported.")

        lines.extend(["", "### Shared Terms", ""])
        shared_terms = term_analysis.get("shared_terms", [])
        if shared_terms:
            for term, occurrence_count, pattern_ids in shared_terms[:15]:
                patterns = ", ".join(str(pattern_id) for pattern_id in pattern_ids)
                lines.append(f"- **{term}**: Patterns={occurrence_count} ({patterns})")
        else:
            lines.append("- No shared terms reported.")

        lines.extend(
            [
                "",
                "---",
                "",
                "*Generated by CEREBRUM FPF Orchestrator*",
            ]
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
