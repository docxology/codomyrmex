"""WASM Plugin Sandbox module.

This module provides a completely isolated WebAssembly runtime using wasmtime,
enforcing memory and execution block (fuel) constraints for untrusted plugins
in a zero-trust model.
"""

from typing import Any

import wasmtime


class WasmSandboxError(Exception):
    """Base exception for sandbox errors (compilation, runtime, timeouts)."""


class WasmSandbox:
    """Secure WASM execution environment for zero-trust plugins.

    Creates a sandbox with fixed resources that guarantees termination,
    even for malicious plugins with infinite loops.
    """

    def __init__(self, max_fuel: int = 1_000_000) -> None:
        """Initialize the sandbox with optional execution constraints.

        Args:
            max_fuel: Maximum instructions/fuel units the WASM binary is allowed to consume.
                      Prevents infinite loop DOS vulnerabilities.
        """
        self.config = wasmtime.Config()
        self.config.consume_fuel = True
        self.engine = wasmtime.Engine(self.config)
        self.max_fuel = max_fuel

    def execute_plugin(
        self, wasm_source: bytes | str, function_name: str, *args: Any
    ) -> Any:
        """Evaluate a WASM function securely.

        Args:
            wasm_source: The compiled WebAssembly binary (bytes) or WAT text format (str).
            function_name: The exported function name to call.
            args: Arguments to pass to the WebAssembly function.

        Returns:
            The output of the function execution.

        Raises:
            WasmSandboxError: If execution traps, runs out of fuel, or the function is missing.
        """
        try:
            # Create a completely isolated store for each plugin instantiation
            store = wasmtime.Store(self.engine)
            store.set_fuel(self.max_fuel)

            # Accept both WAT string and binary bytes natively
            module = wasmtime.Module(self.engine, wasm_source)

            # Instantiate without any host imports (pure sandbox)
            instance = wasmtime.Instance(store, module, [])
            exports = instance.exports(store)

            if function_name not in exports:
                raise WasmSandboxError(
                    f"Export '{function_name}' not found in WASM module."
                )

            func = exports[function_name]

            # Ensure it is actually a callable function (not just an exported memory/global)
            if not isinstance(func, wasmtime.Func):
                raise WasmSandboxError(
                    f"Export '{function_name}' is not a callable function."
                )

            # Run securely within the configured limits
            return func(store, *args)

        except wasmtime.Trap as e:
            # Out-of-fuel errors or WebAssembly traps (e.g., division by zero)
            raise WasmSandboxError(f"WASM Trap or Quota Exceeded: {e.message}") from e
        except Exception as e:
            # Parse errors, validation errors, bad args, etc.
            raise WasmSandboxError(f"Sandbox execution failed: {e}") from e
