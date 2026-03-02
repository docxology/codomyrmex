"""Comprehensive refined utilities."""

import random
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any
from codomyrmex.logging_monitoring.core.logger_config import get_logger

logger = get_logger(__name__)

class RefinedUtilities:
    """A collection of hardened utility methods."""

    @staticmethod
    def deep_merge(dict1: dict[str, Any], dict2: dict[str, Any]) -> dict[str, Any]:
        """Deeply merge two dictionaries."""
        result = dict1.copy()
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = RefinedUtilities.deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    @staticmethod
    def retry(retries: int = 3, backoff_factor: float = 2.0, jitter: bool = True):
        """Retry a function with exponential backoff and optional jitter."""
        def decorator(func: Callable):
            """decorator ."""
            def wrapper(*args, **kwargs):
                """wrapper ."""
                for i in range(retries):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        if i == retries - 1:
                            raise
                        delay = (backoff_factor ** i) + (random.uniform(0, 1) if jitter else 0)
                        logger.warning(f"Retry {i+1}/{retries} after {delay:.2f}s due to: {e}")
                        time.sleep(delay)
            return wrapper
        return decorator

    @staticmethod
    def resolve_path(path_str: str, base_dir: str | None = None) -> Path:
        """Resolve a path string to an absolute Path object."""
        path = Path(path_str)
        if not path.is_absolute():
            base = Path(base_dir) if base_dir else Path.cwd()
            path = (base / path).resolve()
        return path
