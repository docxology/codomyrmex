"""
Unit tests for the codomyrmex.dependency_injection module.

Tests cover the Container, Scope, ScopeContext, ServiceDescriptor,
decorators (@injectable, @inject), exceptions, and introspection functions.
"""

import threading

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
        """Test functionality: scope singleton value."""
        assert Scope.SINGLETON.value == "singleton"

    def test_scope_transient_value(self):
        """Test functionality: scope transient value."""
        assert Scope.TRANSIENT.value == "transient"

    def test_scope_scoped_value(self):
        """Test functionality: scope scoped value."""
        assert Scope.SCOPED.value == "scoped"

    def test_scope_from_string_singleton(self):
        """Test functionality: scope from string singleton."""
        assert Scope.from_string("singleton") is Scope.SINGLETON

    def test_scope_from_string_transient(self):
        """Test functionality: scope from string transient."""
        assert Scope.from_string("transient") is Scope.TRANSIENT

    def test_scope_from_string_scoped(self):
        """Test functionality: scope from string scoped."""
        assert Scope.from_string("scoped") is Scope.SCOPED

    def test_scope_from_string_case_insensitive(self):
        """Test functionality: scope from string case insensitive."""
        assert Scope.from_string("SINGLETON") is Scope.SINGLETON
        assert Scope.from_string("Transient") is Scope.TRANSIENT

    def test_scope_from_string_invalid_raises(self):
        """Test functionality: scope from string invalid raises."""
        with pytest.raises(ValueError, match="Invalid scope"):
            Scope.from_string("invalid_scope")


# ---------------------------------------------------------------------------
# Container registration and resolution tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContainerRegistration:
    """Tests for Container registration methods."""

    def test_register_and_resolve_singleton(self, container: Container):
        """Test functionality: register and resolve singleton."""
        container.register(IService, ConcreteService, scope="singleton")
        instance_a = container.resolve(IService)
        instance_b = container.resolve(IService)
        assert isinstance(instance_a, ConcreteService)
        assert instance_a is instance_b

    def test_register_and_resolve_transient(self, container: Container):
        """Test functionality: register and resolve transient."""
        container.register(IService, ConcreteService, scope="transient")
        instance_a = container.resolve(IService)
        instance_b = container.resolve(IService)
        assert isinstance(instance_a, ConcreteService)
        assert isinstance(instance_b, ConcreteService)
        assert instance_a is not instance_b

    def test_register_returns_container_for_chaining(self, container: Container):
        """Test functionality: register returns container for chaining."""
        result = container.register(IService, ConcreteService)
        assert result is container

    def test_register_raises_type_error_for_non_class(self, container: Container):
        """Test functionality: register raises type error for non class."""
        with pytest.raises(TypeError, match="Expected a class"):
            container.register(IService, "not_a_class")  # type: ignore[arg-type]

    def test_register_raises_value_error_for_invalid_scope(self, container: Container):
        """Test functionality: register raises value error for invalid scope."""
        with pytest.raises(ValueError, match="Invalid scope"):
            container.register(IService, ConcreteService, scope="bad_scope")


@pytest.mark.unit
class TestContainerRegisterInstance:
    """Tests for Container.register_instance."""

    def test_register_instance_returns_same_object(self, container: Container):
        """Test functionality: register instance returns same object."""
        obj = ConcreteService()
        container.register_instance(IService, obj)
        resolved = container.resolve(IService)
        assert resolved is obj

    def test_register_instance_returns_container_for_chaining(self, container: Container):
        """Test functionality: register instance returns container for chaining."""
        result = container.register_instance(IService, ConcreteService())
        assert result is container

    def test_register_instance_raises_on_none(self, container: Container):
        """Test functionality: register instance raises on none."""
        with pytest.raises(TypeError, match="Cannot register None"):
            container.register_instance(IService, None)  # type: ignore[arg-type]

    def test_register_instance_descriptor_is_instance_registration(self, container: Container):
        """Test functionality: register instance descriptor is instance registration."""
        obj = ConcreteService()
        container.register_instance(IService, obj)
        descriptor = container.get_descriptor(IService)
        assert descriptor is not None
        assert descriptor.is_instance_registration() is True


@pytest.mark.unit
class TestContainerRegisterFactory:
    """Tests for Container.register_factory."""

    def test_register_factory_singleton(self, container: Container):
        """Test functionality: register factory singleton."""
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
        """Test functionality: register factory transient."""
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
        """Test functionality: register factory returns container for chaining."""
        result = container.register_factory(IService, ConcreteService)
        assert result is container


# ---------------------------------------------------------------------------
# Container query tests
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestContainerQuery:
    """Tests for Container query methods: has, get_descriptor, registrations."""

    def test_has_returns_true_for_registered(self, container: Container):
        """Test functionality: has returns true for registered."""
        container.register(IService, ConcreteService)
        assert container.has(IService) is True

    def test_has_returns_false_for_unregistered(self, container: Container):
        """Test functionality: has returns false for unregistered."""
        assert container.has(IService) is False

    def test_contains_dunder(self, container: Container):
        """Test functionality: contains dunder."""
        container.register(IService, ConcreteService)
        assert IService in container
        assert AnotherService not in container

    def test_get_descriptor_returns_descriptor(self, container: Container):
        """Test functionality: get descriptor returns descriptor."""
        container.register(IService, ConcreteService, scope="transient")
        descriptor = container.get_descriptor(IService)
        assert isinstance(descriptor, ServiceDescriptor)
        assert descriptor.interface is IService
        assert descriptor.implementation is ConcreteService
        assert descriptor.scope is Scope.TRANSIENT

    def test_get_descriptor_returns_none_for_missing(self, container: Container):
        """Test functionality: get descriptor returns none for missing."""
        assert container.get_descriptor(IService) is None

    def test_registrations_returns_dict_copy(self, container: Container):
        """Test functionality: registrations returns dict copy."""
        container.register(IService, ConcreteService)
        regs = container.registrations
        assert isinstance(regs, dict)
        assert IService in regs
        # Mutating the copy does not affect the container
        regs.clear()
        assert container.has(IService) is True

    def test_len_dunder(self, container: Container):
        """Test functionality: len dunder."""
        assert len(container) == 0
        container.register(IService, ConcreteService)
        assert len(container) == 1

    def test_repr(self, container: Container):
        """Test functionality: repr."""
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
        """Test functionality: reset clears all registrations."""
        container.register(IService, ConcreteService)
        container.register(AnotherService, AnotherService)
        assert len(container) == 2
        container.reset()
        assert len(container) == 0
        assert container.has(IService) is False

    def test_reset_clears_cached_singleton_instances(self, container: Container):
        """Test functionality: reset clears cached singleton instances."""
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
        """Test functionality: resolve unregistered raises key error."""
        with pytest.raises(KeyError, match="No registration found"):
            container.resolve(IService)

    def test_resolution_error_is_exception(self):
        """Test functionality: resolution error is exception."""
        assert issubclass(ResolutionError, Exception)

    def test_circular_dependency_error_inherits_resolution_error(self):
        """Test functionality: circular dependency error inherits resolution error."""
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
        """Test functionality: scoped returns same instance within context."""
        container.register(IService, ConcreteService, scope="scoped")
        with ScopeContext(container) as scope:
            a = scope.resolve(IService)
            b = scope.resolve(IService)
            assert a is b

    def test_scoped_returns_different_instance_across_contexts(self, container: Container):
        """Test functionality: scoped returns different instance across contexts."""
        container.register(IService, ConcreteService, scope="scoped")
        with ScopeContext(container) as scope1:
            a = scope1.resolve(IService)
        with ScopeContext(container) as scope2:
            b = scope2.resolve(IService)
        assert a is not b

    def test_scope_context_active_property(self, container: Container):
        """Test functionality: scope context active property."""
        ctx = ScopeContext(container)
        assert ctx.active is False
        with ctx:
            assert ctx.active is True
        assert ctx.active is False

    def test_scope_context_has_unique_id(self, container: Container):
        """Test functionality: scope context has unique id."""
        ctx1 = ScopeContext(container)
        ctx2 = ScopeContext(container)
        assert ctx1.scope_id != ctx2.scope_id

    def test_resolve_scoped_without_context_raises(self, container: Container):
        """Test functionality: resolve scoped without context raises."""
        container.register(IService, ConcreteService, scope="scoped")
        with pytest.raises(ResolutionError, match="without an active ScopeContext"):
            container.resolve(IService)

    def test_resolve_from_inactive_scope_raises(self, container: Container):
        """Test functionality: resolve from inactive scope raises."""
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
        """Test functionality: scope context repr."""
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
        """Test functionality: default values."""
        desc = ServiceDescriptor(interface=IService)
        assert desc.interface is IService
        assert desc.implementation is None
        assert desc.scope is Scope.SINGLETON
        assert desc.instance is None
        assert desc.factory is None

    def test_is_instance_registration_true(self):
        """Test functionality: is instance registration true."""
        desc = ServiceDescriptor(
            interface=IService,
            implementation=None,
            instance=ConcreteService(),
            factory=None,
        )
        assert desc.is_instance_registration() is True

    def test_is_instance_registration_false_with_implementation(self):
        """Test functionality: is instance registration false with implementation."""
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
        """Test functionality: injectable sets metadata."""
        @injectable(scope="transient")
        class MyService:
            pass

        assert is_injectable(MyService) is True
        meta = get_injectable_metadata(MyService)
        assert meta is not None
        assert meta.scope == "transient"
        assert meta.auto_register is True

    def test_injectable_default_scope_is_singleton(self):
        """Test functionality: injectable default scope is singleton."""
        @injectable()
        class MyService:
            pass

        meta = get_injectable_metadata(MyService)
        assert meta is not None
        assert meta.scope == "singleton"

    def test_injectable_with_tags(self):
        """Test functionality: injectable with tags."""
        @injectable(scope="scoped", tags=("db", "core"))
        class MyService:
            pass

        meta = get_injectable_metadata(MyService)
        assert meta is not None
        assert meta.tags == ("db", "core")

    def test_is_injectable_returns_false_for_plain_class(self):
        """Test functionality: is injectable returns false for plain class."""
        class Plain:
            pass

        assert is_injectable(Plain) is False


@pytest.mark.unit
class TestInjectDecorator:
    """Tests for the @inject decorator."""

    def test_inject_sets_metadata(self):
        """Test functionality: inject sets metadata."""
        class MyService:
            @inject
            def __init__(self, dep: IService):
                self.dep = dep

        meta = get_inject_metadata(MyService.__init__)
        assert meta is not None
        assert meta.resolve_all is True

    def test_inject_precomputes_params(self):
        """Test functionality: inject precomputes params."""
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
        """Test functionality: inject excludes self param."""
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
        """Test functionality: get injectable metadata returns none for undecorated."""
        class Plain:
            pass

        assert get_injectable_metadata(Plain) is None

    def test_get_inject_metadata_returns_none_for_undecorated(self):
        """Test functionality: get inject metadata returns none for undecorated."""
        def plain_func():
            pass

        assert get_inject_metadata(plain_func) is None

    def test_get_injectable_params_returns_empty_for_undecorated(self):
        """Test functionality: get injectable params returns empty for undecorated."""
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
        """Test functionality: auto resolve constructor deps."""
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
        """Test functionality: constructor with no hints creates plain instance."""
        class Simple:
            def __init__(self):
                self.ready = True

        container.register(Simple, Simple, scope="transient")
        instance = container.resolve(Simple)
        assert instance.ready is True
