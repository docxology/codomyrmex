"""Tests for containerization.wasm module."""

import pytest

try:
    from codomyrmex.containerization.wasm import (
        WASMComponentModel,
        WASMExecution,
        WASMInstance,
        WASMModule,
        WASMOrchestrator,
        WASMRuntime,
        WASMRuntimeClient,
        WasmtimeClient,
    )
    HAS_MODULE = True
except ImportError:
    HAS_MODULE = False

if not HAS_MODULE:
    pytest.skip("containerization.wasm module not available", allow_module_level=True)


@pytest.mark.unit
class TestWASMRuntime:
    """Test suite for WASMRuntime."""
    def test_wasmtime(self):
        """Test functionality: wasmtime."""
        assert WASMRuntime.WASMTIME is not None

    def test_wasmer(self):
        """Test functionality: wasmer."""
        assert WASMRuntime.WASMER is not None

    def test_wazero(self):
        """Test functionality: wazero."""
        assert WASMRuntime.WAZERO is not None

    def test_wasmedge(self):
        """Test functionality: wasmedge."""
        assert WASMRuntime.WASMEDGE is not None


@pytest.mark.unit
class TestWASMModule:
    """Test suite for WASMModule."""
    def test_create_module(self):
        """Test functionality: create module."""
        module = WASMModule(name="test-mod", path="/tmp/test.wasm")
        assert module.name == "test-mod"
        assert module.runtime == WASMRuntime.WASMTIME
        assert module.memory_pages == 256

    def test_module_defaults(self):
        """Test functionality: module defaults."""
        module = WASMModule(name="m", path="/m.wasm")
        assert module.fuel_limit is None
        assert module.environment == {}
        assert module.capabilities == []


@pytest.mark.unit
class TestWASMInstance:
    """Test suite for WASMInstance."""
    def test_create_instance(self):
        """Test functionality: create instance."""
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
        """Test functionality: successful execution."""
        execution = WASMExecution(success=True, result=42)
        assert execution.success is True
        assert execution.result == 42
        assert execution.error is None

    def test_failed_execution(self):
        """Test functionality: failed execution."""
        execution = WASMExecution(success=False, error="out of fuel")
        assert execution.success is False
        assert execution.error == "out of fuel"


@pytest.mark.unit
class TestWasmtimeClient:
    """Test suite for WasmtimeClient."""
    def test_create_client(self):
        """Test functionality: create client."""
        client = WasmtimeClient()
        assert client is not None
        assert client.runtime == WASMRuntime.WASMTIME


@pytest.mark.unit
class TestWASMOrchestrator:
    """Test suite for WASMOrchestrator."""
    def test_create_orchestrator(self):
        """Test functionality: create orchestrator."""
        orch = WASMOrchestrator()
        assert orch is not None


@pytest.mark.unit
class TestWASMComponentModel:
    """Test suite for WASMComponentModel."""
    def test_create_model(self):
        """Test functionality: create model."""
        model = WASMComponentModel()
        assert model is not None

    def test_define_interface(self):
        """Test functionality: define interface."""
        model = WASMComponentModel()
        model.define_interface("math", {"add": {"params": ["i32", "i32"], "result": "i32"}})
        iface = model.get_interface("math")
        assert iface is not None
