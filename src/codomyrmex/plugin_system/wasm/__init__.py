"""WASM zero-trust plugin execution system.

This submodule wraps wasmtime to provide a bounded execution environment
for unverified capability plugins, preventing infinite loops and host access.
"""

from .wasm_sandbox import WasmSandbox, WasmSandboxError

__all__ = ["WasmSandbox", "WasmSandboxError"]
