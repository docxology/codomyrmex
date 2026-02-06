"""
Output Manager - Handles saving and managing Ollama outputs

Manages all aspects of saving model outputs, configurations, and results
with integration into the Codomyrmex ecosystem.
"""

import hashlib
import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger

from .ollama_manager import ModelExecutionResult


class OutputManager:
    """
    Manages all output saving and configuration management for Ollama integration.

    Handles saving model outputs, execution results, configurations, and
    provides integration with Codomyrmex data visualization and logging.
    """

    def __init__(self, base_output_dir: str | None = None):
        """
        Initialize the output manager.

        Args:
            base_output_dir: Base directory for all outputs (default: codomyrmex/output/ollama/)
        """
        self.logger = get_logger(__name__)

        if base_output_dir:
            self.base_output_dir = Path(base_output_dir)
        else:
            # Default to Codomyrmex output directory
            self.base_output_dir = Path("examples/output/ollama")

        # Output organization
        self.outputs_dir = self.base_output_dir / "outputs"
        self.configs_dir = self.base_output_dir / "configs"
        self.logs_dir = self.base_output_dir / "logs"
        self.reports_dir = self.base_output_dir / "reports"

        # Create directory structure
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [
            self.base_output_dir,
            self.outputs_dir,
            self.configs_dir,
            self.logs_dir,
            self.reports_dir
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def save_model_output(
        self,
        model_name: str,
        prompt: str,
        response: str,
        execution_time: float,
        output_dir: str | None = None,
        metadata: dict[str, Any] | None = None
    ) -> str:
        """
        Save model execution output to files.

        Args:
            model_name: Name of the model used
            prompt: Input prompt
            response: Model response
            execution_time: Execution time in seconds
            output_dir: Custom output directory (optional)
            metadata: Additional metadata

        Returns:
            Path to the saved output file
        """
        # Generate unique filename based on content
        timestamp = int(time.time())
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
        filename = f"{model_name}_{timestamp}_{prompt_hash}"

        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = self.outputs_dir / model_name
            output_path.mkdir(exist_ok=True)

        # Save main output file
        output_file = output_path / f"{filename}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"MODEL: {model_name}\n")
            f.write(f"TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"EXECUTION TIME: {execution_time:.2f} seconds\n")
            f.write("=" * 80 + "\n\n")

            f.write("PROMPT:\n")
            f.write("-" * 40 + "\n")
            f.write(prompt)
            f.write("\n\n")

            f.write("RESPONSE:\n")
            f.write("-" * 40 + "\n")
            f.write(response)
            f.write("\n")

        # Save metadata if provided
        if metadata:
            metadata_file = output_path / f"{filename}_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, default=str)

        self.logger.info(f"Saved model output to: {output_file}")
        return str(output_file)

    def save_execution_result(
        self,
        result: ModelExecutionResult,
        output_dir: str | None = None
    ) -> str:
        """
        Save complete execution result as JSON.

        Args:
            result: ModelExecutionResult to save
            output_dir: Custom output directory (optional)

        Returns:
            Path to the saved result file
        """
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = self.outputs_dir / "results"
            output_path.mkdir(exist_ok=True)

        # Generate filename
        timestamp = int(time.time())
        filename = f"result_{result.model_name}_{timestamp}.json"

        result_file = output_path / filename

        # Convert result to dictionary
        result_dict = asdict(result)
        result_dict['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')

        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result_dict, f, indent=2, default=str)

        self.logger.info(f"Saved execution result to: {result_file}")
        return str(result_file)

    def save_model_config(
        self,
        model_name: str,
        config: dict[str, Any],
        config_name: str | None = None
    ) -> str:
        """
        Save model configuration.

        Args:
            model_name: Name of the model
            config: Configuration dictionary
            config_name: Optional name for the configuration

        Returns:
            Path to the saved configuration file
        """
        config_path = self.configs_dir / model_name
        config_path.mkdir(exist_ok=True)

        if config_name:
            filename = f"{config_name}.json"
        else:
            timestamp = int(time.time())
            filename = f"config_{timestamp}.json"

        config_file = config_path / filename

        # Add metadata
        config_with_metadata = {
            'model_name': model_name,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'config_name': config_name,
            'configuration': config
        }

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_with_metadata, f, indent=2, default=str)

        self.logger.info(f"Saved model config to: {config_file}")
        return str(config_file)

    def load_model_config(
        self,
        model_name: str,
        config_name: str | None = None
    ) -> dict[str, Any] | None:
        """
        Load model configuration.

        Args:
            model_name: Name of the model
            config_name: Optional name of the configuration

        Returns:
            Configuration dictionary or None if not found
        """
        config_path = self.configs_dir / model_name

        if config_name:
            config_file = config_path / f"{config_name}.json"
        else:
            # Find the most recent config file
            config_files = list(config_path.glob("config_*.json"))
            if not config_files:
                return None
            config_file = max(config_files, key=lambda f: f.stat().st_mtime)

        try:
            with open(config_file, encoding='utf-8') as f:
                config_data = json.load(f)

            self.logger.info(f"Loaded model config from: {config_file}")
            return config_data.get('configuration', config_data)

        except Exception as e:
            self.logger.error(f"Error loading config {config_file}: {e}")
            return None

    def save_batch_results(
        self,
        results: list[ModelExecutionResult],
        batch_name: str,
        output_dir: str | None = None
    ) -> str:
        """
        Save batch execution results.

        Args:
            results: List of execution results
            batch_name: Name for the batch
            output_dir: Custom output directory (optional)

        Returns:
            Path to the saved batch results file
        """
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = self.outputs_dir / "batches"
            output_path.mkdir(exist_ok=True)

        timestamp = int(time.time())
        filename = f"batch_{batch_name}_{timestamp}.json"
        batch_file = output_path / filename

        # Prepare batch data
        batch_data = {
            'batch_name': batch_name,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_executions': len(results),
            'successful_executions': sum(1 for r in results if r.success),
            'failed_executions': sum(1 for r in results if not r.success),
            'total_execution_time': sum(r.execution_time for r in results),
            'results': [asdict(result) for result in results]
        }

        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(batch_data, f, indent=2, default=str)

        self.logger.info(f"Saved batch results to: {batch_file}")
        return str(batch_file)

    def save_benchmark_report(
        self,
        benchmark_results: dict[str, Any],
        model_name: str,
        output_dir: str | None = None
    ) -> str:
        """
        Save benchmark results as a comprehensive report.

        Args:
            benchmark_results: Benchmark results dictionary
            model_name: Name of the benchmarked model
            output_dir: Custom output directory (optional)

        Returns:
            Path to the saved benchmark report
        """
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = self.reports_dir / "benchmarks"
            output_path.mkdir(exist_ok=True)

        timestamp = int(time.time())
        filename = f"benchmark_{model_name}_{timestamp}.json"
        report_file = output_path / filename

        # Add metadata to benchmark results
        benchmark_results['report_metadata'] = {
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'model_name': model_name,
            'report_type': 'benchmark'
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(benchmark_results, f, indent=2, default=str)

        self.logger.info(f"Saved benchmark report to: {report_file}")
        return str(report_file)

    def save_model_comparison(
        self,
        comparison_results: dict[str, Any],
        output_dir: str | None = None
    ) -> str:
        """
        Save model comparison results.

        Args:
            comparison_results: Comparison results dictionary
            output_dir: Custom output directory (optional)

        Returns:
            Path to the saved comparison report
        """
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = self.reports_dir / "comparisons"
            output_path.mkdir(exist_ok=True)

        timestamp = int(time.time())
        filename = f"comparison_{timestamp}.json"
        comparison_file = output_path / filename

        # Add metadata
        comparison_results['report_metadata'] = {
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'report_type': 'model_comparison'
        }

        with open(comparison_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_results, f, indent=2, default=str)

        self.logger.info(f"Saved model comparison to: {comparison_file}")
        return str(comparison_file)

    def list_saved_outputs(
        self,
        model_name: str | None = None,
        output_type: str = "outputs"
    ) -> list[dict[str, Any]]:
        """
        List saved outputs of a specific type.

        Args:
            model_name: Filter by model name (optional)
            output_type: Type of outputs to list ("outputs", "configs", "results", "reports")

        Returns:
            List of output information dictionaries
        """
        if output_type == "outputs":
            search_dir = self.outputs_dir
        elif output_type == "configs":
            search_dir = self.configs_dir
        elif output_type == "results":
            search_dir = self.outputs_dir / "results"
        elif output_type == "reports":
            search_dir = self.reports_dir
        else:
            return []

        outputs = []

        if search_dir.exists():
            for item in search_dir.iterdir():
                if item.is_file() and item.suffix == '.json':
                    try:
                        with open(item, encoding='utf-8') as f:
                            data = json.load(f)

                        output_info = {
                            'file_path': str(item),
                            'filename': item.name,
                            'created_at': item.stat().st_mtime,
                            'size': item.stat().st_size,
                            'data': data
                        }

                        # Filter by model if specified
                        if model_name:
                            if output_type == "outputs" and "model_name" in data:
                                if data.get("model_name") != model_name:
                                    continue
                            elif output_type == "configs" and "model_name" in data:
                                if data.get("model_name") != model_name:
                                    continue

                        outputs.append(output_info)

                    except Exception as e:
                        self.logger.warning(f"Error reading {item}: {e}")

        # Sort by creation time (newest first)
        outputs.sort(key=lambda x: x['created_at'], reverse=True)

        return outputs

    def get_output_stats(self) -> dict[str, Any]:
        """Get statistics about saved outputs."""
        stats = {
            'total_outputs': 0,
            'total_size': 0,
            'by_type': {},
            'by_model': {},
            'oldest_output': None,
            'newest_output': None
        }

        all_outputs = []

        # Collect all outputs
        for output_type in ["outputs", "configs", "results", "reports"]:
            outputs = self.list_saved_outputs(output_type=output_type)
            all_outputs.extend(outputs)
            stats['by_type'][output_type] = len(outputs)

        if not all_outputs:
            return stats

        # Calculate totals
        stats['total_outputs'] = len(all_outputs)
        stats['total_size'] = sum(output['size'] for output in all_outputs)

        # Find oldest and newest
        sorted_outputs = sorted(all_outputs, key=lambda x: x['created_at'])
        stats['oldest_output'] = sorted_outputs[0]['filename']
        stats['newest_output'] = sorted_outputs[-1]['filename']

        # Group by model
        for output in all_outputs:
            model_name = "unknown"
            if 'data' in output:
                data = output['data']
                if 'model_name' in data:
                    model_name = data['model_name']
                elif 'model' in data:
                    model_name = data['model']

            if model_name not in stats['by_model']:
                stats['by_model'][model_name] = 0
            stats['by_model'][model_name] += 1

        return stats

    def cleanup_old_outputs(self, days_old: int = 30) -> int:
        """
        Clean up outputs older than specified days.

        Args:
            days_old: Remove outputs older than this many days

        Returns:
            Number of files removed
        """
        cutoff_time = time.time() - (days_old * 24 * 60 * 60)
        removed_count = 0

        # Search all output directories
        search_dirs = [self.outputs_dir, self.configs_dir, self.logs_dir, self.reports_dir]

        for search_dir in search_dirs:
            if search_dir.exists():
                for item in search_dir.rglob('*'):
                    if item.is_file():
                        if item.stat().st_mtime < cutoff_time:
                            try:
                                item.unlink()
                                removed_count += 1
                                self.logger.info(f"Removed old output: {item}")
                            except Exception as e:
                                self.logger.warning(f"Could not remove {item}: {e}")

        self.logger.info(f"Cleaned up {removed_count} old output files")
        return removed_count
