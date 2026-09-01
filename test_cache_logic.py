import time
from src.codomyrmex.cache.backends.in_memory import InMemoryCache

def test_cache_perf():
    cache = InMemoryCache(max_size=3)

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

if __name__ == "__main__":
    test_cache_perf()
