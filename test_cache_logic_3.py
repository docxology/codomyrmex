import time
from typing import Any
from src.codomyrmex.cache.backends.in_memory import InMemoryCache

class FastInMemoryCache(InMemoryCache):
    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        if key in self._cache:
            del self._cache[key]
        elif len(self._cache) >= self.max_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]

        ttl = ttl or self.default_ttl
        self._cache[key] = (value, time.time(), ttl)
        self._stats.size = len(self._cache)
        return True

def test_cache_perf():
    cache = FastInMemoryCache(max_size=3)

    cache.set("a", 1)
    cache.set("b", 2)
    cache.set("c", 3)

    print("Keys before get:", list(cache._cache.keys()))

    cache.set("d", 4)
    print("Keys after setting d:", list(cache._cache.keys()))

    cache2 = FastInMemoryCache(max_size=10000)
    for i in range(10000):
        cache2.set(f"key{i}", i)

    start = time.time()
    for i in range(10000, 11000):
        cache2.set(f"key{i}", i)
    end = time.time()
    print(f"Time to set 1000 items with full cache (fast O(1)): {end - start:.4f}s")

if __name__ == "__main__":
    test_cache_perf()
