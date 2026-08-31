
## 2026-08-31 - Optimize LRU Cache Eviction from O(N) to O(1)

**Learning:** Dictionary-based LRU caches using manual O(N) deletion (e.g. `min(cache.keys(), key=lambda k: cache[k][1])`) are highly inefficient for large caches and frequently accessed paths.
**Action:** Always use `collections.OrderedDict` with `.popitem(last=False)` and `.move_to_end()` to guarantee O(1) eviction and maintain LRU semantics efficiently without recreating dictionaries or traversing keys.
