#!/usr/bin/env python3
"""Feature Flags Module - Comprehensive Usage Script.

Demonstrates feature flag management with full configurability,
unified logging, and output saving.

Usage:
    python basic_usage.py                          # Run with defaults
    python basic_usage.py --dry-run                # Preview without executing
    python basic_usage.py --verbose                # Verbose output
    python basic_usage.py --flags-file flags.json  # Load flags from file
"""

import sys
import json
import random
from pathlib import Path
from typing import Any, Dict, List

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


class FeatureFlagsScript(ScriptBase):
    """Comprehensive feature flags module demonstration."""

    def __init__(self):
        super().__init__(
            name="feature_flags_usage",
            description="Demonstrate and test feature flag management",
            version="1.0.0",
        )

    def add_arguments(self, parser):
        """Add feature flags-specific arguments."""
        group = parser.add_argument_group("Feature Flags Options")
        group.add_argument(
            "--flags-file", type=Path,
            help="JSON file containing flag definitions"
        )
        group.add_argument(
            "--test-users", type=int, default=100,
            help="Number of test users for rollout simulation (default: 100)"
        )
        group.add_argument(
            "--rollout-percentage", type=int, default=50,
            help="Percentage for rollout tests (default: 50)"
        )
        group.add_argument(
            "--export-results", type=Path,
            help="Export flag evaluation results to file"
        )

    def run(self, args, config: ScriptConfig) -> Dict[str, Any]:
        """Execute feature flags demonstrations."""
        results = {
            "tests_run": 0,
            "tests_passed": 0,
            "flag_evaluations": {},
            "rollout_analysis": {},
        }

        # Load flags from file or use defaults
        flag_config = self._load_flags(args.flags_file)
        self.log_info(f"Loaded {len(flag_config)} flag definitions")

        if config.dry_run:
            self.log_info(f"Would test flags: {list(flag_config.keys())}")
            results["dry_run"] = True
            return results

        # Import feature_flags module (after dry_run check)
        from codomyrmex.feature_flags import FeatureManager

        manager = FeatureManager(config=flag_config)

        # Test 1: Boolean flag evaluation
        self.log_info("\n1. Testing boolean flags")
        try:
            bool_results = self._test_boolean_flags(manager, flag_config)
            results["flag_evaluations"]["boolean"] = bool_results
            results["tests_passed"] += 1
            self.log_success(f"Boolean flags: {bool_results['enabled_count']}/{bool_results['total']} enabled")
        except Exception as e:
            self.log_error(f"Boolean flag test failed: {e}")
        results["tests_run"] += 1

        # Test 2: Percentage rollout
        self.log_info(f"\n2. Testing percentage rollout ({args.rollout_percentage}%)")
        try:
            rollout_results = self._test_percentage_rollout(
                manager, args.test_users, args.rollout_percentage
            )
            results["rollout_analysis"] = rollout_results
            results["tests_passed"] += 1
            self.log_success(f"Rollout: {rollout_results['enabled_percentage']:.1f}% enabled (target: {args.rollout_percentage}%)")
        except Exception as e:
            self.log_error(f"Rollout test failed: {e}")
        results["tests_run"] += 1

        # Test 3: Flag consistency
        self.log_info("\n3. Testing flag consistency across evaluations")
        try:
            consistency_results = self._test_consistency(manager)
            results["consistency"] = consistency_results
            results["tests_passed"] += 1
            self.log_success(f"Consistency: {consistency_results['consistent_percentage']:.1f}%")
        except Exception as e:
            self.log_error(f"Consistency test failed: {e}")
        results["tests_run"] += 1

        # Test 4: Default value handling
        self.log_info("\n4. Testing default value handling")
        try:
            default_results = self._test_defaults(manager)
            results["defaults"] = default_results
            results["tests_passed"] += 1
            self.log_success(f"Defaults: {default_results['tests_passed']}/{default_results['tests_run']} passed")
        except Exception as e:
            self.log_error(f"Default test failed: {e}")
        results["tests_run"] += 1

        # Add metrics
        self.add_metric("tests_run", results["tests_run"])
        self.add_metric("tests_passed", results["tests_passed"])
        self.add_metric("flags_tested", len(flag_config))

        # Export results if requested
        if args.export_results:
            self._export_results(args.export_results, results)

        return results

    def _load_flags(self, flags_file: Path = None) -> Dict[str, Any]:
        """Load flag definitions from file or return defaults."""
        if flags_file and flags_file.exists():
            with open(flags_file) as f:
                return json.load(f)

        return {
            "dark_mode": True,
            "new_dashboard": False,
            "ai_suggestions": True,
            "beta_editor": {"percentage": 50},
            "experimental_api": {"percentage": 10},
            "premium_features": False,
        }

    def _test_boolean_flags(self, manager, config: Dict) -> Dict[str, Any]:
        """Test boolean flag evaluation."""
        results = {"total": 0, "enabled_count": 0, "flags": {}}

        for flag, value in config.items():
            if isinstance(value, bool):
                is_enabled = manager.is_enabled(flag)
                results["flags"][flag] = is_enabled
                results["total"] += 1
                if is_enabled:
                    results["enabled_count"] += 1

        return results

    def _test_percentage_rollout(self, manager, num_users: int, target_percentage: int) -> Dict[str, Any]:
        """Test percentage-based rollout."""
        # Create a test flag with percentage
        manager.flags["test_rollout"] = {"percentage": target_percentage}

        enabled_count = 0
        user_results = {}

        for i in range(num_users):
            user_id = f"test_user_{i}"
            is_enabled = manager.is_enabled("test_rollout", user_id=user_id)
            user_results[user_id] = is_enabled
            if is_enabled:
                enabled_count += 1

        actual_percentage = (enabled_count / num_users) * 100

        return {
            "total_users": num_users,
            "target_percentage": target_percentage,
            "enabled_count": enabled_count,
            "enabled_percentage": actual_percentage,
            "within_tolerance": abs(actual_percentage - target_percentage) < 15,
        }

    def _test_consistency(self, manager) -> Dict[str, Any]:
        """Test that flag values are consistent for same user."""
        manager.flags["consistency_test"] = {"percentage": 50}

        consistent = 0
        total = 100

        for i in range(total):
            user_id = f"consistency_user_{i}"
            first_eval = manager.is_enabled("consistency_test", user_id=user_id)
            second_eval = manager.is_enabled("consistency_test", user_id=user_id)
            if first_eval == second_eval:
                consistent += 1

        return {
            "total_evaluations": total,
            "consistent": consistent,
            "consistent_percentage": (consistent / total) * 100,
        }

    def _test_defaults(self, manager) -> Dict[str, Any]:
        """Test default value handling."""
        tests = [
            ("nonexistent_flag", False, False),
            ("another_missing", True, True),
            ("missing_with_none", None, None),
        ]

        passed = 0
        results = []

        for flag, default, expected in tests:
            result = manager.is_enabled(flag, default=default)
            is_correct = result == expected
            if is_correct:
                passed += 1
            results.append({
                "flag": flag,
                "default": default,
                "result": result,
                "passed": is_correct,
            })

        return {
            "tests_run": len(tests),
            "tests_passed": passed,
            "details": results,
        }

    def _export_results(self, path: Path, results: Dict) -> None:
        """Export results to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(results, f, indent=2)
        self.log_info(f"Exported results to: {path}")


if __name__ == "__main__":
    script = FeatureFlagsScript()
    sys.exit(script.execute())
