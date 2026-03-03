"""
Injection decorators for marking classes and parameters.

Provides @injectable and @inject decorators that store metadata
on classes for the Container to discover and use during resolution.

Usage:
    from codomyrmex.dependency_injection.decorators import injectable, inject

    @injectable(scope="singleton")
    class EmailService:
        @inject
        def __init__(self, smtp_client: SmtpClient, config: AppConfig):
            self.smtp_client = smtp_client
            self.config = config

The container reads the __injectable__ and __inject__ markers to
determine scope and which constructor parameters to auto-resolve.
"""

from __future__ import annotations

import functools
import inspect
from collections.abc import Callable
from typing import Any, TypeVar, get_type_hints

T = TypeVar("T")

# Attribute names used to store metadata on decorated classes/functions
INJECTABLE_ATTR = "__injectable__"
INJECT_ATTR = "__inject__"
INJECT_PARAMS_ATTR = "__inject_params__"


class InjectableMetadata:
    """Metadata attached to classes decorated with @injectable.

    Attributes:
        scope: The lifecycle scope string ("singleton", "transient", "scoped").
        auto_register: Whether the container should pick this up during scanning.
        tags: Optional tags for filtering during bulk registration.
    """

    __slots__ = ("scope", "auto_register", "tags")

    def __init__(
        self,
        scope: str = "singleton",
        auto_register: bool = True,
        tags: tuple | None = None,
    ) -> None:
        self.scope = scope
        self.auto_register = auto_register
        self.tags = tags or ()

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"InjectableMetadata(scope={self.scope!r}, "
            f"auto_register={self.auto_register}, tags={self.tags})"
        )


class InjectMetadata:
    """Metadata attached to __init__ methods decorated with @inject.

    Stores information about which parameters should be auto-resolved
    by the container and any explicit overrides.

    Attributes:
        params: Mapping of parameter name to injection configuration.
        resolve_all: If True, resolve all typed parameters (not just marked ones).
    """

    __slots__ = ("params", "resolve_all")

    def __init__(
        self,
        params: dict[str, Any] | None = None,
        resolve_all: bool = True,
    ) -> None:
        self.params = params or {}
        self.resolve_all = resolve_all

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"InjectMetadata(params={self.params}, "
            f"resolve_all={self.resolve_all})"
        )


def injectable(
    scope: str = "singleton",
    auto_register: bool = True,
    tags: tuple | None = None,
) -> Callable[[type[T]], type[T]]:
    """Decorator that marks a class as injectable with a given scope.

    This stores an InjectableMetadata instance on the class under the
    ``__injectable__`` attribute. The container reads this during
    registration or scanning.

    Args:
        scope: Lifecycle scope - "singleton", "transient", or "scoped".
        auto_register: Whether auto-scanning should pick up this class.
        tags: Optional tags for categorical filtering.

    Returns:
        The decorated class, unchanged except for the added metadata attribute.

    Example:
        @injectable(scope="transient")
        class RequestHandler:
            pass

        assert hasattr(RequestHandler, "__injectable__")
        assert RequestHandler.__injectable__.scope == "transient"
    """

    def decorator(cls: type[T]) -> type[T]:
        """Decorator."""
        metadata = InjectableMetadata(
            scope=scope,
            auto_register=auto_register,
            tags=tags,
        )
        setattr(cls, INJECTABLE_ATTR, metadata)
        return cls

    return decorator


def inject(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that marks a constructor (or any method) for auto-injection.

    When placed on ``__init__``, the container will inspect the method's
    type hints and automatically resolve parameters from registered services.

    The decorator stores an InjectMetadata instance under ``__inject__``
    on the function. It also resolves type hints eagerly where possible
    and stores them under ``__inject_params__``.

    Args:
        fn: The function (typically __init__) to mark for injection.

    Returns:
        The original function with injection metadata attached.

    Example:
        class UserService:
            @inject
            def __init__(self, repo: UserRepository, logger: Logger):
                self.repo = repo
                self.logger = logger

        assert hasattr(UserService.__init__, "__inject__")
    """
    metadata = InjectMetadata(resolve_all=True)
    setattr(fn, INJECT_ATTR, metadata)

    # Pre-compute injectable parameters from type hints
    try:
        hints = get_type_hints(fn)
    except Exception:
        hints = getattr(fn, "__annotations__", {})

    sig = inspect.signature(fn)
    injectable_params: dict[str, type] = {}

    for name, _param in sig.parameters.items():
        if name == "self":
            continue
        if name == "return":
            continue
        hint = hints.get(name)
        if hint is not None:
            injectable_params[name] = hint

    setattr(fn, INJECT_PARAMS_ATTR, injectable_params)

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """Wrapper."""
        return fn(*args, **kwargs)

    # Transfer metadata to wrapper
    setattr(wrapper, INJECT_ATTR, metadata)
    setattr(wrapper, INJECT_PARAMS_ATTR, injectable_params)

    return wrapper


def get_injectable_metadata(cls: type[Any]) -> InjectableMetadata | None:
    """Retrieve the InjectableMetadata from a class, if present.

    Args:
        cls: The class to inspect.

    Returns:
        InjectableMetadata if the class was decorated with @injectable,
        otherwise None.
    """
    return getattr(cls, INJECTABLE_ATTR, None)


def get_inject_metadata(fn: Callable[..., Any]) -> InjectMetadata | None:
    """Retrieve the InjectMetadata from a function, if present.

    Args:
        fn: The function to inspect.

    Returns:
        InjectMetadata if the function was decorated with @inject,
        otherwise None.
    """
    return getattr(fn, INJECT_ATTR, None)


def get_injectable_params(fn: Callable[..., Any]) -> dict[str, type]:
    """Retrieve the pre-computed injectable parameter hints from a function.

    Args:
        fn: The function to inspect.

    Returns:
        A dict mapping parameter names to their type hints.
        Empty dict if no @inject decorator was applied.
    """
    return getattr(fn, INJECT_PARAMS_ATTR, {})


def is_injectable(cls: type[Any]) -> bool:
    """Check whether a class has been marked with @injectable.

    Args:
        cls: The class to check.

    Returns:
        True if the class carries InjectableMetadata.
    """
    return hasattr(cls, INJECTABLE_ATTR)
