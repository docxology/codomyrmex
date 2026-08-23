## 2026-03-10 - Refactored Synchronous API Wrappers for asyncio Completeness

**Vulnerability/Performance Issue:** Synchronous blocking `time.sleep` calls were present in retry loops during API interaction logic. When the framework executes in an event loop environment, these synchronous blocking calls could stall the event loop. Furthermore, maintaining split implementation blocks (sync vs async) introduced duplication and bugs.
**Learning:** `asyncio.run()` cannot be called when an event loop is already running. For unified API endpoints needing sync wrappers that might be called within existing asyncio event loops, standard practice is to use a ThreadPoolExecutor wrapper (`pool.submit(asyncio.run, coro).result()`) to isolate the new loop from the running one, thus preventing `RuntimeError: asyncio.run() cannot be called from a running event loop`.
**Prevention:** Avoid split sync/async codebase logic if async wrappers or pure async calls are sufficient. Always test sync-wrapper methods in an event loop environment (e.g., using `pytest.mark.asyncio`) to catch runtime boundary errors.

## 2024-07-10 - Avoid inline dictionaries for type mapping

**Learning:** Recreating static dictionaries on every function call (e.g. `type_map = {"int": int, ...}` inside `deserialize`) adds significant overhead in frequently called code paths.
**Action:** Move static mapping dictionaries to class-level or module-level constants (e.g. `_TYPE_MAP`) to initialize them once and eliminate per-call allocation overhead.
## 2026-08-23 - O(1) Cache Eviction using OrderedDict
**Learning:** The in-memory cache implementation was previously using a standard dictionary and resolving evictions by finding the minimum timestamp with an O(n) operation `min(self._cache.keys(), key=lambda k: self._cache[k][1])`. This can become a performance bottleneck when the cache grows large, as eviction takes O(n) time for every set operation that exceeds the capacity.
**Action:** Replaced standard dict with `collections.OrderedDict`, mapped sets with `self._cache.move_to_end(key)` and resolved evictions with `self._cache.popitem(last=False)` reducing time complexity from O(n) to O(1) during max capacity eviction, aligning with correct LRU semantics while preventing performance bottlenecks.
