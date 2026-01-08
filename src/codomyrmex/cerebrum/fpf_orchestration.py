from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse
import json

import csv
import matplotlib
import matplotlib.pyplot as plt

from codomyrmex.cerebrum import (
from codomyrmex.cerebrum.bayesian import Distribution
from codomyrmex.cerebrum.visualization import (
from codomyrmex.fpf import FPFClient, FPFAnalyzer, TermAnalyzer
from codomyrmex.logging_monitoring import get_logger, setup_logging






    ActiveInferenceAgent,
    BayesianNetwork,
    CaseRetriever,
    CerebrumConfig,
    InferenceEngine,
    Model,
    Case,
    CaseBase,
    CerebrumEngine,
    ReasoningResult,
)
"""CEREBRUM orchestration for FPF analysis.

This script demonstrates comprehensive application of CEREBRUM methods
(case-based reasoning, Bayesian inference, active inference) to analyze
and reason about the First Principles Framework specification.
"""

try:
    matplotlib.use('Agg')  # Use non-interactive backend
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    plt = None


    CaseVisualizer,
    InferenceVisualizer,
    ModelVisualizer,
)

logger = get_logger(__name__)


class FPFOrchestrator:
    """Orchestrates CEREBRUM methods for comprehensive FPF analysis."""

    def __init__(self, fpf_spec_path: Optional[str] = None, output_dir: str = "output/cerebrum/orchestration"):
        """Initialize FPF orchestrator.

        Args:
            fpf_spec_path: Path to FPF-Spec.md (if None, will fetch from GitHub)
            output_dir: Directory for output files (default: output/cerebrum/orchestration)
        """
        setup_logging()
        self.logger = get_logger(__name__)

        # Initialize FPF client
        self.fpf_client = FPFClient()
        if fpf_spec_path:
            self.spec = self.fpf_client.load_from_file(fpf_spec_path)
        else:
            self.spec = self.fpf_client.fetch_and_load()

        # Initialize CEREBRUM engine
        config = CerebrumConfig(
            case_similarity_threshold=0.6,
            max_retrieved_cases=20,
            inference_method="variable_elimination",
            adaptation_rate=0.1,
        )
        self.cerebrum = CerebrumEngine(config)

        # Initialize analyzers
        self.fpf_analyzer = FPFAnalyzer(self.spec)
        self.term_analyzer = TermAnalyzer()

        # Output directory
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Initialized FPF Orchestrator with {len(self.spec.patterns)} patterns")

    def create_pattern_cases(self) -> List[Case]:
        """Create cases from FPF patterns for case-based reasoning.

        Returns:
            List of Case objects
        """
        cases = []
        for pattern in self.spec.patterns:
            # Extract features from pattern
            features = {
                "status": pattern.status,
                "part": pattern.part or "Other",
                "num_keywords": len(pattern.keywords),
                "num_dependencies": sum(len(deps) for deps in pattern.dependencies.values()),
                "has_builds_on": len(pattern.dependencies.get("builds_on", [])) > 0,
                "has_prerequisite": len(pattern.dependencies.get("prerequisite_for", [])) > 0,
            }

            # Add keyword features
            for keyword in pattern.keywords[:5]:  # Limit to top 5 keywords
                features[f"keyword_{keyword.lower().replace(' ', '_')}"] = 1.0

            # Outcome: pattern importance (will be computed)
            case = Case(
                case_id=f"pattern_{pattern.id}",
                features=features,
                context={
                    "pattern_id": pattern.id,
                    "title": pattern.title,
                    "keywords": pattern.keywords,
                    "dependencies": pattern.dependencies,
                },
                outcome=None,  # Will be set after analysis
                metadata={
                    "pattern_id": pattern.id,
                    "title": pattern.title,
                    "part": pattern.part,
                },
            )
            cases.append(case)

        self.logger.info(f"Created {len(cases)} cases from FPF patterns")
        return cases

    def build_bayesian_network_from_fpf(self) -> BayesianNetwork:
        """Build Bayesian network from FPF pattern relationships.

        Returns:
            BayesianNetwork representing FPF structure
        """
        network = BayesianNetwork(name="fpf_pattern_network")

        # Add nodes for pattern status
        network.add_node("pattern_status", values=["Stable", "Draft", "Stub", "New"])

        # Add nodes for parts
        parts = {p.part for p in self.spec.patterns if p.part}
        for part in parts:
            network.add_node(f"part_{part}", values=["present", "absent"])

        # Add nodes for key concepts
        important_concepts = self.term_analyzer.get_important_terms(self.spec, top_n=10)
        for concept, _, _ in important_concepts[:5]:  # Top 5 concepts
            node_name = f"concept_{concept.lower().replace('.', '_').replace(' ', '_')[:20]}"
            network.add_node(node_name, values=["high", "medium", "low"])

        # Add relationship nodes
        network.add_node("has_dependencies", values=["yes", "no"])
        network.add_node("pattern_importance", values=["high", "medium", "low"])

        # Add edges
        network.add_edge("pattern_status", "pattern_importance")
        network.add_edge("has_dependencies", "pattern_importance")

        # Set conditional probability tables
        # Pattern importance given status
        network.set_cpt("pattern_importance", {
            ("Stable", "yes"): {"high": 0.7, "medium": 0.2, "low": 0.1},
            ("Stable", "no"): {"high": 0.3, "medium": 0.4, "low": 0.3},
            ("Draft", "yes"): {"high": 0.4, "medium": 0.4, "low": 0.2},
            ("Draft", "no"): {"high": 0.2, "medium": 0.3, "low": 0.5},
            ("Stub", "yes"): {"high": 0.2, "medium": 0.3, "low": 0.5},
            ("Stub", "no"): {"high": 0.1, "medium": 0.2, "low": 0.7},
            ("New", "yes"): {"high": 0.3, "medium": 0.4, "low": 0.3},
            ("New", "no"): {"high": 0.1, "medium": 0.3, "low": 0.6},
        })

        self.logger.info(f"Built Bayesian network with {len(network.nodes)} nodes")
        return network

    def analyze_with_case_based_reasoning(self) -> Dict[str, Any]:
        """Analyze FPF using case-based reasoning.

        Returns:
            Dictionary with analysis results
        """
        self.logger.info("Starting case-based reasoning analysis")

        # Create cases
        cases = self.create_pattern_cases()

        # Add cases to case base
        for case in cases:
            self.cerebrum.add_case(case)

        # Compute pattern importance from FPF analyzer
        importance_scores = self.fpf_analyzer.calculate_pattern_importance()

        # Update cases with importance outcomes
        for pattern in self.spec.patterns:
            case_id = f"pattern_{pattern.id}"
            importance = importance_scores.get(pattern.id, 0.5)
            # Normalize to [0, 1]
            normalized_importance = min(1.0, importance * 2.0) if importance > 0 else 0.0
            self.cerebrum.learn_from_case(
                Case(
                    case_id=case_id,
                    features=cases[0].features if cases else {},
                    outcome=normalized_importance,
                ),
                normalized_importance,
            )

        # Find similar patterns for each pattern
        similarity_analysis = {}
        for pattern in self.spec.patterns[:20]:  # Analyze top 20 patterns
            query_case = Case(
                case_id="query",
                features={
                    "status": pattern.status,
                    "part": pattern.part or "Other",
                    "num_keywords": len(pattern.keywords),
                    "num_dependencies": sum(len(deps) for deps in pattern.dependencies.values()),
                },
            )

            result = self.cerebrum.reason(query_case)
            similarity_analysis[pattern.id] = {
                "prediction": result.prediction,
                "confidence": result.confidence,
                "retrieved_count": len(result.retrieved_cases),
                "similar_patterns": [
                    {
                        "pattern_id": c.metadata.get("pattern_id"),
                        "title": c.metadata.get("title"),
                        "similarity": None,  # Would need to compute
                    }
                    for c in result.retrieved_cases[:5]
                ],
            }

        self.logger.info(f"Completed case-based reasoning for {len(similarity_analysis)} patterns")
        return {
            "similarity_analysis": similarity_analysis,
            "total_cases": len(cases),
            "case_base_size": self.cerebrum.case_base.size(),
        }

    def analyze_with_bayesian_inference(self) -> Dict[str, Any]:
        """Analyze FPF using Bayesian inference.

        Returns:
            Dictionary with inference results
        """
        self.logger.info("Starting Bayesian inference analysis")

        # Build network
        network = self.build_bayesian_network_from_fpf()
        self.cerebrum.set_bayesian_network(network)

        # Perform inference for each pattern
        inference_results = {}
        for pattern in self.spec.patterns[:20]:  # Analyze top 20
            # Prepare evidence
            evidence = {
                "pattern_status": pattern.status,
                "has_dependencies": "yes" if any(pattern.dependencies.values()) else "no",
            }

            # Query pattern importance
            inference = InferenceEngine(network, method="variable_elimination")
            try:
                result = inference.compute_marginal("pattern_importance", evidence)
                inference_results[pattern.id] = {
                    "importance_distribution": {
                        "high": result.probabilities[result.values.index("high")] if "high" in result.values else 0.0,
                        "medium": result.probabilities[result.values.index("medium")] if "medium" in result.values else 0.0,
                        "low": result.probabilities[result.values.index("low")] if "low" in result.values else 0.0,
                    },
                    "most_likely": result.mode(),
                    "evidence": evidence,
                }
            except Exception as e:
                self.logger.warning(f"Inference failed for {pattern.id}: {e}")
                inference_results[pattern.id] = {"error": str(e)}

        self.logger.info(f"Completed Bayesian inference for {len(inference_results)} patterns")
        return {
            "inference_results": inference_results,
            "network_nodes": len(network.nodes),
            "network_edges": sum(len(edges) for edges in network.edges.values()),
        }

    def analyze_with_active_inference(self) -> Dict[str, Any]:
        """Analyze FPF using active inference.

        Returns:
            Dictionary with active inference results
        """
        self.logger.info("Starting active inference analysis")

        # Define states (pattern exploration states)
        states = ["unexplored", "exploring", "analyzed", "completed"]

        # Define observations (what we can observe about patterns)
        observations = ["high_importance", "medium_importance", "low_importance", "unknown"]

        # Define actions (exploration actions)
        actions = ["analyze_pattern", "explore_dependencies", "analyze_concepts", "skip"]

        # Create active inference agent
        agent = ActiveInferenceAgent(
            states=states,
            observations=observations,
            actions=actions,
            precision=1.0,
            policy_horizon=3,
        )

        # Set transition model
        transition_model = {
            "unexplored_analyze_pattern": {"exploring": 0.8, "analyzed": 0.2},
            "exploring_analyze_pattern": {"analyzed": 0.9, "exploring": 0.1},
            "analyzed_explore_dependencies": {"exploring": 0.6, "completed": 0.4},
            "analyzed_analyze_concepts": {"completed": 0.7, "analyzed": 0.3},
        }
        agent.set_transition_model(transition_model)

        # Set observation model
        importance_scores = self.fpf_analyzer.calculate_pattern_importance()
        observation_model = {
            "analyzed": {
                "high_importance": 0.6,
                "medium_importance": 0.3,
                "low_importance": 0.1,
                "unknown": 0.0,
            },
            "exploring": {
                "high_importance": 0.2,
                "medium_importance": 0.3,
                "low_importance": 0.2,
                "unknown": 0.3,
            },
        }
        agent.set_observation_model(observation_model)

        # Simulate exploration of patterns
        exploration_path = []
        for pattern in self.spec.patterns[:10]:  # Explore top 10
            importance = importance_scores.get(pattern.id, 0.5)

            # Determine observation
            if importance > 0.7:
                observation = {"test": "high_importance"}
            elif importance > 0.4:
                observation = {"test": "medium_importance"}
            else:
                observation = {"test": "low_importance"}

            agent.update_beliefs(observation)
            action = agent.select_action()
            free_energy = agent.compute_free_energy()

            exploration_path.append({
                "pattern_id": pattern.id,
                "action": action,
                "free_energy": free_energy,
                "importance": importance,
            })

        self.cerebrum.set_active_inference_agent(agent)

        self.logger.info(f"Completed active inference exploration for {len(exploration_path)} patterns")
        return {
            "exploration_path": exploration_path,
            "final_beliefs": agent.get_beliefs().to_dict(),
        }

    def generate_comprehensive_analysis(self) -> Dict[str, Any]:
        """Generate comprehensive analysis combining all CEREBRUM methods.

        Returns:
            Dictionary with all analysis results
        """
        self.logger.info("Generating comprehensive CEREBRUM analysis")

        # Run all analyses
        cbr_results = self.analyze_with_case_based_reasoning()
        bayesian_results = self.analyze_with_bayesian_inference()
        active_inference_results = self.analyze_with_active_inference()

        # Get FPF analyzer results
        fpf_analysis = self.fpf_analyzer.get_analysis_summary()
        critical_patterns = self.fpf_analyzer.get_critical_patterns(top_n=20)
        isolated_patterns = self.fpf_analyzer.get_isolated_patterns()
        part_cohesion = self.fpf_analyzer.analyze_part_cohesion()

        # Get term analysis
        shared_terms = self.term_analyzer.get_shared_terms(self.spec, min_occurrences=3)
        important_terms = self.term_analyzer.get_important_terms(self.spec, top_n=30)

        # Combine results
        comprehensive = {
            "fpf_statistics": {
                "total_patterns": len(self.spec.patterns),
                "total_concepts": len(self.spec.concepts),
                "total_relationships": len(self.spec.relationships),
            },
            "case_based_reasoning": cbr_results,
            "bayesian_inference": bayesian_results,
            "active_inference": active_inference_results,
            "fpf_analysis": {
                "pattern_importance": fpf_analysis["pattern_importance"],
                "critical_patterns": critical_patterns,
                "isolated_patterns": isolated_patterns,
                "part_cohesion": part_cohesion,
            },
            "term_analysis": {
                "shared_terms": shared_terms[:20],  # Top 20
                "important_terms": important_terms,
            },
        }

        return comprehensive

    def generate_visualizations(self, analysis_results: Dict[str, Any]) -> None:
        """Generate all visualizations.

        Args:
            analysis_results: Comprehensive analysis results
        """
        self.logger.info("Generating visualizations")

        viz_dir = self.output_dir / "visualizations"
        viz_dir.mkdir(parents=True, exist_ok=True)

        # Visualize Bayesian network
        if self.cerebrum.bayesian_network:
            try:
                matplotlib.use('Agg')  # Use non-interactive backend
                visualizer = ModelVisualizer(figure_size=(14, 10), dpi=300)
                fig = visualizer.visualize_network(
                    self.cerebrum.bayesian_network,
                    layout="hierarchical",
                    node_size_metric="degree",
                    show_legend=True,
                )
                visualizer.save_figure(fig, str(viz_dir / "bayesian_network.png"))
                self.logger.info("Saved Bayesian network visualization")
                
                # Export raw data
                network_data = {
                    "network_name": self.cerebrum.bayesian_network.name,
                    "nodes": list(self.cerebrum.bayesian_network.nodes),
                    "edges": [
                        {"parent": parent, "child": child}
                        for parent, children in self.cerebrum.bayesian_network.edges.items()
                        for child in children
                    ]
                }
                json_path = viz_dir / "bayesian_network.json"
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(network_data, f, indent=2)
                self.logger.info(f"Exported Bayesian network raw data to {json_path}")
            except Exception as e:
                self.logger.warning(f"Failed to visualize network: {e}", exc_info=True)

        # Visualize case similarity
        try:
            # Get some example cases
            cases_with_similarity = []
            case_data_rows = []
            for pattern_id, cbr_data in list(analysis_results["case_based_reasoning"]["similarity_analysis"].items())[:10]:
                pattern = self.spec.get_pattern_by_id(pattern_id)
                if pattern:
                    query_case = Case(
                        case_id="query",
                        features={"status": pattern.status, "part": pattern.part or "Other"},
                    )
                    similar = self.cerebrum.case_base.retrieve_similar(query_case, k=5)
                    cases_with_similarity.extend(similar)
                    
                    # Collect data for export
                    for case, similarity in similar:
                        case_data_rows.append({
                            "case_id": case.case_id,
                            "similarity_score": similarity,
                            "pattern_id": pattern_id,
                            "status": pattern.status or "",
                            "part": pattern.part or "Other"
                        })

            if cases_with_similarity:
                case_viz = CaseVisualizer(figure_size=(12, 10), dpi=300)
                fig = case_viz.plot_case_similarity(
                    cases_with_similarity[:20],
                    show_threshold=True,
                    threshold=0.5,
                )
                case_viz.save_figure(fig, str(viz_dir / "case_similarity.png"))
                self.logger.info("Saved case similarity visualization")
                
                # Export raw data
                if case_data_rows:
                    csv_path = viz_dir / "case_similarity.csv"
                    with open(csv_path, "w", encoding="utf-8", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=["case_id", "similarity_score", "pattern_id", "status", "part"])
                        writer.writeheader()
                        writer.writerows(case_data_rows[:20])  # Match visualization limit
                    self.logger.info(f"Exported case similarity raw data to {csv_path}")
        except Exception as e:
            self.logger.warning(f"Failed to visualize case similarity: {e}", exc_info=True)

        # Visualize inference results
        try:
            if analysis_results["bayesian_inference"]["inference_results"]:
                inference_viz = InferenceVisualizer()
                # Convert to distribution format
                inference_data = {}
                inference_rows = []
                for pattern_id, result in list(analysis_results["bayesian_inference"]["inference_results"].items())[:5]:
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
                        
                        # Collect data for export
                        inference_rows.append({
                            "pattern_id": pattern_id,
                            "high_probability": result["importance_distribution"]["high"],
                            "medium_probability": result["importance_distribution"]["medium"],
                            "low_probability": result["importance_distribution"]["low"],
                            "most_likely": result.get("most_likely", "")
                        })

                if inference_data:
                    inference_viz = InferenceVisualizer(figure_size=(12, 8), dpi=300)
                    fig = inference_viz.plot_inference_results(inference_data)
                    inference_viz.save_figure(fig, str(viz_dir / "inference_results.png"))
                    self.logger.info("Saved inference results visualization")
                    
                    # Export raw data
                    if inference_rows:
                        csv_path = viz_dir / "inference_results.csv"
                        with open(csv_path, "w", encoding="utf-8", newline="") as f:
                            writer = csv.DictWriter(f, fieldnames=["pattern_id", "high_probability", "medium_probability", "low_probability", "most_likely"])
                            writer.writeheader()
                            writer.writerows(inference_rows)
                        self.logger.info(f"Exported inference results raw data to {csv_path}")
        except Exception as e:
            self.logger.warning(f"Failed to visualize inference results: {e}", exc_info=True)

        # Generate concordance visualizations
        self._generate_concordance_visualizations(analysis_results, viz_dir)

        # Generate composition visualizations
        self._generate_composition_visualizations(analysis_results, viz_dir)

    def _generate_concordance_visualizations(
        self, analysis_results: Dict[str, Any], viz_dir: Path
    ) -> None:
        """Generate concordance visualizations comparing different analyses.

        Args:
            analysis_results: Comprehensive analysis results
            viz_dir: Visualization directory
        """
        try:
            matplotlib.use('Agg')

            concordance_viz = ConcordanceVisualizer(figure_size=(14, 10), dpi=300)

            # Extract results for concordance analysis
            cbr_results = {}
            bayesian_results = {}
            pattern_ids = []

            # Get CBR results
            if "case_based_reasoning" in analysis_results:
                cbr_data = analysis_results["case_based_reasoning"].get("similarity_analysis", {})
                for pattern_id, data in cbr_data.items():
                    if isinstance(data, dict) and "average_similarity" in data:
                        cbr_results[pattern_id] = data["average_similarity"]
                        pattern_ids.append(pattern_id)

            # Get Bayesian results
            if "bayesian_inference" in analysis_results:
                bayesian_data = analysis_results["bayesian_inference"].get("inference_results", {})
                for pattern_id, data in bayesian_data.items():
                    if isinstance(data, dict) and "most_likely" in data:
                        # Convert importance to score
                        importance_dist = data.get("importance_distribution", {})
                        score = importance_dist.get("high", 0.0) * 1.0 + importance_dist.get("medium", 0.0) * 0.5
                        bayesian_results[pattern_id] = score
                        if pattern_id not in pattern_ids:
                            pattern_ids.append(pattern_id)

            if cbr_results and bayesian_results:
                # Analysis concordance matrix
                fig = concordance_viz.plot_analysis_concordance_matrix(
                    cbr_results, bayesian_results, pattern_ids=pattern_ids[:20]
                )
                concordance_viz.theme.apply_to_axes(fig.axes[0])
                fig.savefig(viz_dir / "analysis_concordance_matrix.png", dpi=300, bbox_inches="tight")
                plt.close(fig)
                self.logger.info("Saved analysis concordance matrix")

        except Exception as e:
            self.logger.warning(f"Failed to generate concordance visualizations: {e}", exc_info=True)

    def _generate_composition_visualizations(
        self, analysis_results: Dict[str, Any], viz_dir: Path
    ) -> None:
        """Generate composition visualizations (dashboards, summaries).

        Args:
            analysis_results: Comprehensive analysis results
            viz_dir: Visualization directory
        """
        try:
            matplotlib.use('Agg')

            composition_viz = CompositionVisualizer(figure_size=(20, 14), dpi=300)

            # Build analysis summary
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

            # Extract summary data from results
            if "case_based_reasoning" in analysis_results:
                cbr_data = analysis_results["case_based_reasoning"]
                analysis_summary["method_summary"]["CBR"] = len(cbr_data.get("similarity_analysis", {}))

            if "bayesian_inference" in analysis_results:
                bayesian_data = analysis_results["bayesian_inference"]
                analysis_summary["method_summary"]["Bayesian"] = len(bayesian_data.get("inference_results", {}))

            if self.cerebrum.bayesian_network:
                analysis_summary["network_summary"]["nodes"] = len(self.cerebrum.bayesian_network.nodes)
                analysis_summary["network_summary"]["edges"] = sum(
                    len(children) for children in self.cerebrum.bayesian_network.edges.values()
                )

            # Create dashboard
            composition_viz.create_analysis_overview_dashboard(
                analysis_summary, output_path=viz_dir / "analysis_overview.png"
            )
            self.logger.info("Saved analysis overview dashboard")

        except Exception as e:
            self.logger.warning(f"Failed to generate composition visualizations: {e}", exc_info=True)

    def export_results(self, analysis_results: Dict[str, Any]) -> None:
        """Export all results to JSON and markdown.

        Args:
            analysis_results: Comprehensive analysis results
        """
        self.logger.info("Exporting results")

        # Export JSON
        json_path = self.output_dir / "comprehensive_analysis.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(analysis_results, f, indent=2, default=str)
        self.logger.info(f"Exported JSON to {json_path}")

        # Export markdown report
        md_path = self.output_dir / "comprehensive_analysis.md"
        self._generate_markdown_report(analysis_results, md_path)
        self.logger.info(f"Exported markdown report to {md_path}")

    def _generate_markdown_report(self, results: Dict[str, Any], output_path: Path) -> None:
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

        # Add similarity results
        for pattern_id, data in list(results["case_based_reasoning"]["similarity_analysis"].items())[:10]:
            lines.append(f"### Pattern {pattern_id}")
            lines.append(f"- **Predicted Importance**: {data.get('prediction', 'N/A'):.3f}")
            lines.append(f"- **Confidence**: {data.get('confidence', 0):.3f}")
            lines.append(f"- **Similar Patterns Found**: {data.get('retrieved_count', 0)}")
            lines.append("")

        lines.extend([
            "## Bayesian Inference Analysis",
            "",
            f"- **Network Nodes**: {results['bayesian_inference']['network_nodes']}",
            f"- **Network Edges**: {results['bayesian_inference']['network_edges']}",
            "",
            "### Inference Results",
            "",
        ])

        # Add inference results
        for pattern_id, data in list(results["bayesian_inference"]["inference_results"].items())[:10]:
            if "importance_distribution" in data:
                lines.append(f"### Pattern {pattern_id}")
                dist = data["importance_distribution"]
                lines.append(f"- **High Importance**: {dist.get('high', 0):.3f}")
                lines.append(f"- **Medium Importance**: {dist.get('medium', 0):.3f}")
                lines.append(f"- **Low Importance**: {dist.get('low', 0):.3f}")
                lines.append(f"- **Most Likely**: {data.get('most_likely', 'N/A')}")
                lines.append("")

        lines.extend([
            "## Active Inference Exploration",
            "",
            "### Exploration Path",
            "",
        ])

        # Add exploration path
        for step in results["active_inference"]["exploration_path"][:10]:
            lines.append(f"- **{step['pattern_id']}**: {step['action']} (Free Energy: {step['free_energy']:.3f})")
        lines.append("")

        lines.extend([
            "## FPF Analysis",
            "",
            "### Critical Patterns",
            "",
        ])

        # Add critical patterns
        for pattern_id, score in results["fpf_analysis"]["critical_patterns"][:10]:
            lines.append(f"- **{pattern_id}**: {score:.3f}")
        lines.append("")

        lines.extend([
            "### Part Cohesion",
            "",
        ])

        # Add part cohesion
        for part, cohesion in results["fpf_analysis"]["part_cohesion"].items():
            lines.append(f"- **Part {part}**: {cohesion:.3f}")
        lines.append("")

        lines.extend([
            "## Term Analysis",
            "",
            "### Shared Terms",
            "",
        ])

        # Add shared terms
        for term, count, pattern_ids in results["term_analysis"]["shared_terms"][:15]:
            lines.append(f"- **{term}**: appears in {count} patterns ({', '.join(pattern_ids[:5])})")
        lines.append("")

        output_path.write_text("\n".join(lines), encoding="utf-8")

    def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run complete comprehensive analysis pipeline.

        Returns:
            Complete analysis results
        """
        self.logger.info("Starting comprehensive CEREBRUM-FPF analysis")

        # Generate comprehensive analysis
        results = self.generate_comprehensive_analysis()

        # Export results first (so we have them even if visualization fails)
        self.export_results(results)

        # Generate visualizations (with error handling to not crash the script)
        try:
            self.generate_visualizations(results)
        except Exception as e:
            self.logger.error(f"Visualization generation failed: {e}", exc_info=True)
            # Continue even if visualization fails

        self.logger.info(f"Analysis complete. Results saved to {self.output_dir}")
        return results


def main():
    """Main entry point for FPF-CEREBRUM orchestration."""

    parser = argparse.ArgumentParser(description="CEREBRUM orchestration for FPF analysis")
    parser.add_argument(
        "--fpf-spec",
        type=str,
        default=None,
        help="Path to FPF-Spec.md (default: fetch from GitHub)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output/fpf_cerebrum",
        help="Output directory for results",
    )

    args = parser.parse_args()

    # Create orchestrator
    orchestrator = FPFOrchestrator(
        fpf_spec_path=args.fpf_spec,
        output_dir=args.output_dir,
    )

    # Run comprehensive analysis
    results = orchestrator.run_comprehensive_analysis()

    print(f"\n✅ Analysis complete!")
    print(f"📊 Results saved to: {orchestrator.output_dir}")
    print(f"📈 Analyzed {results['fpf_statistics']['total_patterns']} patterns")
    print(f"🔍 Created {results['case_based_reasoning']['total_cases']} cases")
    print(f"🌐 Built Bayesian network with {results['bayesian_inference']['network_nodes']} nodes")


if __name__ == "__main__":
    main()

