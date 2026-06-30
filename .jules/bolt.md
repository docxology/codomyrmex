## 2026-03-10 - Refactored Synchronous API Wrappers for asyncio Completeness

**Vulnerability/Performance Issue:** Synchronous blocking `time.sleep` calls were present in retry loops during API interaction logic. When the framework executes in an event loop environment, these synchronous blocking calls could stall the event loop. Furthermore, maintaining split implementation blocks (sync vs async) introduced duplication and bugs.
**Learning:** `asyncio.run()` cannot be called when an event loop is already running. For unified API endpoints needing sync wrappers that might be called within existing asyncio event loops, standard practice is to use a ThreadPoolExecutor wrapper (`pool.submit(asyncio.run, coro).result()`) to isolate the new loop from the running one, thus preventing `RuntimeError: asyncio.run() cannot be called from a running event loop`.
**Prevention:** Avoid split sync/async codebase logic if async wrappers or pure async calls are sufficient. Always test sync-wrapper methods in an event loop environment (e.g., using `pytest.mark.asyncio`) to catch runtime boundary errors.

## 2024-05-18 - Avoid Hexdigest for Integer Conversions
**Learning:** In tight loops like `MinHash._shingle`, converting a hash to an integer using `int.from_bytes(hash_obj.digest(), 'big')` is ~6-7% faster than using `int(hash_obj.hexdigest(), 16)`. The latter involves unnecessary string allocation and parsing overhead in Python, which becomes a bottleneck in hot paths.
**Action:** Always prefer `int.from_bytes(hash_obj.digest(), 'big')` when you need the integer value of a hash, especially within loops or highly concurrent functions (e.g., A/B test routing or deduplication).
