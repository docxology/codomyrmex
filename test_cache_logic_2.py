import time
from src.codomyrmex.cache.backends.in_memory import InMemoryCache

class FastInMemoryCache(InMemoryCache):
    def set(self, key: str, value: any, ttl: int | None = None) -> bool:
        if len(self._cache) >= self.max_size and key not in self._cache:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            self._stats.size -= 1

        if key in self._cache:
            del self._cache[key]

        ttl = ttl or self.default_ttl
        self._cache[key] = (value, time.time(), ttl)
        self._stats.size = len(self._cache)
        return True

def test_cache_perf():
    cache = FastInMemoryCache(max_size=3)

    cache.set("a", 1)
    time.sleep(0.01)
    cache.set("b", 2)
    time.sleep(0.01)
    cache.set("c", 3)
    time.sleep(0.01)

    print("Keys before update:", list(cache._cache.keys()))
    # a, b, c

    cache.set("a", 10) # update a
    time.sleep(0.01)

    # if we set d, max_size is 3, what gets evicted?
    # old logic: 'b' should get evicted, since 'a' was updated
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
