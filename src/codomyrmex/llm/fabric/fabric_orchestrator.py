"""
Fabric Orchestrator - Workflow orchestration for Fabric + Codomyrmex

Provides high-level orchestration combining Fabric patterns with Codomyrmex capabilities.
"""

from typing import Any

from codomyrmex.logging_monitoring import get_logger

from .fabric_manager import FabricManager


class FabricOrchestrator:
    """
    Orchestrates workflows combining Fabric patterns with Codomyrmex capabilities.

    Provides high-level methods for common workflows like code analysis,
    content analysis, and visualization.
    """

    def __init__(self, fabric_binary: str = "fabric"):
        """
        Initialize the Fabric orchestrator.

        Args:
            fabric_binary: Path to fabric binary (default: "fabric")
        """
        self.fabric_manager = FabricManager(fabric_binary)
        self.logger = get_logger(__name__)

    def analyze_code(
        self,
        code_content: str,
        analysis_type: str = "comprehensive"
    ) -> dict[str, Any]:
        """
        Analyze code using appropriate Fabric patterns.

        Args:
            code_content: Code to analyze
            analysis_type: Type of analysis (comprehensive, security, quality, documentation, optimization)

        Returns:
            Dictionary with analysis results
        """
        analysis_patterns = {
            "comprehensive": ["analyze_code", "find_code_smells", "security_review"],
            "security": ["security_review", "find_vulnerabilities"],
            "quality": ["analyze_code", "find_code_smells"],
            "documentation": ["write_docstring", "explain_code"],
            "optimization": ["optimize_code", "improve_performance"]
        }

        patterns = analysis_patterns.get(analysis_type, ["analyze_code"])
        results = {}

        for pattern in patterns:
            self.logger.info(f"Running Fabric pattern: {pattern}")
            result = self.fabric_manager.run_pattern(pattern, code_content)
            results[pattern] = result

            if result["success"]:
                self.logger.info(f"Pattern '{pattern}' completed successfully")
            else:
                self.logger.error(f"Pattern '{pattern}' failed: {result.get('error', 'Unknown error')}")

        return {
            "analysis_type": analysis_type,
            "patterns_used": patterns,
            "results": results,
            "summary": self._create_analysis_summary(results)
        }

    def _create_analysis_summary(self, results: dict[str, dict]) -> dict[str, Any]:
        """Create summary of analysis results."""
        successful_patterns = sum(1 for r in results.values() if r["success"])
        total_patterns = len(results)

        return {
            "successful_patterns": successful_patterns,
            "total_patterns": total_patterns,
            "success_rate": (successful_patterns / total_patterns) * 100 if total_patterns > 0 else 0,
            "total_output_length": sum(len(r.get("output", "")) for r in results.values()),
            "average_duration": (
                sum(r.get("duration", 0) for r in results.values()) / len(results)
                if results else 0
            )
        }

    def create_workflow_visualization(
        self,
        output_path: str = "workflow_metrics.png"
    ) -> bool:
        """
        Create visualization of workflow results using Codomyrmex.

        Args:
            output_path: Path to save visualization

        Returns:
            True if successful
        """
        try:
            from codomyrmex.data_visualization import create_bar_chart
        except ImportError:
            self.logger.warning("Data visualization module not available")
            return False

        results_history = self.fabric_manager.get_results_history()
        if not results_history:
            return False

        try:
            # Extract metrics from results history
            pattern_stats = {}
            for result in results_history:
                pattern = result["pattern"]
                if pattern not in pattern_stats:
                    pattern_stats[pattern] = {"successes": 0, "total": 0, "durations": []}

                pattern_stats[pattern]["total"] += 1
                if result["success"]:
                    pattern_stats[pattern]["successes"] += 1
                if "duration" in result:
                    pattern_stats[pattern]["durations"].append(result["duration"])

            patterns = []
            success_rates = []

            for pattern, stats in pattern_stats.items():
                patterns.append(pattern)
                success_rates.append((stats["successes"] / stats["total"]) * 100)

            if patterns:
                create_bar_chart(
                    categories=patterns,
                    values=success_rates,
                    title="Fabric Pattern Success Rates",
                    x_label="Fabric Patterns",
                    y_label="Success Rate (%)",
                    output_path=output_path,
                    show_plot=False,
                    bar_color="lightgreen"
                )

                self.logger.info(f"Created workflow visualization: {output_path}")
                return True

        except Exception as e:
            self.logger.error(f"Failed to create visualization: {e}")
            return False

        return False

    def is_available(self) -> bool:
        """Check if Fabric is available."""
        return self.fabric_manager.is_available()

    def list_patterns(self) -> list[str]:
        """Get list of available Fabric patterns."""
        return self.fabric_manager.list_patterns()


