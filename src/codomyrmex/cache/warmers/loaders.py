"""Value loaders: callable and batch-capable."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Generic, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class ValueLoader(ABC, Generic[K, V]):
    """Base class for loading values during cache warming."""

    @abstractmethod
    def load(self, key: K) -> V:
        """Load a value for a given key."""


class CallableValueLoader(ValueLoader[K, V]):
    """Load each value individually via a callable."""

    def __init__(self, func: Callable[[K], V]):
        self._func = func

    def load(self, key: K) -> V:
        return self._func(key)


class BatchValueLoader(ValueLoader[K, V]):
    """
    Load values in batches for efficiency.

    The batch function accepts a list of keys and returns a dict mapping keys to values.
    """

    def __init__(self, batch_func: Callable[[list[K]], dict[K, V]]):
        self._batch_func = batch_func
        self._cache: dict[K, V] = {}

    def load_batch(self, keys: list[K]) -> dict[K, V]:
        """Load a batch of values and cache locally."""
        result = self._batch_func(keys)
        self._cache.update(result)
        return result

    def load(self, key: K) -> V:
        """Load a single value, using local cache if available."""
        if key in self._cache:
            return self._cache[key]
        result = self._batch_func([key])
        return result.get(key)  # type: ignore
