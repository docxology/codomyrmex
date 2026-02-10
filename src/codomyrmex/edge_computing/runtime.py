"""Edge function runtime execution."""

import time
from typing import Any

from .models import EdgeExecutionError, EdgeFunction, EdgeNode


class EdgeRuntime:
    """Runtime for edge function execution."""

    def __init__(self, node: EdgeNode):
        self.node = node
        self._functions: dict[str, EdgeFunction] = {}

    def deploy(self, function: EdgeFunction) -> None:
        """Deploy a function to edge."""
        self._functions[function.id] = function

    def undeploy(self, function_id: str) -> bool:
        """Undeploy a function."""
        if function_id in self._functions:
            del self._functions[function_id]
            return True
        return False

    def invoke(self, function_id: str, *args, **kwargs) -> Any:
        """Invoke an edge function."""
        func = self._functions.get(function_id)
        if not func:
            raise ValueError(f"Function not found: {function_id}")

        start = time.time()
        try:
            result = func.handler(*args, **kwargs)
            elapsed = time.time() - start
            if elapsed > func.timeout_seconds:
                raise TimeoutError(f"Function exceeded timeout: {elapsed}s")
            return result
        except Exception as e:
            raise EdgeExecutionError(f"Edge function failed: {e}") from e

    def list_functions(self) -> list[EdgeFunction]:
        return list(self._functions.values())
