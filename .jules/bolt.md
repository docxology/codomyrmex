## 2026-03-10 - Refactored Synchronous API Wrappers for asyncio Completeness

**Vulnerability/Performance Issue:** Synchronous blocking `time.sleep` calls were present in retry loops during API interaction logic. When the framework executes in an event loop environment, these synchronous blocking calls could stall the event loop. Furthermore, maintaining split implementation blocks (sync vs async) introduced duplication and bugs.
**Learning:** `asyncio.run()` cannot be called when an event loop is already running. For unified API endpoints needing sync wrappers that might be called within existing asyncio event loops, standard practice is to use a ThreadPoolExecutor wrapper (`pool.submit(asyncio.run, coro).result()`) to isolate the new loop from the running one, thus preventing `RuntimeError: asyncio.run() cannot be called from a running event loop`.
**Prevention:** Avoid split sync/async codebase logic if async wrappers or pure async calls are sufficient. Always test sync-wrapper methods in an event loop environment (e.g., using `pytest.mark.asyncio`) to catch runtime boundary errors.

## 2024-05-18 - Replacing hexdigest() with digest() for integer hashing

**Learning:** When converting a `hashlib` digest into an integer (e.g., for consistent hashing or deterministic bucket assignment), converting `.hexdigest()` to a string and then parsing it as base-16 via `int(..., 16)` introduces unnecessary overhead from string allocation and base parsing.
**Action:** Extract integer values directly from the bytes object using `int.from_bytes(digest(), 'big')` instead of `int(hexdigest(), 16)` to optimize hashing logic that executes frequently or in tight loops.
