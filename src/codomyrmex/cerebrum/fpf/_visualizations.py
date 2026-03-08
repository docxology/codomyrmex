"""Mixin for FPF orchestrator visualization generation."""

import csv
import json
from pathlib import Path
from typing import Any

import matplotlib as mpl
import matplotlib.pyplot as plt

from codomyrmex.cerebrum import (
    Case,
    CaseVisualizer,
    CompositionVisualizer,
    ConcordanceVisualizer,
    Distribution,
    InferenceVisualizer,
    ModelVisualizer,
)
from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)


class FPFVisualizationMixin:
    """Visualization generation for FPF analysis results.

    Requires ``cerebrum``, ``spec``, ``output_dir``, and ``logger`` from the host class.
    """

    def generate_visualizations(self, analysis_results: dict[str, Any]) -> None:
        """Generate all visualizations.

        Args:
            analysis_results: Comprehensive analysis results
        """
        self.logger.info("Generating visualizations")

        viz_dir = self.output_dir / "visualizations"
        viz_dir.mkdir(parents=True, exist_ok=True)

        self._visualize_bayesian_network(viz_dir)
        self._visualize_case_similarity(analysis_results, viz_dir)
        self._visualize_inference_results(analysis_results, viz_dir)
        self._generate_concordance_visualizations(analysis_results, viz_dir)
        self._generate_composition_visualizations(analysis_results, viz_dir)

    def _visualize_bayesian_network(self, viz_dir: Path) -> None:
        """Visualize the Bayesian network."""
        if not self.cerebrum.bayesian_network:
            return
        try:
            mpl.use("Agg")
            visualizer = ModelVisualizer(figure_size=(14, 10), dpi=300)
            fig = visualizer.visualize_network(
                self.cerebrum.bayesian_network,
                layout="hierarchical",
                node_size_metric="degree",
                show_legend=True,
            )
            visualizer.save_figure(fig, str(viz_dir / "bayesian_network.png"))
            self.logger.info("Saved Bayesian network visualization")

            network_data = {
                "network_name": self.cerebrum.bayesian_network.name,
                "nodes": list(self.cerebrum.bayesian_network.nodes),
                "edges": [
                    {"parent": parent, "child": child}
                    for parent, children in self.cerebrum.bayesian_network.edges.items()
                    for child in children
                ],
            }
            json_path = viz_dir / "bayesian_network.json"
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(network_data, f, indent=2)
            self.logger.info("Exported Bayesian network raw data to %s", json_path)
        except Exception as e:
            self.logger.warning("Failed to visualize network: %s", e, exc_info=True)

    def _visualize_case_similarity(
        self, analysis_results: dict[str, Any], viz_dir: Path
    ) -> None:
        """Visualize case similarity across patterns."""
        try:
            cases_with_similarity = []
            case_data_rows = []
            for pattern_id, _cbr_data in list(
                analysis_results["case_based_reasoning"]["similarity_analysis"].items()
            )[:10]:
                pattern = self.spec.get_pattern_by_id(pattern_id)
                if pattern:
                    query_case = Case(
                        case_id="query",
                        features={
                            "status": pattern.status,
                            "part": pattern.part or "Other",
                        },
                    )
                    similar = self.cerebrum.case_base.retrieve_similar(query_case, k=5)
                    cases_with_similarity.extend(similar)

                    for case, similarity in similar:
                        case_data_rows.append(
                            {
                                "case_id": case.case_id,
                                "similarity_score": similarity,
                                "pattern_id": pattern_id,
                                "status": pattern.status or "",
                                "part": pattern.part or "Other",
                            }
                        )

            if cases_with_similarity:
                case_viz = CaseVisualizer(figure_size=(12, 10), dpi=300)
                fig = case_viz.plot_case_similarity(
                    cases_with_similarity[:20],
                    show_threshold=True,
                    threshold=0.5,
                )
                case_viz.save_figure(fig, str(viz_dir / "case_similarity.png"))
                self.logger.info("Saved case similarity visualization")

                if case_data_rows:
                    csv_path = viz_dir / "case_similarity.csv"
                    with open(csv_path, "w", encoding="utf-8", newline="") as f:
                        writer = csv.DictWriter(
                            f,
                            fieldnames=[
                                "case_id",
                                "similarity_score",
                                "pattern_id",
                                "status",
                                "part",
                            ],
                        )
                        writer.writeheader()
                        writer.writerows(case_data_rows[:20])
                    self.logger.info("Exported case similarity raw data to %s", csv_path)
        except Exception as e:
            self.logger.warning(
                "Failed to visualize case similarity: %s", e, exc_info=True
            )

    def _visualize_inference_results(
        self, analysis_results: dict[str, Any], viz_dir: Path
    ) -> None:
        """Visualize Bayesian inference results."""
        try:
            if not analysis_results["bayesian_inference"]["inference_results"]:
                return

            inference_data = {}
            inference_rows = []
            for pattern_id, result in list(
                analysis_results["bayesian_inference"]["inference_results"].items()
            )[:5]:
                if "importance_distribution" in result:
                    dist = Distribution(
                        values=["high", "medium", "low"],
                        probabilities=[
                            result["importance_distribution"]["high"],
                            result["importance_distribution"]["medium"],
                            result["importance_distribution"]["low"],
                        ],
                    )
                    inference_data[pattern_id] = dist

                    inference_rows.append(
                        {
                            "pattern_id": pattern_id,
                            "high_probability": result["importance_distribution"]["high"],
                            "medium_probability": result["importance_distribution"][
                                "medium"
                            ],
                            "low_probability": result["importance_distribution"]["low"],
                            "most_likely": result.get("most_likely", ""),
                        }
                    )

            if inference_data:
                inference_viz = InferenceVisualizer(figure_size=(12, 8), dpi=300)
                fig = inference_viz.plot_inference_results(inference_data)
                inference_viz.save_figure(fig, str(viz_dir / "inference_results.png"))
                self.logger.info("Saved inference results visualization")

                if inference_rows:
                    csv_path = viz_dir / "inference_results.csv"
                    with open(csv_path, "w", encoding="utf-8", newline="") as f:
                        writer = csv.DictWriter(
                            f,
                            fieldnames=[
                                "pattern_id",
                                "high_probability",
                                "medium_probability",
                                "low_probability",
                                "most_likely",
                            ],
                        )
                        writer.writeheader()
                        writer.writerows(inference_rows)
                    self.logger.info(
                        "Exported inference results raw data to %s", csv_path
                    )
        except Exception as e:
            self.logger.warning(
                "Failed to visualize inference results: %s", e, exc_info=True
            )

    def _generate_concordance_visualizations(
        self, analysis_results: dict[str, Any], viz_dir: Path
    ) -> None:
        """Generate concordance visualizations comparing different analyses."""
        try:
            mpl.use("Agg")
            concordance_viz = ConcordanceVisualizer(figure_size=(14, 10), dpi=300)

            cbr_results = {}
            bayesian_results = {}
            pattern_ids = []

            if "case_based_reasoning" in analysis_results:
                cbr_data = analysis_results["case_based_reasoning"].get(
                    "similarity_analysis", {}
                )
                for pattern_id, data in cbr_data.items():
                    if isinstance(data, dict) and "average_similarity" in data:
                        cbr_results[pattern_id] = data["average_similarity"]
                        pattern_ids.append(pattern_id)

            if "bayesian_inference" in analysis_results:
                bayesian_data = analysis_results["bayesian_inference"].get(
                    "inference_results", {}
                )
                for pattern_id, data in bayesian_data.items():
                    if isinstance(data, dict) and "most_likely" in data:
                        importance_dist = data.get("importance_distribution", {})
                        score = (
                            importance_dist.get("high", 0.0) * 1.0
                            + importance_dist.get("medium", 0.0) * 0.5
                        )
                        bayesian_results[pattern_id] = score
                        if pattern_id not in pattern_ids:
                            pattern_ids.append(pattern_id)

            if cbr_results and bayesian_results:
                fig = concordance_viz.plot_analysis_concordance_matrix(
                    cbr_results, bayesian_results, pattern_ids=pattern_ids[:20]
                )
                concordance_viz.theme.apply_to_axes(fig.axes[0])
                fig.savefig(
                    viz_dir / "analysis_concordance_matrix.png",
                    dpi=300,
                    bbox_inches="tight",
                )
                plt.close(fig)
                self.logger.info("Saved analysis concordance matrix")

        except Exception as e:
            self.logger.warning(
                "Failed to generate concordance visualizations: %s", e, exc_info=True
            )

    def _generate_composition_visualizations(
        self, analysis_results: dict[str, Any], viz_dir: Path
    ) -> None:
        """Generate composition visualizations (dashboards, summaries)."""
        try:
            mpl.use("Agg")
            composition_viz = CompositionVisualizer(figure_size=(20, 14), dpi=300)

            analysis_summary = {
                "status_distribution": {},
                "importance_distribution": {"high": 0, "medium": 0, "low": 0},
                "method_summary": {},
                "network_summary": {"nodes": 0, "edges": 0},
                "key_metrics": {},
                "part_distribution": {},
                "similarity_distribution": [],
                "coverage": {},
            }

            if "case_based_reasoning" in analysis_results:
                cbr_data = analysis_results["case_based_reasoning"]
                analysis_summary["method_summary"]["CBR"] = len(
                    cbr_data.get("similarity_analysis", {})
                )

            if "bayesian_inference" in analysis_results:
                bayesian_data = analysis_results["bayesian_inference"]
                analysis_summary["method_summary"]["Bayesian"] = len(
                    bayesian_data.get("inference_results", {})
                )

            if self.cerebrum.bayesian_network:
                analysis_summary["network_summary"]["nodes"] = len(
                    self.cerebrum.bayesian_network.nodes
                )
                analysis_summary["network_summary"]["edges"] = sum(
                    len(children)
                    for children in self.cerebrum.bayesian_network.edges.values()
                )

            composition_viz.create_analysis_overview_dashboard(
                analysis_summary, output_path=viz_dir / "analysis_overview.png"
            )
            self.logger.info("Saved analysis overview dashboard")

        except Exception as e:
            self.logger.warning(
                "Failed to generate composition visualizations: %s", e, exc_info=True
            )
