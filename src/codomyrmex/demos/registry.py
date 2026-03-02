"""Demo Registry and Execution logic."""

import functools
import inspect
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from codomyrmex.logging_monitoring import get_logger
from codomyrmex.orchestrator import thin

logger = get_logger(__name__)


@dataclass
class DemoInfo:
    """Metadata for a demonstration."""
    name: str
    description: str
    target: Callable | Path
    module: str | None = None
    category: str = "general"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DemoResult:
    """Result of a demonstration execution."""
    name: str
    success: bool
    output: str = ""
    error: str | None = None
    execution_time: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class DemoRegistry:
    """Registry for managing and running demonstrations."""

    def __init__(self) -> None:
        self._demos: dict[str, DemoInfo] = {}

    def register(
        self,
        name: str,
        description: str,
        target: Callable | Path,
        module: str | None = None,
        category: str = "general",
        **metadata: Any
    ) -> None:
        """Register a new demonstration."""
        if name in self._demos:
            logger.warning(f"Overwriting demo: {name}")

        self._demos[name] = DemoInfo(
            name=name,
            description=description,
            target=target,
            module=module,
            category=category,
            metadata=metadata
        )
        logger.debug(f"Registered demo: {name}")

    def get_demo(self, name: str) -> DemoInfo | None:
        """Get demo info by name."""
        return self._demos.get(name)

    def list_demos(
        self,
        module: str | None = None,
        category: str | None = None
    ) -> list[DemoInfo]:
        """List registered demos, optionally filtered."""
        results = list(self._demos.values())
        if module:
            results = [d for d in results if d.module == module]
        if category:
            results = [d for d in results if d.category == category]
        return results

    def discover_scripts(self, directory: str | Path, pattern: str = "demo_*.py") -> None:
        """Discover demo scripts in a directory."""
        dir_path = Path(directory)
        if not dir_path.exists() or not dir_path.is_dir():
            logger.error(f"Discovery directory does not exist: {directory}")
            return

        for script_path in dir_path.glob(pattern):
            name = script_path.stem
            # Simple heuristic for description: first line of docstring
            description = f"Script demo: {name}"
            try:
                content = script_path.read_text()
                if '"""' in content:
                    doc = content.split('"""')[1].strip()
                    description = doc.split("\n")[0]
            except Exception:
                pass

            self.register(
                name=name,
                description=description,
                target=script_path,
                category="script"
            )

    def run_demo(self, name: str, **kwargs: Any) -> DemoResult:
        """Run a registered demonstration."""
        info = self.get_demo(name)
        if not info:
            return DemoResult(
                name=name,
                success=False,
                error=f"Demo '{name}' not found."
            )

        start_time = time.time()
        logger.info(f"Starting demo: {name}")

        try:
            if isinstance(info.target, Path):
                # Run as script
                res = thin.run(info.target, **kwargs)
                # thin.run returns a result from run_script or shell
                # For run_script, success is determined by exit code
                success = res.get("success") if "success" in res else (res.get("status") == "passed")
                output = res.get("stdout", "")
                error = res.get("stderr") if not success else None
            else:
                # Run as callable
                if inspect.iscoroutinefunction(info.target):
                    import asyncio
                    val = asyncio.run(info.target(**kwargs))
                else:
                    val = info.target(**kwargs)

                success = True if val is None else bool(val)
                output = str(val) if val is not None else ""
                error = None

            execution_time = time.time() - start_time
            logger.info(f"Demo '{name}' finished in {execution_time:.2f}s (success={success})")

            return DemoResult(
                name=name,
                success=success,
                output=output,
                error=error,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Demo '{name}' failed: {e}", exc_info=True)
            return DemoResult(
                name=name,
                success=False,
                error=str(e),
                execution_time=execution_time
            )

    def run_all(self, **kwargs: Any) -> list[DemoResult]:
        """Run all registered demos."""
        return [self.run_demo(name, **kwargs) for name in self._demos]


# Global registry instance
_registry = DemoRegistry()


def get_registry() -> DemoRegistry:
    """Get the global demo registry."""
    return _registry


def demo(
    name: str | None = None,
    description: str = "",
    module: str | None = None,
    category: str = "general",
    **metadata: Any
) -> Callable:
    """Decorator to register a function as a demo."""
    def decorator(func: Callable) -> Callable:
        demo_name = name or func.__name__
        demo_desc = description or (func.__doc__ or "").split("\n")[0]

        # Determine module if not provided
        demo_module = module
        if not demo_module:
            mod = inspect.getmodule(func)
            if mod:
                demo_module = mod.__name__.split(".")[-1]

        get_registry().register(
            name=demo_name,
            description=demo_desc,
            target=func,
            module=demo_module,
            category=category,
            **metadata
        )

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

    return decorator
