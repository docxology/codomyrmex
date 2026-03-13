"""Evaluation mixin for Ollama Model Runner.

Extracted from model_runner.py.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .model_runner import ExecutionOptions


class OllamaEvaluationMixin:
    """Mixin for evaluating and benchmarking models."""

    # Note: Requires self.ollama_manager, self.logger, and self.run_with_options

    def benchmark_model(
        self,
        model_name: str,
        test_prompts: list[str],
        options: ExecutionOptions | None = None,
    ) -> dict[str, Any]:
        """Benchmark a model with multiple test prompts."""
        self.logger.info(
            "Benchmarking model %s with %s prompts", model_name, len(test_prompts)
        )

        results = []
        total_start_time = time.time()

        for i, prompt in enumerate(test_prompts):
            self.logger.info("Running benchmark prompt %s/%s", i + 1, len(test_prompts))

            result = self.run_with_options(model_name, prompt, options)

            benchmark_data = {
                "prompt_index": i,
                "prompt_length": len(prompt),
                "execution_time": result.execution_time,
                "success": result.success,
                "response_length": len(result.response) if result.success else 0,
                "tokens_per_second": len(result.response) / result.execution_time
                if result.success and result.execution_time > 0
                else 0,
            }

            results.append(benchmark_data)

        total_time = time.time() - total_start_time

        # Calculate statistics
        successful_runs = [r for r in results if r["success"]]
        failed_runs = [r for r in results if not r["success"]]

        benchmark_summary = {
            "model_name": model_name,
            "total_prompts": len(test_prompts),
            "successful_runs": len(successful_runs),
            "failed_runs": len(failed_runs),
            "total_time": total_time,
            "avg_execution_time": sum(r["execution_time"] for r in successful_runs)
            / len(successful_runs)
            if successful_runs
            else 0,
            "avg_tokens_per_second": sum(
                r["tokens_per_second"] for r in successful_runs
            )
            / len(successful_runs)
            if successful_runs
            else 0,
            "detailed_results": results,
        }

        self.logger.info(
            "Benchmark completed: %s/%s successful",
            len(successful_runs),
            len(test_prompts),
        )
        return benchmark_summary

    def create_model_comparison(
        self,
        model_names: list[str],
        test_prompt: str,
        options: ExecutionOptions | None = None,
    ) -> dict[str, Any]:
        """Compare multiple models on the same prompt."""
        self.logger.info("Comparing %s models on the same prompt", len(model_names))

        comparison_results = {}

        for model_name in model_names:
            if not self.ollama_manager.is_model_available(model_name):
                self.logger.warning("Model %s not available, skipping", model_name)
                continue

            result = self.run_with_options(model_name, test_prompt, options)

            comparison_results[model_name] = {
                "success": result.success,
                "execution_time": result.execution_time,
                "response_length": len(result.response) if result.success else 0,
                "tokens_per_second": len(result.response) / result.execution_time
                if result.success and result.execution_time > 0
                else 0,
                "response_preview": result.response[:200] + "..."
                if result.success and len(result.response) > 200
                else result.response,
                "error": result.error_message if not result.success else None,
            }

        return {
            "test_prompt": test_prompt,
            "models_compared": len(comparison_results),
            "results": comparison_results,
            "summary": self._create_comparison_summary(comparison_results),
        }

    def _create_comparison_summary(self, results: dict[str, dict]) -> dict[str, Any]:
        """Create summary statistics for model comparison."""
        successful_results = {
            name: data for name, data in results.items() if data["success"]
        }

        if not successful_results:
            return {"error": "No successful model executions"}

        execution_times = [
            data["execution_time"] for data in successful_results.values()
        ]
        tokens_per_sec = [
            data["tokens_per_second"] for data in successful_results.values()
        ]

        return {
            "fastest_model": min(
                successful_results.items(), key=lambda x: x[1]["execution_time"]
            )[0],
            "slowest_model": max(
                successful_results.items(), key=lambda x: x[1]["execution_time"]
            )[0],
            "most_efficient": max(
                successful_results.items(), key=lambda x: x[1]["tokens_per_second"]
            )[0],
            "avg_execution_time": sum(execution_times) / len(execution_times),
            "avg_tokens_per_second": sum(tokens_per_sec) / len(tokens_per_sec),
            "success_rate": len(successful_results) / len(results),
        }
