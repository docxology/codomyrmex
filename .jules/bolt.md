## 2026-03-10 - Refactored Synchronous API Wrappers for asyncio Completeness

**Vulnerability/Performance Issue:** Synchronous blocking `time.sleep` calls were present in retry loops during API interaction logic. When the framework executes in an event loop environment, these synchronous blocking calls could stall the event loop. Furthermore, maintaining split implementation blocks (sync vs async) introduced duplication and bugs.
**Learning:** `asyncio.run()` cannot be called when an event loop is already running. For unified API endpoints needing sync wrappers that might be called within existing asyncio event loops, standard practice is to use a ThreadPoolExecutor wrapper (`pool.submit(asyncio.run, coro).result()`) to isolate the new loop from the running one, thus preventing `RuntimeError: asyncio.run() cannot be called from a running event loop`.
**Prevention:** Avoid split sync/async codebase logic if async wrappers or pure async calls are sufficient. Always test sync-wrapper methods in an event loop environment (e.g., using `pytest.mark.asyncio`) to catch runtime boundary errors.

## 2026-03-10 - Optimized MD5 Integer Extraction

**Performance Issue:** Extracting integer values from `hashlib.md5().hexdigest()` via `int(hexdigest(), 16)` introduces unnecessary string allocation and parsing overhead.
**Learning:** For performance optimization when extracting integer values from `hashlib` digests in Python, use `int.from_bytes(digest(), 'big')` instead of `int(hexdigest(), 16)`. This avoids significant string allocation and parsing overhead while preserving the exact 128-bit integer values required for backward compatibility (e.g., in MinHash deduplication signatures).
**Action:** When converting hash digests to large integers, use `.digest()` with `int.from_bytes(..., 'big')` instead of hex string parsing.
