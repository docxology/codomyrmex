"""
Unit tests for the codomyrmex.dependency_injection module.

Tests cover the Container, Scope, ScopeContext, ServiceDescriptor,
decorators (@injectable, @inject), exceptions, and introspection functions.
"""

import sys
import threading
from typing import Optional

import pytest

from codomyrmex.dependency_injection import (
    CircularDependencyError,
    Container,
    ResolutionError,
    Scope,
    ScopeContext,
    ServiceDescriptor,
    get_inject_metadata,
    get_injectable_metadata,
    get_injectable_params,
    inject,
    injectable,
    is_injectable,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


class IService:
    """Abstract interface for testing."""

    pass


class ConcreteService(IService):
    """Concrete implementation for testing."""

    def __init__(self):
        self.value = 42


class AnotherService:
    """Another concrete service for testing."""

    pass


@pytest.fixture
def container() -> Container:
    """Provide a fresh Container for each test."""
    return Container()


# ---------------------------------------------------------------------------
# Scope enum tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestScope:
    """Tests for the Scope enum."""

    def test_scope_singleton_value(self):
        """Verify scope singleton value behavior."""
        assert Scope.SINGLETON.value == "singleton"

    def test_scope_transient_value(self):
        """Verify scope transient value behavior."""
        assert Scope.TRANSIENT.value == "transient"

    def test_scope_scoped_value(self):
        """Verify scope scoped value behavior."""
        assert Scope.SCOPED.value == "scoped"

    def test_scope_from_string_singleton(self):
        """Verify scope from string singleton behavior."""
        assert Scope.from_string("singleton") is Scope.SINGLETON

    def test_scope_from_string_transient(self):
        """Verify scope from string transient behavior."""
        assert Scope.from_string("transient") is Scope.TRANSIENT

    def test_scope_from_string_scoped(self):
        """Verify scope from string scoped behavior."""
        assert Scope.from_string("scoped") is Scope.SCOPED

    def test_scope_from_string_case_insensitive(self):
        """Verify scope from string case insensitive behavior."""
        assert Scope.from_string("SINGLETON") is Scope.SINGLETON
        assert Scope.from_string("Transient") is Scope.TRANSIENT

    def test_scope_from_string_invalid_raises(self):
        """Verify scope from string invalid raises behavior."""
        with pytest.raises(ValueError, match="Invalid scope"):
            Scope.from_string("invalid_scope")


# ---------------------------------------------------------------------------
# Container registration and resolution tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContainerRegistration:
    """Tests for Container registration methods."""

    def test_register_and_resolve_singleton(self, container: Container):
        """Verify register and resolve singleton behavior."""
        container.register(IService, ConcreteService, scope="singleton")
        instance_a = container.resolve(IService)
        instance_b = container.resolve(IService)
        assert isinstance(instance_a, ConcreteService)
        assert instance_a is instance_b

    def test_register_and_resolve_transient(self, container: Container):
        """Verify register and resolve transient behavior."""
        container.register(IService, ConcreteService, scope="transient")
        instance_a = container.resolve(IService)
        instance_b = container.resolve(IService)
        assert isinstance(instance_a, ConcreteService)
        assert isinstance(instance_b, ConcreteService)
        assert instance_a is not instance_b

    def test_register_returns_container_for_chaining(self, container: Container):
        """Verify register returns container for chaining behavior."""
        result = container.register(IService, ConcreteService)
        assert result is container

    def test_register_raises_type_error_for_non_class(self, container: Container):
        """Verify register raises type error for non class behavior."""
        with pytest.raises(TypeError, match="Expected a class"):
            container.register(IService, "not_a_class")  # type: ignore[arg-type]

    def test_register_raises_value_error_for_invalid_scope(self, container: Container):
        """Verify register raises value error for invalid scope behavior."""
        with pytest.raises(ValueError, match="Invalid scope"):
            container.register(IService, ConcreteService, scope="bad_scope")


@pytest.mark.unit
class TestContainerRegisterInstance:
    """Tests for Container.register_instance."""

    def test_register_instance_returns_same_object(self, container: Container):
        """Verify register instance returns same object behavior."""
        obj = ConcreteService()
        container.register_instance(IService, obj)
        resolved = container.resolve(IService)
        assert resolved is obj

    def test_register_instance_returns_container_for_chaining(self, container: Container):
        """Verify register instance returns container for chaining behavior."""
        result = container.register_instance(IService, ConcreteService())
        assert result is container

    def test_register_instance_raises_on_none(self, container: Container):
        """Verify register instance raises on none behavior."""
        with pytest.raises(TypeError, match="Cannot register None"):
            container.register_instance(IService, None)  # type: ignore[arg-type]

    def test_register_instance_descriptor_is_instance_registration(self, container: Container):
        """Verify register instance descriptor is instance registration behavior."""
        obj = ConcreteService()
        container.register_instance(IService, obj)
        descriptor = container.get_descriptor(IService)
        assert descriptor is not None
        assert descriptor.is_instance_registration() is True


@pytest.mark.unit
class TestContainerRegisterFactory:
    """Tests for Container.register_factory."""

    def test_register_factory_singleton(self, container: Container):
        """Verify register factory singleton behavior."""
        call_count = 0

        def factory():
            nonlocal call_count
            call_count += 1
            return ConcreteService()

        container.register_factory(IService, factory, scope="singleton")
        instance_a = container.resolve(IService)
        instance_b = container.resolve(IService)
        assert isinstance(instance_a, ConcreteService)
        assert instance_a is instance_b
        assert call_count == 1

    def test_register_factory_transient(self, container: Container):
        """Verify register factory transient behavior."""
        call_count = 0

        def factory():
            nonlocal call_count
            call_count += 1
            return ConcreteService()

        container.register_factory(IService, factory, scope="transient")
        instance_a = container.resolve(IService)
        instance_b = container.resolve(IService)
        assert instance_a is not instance_b
        assert call_count == 2

    def test_register_factory_returns_container_for_chaining(self, container: Container):
        """Verify register factory returns container for chaining behavior."""
        result = container.register_factory(IService, ConcreteService)
        assert result is container


# ---------------------------------------------------------------------------
# Container query tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContainerQuery:
    """Tests for Container query methods: has, get_descriptor, registrations."""

    def test_has_returns_true_for_registered(self, container: Container):
        """Verify has returns true for registered behavior."""
        container.register(IService, ConcreteService)
        assert container.has(IService) is True

    def test_has_returns_false_for_unregistered(self, container: Container):
        """Verify has returns false for unregistered behavior."""
        assert container.has(IService) is False

    def test_contains_dunder(self, container: Container):
        """Verify contains dunder behavior."""
        container.register(IService, ConcreteService)
        assert IService in container
        assert AnotherService not in container

    def test_get_descriptor_returns_descriptor(self, container: Container):
        """Verify get descriptor returns descriptor behavior."""
        container.register(IService, ConcreteService, scope="transient")
        descriptor = container.get_descriptor(IService)
        assert isinstance(descriptor, ServiceDescriptor)
        assert descriptor.interface is IService
        assert descriptor.implementation is ConcreteService
        assert descriptor.scope is Scope.TRANSIENT

    def test_get_descriptor_returns_none_for_missing(self, container: Container):
        """Verify get descriptor returns none for missing behavior."""
        assert container.get_descriptor(IService) is None

    def test_registrations_returns_dict_copy(self, container: Container):
        """Verify registrations returns dict copy behavior."""
        container.register(IService, ConcreteService)
        regs = container.registrations
        assert isinstance(regs, dict)
        assert IService in regs
        # Mutating the copy does not affect the container
        regs.clear()
        assert container.has(IService) is True

    def test_len_dunder(self, container: Container):
        """Verify len dunder behavior."""
        assert len(container) == 0
        container.register(IService, ConcreteService)
        assert len(container) == 1

    def test_repr(self, container: Container):
        """Verify repr behavior."""
        container.register(IService, ConcreteService)
        r = repr(container)
        assert "Container" in r
        assert "registrations=1" in r


# ---------------------------------------------------------------------------
# Container reset tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContainerReset:
    """Tests for Container.reset."""

    def test_reset_clears_all_registrations(self, container: Container):
        """Verify reset clears all registrations behavior."""
        container.register(IService, ConcreteService)
        container.register(AnotherService, AnotherService)
        assert len(container) == 2
        container.reset()
        assert len(container) == 0
        assert container.has(IService) is False

    def test_reset_clears_cached_singleton_instances(self, container: Container):
        """Verify reset clears cached singleton instances behavior."""
        container.register(IService, ConcreteService, scope="singleton")
        first = container.resolve(IService)
        container.reset()
        container.register(IService, ConcreteService, scope="singleton")
        second = container.resolve(IService)
        assert first is not second


# ---------------------------------------------------------------------------
# Resolution error tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestResolutionErrors:
    """Tests for resolution errors."""

    def test_resolve_unregistered_raises_key_error(self, container: Container):
        """Verify resolve unregistered raises key error behavior."""
        with pytest.raises(KeyError, match="No registration found"):
            container.resolve(IService)

    def test_resolution_error_is_exception(self):
        """Verify resolution error is exception behavior."""
        assert issubclass(ResolutionError, Exception)

    def test_circular_dependency_error_inherits_resolution_error(self):
        """Verify circular dependency error inherits resolution error behavior."""
        assert issubclass(CircularDependencyError, ResolutionError)

    def test_circular_dependency_detected(self, container: Container):
        """A self-referencing type triggers circular dependency detection."""

        class SelfRef:
            def __init__(self, other: "SelfRef"):
                self.other = other

        # Patch the annotation to reference the actual class (not the string).
        SelfRef.__init__.__annotations__["other"] = SelfRef

        container.register(SelfRef, SelfRef, scope="transient")

        with pytest.raises(CircularDependencyError, match="Circular dependency"):
            container.resolve(SelfRef)


# ---------------------------------------------------------------------------
# ScopeContext tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestScopeContext:
    """Tests for ScopeContext lifecycle and scoped resolution."""

    def test_scoped_returns_same_instance_within_context(self, container: Container):
        """Verify scoped returns same instance within context behavior."""
        container.register(IService, ConcreteService, scope="scoped")
        with ScopeContext(container) as scope:
            a = scope.resolve(IService)
            b = scope.resolve(IService)
            assert a is b

    def test_scoped_returns_different_instance_across_contexts(self, container: Container):
        """Verify scoped returns different instance across contexts behavior."""
        container.register(IService, ConcreteService, scope="scoped")
        with ScopeContext(container) as scope1:
            a = scope1.resolve(IService)
        with ScopeContext(container) as scope2:
            b = scope2.resolve(IService)
        assert a is not b

    def test_scope_context_active_property(self, container: Container):
        """Verify scope context active property behavior."""
        ctx = ScopeContext(container)
        assert ctx.active is False
        with ctx:
            assert ctx.active is True
        assert ctx.active is False

    def test_scope_context_has_unique_id(self, container: Container):
        """Verify scope context has unique id behavior."""
        ctx1 = ScopeContext(container)
        ctx2 = ScopeContext(container)
        assert ctx1.scope_id != ctx2.scope_id

    def test_resolve_scoped_without_context_raises(self, container: Container):
        """Verify resolve scoped without context raises behavior."""
        container.register(IService, ConcreteService, scope="scoped")
        with pytest.raises(ResolutionError, match="without an active ScopeContext"):
            container.resolve(IService)

    def test_resolve_from_inactive_scope_raises(self, container: Container):
        """Verify resolve from inactive scope raises behavior."""
        ctx = ScopeContext(container)
        with pytest.raises(RuntimeError, match="inactive ScopeContext"):
            ctx.resolve(IService)

    def test_scope_context_dispose_calls_close(self, container: Container):
        """Verify that ScopeContext._dispose calls close() on cached instances."""
        closed = []

        class Closeable:
            def close(self):
                closed.append(True)

        container.register(Closeable, Closeable, scope="scoped")
        with ScopeContext(container) as scope:
            scope.resolve(Closeable)
        assert len(closed) == 1

    def test_scope_context_repr(self, container: Container):
        """Verify scope context repr behavior."""
        ctx = ScopeContext(container)
        r = repr(ctx)
        assert "ScopeContext" in r
        assert "active=False" in r


# ---------------------------------------------------------------------------
# ServiceDescriptor tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestServiceDescriptor:
    """Tests for the ServiceDescriptor dataclass."""

    def test_default_values(self):
        """Verify default values behavior."""
        desc = ServiceDescriptor(interface=IService)
        assert desc.interface is IService
        assert desc.implementation is None
        assert desc.scope is Scope.SINGLETON
        assert desc.instance is None
        assert desc.factory is None

    def test_is_instance_registration_true(self):
        """Verify is instance registration true behavior."""
        desc = ServiceDescriptor(
            interface=IService,
            implementation=None,
            instance=ConcreteService(),
            factory=None,
        )
        assert desc.is_instance_registration() is True

    def test_is_instance_registration_false_with_implementation(self):
        """Verify is instance registration false with implementation behavior."""
        desc = ServiceDescriptor(
            interface=IService,
            implementation=ConcreteService,
            instance=ConcreteService(),
        )
        assert desc.is_instance_registration() is False


# ---------------------------------------------------------------------------
# Decorator tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestInjectableDecorator:
    """Tests for the @injectable decorator."""

    def test_injectable_sets_metadata(self):
        """Verify injectable sets metadata behavior."""
        @injectable(scope="transient")
        class MyService:
            pass

        assert is_injectable(MyService) is True
        meta = get_injectable_metadata(MyService)
        assert meta is not None
        assert meta.scope == "transient"
        assert meta.auto_register is True

    def test_injectable_default_scope_is_singleton(self):
        """Verify injectable default scope is singleton behavior."""
        @injectable()
        class MyService:
            pass

        meta = get_injectable_metadata(MyService)
        assert meta is not None
        assert meta.scope == "singleton"

    def test_injectable_with_tags(self):
        """Verify injectable with tags behavior."""
        @injectable(scope="scoped", tags=("db", "core"))
        class MyService:
            pass

        meta = get_injectable_metadata(MyService)
        assert meta is not None
        assert meta.tags == ("db", "core")

    def test_is_injectable_returns_false_for_plain_class(self):
        """Verify is injectable returns false for plain class behavior."""
        class Plain:
            pass

        assert is_injectable(Plain) is False


@pytest.mark.unit
class TestInjectDecorator:
    """Tests for the @inject decorator."""

    def test_inject_sets_metadata(self):
        """Verify inject sets metadata behavior."""
        class MyService:
            @inject
            def __init__(self, dep: IService):
                self.dep = dep

        meta = get_inject_metadata(MyService.__init__)
        assert meta is not None
        assert meta.resolve_all is True

    def test_inject_precomputes_params(self):
        """Verify inject precomputes params behavior."""
        class MyService:
            @inject
            def __init__(self, dep: IService, other: AnotherService):
                self.dep = dep
                self.other = other

        params = get_injectable_params(MyService.__init__)
        assert "dep" in params
        assert params["dep"] is IService
        assert "other" in params
        assert params["other"] is AnotherService

    def test_inject_excludes_self_param(self):
        """Verify inject excludes self param behavior."""
        class MyService:
            @inject
            def __init__(self, dep: IService):
                pass

        params = get_injectable_params(MyService.__init__)
        assert "self" not in params

    def test_inject_decorator_auto_resolves_in_container(self, container: Container):
        """End-to-end: @inject causes the container to resolve constructor deps."""

        class Config:
            def __init__(self):
                self.value = "production"

        class App:
            @inject
            def __init__(self, config: Config):
                self.config = config

        container.register(Config, Config, scope="singleton")
        container.register(App, App, scope="transient")

        app = container.resolve(App)
        assert isinstance(app.config, Config)
        assert app.config.value == "production"


# ---------------------------------------------------------------------------
# Introspection function tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestIntrospectionFunctions:
    """Tests for get_injectable_metadata, get_inject_metadata, get_injectable_params."""

    def test_get_injectable_metadata_returns_none_for_undecorated(self):
        """Verify get injectable metadata returns none for undecorated behavior."""
        class Plain:
            pass

        assert get_injectable_metadata(Plain) is None

    def test_get_inject_metadata_returns_none_for_undecorated(self):
        """Verify get inject metadata returns none for undecorated behavior."""
        def plain_func():
            pass

        assert get_inject_metadata(plain_func) is None

    def test_get_injectable_params_returns_empty_for_undecorated(self):
        """Verify get injectable params returns empty for undecorated behavior."""
        def plain_func():
            pass

        assert get_injectable_params(plain_func) == {}


# ---------------------------------------------------------------------------
# Thread safety (basic) tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestThreadSafety:
    """Basic thread-safety tests for Container."""

    def test_concurrent_resolve_singleton(self, container: Container):
        """Multiple threads resolving a singleton should get the same instance."""
        container.register(IService, ConcreteService, scope="singleton")
        results: list = []
        errors: list = []

        def resolve_task():
            try:
                instance = container.resolve(IService)
                results.append(instance)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=resolve_task) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 10
        # All threads should have gotten the same singleton instance
        assert all(r is results[0] for r in results)

    def test_concurrent_register_and_resolve(self, container: Container):
        """Concurrent registration and resolution should not raise."""
        errors: list = []

        def register_task():
            try:
                container.register(AnotherService, AnotherService, scope="transient")
            except Exception as e:
                errors.append(e)

        def resolve_task():
            try:
                if container.has(AnotherService):
                    container.resolve(AnotherService)
            except Exception as e:
                errors.append(e)

        threads = []
        for _ in range(5):
            threads.append(threading.Thread(target=register_task))
            threads.append(threading.Thread(target=resolve_task))

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0


# ---------------------------------------------------------------------------
# Auto-resolution via type hints (no @inject) tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestAutoResolutionViaHints:
    """Test that the container resolves constructor deps via type hints even without @inject."""

    def test_auto_resolve_constructor_deps(self, container: Container):
        """Verify auto resolve constructor deps behavior."""
        class Logger:
            def __init__(self):
                self.name = "logger"

        class Worker:
            def __init__(self, logger: Logger):
                self.logger = logger

        container.register(Logger, Logger, scope="singleton")
        container.register(Worker, Worker, scope="transient")

        worker = container.resolve(Worker)
        assert isinstance(worker.logger, Logger)
        assert worker.logger.name == "logger"

    def test_constructor_with_no_hints_creates_plain_instance(self, container: Container):
        """Verify constructor with no hints creates plain instance behavior."""
        class Simple:
            def __init__(self):
                self.ready = True

        container.register(Simple, Simple, scope="transient")
        instance = container.resolve(Simple)
        assert instance.ready is True


# ---------------------------------------------------------------------------
# Advanced resolution features tests
# ---------------------------------------------------------------------------

@injectable(scope="singleton")
class GlobalAutoRegistered:
    pass


@pytest.mark.unit
class TestContainerAdvancedFeatures:
    """Tests for new advanced features: named, collection, and optional resolution."""

    def test_named_registration(self, container: Container):
        """Verify named registration and resolution behavior."""
        container.register(IService, ConcreteService, name="primary")

        class SecondaryService(IService):
            pass

        container.register(IService, SecondaryService, name="secondary")

        primary = container.resolve(IService, name="primary")
        secondary = container.resolve(IService, name="secondary")

        assert isinstance(primary, ConcreteService)
        assert isinstance(secondary, SecondaryService)

    def test_resolve_list(self, container: Container):
        """Verify resolve all implementations via List[T] behavior."""
        container.register(IService, ConcreteService)

        class AnotherImpl(IService):
            pass

        container.register(IService, AnotherImpl)

        services = container.resolve(list[IService])
        assert len(services) == 2
        assert any(isinstance(s, ConcreteService) for s in services)
        assert any(isinstance(s, AnotherImpl) for s in services)

    def test_resolve_optional(self, container: Container):
        """Verify resolve optional dependency via Optional[T] behavior."""
        # Not registered
        val = container.resolve(Optional[IService])  # noqa: UP045
        assert val is None

        # Registered
        container.register(IService, ConcreteService)
        val = container.resolve(Optional[IService])  # noqa: UP045
        assert isinstance(val, ConcreteService)

    def test_scan_auto_registration(self, container: Container):
        """Verify auto-scanning for @injectable classes behavior."""
        current_module = sys.modules[__name__]
        container.scan(current_module)

        assert container.has(GlobalAutoRegistered)
        assert isinstance(container.resolve(GlobalAutoRegistered), GlobalAutoRegistered)

    def test_circular_dependency_with_names(self, container: Container):
        """Verify circular dependency detection includes names in error behavior."""
        class A:
            def __init__(self, b: "B"):
                self.b = b

        class B:
            def __init__(self, a: A):
                self.a = a

        A.__init__.__annotations__['b'] = B
        B.__init__.__annotations__['a'] = A

        container.register(A, A, name="a_named")
        container.register(B, B, name="b_named")

        # Since auto-resolver doesn't know about names yet, we just trigger
        # a circular dependency by resolving one that depends on the other.
        # Here we manually simulate the chain if needed, or just let auto-resolve
        # (which uses default None name) fail if they were registered without names.

        # To actually use the names in auto-resolve, we'd need @inject(b='b_named')
        # For now, let's just verify circular detection works with the new key format.

        with pytest.raises(CircularDependencyError, match="a_named"):
            container.resolve(A, name="a_named")
