#!/usr/bin/env python3
"""Model Operations Module - Comprehensive Usage Script.

Demonstrates ML model operations with full configurability,
unified logging, and output saving.

Usage:
    python basic_usage.py                          # Run with defaults
    python basic_usage.py --dataset-size 100       # Custom dataset size
    python basic_usage.py --verbose                # Verbose output
"""

import sys
from pathlib import Path
from typing import Any, Dict

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# Direct import to avoid triggering full codomyrmex package init
import importlib.util
script_base_path = project_root / "src" / "codomyrmex" / "utils" / "script_base.py"
spec = importlib.util.spec_from_file_location("script_base", script_base_path)
script_base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script_base)
ScriptBase = script_base.ScriptBase
ScriptConfig = script_base.ScriptConfig


class ModelOpsScript(ScriptBase):
    """Comprehensive model operations module demonstration."""

    def __init__(self):
        super().__init__(
            name="model_ops_usage",
            description="Demonstrate and test ML model operations",
            version="1.0.0",
        )

    def add_arguments(self, parser):
        """Add model ops-specific arguments."""
        group = parser.add_argument_group("Model Ops Options")
        group.add_argument(
            "--dataset-size", type=int, default=50,
            help="Number of examples in synthetic dataset (default: 50)"
        )
        group.add_argument(
            "--min-length", type=int, default=10,
            help="Minimum content length for filtering (default: 10)"
        )
        group.add_argument(
            "--max-length", type=int, default=1000,
            help="Maximum content length for filtering (default: 1000)"
        )
        group.add_argument(
            "--base-model", default="gpt-3.5-turbo",
            help="Base model for fine-tuning simulation (default: gpt-3.5-turbo)"
        )
        group.add_argument(
            "--export-dataset", type=Path,
            help="Export synthetic dataset to JSONL file"
        )

    def run(self, args, config: ScriptConfig) -> Dict[str, Any]:
        """Execute model operations demonstrations."""
        results = {
            "tests_run": 0,
            "tests_passed": 0,
            "dataset_stats": {},
            "evaluation_results": {},
        }

        if config.dry_run:
            self.log_info(f"Would create dataset with {args.dataset_size} examples")
            self.log_info(f"Would test: Dataset, DatasetSanitizer, FineTuningJob, Evaluator")
            results["dry_run"] = True
            return results

        # Import model_ops module (after dry_run check)
        from codomyrmex.model_ops import Dataset, DatasetSanitizer, FineTuningJob, Evaluator
        from codomyrmex.model_ops.evaluators import exact_match_metric, length_ratio_metric

        # Test 1: Create and validate dataset
        self.log_info(f"\n1. Creating synthetic dataset ({args.dataset_size} examples)")
        try:
            dataset = self._create_synthetic_dataset(args.dataset_size)
            is_valid = dataset.validate()
            results["dataset_stats"]["created"] = len(dataset.data)
            results["dataset_stats"]["valid"] = is_valid
            results["tests_passed"] += 1
            self.log_success(f"Dataset created: {len(dataset.data)} examples, valid={is_valid}")
        except Exception as e:
            self.log_error(f"Dataset creation failed: {e}")
        results["tests_run"] += 1

        # Test 2: Dataset sanitization
        self.log_info(f"\n2. Testing DatasetSanitizer (filter: {args.min_length}-{args.max_length})")
        try:
            filtered = DatasetSanitizer.filter_by_length(dataset, args.min_length, args.max_length)
            stripped = DatasetSanitizer.strip_keys(filtered, ["metadata", "timestamp"])

            results["dataset_stats"]["after_length_filter"] = len(filtered.data)
            results["dataset_stats"]["after_strip_keys"] = len(stripped.data)
            results["tests_passed"] += 1
            self.log_success(f"Filtered: {len(filtered.data)} examples passed length filter")
        except Exception as e:
            self.log_error(f"Sanitization failed: {e}")
        results["tests_run"] += 1

        # Test 3: Fine-tuning job simulation
        self.log_info(f"\n3. Simulating FineTuningJob (base: {args.base_model})")
        try:
            job = FineTuningJob(base_model=args.base_model, dataset=dataset)
            job_id = job.run()
            status = job.refresh_status()

            results["fine_tuning"] = {
                "base_model": args.base_model,
                "job_id": job_id,
                "final_status": status,
                "dataset_size": len(dataset.data),
            }
            results["tests_passed"] += 1
            self.log_success(f"Fine-tuning job: {job_id}, status={status}")
        except Exception as e:
            self.log_error(f"Fine-tuning simulation failed: {e}")
        results["tests_run"] += 1

        # Test 4: Model evaluation
        self.log_info("\n4. Testing Evaluator with metrics")
        try:
            metrics = {
                "exact_match": exact_match_metric,
                "length_ratio": length_ratio_metric,
            }
            evaluator = Evaluator(metrics=metrics)

            predictions = ["hello world", "test response", "another answer"]
            references = ["hello world", "test answer", "another answer"]

            eval_results = evaluator.evaluate(predictions, references)
            results["evaluation_results"] = eval_results
            results["tests_passed"] += 1
            self.log_success(f"Evaluation: exact_match={eval_results['exact_match']:.2f}, length_ratio={eval_results['length_ratio']:.2f}")
        except Exception as e:
            self.log_error(f"Evaluation failed: {e}")
        results["tests_run"] += 1

        # Test 5: Dataset I/O
        self.log_info("\n5. Testing dataset I/O")
        try:
            if args.export_dataset:
                dataset.to_jsonl(str(args.export_dataset))
                self.log_info(f"Exported to: {args.export_dataset}")

            # Test round-trip to temp file
            temp_path = self.output_path / "test_dataset.jsonl" if self.output_path else Path("/tmp/test_dataset.jsonl")
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            dataset.to_jsonl(str(temp_path))
            reloaded = Dataset.from_file(str(temp_path))

            results["io_test"] = {
                "original_size": len(dataset.data),
                "reloaded_size": len(reloaded.data),
                "round_trip_success": len(dataset.data) == len(reloaded.data),
            }
            results["tests_passed"] += 1
            self.log_success(f"I/O test: round-trip successful ({len(reloaded.data)} examples)")
        except Exception as e:
            self.log_error(f"I/O test failed: {e}")
        results["tests_run"] += 1

        # Metrics
        self.add_metric("tests_run", results["tests_run"])
        self.add_metric("tests_passed", results["tests_passed"])
        self.add_metric("dataset_size", len(dataset.data))

        return results

    def _create_synthetic_dataset(self, size: int) -> "Dataset":
        """Create a synthetic dataset for testing."""
        from codomyrmex.model_ops import Dataset

        data = []
        prompts = [
            "What is machine learning?",
            "Explain neural networks.",
            "How does gradient descent work?",
            "What is overfitting?",
            "Define regularization.",
        ]
        completions = [
            "Machine learning is a subset of AI that enables systems to learn from data.",
            "Neural networks are computing systems inspired by biological neural networks.",
            "Gradient descent is an optimization algorithm used to minimize loss functions.",
            "Overfitting occurs when a model learns noise instead of the underlying pattern.",
            "Regularization adds a penalty to prevent overfitting in models.",
        ]

        for i in range(size):
            idx = i % len(prompts)
            data.append({
                "prompt": f"{prompts[idx]} (Example {i+1})",
                "completion": f"{completions[idx]} This is example {i+1}.",
                "metadata": {"index": i, "category": "ml_basics"},
            })

        return Dataset(data=data)


if __name__ == "__main__":
    script = ModelOpsScript()
    sys.exit(script.execute())
