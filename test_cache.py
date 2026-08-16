import time
from src.codomyrmex.cache.backends.in_memory import InMemoryCache

def test_cache_perf():
    cache = InMemoryCache(max_size=10000)

    # Fill cache
    for i in range(10000):
        cache.set(f"key{i}", i)

    start = time.time()
    # Trigger evictions
    for i in range(10000, 11000):
        cache.set(f"key{i}", i)
    end = time.time()
    print(f"Time to set 1000 items with full cache (current O(N)): {end - start:.4f}s")

if __name__ == "__main__":
    test_cache_perf()
