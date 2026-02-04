"""
Skill Testing submodule.

Provides a testing framework for validating, benchmarking, and running test cases against skills.
"""

import logging
import time
from typing import Any, Dict, List, Optional

try:
    from codomyrmex.logging_monitoring.logger_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)


class SkillTestResult:
    """Result of a single skill test case."""

    def __init__(self, name: str, passed: bool, expected: Any = None, actual: Any = None, error: Optional[str] = None):
        self.name = name
        self.passed = passed
        self.expected = expected
        self.actual = actual
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "name": self.name,
            "passed": self.passed,
        }
        if self.expected is not None:
            result["expected"] = self.expected
        if self.actual is not None:
            result["actual"] = self.actual
        if self.error:
            result["error"] = self.error
        return result


class SkillTestRunner:
    """Runs test cases against skills and produces reports."""

    def test_skill(self, skill, test_cases: List[Dict[str, Any]]) -> List[SkillTestResult]:
        """
        Run test cases against a skill.

        Each test case is a dict with:
            - 'name': Test case name
            - 'inputs': Dict of keyword arguments
            - 'expected': Expected return value (optional, for equality check)

        Args:
            skill: Skill instance to test
            test_cases: List of test case dictionaries

        Returns:
            List of SkillTestResult objects
        """
        results = []
        skill_name = getattr(getattr(skill, 'metadata', None), 'name', str(skill))
        logger.info(f"Running {len(test_cases)} test cases for skill: {skill_name}")

        for case in test_cases:
            name = case.get("name", "unnamed")
            inputs = case.get("inputs", {})
            expected = case.get("expected")

            try:
                actual = skill.execute(**inputs)
                if expected is not None:
                    passed = actual == expected
                else:
                    passed = True  # No expected value means we just check it doesn't raise

                results.append(SkillTestResult(
                    name=name,
                    passed=passed,
                    expected=expected,
                    actual=actual,
                ))
            except Exception as e:
                results.append(SkillTestResult(
                    name=name,
                    passed=False,
                    expected=expected,
                    error=str(e),
                ))

        passed_count = sum(1 for r in results if r.passed)
        logger.info(f"Test results for {skill_name}: {passed_count}/{len(results)} passed")
        return results

    def validate_skill(self, skill) -> Dict[str, Any]:
        """
        Validate a skill's metadata and parameter definitions.

        Args:
            skill: Skill instance to validate

        Returns:
            Dictionary with validation results
        """
        issues = []

        if not hasattr(skill, 'metadata'):
            issues.append("Missing 'metadata' attribute")
            return {"valid": False, "issues": issues}

        metadata = skill.metadata

        if not getattr(metadata, 'name', None):
            issues.append("Metadata missing 'name'")
        if not getattr(metadata, 'description', None):
            issues.append("Metadata missing 'description'")
        if not getattr(metadata, 'id', None):
            issues.append("Metadata missing 'id'")

        if not hasattr(skill, 'execute'):
            issues.append("Missing 'execute' method")
        if not hasattr(skill, 'validate_params'):
            issues.append("Missing 'validate_params' method")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "skill_name": getattr(metadata, 'name', 'unknown'),
        }

    def benchmark_skill(self, skill, iterations: int = 100, **kwargs) -> Dict[str, Any]:
        """
        Benchmark a skill's execution performance.

        Args:
            skill: Skill instance to benchmark
            iterations: Number of iterations to run
            **kwargs: Parameters to pass to the skill

        Returns:
            Dictionary with benchmark results (min, max, avg, total times)
        """
        skill_name = getattr(getattr(skill, 'metadata', None), 'name', str(skill))
        logger.info(f"Benchmarking skill {skill_name} with {iterations} iterations")

        times = []
        errors = 0

        for _ in range(iterations):
            start = time.monotonic()
            try:
                skill.execute(**kwargs)
            except Exception:
                errors += 1
            elapsed = time.monotonic() - start
            times.append(elapsed)

        return {
            "skill": skill_name,
            "iterations": iterations,
            "errors": errors,
            "total_time": sum(times),
            "avg_time": sum(times) / len(times) if times else 0,
            "min_time": min(times) if times else 0,
            "max_time": max(times) if times else 0,
        }


__all__ = ["SkillTestRunner", "SkillTestResult"]
