"""Tests for containerization.wasm module."""

import pytest
import wasmtime  # core dependency (pyproject [project.dependencies])

from codomyrmex.containerization.wasm import (
    WASMComponentModel,
    WASMExecution,
    WASMInstance,
    WASMModule,
    WASMOrchestrator,
    WASMRuntime,
    WasmtimeClient,
)


@pytest.mark.unit
class TestWASMRuntime:
    """Test suite for WASMRuntime."""

    def test_wasmtime(self):
        assert WASMRuntime.WASMTIME is not None

    def test_wasmer(self):
        assert WASMRuntime.WASMER is not None

    def test_wazero(self):
        assert WASMRuntime.WAZERO is not None

    def test_wasmedge(self):
        assert WASMRuntime.WASMEDGE is not None


@pytest.mark.unit
class TestWASMModule:
    """Test suite for WASMModule."""

    def test_create_module(self):
        module = WASMModule(name="test-mod", path="/tmp/test.wasm")
        assert module.name == "test-mod"
        assert module.runtime == WASMRuntime.WASMTIME
        assert module.memory_pages == 256

    def test_module_defaults(self):
        module = WASMModule(name="m", path="/m.wasm")
        assert module.fuel_limit is None
        assert module.environment == {}
        assert module.capabilities == []


@pytest.mark.unit
class TestWASMInstance:
    """Test suite for WASMInstance."""

    def test_create_instance(self):
        module = WASMModule(name="m", path="/m.wasm")
        instance = WASMInstance(id="inst-1", module=module)
        assert instance.id == "inst-1"
        assert instance.status == "running"
        assert instance.memory_used_bytes == 0
        assert instance.fuel_consumed == 0


@pytest.mark.unit
class TestWASMExecution:
    """Test suite for WASMExecution."""

    def test_successful_execution(self):
        execution = WASMExecution(success=True, result=42)
        assert execution.success is True
        assert execution.result == 42
        assert execution.error is None

    def test_failed_execution(self):
        execution = WASMExecution(success=False, error="out of fuel")
        assert execution.success is False
        assert execution.error == "out of fuel"


@pytest.mark.unit
class TestWasmtimeClient:
    """Test suite for WasmtimeClient."""

    def test_create_client(self):
        client = WasmtimeClient()
        assert client is not None
        assert client.runtime == WASMRuntime.WASMTIME


@pytest.mark.unit
class TestWASMOrchestrator:
    """Test suite for WASMOrchestrator."""

    def test_create_orchestrator(self):
        orch = WASMOrchestrator()
        assert orch is not None


@pytest.mark.unit
class TestWASMComponentModel:
    """Test suite for WASMComponentModel."""

    def test_create_model(self):
        model = WASMComponentModel()
        assert model is not None

    def test_define_interface(self):
        model = WASMComponentModel()
        model.define_interface(
            "math", {"add": {"params": ["i32", "i32"], "result": "i32"}}
        )
        iface = model.get_interface("math")
        assert iface is not None


# ---------------------------------------------------------------------------
# Real wasmtime execution (modules compiled from WAT with wasmtime.wat2wasm)
# ---------------------------------------------------------------------------


MATH_WAT = """
(module
  (memory (export "memory") 1 4)
  (func (export "add") (param i32 i32) (result i32)
    local.get 0 local.get 1 i32.add)
  (func (export "pair") (result i32 i64) i32.const 7 i64.const 9)
  (func (export "noop"))
  (func (export "spin") (loop br 0))
  (func (export "div") (param i32 i32) (result i32)
    local.get 0 local.get 1 i32.div_s)
  (func (export "grow") (param i32) (result i32) local.get 0 memory.grow)
)
"""

WASI_ENV_WAT = """
(module
  (import "wasi_snapshot_preview1" "environ_sizes_get"
    (func $sizes (param i32 i32) (result i32)))
  (memory (export "memory") 1)
  (func (export "env_count") (result i32)
    (drop (call $sizes (i32.const 0) (i32.const 4)))
    (i32.load (i32.const 0)))
)
"""


def _error_of(execution: WASMExecution) -> str:
    """Return the error of a failed execution."""
    assert execution.success is False
    assert execution.error is not None
    return execution.error


def _wasm_file(tmp_path, wat: str, name: str = "mod.wasm") -> str:
    path = tmp_path / name
    path.write_bytes(bytes(wasmtime.wat2wasm(wat)))
    return str(path)


@pytest.fixture
def math_module(tmp_path):
    return WASMModule(name="math", path=_wasm_file(tmp_path, MATH_WAT))


@pytest.mark.unit
class TestWasmtimeClientExecution:
    """WasmtimeClient runs real modules and reports measured values."""

    def test_load_reports_exported_memory(self, math_module):
        client = WasmtimeClient()
        instance = client.load_module(math_module)
        assert instance.id == "wasm-1"
        assert instance.status == "running"
        assert instance.memory_used_bytes == 65536  # one page exported
        assert client.list_instances() == [instance]

    def test_execute_add(self, math_module):
        client = WasmtimeClient()
        instance = client.load_module(math_module)
        execution = client.execute(instance.id, "add", [2, 40])
        assert execution.success is True
        assert execution.result == 42
        assert execution.error is None
        assert execution.fuel_consumed > 0
        assert execution.execution_time_ms >= 0.0
        assert execution.memory_used_bytes == 65536

    def test_fuel_is_accumulated_on_instance(self, math_module):
        client = WasmtimeClient()
        instance = client.load_module(math_module)
        first = client.execute(instance.id, "add", [1, 1])
        second = client.execute(instance.id, "add", [1, 1])
        assert first.fuel_consumed == second.fuel_consumed
        assert instance.fuel_consumed == first.fuel_consumed + second.fuel_consumed

    def test_multi_value_and_void_results(self, math_module):
        client = WasmtimeClient()
        instance = client.load_module(math_module)
        assert list(client.execute(instance.id, "pair").result) == [7, 9]
        noop = client.execute(instance.id, "noop")
        assert noop.success is True
        assert noop.result is None

    def test_fuel_limit_stops_infinite_loop(self, tmp_path):
        module = WASMModule(
            name="spin", path=_wasm_file(tmp_path, MATH_WAT), fuel_limit=5_000
        )
        client = WasmtimeClient()
        instance = client.load_module(module)
        execution = client.execute(instance.id, "spin")
        assert execution.success is False
        assert "fuel" in _error_of(execution)
        assert execution.fuel_consumed == 5_000
        # The budget is per call: the instance stays usable.
        assert client.execute(instance.id, "add", [3, 4]).result == 7

    def test_trap_is_reported(self, math_module):
        client = WasmtimeClient()
        instance = client.load_module(math_module)
        execution = client.execute(instance.id, "div", [1, 0])
        assert execution.success is False
        assert "divide by zero" in _error_of(execution)

    def test_bad_arguments_are_reported(self, math_module):
        client = WasmtimeClient()
        instance = client.load_module(math_module)
        too_few = client.execute(instance.id, "add", [1])
        assert too_few.success is False
        assert "too few parameters" in _error_of(too_few)
        wrong_type = client.execute(instance.id, "add", ["x", 1])
        assert wrong_type.success is False
        assert "i32" in _error_of(wrong_type)

    def test_missing_and_non_function_exports(self, math_module):
        client = WasmtimeClient()
        instance = client.load_module(math_module)
        missing = client.execute(instance.id, "nope")
        assert missing.success is False
        assert "not found" in _error_of(missing)
        memory = client.execute(instance.id, "memory")
        assert memory.success is False
        assert "not a function" in _error_of(memory)

    def test_unknown_instance(self):
        execution = WasmtimeClient().execute("wasm-404", "add", [1, 2])
        assert execution.success is False
        assert execution.error == "Instance not found: wasm-404"

    def test_memory_pages_cap_memory_growth(self, tmp_path):
        module = WASMModule(
            name="m", path=_wasm_file(tmp_path, MATH_WAT), memory_pages=2
        )
        client = WasmtimeClient()
        instance = client.load_module(module)
        assert client.execute(instance.id, "grow", [1]).result == 1  # 1 -> 2 pages
        refused = client.execute(instance.id, "grow", [1])  # 3 pages > cap
        assert refused.result == -1
        assert refused.memory_used_bytes == 2 * 65536
        assert instance.memory_used_bytes == 2 * 65536

    def test_memory_cap_below_module_minimum_fails_to_load(self, tmp_path):
        module = WASMModule(
            name="m", path=_wasm_file(tmp_path, MATH_WAT), memory_pages=0
        )
        with pytest.raises(wasmtime.WasmtimeError, match="memory"):
            WasmtimeClient().load_module(module)

    def test_wat_text_file_is_accepted(self, tmp_path):
        path = tmp_path / "math.wat"
        path.write_text(MATH_WAT)
        client = WasmtimeClient()
        instance = client.load_module(WASMModule(name="wat", path=str(path)))
        assert client.execute(instance.id, "add", [5, 6]).result == 11

    def test_wasi_environment_is_visible_to_guest(self, tmp_path):
        module = WASMModule(
            name="env",
            path=_wasm_file(tmp_path, WASI_ENV_WAT),
            environment={"A": "1", "B": "2"},
        )
        client = WasmtimeClient()
        instance = client.load_module(module)
        assert client.execute(instance.id, "env_count").result == 2

    def test_unsupported_import_fails_to_load(self, tmp_path):
        path = _wasm_file(tmp_path, '(module (import "env" "f" (func)))')
        with pytest.raises(wasmtime.WasmtimeError, match="unknown import"):
            WasmtimeClient().load_module(WASMModule(name="imp", path=path))

    def test_unknown_capability_rejected(self, math_module):
        math_module.capabilities = ["stdout", "network"]
        with pytest.raises(ValueError, match="network"):
            WasmtimeClient().load_module(math_module)

    def test_missing_file_rejected(self, tmp_path):
        module = WASMModule(name="x", path=str(tmp_path / "missing.wasm"))
        with pytest.raises(FileNotFoundError):
            WasmtimeClient().load_module(module)

    def test_invalid_binary_rejected(self, tmp_path):
        path = tmp_path / "bad.wasm"
        path.write_bytes(b"\x00asm\x01\x00\x00\x00garbage")
        with pytest.raises(wasmtime.WasmtimeError):
            WasmtimeClient().load_module(WASMModule(name="bad", path=str(path)))

    def test_terminate(self, math_module):
        client = WasmtimeClient()
        instance = client.load_module(math_module)
        assert client.terminate(instance.id) is True
        assert instance.status == "terminated"
        assert client.terminate(instance.id) is False
        assert client.execute(instance.id, "add", [1, 2]).success is False


@pytest.mark.unit
class TestWASMOrchestratorExecution:
    """Orchestrator deploys and executes through a real runtime."""

    def test_deploy_and_execute(self, math_module):
        orch = WASMOrchestrator()
        orch.register_runtime(WasmtimeClient())
        orch.register_module(math_module)
        instance = orch.deploy("math")
        assert instance is not None
        execution = orch.execute(instance.id, "add", [20, 22])
        assert execution is not None
        assert execution.result == 42

    def test_unknown_module_runtime_and_instance(self, math_module):
        orch = WASMOrchestrator()
        assert orch.deploy("missing") is None
        orch.register_module(math_module)
        assert orch.deploy("math") is None  # no runtime registered
        orch.register_runtime(WasmtimeClient())
        assert orch.execute("wasm-404", "add", [1, 2]) is None


@pytest.mark.unit
class TestWASMComponentModelValidation:
    """validate_module inspects the compiled module's exports."""

    def test_matching_interface(self, math_module):
        model = WASMComponentModel()
        model.define_interface(
            "math",
            {
                "add": {"params": ["i32", "i32"], "result": "i32"},
                "pair": {"results": ["i32", "i64"]},
                "noop": {"params": [], "result": None},
            },
        )
        assert model.interface_mismatches(math_module, "math") == []
        assert model.validate_module(math_module, "math") is True

    def test_mismatched_interface(self, math_module):
        model = WASMComponentModel()
        model.define_interface(
            "bad",
            {
                "add": {"params": ["i64", "i64"], "result": "i64"},
                "sub": {"params": ["i32", "i32"]},
                "memory": {},
            },
        )
        problems = model.interface_mismatches(math_module, "bad")
        assert len(problems) == 4
        assert any("missing export 'sub'" in p for p in problems)
        assert any("'memory' is not a function" in p for p in problems)
        assert model.validate_module(math_module, "bad") is False

    def test_undefined_interface(self, math_module):
        model = WASMComponentModel()
        assert model.validate_module(math_module, "nope") is False
        with pytest.raises(KeyError):
            model.interface_mismatches(math_module, "nope")
