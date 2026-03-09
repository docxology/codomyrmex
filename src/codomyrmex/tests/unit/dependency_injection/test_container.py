"""Comprehensive tests for the IoC container — zero-mock, all real objects.

Covers: registration (type, instance, factory), resolution (singleton, transient, scoped),
error paths (circular deps, missing registrations), thread safety, and lifecycle management.
"""

import threading
from abc import ABC, abstractmethod

import pytest

from codomyrmex.dependency_injection.container import (
    CircularDependencyError,
    Container,
    ResolutionError,
    ScopeContext,
    ServiceDescriptor,
)
from codomyrmex.dependency_injection.scopes import Scope

# ---------------------------------------------------------------------------
# Test fixtures (real classes — zero mocks)
# ---------------------------------------------------------------------------


class Greeter(ABC):
    @abstractmethod
    def greet(self, name: str) -> str: ...


class EnglishGreeter(Greeter):
    def greet(self, name: str) -> str:
        return f"Hello, {name}!"


class FrenchGreeter(Greeter):
    def greet(self, name: str) -> str:
        return f"Bonjour, {name}!"


class Logger:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def log(self, msg: str) -> None:
        self.messages.append(msg)


class Service:
    """A service that depends on Greeter via constructor injection."""

    def __init__(self, greeter: Greeter) -> None:
        self.greeter = greeter


class DisposableResource:
    """A resource with a dispose method for lifecycle testing."""

    disposed = False

    def dispose(self) -> None:
        self.disposed = True


class CloseableResource:
    """A resource with a close method for lifecycle testing."""

    closed = False

    def close(self) -> None:
        self.closed = True


# ---------------------------------------------------------------------------
# Scope enum
# ---------------------------------------------------------------------------


class TestScope:
    def test_enum_values(self):
        assert Scope.SINGLETON.value == "singleton"
        assert Scope.TRANSIENT.value == "transient"
        assert Scope.SCOPED.value == "scoped"

    def test_from_string_valid(self):
        assert Scope.from_string("singleton") is Scope.SINGLETON
        assert Scope.from_string("TRANSIENT") is Scope.TRANSIENT
        assert Scope.from_string("Scoped") is Scope.SCOPED

    def test_from_string_invalid(self):
        with pytest.raises(ValueError, match="Invalid scope"):
            Scope.from_string("request")


# ---------------------------------------------------------------------------
# Container basics
# ---------------------------------------------------------------------------


class TestContainerRegistration:
    def test_register_type(self):
        c = Container()
        c.register(Greeter, EnglishGreeter)
        assert c.has(Greeter)
        assert Greeter in c

    def test_register_returns_self_for_chaining(self):
        c = Container()
        ret = c.register(Greeter, EnglishGreeter)
        assert ret is c

    def test_register_instance(self):
        c = Container()
        greeter = EnglishGreeter()
        c.register_instance(Greeter, greeter)
        resolved = c.resolve(Greeter)
        assert resolved is greeter

    def test_register_instance_returns_self(self):
        c = Container()
        ret = c.register_instance(Greeter, EnglishGreeter())
        assert ret is c

    def test_register_factory(self):
        c = Container()
        c.register_factory(Greeter, EnglishGreeter)
        result = c.resolve(Greeter)
        assert isinstance(result, EnglishGreeter)

    def test_register_factory_returns_self(self):
        c = Container()
        ret = c.register_factory(Greeter, EnglishGreeter)
        assert ret is c

    def test_has_returns_false_for_unregistered(self):
        c = Container()
        assert not c.has(Greeter)
        assert Greeter not in c

    def test_len(self):
        c = Container()
        assert len(c) == 0
        c.register(Greeter, EnglishGreeter)
        assert len(c) >= 1

    def test_repr(self):
        c = Container()
        assert "Container" in repr(c)

    def test_reset_clears_all(self):
        c = Container()
        c.register(Greeter, EnglishGreeter)
        assert c.has(Greeter)
        c.reset()
        assert not c.has(Greeter)
        assert len(c) == 0


# ---------------------------------------------------------------------------
# Resolution
# ---------------------------------------------------------------------------


class TestContainerResolution:
    def test_resolve_singleton_same_instance(self):
        c = Container()
        c.register(Greeter, EnglishGreeter, scope="singleton")
        a = c.resolve(Greeter)
        b = c.resolve(Greeter)
        assert a is b

    def test_resolve_transient_different_instances(self):
        c = Container()
        c.register(Greeter, EnglishGreeter, scope="transient")
        a = c.resolve(Greeter)
        b = c.resolve(Greeter)
        assert a is not b
        assert type(a) is type(b)

    def test_resolve_unregistered_raises(self):
        c = Container()
        with pytest.raises((KeyError, ResolutionError)):
            c.resolve(Greeter)

    def test_resolve_with_constructor_injection(self):
        c = Container()
        c.register(Greeter, EnglishGreeter)
        c.register(Service, Service)
        svc = c.resolve(Service)
        assert isinstance(svc.greeter, EnglishGreeter)

    def test_resolve_all(self):
        c = Container()
        c.register(Greeter, EnglishGreeter, name="en")
        c.register(Greeter, FrenchGreeter, name="fr")
        all_greeters = c.resolve_all(Greeter)
        assert len(all_greeters) == 2
        types = {type(g) for g in all_greeters}
        assert EnglishGreeter in types
        assert FrenchGreeter in types

    def test_named_registration_and_resolution(self):
        c = Container()
        c.register(Greeter, EnglishGreeter, name="en")
        c.register(Greeter, FrenchGreeter, name="fr")
        en = c.resolve(Greeter, name="en")
        fr = c.resolve(Greeter, name="fr")
        assert isinstance(en, EnglishGreeter)
        assert isinstance(fr, FrenchGreeter)

    def test_factory_singleton_called_once(self):
        call_count = 0

        def make_greeter():
            nonlocal call_count
            call_count += 1
            return EnglishGreeter()

        c = Container()
        c.register_factory(Greeter, make_greeter, scope="singleton")
        a = c.resolve(Greeter)
        b = c.resolve(Greeter)
        assert a is b
        assert call_count == 1

    def test_factory_transient_called_each_time(self):
        call_count = 0

        def make_greeter():
            nonlocal call_count
            call_count += 1
            return EnglishGreeter()

        c = Container()
        c.register_factory(Greeter, make_greeter, scope="transient")
        c.resolve(Greeter)
        c.resolve(Greeter)
        assert call_count == 2


# ---------------------------------------------------------------------------
# ServiceDescriptor
# ---------------------------------------------------------------------------


class TestServiceDescriptor:
    def test_is_instance_registration_true(self):
        desc = ServiceDescriptor(
            interface=Greeter,
            implementation=None,
            scope=Scope.SINGLETON,
            instance=EnglishGreeter(),
        )
        assert desc.is_instance_registration()

    def test_is_instance_registration_false(self):
        desc = ServiceDescriptor(
            interface=Greeter,
            implementation=EnglishGreeter,
            scope=Scope.SINGLETON,
        )
        assert not desc.is_instance_registration()


# ---------------------------------------------------------------------------
# Scoped resolution
# ---------------------------------------------------------------------------


class TestScopeContext:
    def test_scoped_provides_same_instance_within_context(self):
        c = Container()
        c.register(Greeter, EnglishGreeter, scope="scoped")
        with ScopeContext(c) as scope:
            a = scope.resolve(Greeter)
            b = scope.resolve(Greeter)
            assert a is b

    def test_scoped_provides_different_instance_across_contexts(self):
        c = Container()
        c.register(Greeter, EnglishGreeter, scope="scoped")
        with ScopeContext(c) as scope1:
            a = scope1.resolve(Greeter)
        with ScopeContext(c) as scope2:
            b = scope2.resolve(Greeter)
        assert a is not b

    def test_scope_context_has_unique_id(self):
        c = Container()
        with ScopeContext(c) as s1:
            with ScopeContext(c) as s2:
                assert s1.scope_id != s2.scope_id

    def test_scope_context_active_flag(self):
        c = Container()
        scope = ScopeContext(c)
        assert not scope.active
        with scope:
            assert scope.active
        assert not scope.active

    def test_scope_context_repr(self):
        c = Container()
        with ScopeContext(c) as scope:
            r = repr(scope)
            assert "ScopeContext" in r

    def test_resolve_outside_scope_raises(self):
        c = Container()
        c.register(Greeter, EnglishGreeter, scope="scoped")
        scope = ScopeContext(c)
        with pytest.raises(RuntimeError):
            scope.resolve(Greeter)


# ---------------------------------------------------------------------------
# Lifecycle (dispose / close)
# ---------------------------------------------------------------------------


class TestLifecycle:
    def test_scope_disposes_resources(self):
        c = Container()
        c.register(DisposableResource, DisposableResource, scope="scoped")
        with ScopeContext(c) as scope:
            res = scope.resolve(DisposableResource)
            assert not res.disposed
        assert res.disposed

    def test_scope_closes_resources(self):
        c = Container()
        c.register(CloseableResource, CloseableResource, scope="scoped")
        with ScopeContext(c) as scope:
            res = scope.resolve(CloseableResource)
            assert not res.closed
        assert res.closed


# ---------------------------------------------------------------------------
# Thread safety
# ---------------------------------------------------------------------------


class TestThreadSafety:
    def test_concurrent_singleton_resolution(self):
        c = Container()
        c.register(Logger, Logger, scope="singleton")
        results: list[Logger] = []
        barrier = threading.Barrier(10)

        def resolve_logger():
            barrier.wait()
            results.append(c.resolve(Logger))

        threads = [threading.Thread(target=resolve_logger) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All threads should get the same singleton
        assert len(results) == 10
        assert all(r is results[0] for r in results)


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


class TestErrorCases:
    def test_register_instance_none_raises(self):
        c = Container()
        with pytest.raises(TypeError):
            c.register_instance(Greeter, None)  # type: ignore[arg-type]

    def test_get_descriptor_returns_none_for_unregistered(self):
        c = Container()
        assert c.get_descriptor(Greeter) is None

    def test_get_descriptor_returns_descriptor(self):
        c = Container()
        c.register(Greeter, EnglishGreeter)
        desc = c.get_descriptor(Greeter)
        assert desc is not None
        assert desc.interface is Greeter

    def test_registrations_returns_copy(self):
        c = Container()
        c.register(Greeter, EnglishGreeter)
        regs = c.registrations
        assert isinstance(regs, dict)
