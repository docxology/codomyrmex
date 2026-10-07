"""
WebAssembly Runtime Support

WASM runtime support for containerization. :class:`WasmtimeClient` compiles,
instantiates and runs real WebAssembly modules (binary ``.wasm`` or text
``.wat``) with the ``wasmtime`` runtime, metering execution with wasmtime fuel
and capping linear memory at ``WASMModule.memory_pages``.
"""

from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import wasmtime

from codomyrmex.logging_monitoring import get_logger

logger = get_logger(__name__)

#: Bytes in one WebAssembly linear-memory page.
WASM_PAGE_SIZE = 65536

#: Fuel given to a store when the module sets no ``fuel_limit``. Fuel is still
#: consumed (and reported), it just never runs out in practice.
UNLIMITED_FUEL = 2**64 - 1

#: Supported ``WASMModule.capabilities`` values and the WASI stdio stream each
#: one lets the guest inherit from the host process.
WASI_STDIO_CAPABILITIES: dict[str, str] = {
    "stdin": "inherit_stdin",
    "stdout": "inherit_stdout",
    "stderr": "inherit_stderr",
}


class WASMRuntime(Enum):
    """Supported WASM runtimes."""

    WASMTIME = "wasmtime"
    WASMER = "wasmer"
    WAZERO = "wazero"
    WASMEDGE = "wasmedge"


@dataclass
class WASMModule:
    """A WebAssembly module."""

    name: str
    path: str
    runtime: WASMRuntime = WASMRuntime.WASMTIME
    memory_pages: int = 256  # 64KB per page
    fuel_limit: int | None = None  # Execution cycles limit
    environment: dict[str, str] = field(default_factory=dict)
    capabilities: list[str] = field(default_factory=list)  # WASI capabilities
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WASMInstance:
    """A running WASM instance."""

    id: str
    module: WASMModule
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "running"
    memory_used_bytes: int = 0
    fuel_consumed: int = 0


@dataclass
class WASMExecution:
    """Result of a WASM function execution."""

    success: bool
    result: Any = None
    error: str | None = None
    execution_time_ms: float = 0.0
    fuel_consumed: int = 0
    memory_used_bytes: int = 0


class WASMRuntimeClient(ABC):
    """Abstract base class for WASM runtime clients."""

    @property
    @abstractmethod
    def runtime(self) -> WASMRuntime:
        """Runtime."""

    @abstractmethod
    def load_module(self, module: WASMModule) -> WASMInstance:
        """Load a WASM module."""

    @abstractmethod
    def execute(
        self,
        instance_id: str,
        function_name: str,
        args: list[Any] | None = None,
    ) -> WASMExecution:
        """Execute a function in a WASM instance."""

    @abstractmethod
    def terminate(self, instance_id: str) -> bool:
        """Terminate a WASM instance."""


def _compile(engine: wasmtime.Engine, path: str) -> wasmtime.Module:
    """Compile a ``.wasm`` binary or ``.wat`` text file."""
    module_path = Path(path)
    if not module_path.is_file():
        raise FileNotFoundError(f"WASM module not found: {module_path}")
    return wasmtime.Module.from_file(engine, str(module_path))


def _exported_memory_bytes(store: wasmtime.Store, instance: wasmtime.Instance) -> int:
    """Total size of the instance's exported linear memories, in bytes.

    Memories the module does not export cannot be observed from the host and
    are not counted.
    """
    return sum(
        extern.data_len(store)
        for extern in instance.exports(store).values()
        if isinstance(extern, wasmtime.Memory)
    )


@dataclass
class _LiveInstance:
    """Runtime state behind a :class:`WASMInstance` (a store is single-threaded)."""

    store: wasmtime.Store
    instance: wasmtime.Instance
    lock: threading.Lock = field(default_factory=threading.Lock)


class WasmtimeClient(WASMRuntimeClient):
    """Wasmtime runtime client.

    Each loaded module gets its own store, so instances are isolated from each
    other. ``WASMModule.fuel_limit`` is the fuel budget for instantiation and,
    separately, for every :meth:`execute` call; ``memory_pages`` caps each
    linear memory; ``environment`` becomes the WASI environment and
    ``capabilities`` may grant ``"stdin"``, ``"stdout"`` and ``"stderr"``.
    """

    def __init__(self) -> None:
        config = wasmtime.Config()
        config.consume_fuel = True
        self._engine = wasmtime.Engine(config)
        self._instances: dict[str, WASMInstance] = {}
        self._live: dict[str, _LiveInstance] = {}
        self._counter = 0
        self._lock = threading.Lock()

    @property
    def runtime(self) -> WASMRuntime:
        """Runtime."""
        return WASMRuntime.WASMTIME

    def load_module(self, module: WASMModule) -> WASMInstance:
        """Compile and instantiate a WASM module with wasmtime.

        Raises:
            FileNotFoundError: If ``module.path`` does not exist.
            ValueError: If ``module.capabilities`` names an unsupported capability
                or ``memory_pages``/``fuel_limit`` is negative.
            wasmtime.WasmtimeError: If the module is invalid or has imports
                other than WASI.
            wasmtime.Trap: If the module's start function traps.
        """
        if module.memory_pages < 0:
            raise ValueError(f"memory_pages must be >= 0, got {module.memory_pages}")
        if module.fuel_limit is not None and module.fuel_limit < 0:
            raise ValueError(f"fuel_limit must be >= 0, got {module.fuel_limit}")
        wasi = self._wasi_config(module)
        compiled = _compile(self._engine, module.path)

        store = wasmtime.Store(self._engine)
        store.set_limits(memory_size=module.memory_pages * WASM_PAGE_SIZE)
        store.set_wasi(wasi)
        budget = self._fuel_budget(module)
        store.set_fuel(budget)

        linker = wasmtime.Linker(self._engine)
        linker.define_wasi()
        instance = linker.instantiate(store, compiled)

        with self._lock:
            self._counter += 1
            wasm_instance = WASMInstance(
                id=f"wasm-{self._counter}",
                module=module,
                memory_used_bytes=_exported_memory_bytes(store, instance),
                fuel_consumed=budget - store.get_fuel(),
            )
            self._instances[wasm_instance.id] = wasm_instance
            self._live[wasm_instance.id] = _LiveInstance(store, instance)
        logger.info("Loaded WASM module %s as %s", module.name, wasm_instance.id)
        return wasm_instance

    def execute(
        self,
        instance_id: str,
        function_name: str,
        args: list[Any] | None = None,
    ) -> WASMExecution:
        """Call an exported function and measure time, fuel and memory.

        Traps (including running out of fuel), wrong argument counts or types
        and missing exports are reported as ``success=False`` with the
        runtime's error message.
        """
        with self._lock:
            instance = self._instances.get(instance_id)
            live = self._live.get(instance_id)
        if instance is None or live is None:
            return WASMExecution(
                success=False,
                error=f"Instance not found: {instance_id}",
            )

        with live.lock:
            store = live.store
            export = live.instance.exports(store).get(function_name)
            if not isinstance(export, wasmtime.Func):
                problem = "is not a function" if export is not None else "not found"
                return WASMExecution(
                    success=False,
                    error=f"Export {function_name!r} {problem} in {instance_id}",
                    memory_used_bytes=_exported_memory_bytes(store, live.instance),
                )

            budget = self._fuel_budget(instance.module)
            store.set_fuel(budget)
            result: Any = None
            error: str | None = None
            start = time.perf_counter()
            try:
                result = export(store, *(args or []))
            except (wasmtime.Trap, wasmtime.WasmtimeError, TypeError) as exc:
                error = str(exc)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            fuel_used = budget - store.get_fuel()
            memory_bytes = _exported_memory_bytes(store, live.instance)

        instance.fuel_consumed += fuel_used
        instance.memory_used_bytes = memory_bytes
        return WASMExecution(
            success=error is None,
            result=result,
            error=error,
            execution_time_ms=elapsed_ms,
            fuel_consumed=fuel_used,
            memory_used_bytes=memory_bytes,
        )

    def terminate(self, instance_id: str) -> bool:
        """Terminate instance."""
        with self._lock:
            if instance_id in self._instances:
                self._instances[instance_id].status = "terminated"
                del self._instances[instance_id]
                self._live.pop(instance_id, None)
                return True
            return False

    def list_instances(self) -> list[WASMInstance]:
        """list all instances."""
        return list(self._instances.values())

    @staticmethod
    def _fuel_budget(module: WASMModule) -> int:
        return module.fuel_limit if module.fuel_limit is not None else UNLIMITED_FUEL

    @staticmethod
    def _wasi_config(module: WASMModule) -> wasmtime.WasiConfig:
        unknown = sorted(set(module.capabilities) - set(WASI_STDIO_CAPABILITIES))
        if unknown:
            raise ValueError(
                f"Unsupported WASI capabilities for module {module.name!r}: "
                f"{', '.join(unknown)}; supported: "
                f"{', '.join(sorted(WASI_STDIO_CAPABILITIES))}"
            )
        wasi = wasmtime.WasiConfig()
        if module.environment:
            wasi.env = list(module.environment.items())
        for capability in module.capabilities:
            getattr(wasi, WASI_STDIO_CAPABILITIES[capability])()
        return wasi


class WASMOrchestrator:
    """Orchestrate WASM containers."""

    def __init__(self):
        self._runtimes: dict[WASMRuntime, WASMRuntimeClient] = {}
        self._modules: dict[str, WASMModule] = {}

    def register_runtime(self, client: WASMRuntimeClient) -> None:
        """Register a WASM runtime."""
        self._runtimes[client.runtime] = client

    def register_module(self, module: WASMModule) -> None:
        """Register a module for deployment."""
        self._modules[module.name] = module

    def deploy(
        self,
        module_name: str,
        runtime: WASMRuntime | None = None,
    ) -> WASMInstance | None:
        """Deploy a registered module."""
        module = self._modules.get(module_name)
        if not module:
            return None

        target_runtime = runtime or module.runtime
        client = self._runtimes.get(target_runtime)
        if not client:
            return None

        return client.load_module(module)

    def execute(
        self,
        instance_id: str,
        function_name: str,
        args: list[Any] | None = None,
    ) -> WASMExecution | None:
        """Execute a function on whichever runtime owns ``instance_id``.

        Returns ``None`` if no registered runtime knows the instance.
        """
        for client in self._runtimes.values():
            result = client.execute(instance_id, function_name, args)
            if result.success or result.error != f"Instance not found: {instance_id}":
                return result
        return None


class WASMComponentModel:
    """Support for WASM Component Model (interface types)."""

    def __init__(self):
        self._interfaces: dict[str, dict[str, Any]] = {}

    def define_interface(
        self,
        name: str,
        functions: dict[str, dict[str, Any]],
    ) -> None:
        """Define a component interface.

        Each function maps to an optional ``"params"`` list and either a
        ``"result"`` (single type or ``None``) or a ``"results"`` list, using
        WebAssembly value type names (``"i32"``, ``"i64"``, ``"f32"``,
        ``"f64"``, ...). Omitted keys are not checked.
        """
        self._interfaces[name] = functions

    def get_interface(self, name: str) -> dict[str, Any] | None:
        """Get interface definition."""
        return self._interfaces.get(name)

    def interface_mismatches(
        self,
        module: WASMModule,
        interface_name: str,
    ) -> list[str]:
        """List how the compiled module's exports differ from an interface.

        Raises:
            KeyError: If the interface is not defined.
            FileNotFoundError: If the module file does not exist.
            wasmtime.WasmtimeError: If the module cannot be compiled.
        """
        if interface_name not in self._interfaces:
            raise KeyError(f"Interface not defined: {interface_name}")
        compiled = _compile(wasmtime.Engine(), module.path)
        exports = {export.name: export.type for export in compiled.exports}

        problems: list[str] = []
        for fn_name, spec in self._interfaces[interface_name].items():
            export_type = exports.get(fn_name)
            if export_type is None:
                problems.append(f"missing export {fn_name!r}")
                continue
            if not isinstance(export_type, wasmtime.FuncType):
                problems.append(f"export {fn_name!r} is not a function")
                continue
            params = [str(p) for p in export_type.params]
            results = [str(r) for r in export_type.results]
            if "params" in spec and params != list(spec["params"]):
                problems.append(
                    f"{fn_name!r} params {params} != expected {list(spec['params'])}"
                )
            expected_results = _expected_results(spec)
            if expected_results is not None and results != expected_results:
                problems.append(
                    f"{fn_name!r} results {results} != expected {expected_results}"
                )
        return problems

    def validate_module(
        self,
        module: WASMModule,
        interface_name: str,
    ) -> bool:
        """Validate that the module's exports implement the interface.

        Returns ``False`` for an undefined interface or any mismatch (see
        :meth:`interface_mismatches`).
        """
        if interface_name not in self._interfaces:
            return False
        problems = self.interface_mismatches(module, interface_name)
        for problem in problems:
            logger.info(
                "Module %s does not satisfy %s: %s",
                module.name,
                interface_name,
                problem,
            )
        return not problems


def _expected_results(spec: dict[str, Any]) -> list[str] | None:
    if "results" in spec:
        return list(spec["results"])
    if "result" in spec:
        return [] if spec["result"] is None else [spec["result"]]
    return None


__all__ = [
    "UNLIMITED_FUEL",
    "WASI_STDIO_CAPABILITIES",
    "WASM_PAGE_SIZE",
    "WASMComponentModel",
    "WASMExecution",
    "WASMInstance",
    "WASMModule",
    "WASMOrchestrator",
    "WASMRuntime",
    "WASMRuntimeClient",
    "WasmtimeClient",
]
