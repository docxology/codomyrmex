## 2026-03-10 - Refactored Synchronous API Wrappers for asyncio Completeness

**Vulnerability/Performance Issue:** Synchronous blocking `time.sleep` calls were present in retry loops during API interaction logic. When the framework executes in an event loop environment, these synchronous blocking calls could stall the event loop. Furthermore, maintaining split implementation blocks (sync vs async) introduced duplication and bugs.
**Learning:** `asyncio.run()` cannot be called when an event loop is already running. For unified API endpoints needing sync wrappers that might be called within existing asyncio event loops, standard practice is to use a ThreadPoolExecutor wrapper (`pool.submit(asyncio.run, coro).result()`) to isolate the new loop from the running one, thus preventing `RuntimeError: asyncio.run() cannot be called from a running event loop`.
**Prevention:** Avoid split sync/async codebase logic if async wrappers or pure async calls are sufficient. Always test sync-wrapper methods in an event loop environment (e.g., using `pytest.mark.asyncio`) to catch runtime boundary errors.

## 2026-03-11 - Fast Integer Hashing for Deduplication
**Learning:** `int.from_bytes(hashlib.md5(...).digest(), 'big')` is measurably faster than `int(hashlib.md5(...).hexdigest(), 16)` and is safer since it avoids string parsing overhead while strictly keeping exactly the same 128-bit integer result. This saves CPU cycles on intensive hashing and LSH deduplication tasks.
**Action:** Use `int.from_bytes(..., 'big')` instead of hexadecimal string parsing when working with `hashlib` or similar cryptographic primitives for raw integer conversion.
