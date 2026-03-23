import argparse
from pathlib import Path
from typing import Any

import matplotlib as mpl

from codomyrmex.cerebrum import (
    ActiveInferenceAgent,
    BayesianNetwork,
    Case,
    CerebrumConfig,
    CerebrumEngine,
    InferenceEngine,
)
from codomyrmex.fpf import FPFAnalyzer, FPFClient, TermAnalyzer
from codomyrmex.logging_monitoring import get_logger, setup_logging

from ._reports import FPFReportMixin
from ._visualizations import FPFVisualizationMixin

"""CEREBRUM orchestration for FPF analysis.

This script demonstrates comprehensive application of CEREBRUM methods
(case-based reasoning, Bayesian inference, active inference) to analyze
and reason about the First Principles Framework specification.
"""

try:
    mpl.use("Agg")  # Use non-interactive backend
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

logger = get_logger(__name__)


class FPFOrchestrator(FPFVisualizationMixin, FPFReportMixin):
    """Orchestrates CEREBRUM methods for comprehensive FPF analysis.

    Visualization and report generation are delegated to focused mixin classes
    for improved maintainability.
    """

    def __init__(
        self,
        fpf_spec_path: str | None = None,
        output_dir: str = "output/cerebrum/orchestration",
    ):
        """Initialize FPF orchestrator.

        Args:
            fpf_spec_path: Path to FPF-Spec.md (if None, will fetch from GitHub)
            output_dir: Directory for output files (default: output/cerebrum/orchestration)
        """
        setup_logging()
        self.logger = get_logger(__name__)

        self.fpf_client = FPFClient()
        if fpf_spec_path:
            self.spec = self.fpf_client.load_from_file(fpf_spec_path)
        else:
            self.spec = self.fpf_client.fetch_and_load()

        config = CerebrumConfig(
            case_similarity_threshold=0.6,
            max_retrieved_cases=20,
            inference_method="variable_elimination",
            adaptation_rate=0.1,
        )
        self.cerebrum = CerebrumEngine(config)

        self.fpf_analyzer = FPFAnalyzer(self.spec)
        self.term_analyzer = TermAnalyzer()

        # Output directory
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info(
            "Initialized FPF Orchestrator with %s patterns", len(self.spec.patterns)
        )

    def create_pattern_cases(self) -> list[Case]:
        """Create cases from FPF patterns for case-based reasoning.

        Returns:
            list of Case objects
        """
        cases = []
        for pattern in self.spec.patterns:
            # Extract features from pattern
            features = {
                "status": pattern.status,
                "part": pattern.part or "Other",
                "num_keywords": len(pattern.keywords),
                "num_dependencies": sum(
                    len(deps) for deps in pattern.dependencies.values()
                ),
                "has_builds_on": len(pattern.dependencies.get("builds_on", [])) > 0,
                "has_prerequisite": len(
                    pattern.dependencies.get("prerequisite_for", [])
                )
                > 0,
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

        self.logger.info("Created %s cases from FPF patterns", len(cases))
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
            node_name = (
                f"concept_{concept.lower().replace('.', '_').replace(' ', '_')[:20]}"
            )
            network.add_node(node_name, values=["high", "medium", "low"])

        # Add relationship nodes
        network.add_node("has_dependencies", values=["yes", "no"])
        network.add_node("pattern_importance", values=["high", "medium", "low"])

        # Add edges
        network.add_edge("pattern_status", "pattern_importance")
        network.add_edge("has_dependencies", "pattern_importance")

        # set conditional probability tables
        # Pattern importance given status
        network.set_cpt(
            "pattern_importance",
            {
                ("Stable", "yes"): {"high": 0.7, "medium": 0.2, "low": 0.1},
                ("Stable", "no"): {"high": 0.3, "medium": 0.4, "low": 0.3},
                ("Draft", "yes"): {"high": 0.4, "medium": 0.4, "low": 0.2},
                ("Draft", "no"): {"high": 0.2, "medium": 0.3, "low": 0.5},
                ("Stub", "yes"): {"high": 0.2, "medium": 0.3, "low": 0.5},
                ("Stub", "no"): {"high": 0.1, "medium": 0.2, "low": 0.7},
                ("New", "yes"): {"high": 0.3, "medium": 0.4, "low": 0.3},
                ("New", "no"): {"high": 0.1, "medium": 0.3, "low": 0.6},
            },
        )

        self.logger.info("Built Bayesian network with %s nodes", len(network.nodes))
        return network

    def analyze_with_case_based_reasoning(self) -> dict[str, Any]:
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
            normalized_importance = (
                min(1.0, importance * 2.0) if importance > 0 else 0.0
            )
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
                    "num_dependencies": sum(
                        len(deps) for deps in pattern.dependencies.values()
                    ),
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

        self.logger.info(
            "Completed case-based reasoning for %s patterns", len(similarity_analysis)
        )
        return {
            "similarity_analysis": similarity_analysis,
            "total_cases": len(cases),
            "case_base_size": self.cerebrum.case_base.size(),
        }

    def analyze_with_bayesian_inference(self) -> dict[str, Any]:
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
                "has_dependencies": "yes"
                if any(pattern.dependencies.values())
                else "no",
            }

            # Query pattern importance
            inference = InferenceEngine(network, method="variable_elimination")
            try:
                result = inference.compute_marginal("pattern_importance", evidence)
                inference_results[pattern.id] = {
                    "importance_distribution": {
                        "high": result.probabilities[result.values.index("high")]
                        if "high" in result.values
                        else 0.0,
                        "medium": result.probabilities[result.values.index("medium")]
                        if "medium" in result.values
                        else 0.0,
                        "low": result.probabilities[result.values.index("low")]
                        if "low" in result.values
                        else 0.0,
                    },
                    "most_likely": result.mode(),
                    "evidence": evidence,
                }
            except Exception as e:
                self.logger.warning("Inference failed for %s: %s", pattern.id, e)
                inference_results[pattern.id] = {"error": str(e)}

        self.logger.info(
            "Completed Bayesian inference for %s patterns", len(inference_results)
        )
        return {
            "inference_results": inference_results,
            "network_nodes": len(network.nodes),
            "network_edges": sum(len(edges) for edges in network.edges.values()),
        }

    def analyze_with_active_inference(self) -> dict[str, Any]:
        """Analyze FPF using active inference.

        Returns:
            Dictionary with active inference results
        """
        self.logger.info("Starting active inference analysis")

        # Define states (pattern exploration states)
        states = ["unexplored", "exploring", "analyzed", "completed"]

        # Define observations (what we can observe about patterns)
        observations = [
            "high_importance",
            "medium_importance",
            "low_importance",
            "unknown",
        ]

        # Define actions (exploration actions)
        actions = [
            "analyze_pattern",
            "explore_dependencies",
            "analyze_concepts",
            "skip",
        ]

        # Create active inference agent
        agent = ActiveInferenceAgent(
            states=states,
            observations=observations,
            actions=actions,
            precision=1.0,
            policy_horizon=3,
        )

        # set transition model
        transition_model = {
            "unexplored_analyze_pattern": {"exploring": 0.8, "analyzed": 0.2},
            "exploring_analyze_pattern": {"analyzed": 0.9, "exploring": 0.1},
            "analyzed_explore_dependencies": {"exploring": 0.6, "completed": 0.4},
            "analyzed_analyze_concepts": {"completed": 0.7, "analyzed": 0.3},
        }
        agent.set_transition_model(transition_model)

        # set observation model
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

            exploration_path.append(
                {
                    "pattern_id": pattern.id,
                    "action": action,
                    "free_energy": free_energy,
                    "importance": importance,
                }
            )

        self.cerebrum.set_active_inference_agent(agent)

        self.logger.info(
            "Completed active inference exploration for %s patterns",
            len(exploration_path),
        )
        return {
            "exploration_path": exploration_path,
            "final_beliefs": agent.get_beliefs().to_dict(),
        }

    def generate_comprehensive_analysis(self) -> dict[str, Any]:
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

    # Visualization and report methods are provided by
    # FPFVisualizationMixin and FPFReportMixin via multiple inheritance.

    def run_comprehensive_analysis(self) -> dict[str, Any]:
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
            self.logger.error("Visualization generation failed: %s", e, exc_info=True)
            # Continue even if visualization fails

        self.logger.info("Analysis complete. Results saved to %s", self.output_dir)
        return results


def main():
    """Main entry point for FPF-CEREBRUM orchestration."""

    parser = argparse.ArgumentParser(
        description="CEREBRUM orchestration for FPF analysis"
    )
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

    print("\n✅ Analysis complete!")
    print(f"📊 Results saved to: {orchestrator.output_dir}")
    print(f"📈 Analyzed {results['fpf_statistics']['total_patterns']} patterns")
    print(f"🔍 Created {results['case_based_reasoning']['total_cases']} cases")
    print(
        f"🌐 Built Bayesian network with {results['bayesian_inference']['network_nodes']} nodes"
    )


if __name__ == "__main__":
    main()
