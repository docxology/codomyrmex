"""Key providers: static list and callable."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Generic, TypeVar

K = TypeVar("K")


class KeyProvider(ABC, Generic[K]):
    """Base class for providing keys to warm."""

    @abstractmethod
    def get_keys(self) -> list[K]:
        """Return list of keys to warm."""


class StaticKeyProvider(KeyProvider[K]):
    """Provide a fixed list of keys."""

    def __init__(self, keys: list[K]):
        self._keys = keys

    def get_keys(self) -> list[K]:
        return self._keys.copy()


class CallableKeyProvider(KeyProvider[K]):
    """Provide keys dynamically from a callable."""

    def __init__(self, func: Callable[[], list[K]]):
        self._func = func

    def get_keys(self) -> list[K]:
        return self._func()
