"""Config cascading invariant checker.

Verifies that configuration resolution (env → yaml → default) is
deterministic — the same inputs always produce the same outputs,
regardless of load order.

Example::

    checker = ConfigInvariantChecker()
    results = checker.verify_determinism()
    assert all(r.passed for r in results)
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class InvariantResult:
    """Result of a single invariant check.

    Attributes:
        key: Configuration key name.
        passed: Whether the invariant holds.
        expected: Expected resolved value.
        actual: Actual resolved value.
        message: Human-readable description.
    """

    key: str
    passed: bool
    expected: Any = None
    actual: Any = None
    message: str = ""


class ConfigInvariantChecker:
    """Checks determinism of configuration cascading.

    Verifies that config resolution follows a strict precedence:
    ``env_var > yaml_file > default_value``.

    Args:
        defaults: Default configuration values.
        yaml_overrides: Values from YAML config files.
        env_prefix: Environment variable prefix (default: ``CODOMYRMEX_``).

    Example::

        checker = ConfigInvariantChecker(
            defaults={"port": 8787, "debug": False},
            yaml_overrides={"port": 9000},
        )
        results = checker.verify_determinism()
    """

    def __init__(
        self,
        defaults: dict[str, Any] | None = None,
        yaml_overrides: dict[str, Any] | None = None,
        env_prefix: str = "CODOMYRMEX_",
    ) -> None:
        self._defaults = defaults or {}
        self._yaml = yaml_overrides or {}
        self._env_prefix = env_prefix

    def _resolve_key(self, key: str) -> tuple[Any, str]:
        """Resolve a config key through the cascade.

        Returns:
            Tuple of (resolved_value, source_layer).
        """
        # Layer 1: Environment variable (highest priority)
        env_key = f"{self._env_prefix}{key.upper()}"
        env_val = os.environ.get(env_key)
        if env_val is not None:
            return self._coerce(env_val, key), "env"

        # Layer 2: YAML override
        if key in self._yaml:
            return self._yaml[key], "yaml"

        # Layer 3: Default value
        if key in self._defaults:
            return self._defaults[key], "default"

        return None, "unset"

    def _coerce(self, value: str, key: str) -> Any:
        """Coerce an env string to the expected type based on defaults."""
        default = self._defaults.get(key)
        if default is None:
            return value
        if isinstance(default, bool):
            return value.lower() in ("true", "1", "yes")
        if isinstance(default, int):
            try:
                return int(value)
            except ValueError:
                return value
        if isinstance(default, float):
            try:
                return float(value)
            except ValueError:
                return value
        return value

    def _get_all_keys(self) -> set[str]:
        """Get all known configuration keys."""
        keys = set(self._defaults.keys())
        keys.update(self._yaml.keys())
        return keys

    def verify_determinism(self) -> list[InvariantResult]:
        """Verify that config resolution is deterministic.

        Resolves each key twice and asserts identical results.

        Returns:
            List of :class:`InvariantResult` for each config key.
        """
        results: list[InvariantResult] = []
        keys = sorted(self._get_all_keys())

        for key in keys:
            val1, src1 = self._resolve_key(key)
            val2, src2 = self._resolve_key(key)

            passed = val1 == val2 and src1 == src2
            results.append(InvariantResult(
                key=key,
                passed=passed,
                expected=val1,
                actual=val2,
                message=f"{key}: {src1}={val1}" if passed else f"{key}: non-deterministic ({src1}={val1} vs {src2}={val2})",
            ))

        logger.info(
            "Verified %d config keys: %d passed, %d failed",
            len(results),
            sum(1 for r in results if r.passed),
            sum(1 for r in results if not r.passed),
        )
        return results

    def verify_precedence(self) -> list[InvariantResult]:
        """Verify that env vars override YAML which overrides defaults.

        Returns:
            List of :class:`InvariantResult` for precedence checks.
        """
        results: list[InvariantResult] = []

        for key in sorted(self._get_all_keys()):
            val, source = self._resolve_key(key)

            env_key = f"{self._env_prefix}{key.upper()}"
            env_val = os.environ.get(env_key)

            # If env is set, it must win
            if env_val is not None:
                coerced = self._coerce(env_val, key)
                passed = val == coerced and source == "env"
                results.append(InvariantResult(
                    key=key,
                    passed=passed,
                    expected=coerced,
                    actual=val,
                    message=f"{key}: env precedence {'holds' if passed else 'VIOLATED'}",
                ))
            # If yaml is set (and env is not), yaml must win
            elif key in self._yaml:
                passed = val == self._yaml[key] and source == "yaml"
                results.append(InvariantResult(
                    key=key,
                    passed=passed,
                    expected=self._yaml[key],
                    actual=val,
                    message=f"{key}: yaml precedence {'holds' if passed else 'VIOLATED'}",
                ))
            # Otherwise default must win
            elif key in self._defaults:
                passed = val == self._defaults[key] and source == "default"
                results.append(InvariantResult(
                    key=key,
                    passed=passed,
                    expected=self._defaults[key],
                    actual=val,
                    message=f"{key}: default precedence {'holds' if passed else 'VIOLATED'}",
                ))

        return results

    def get_summary(self) -> dict[str, Any]:
        """Return a summary of all invariant checks.

        Returns:
            Dict with ``total_keys``, ``determinism_pass``, ``precedence_pass``.
        """
        det = self.verify_determinism()
        prec = self.verify_precedence()
        return {
            "total_keys": len(det),
            "determinism_pass": sum(1 for r in det if r.passed),
            "determinism_fail": sum(1 for r in det if not r.passed),
            "precedence_pass": sum(1 for r in prec if r.passed),
            "precedence_fail": sum(1 for r in prec if not r.passed),
        }


__all__ = [
    "ConfigInvariantChecker",
    "InvariantResult",
]
