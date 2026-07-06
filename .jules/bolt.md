## 2026-03-10 - Refactored Synchronous API Wrappers for asyncio Completeness

**Vulnerability/Performance Issue:** Synchronous blocking `time.sleep` calls were present in retry loops during API interaction logic. When the framework executes in an event loop environment, these synchronous blocking calls could stall the event loop. Furthermore, maintaining split implementation blocks (sync vs async) introduced duplication and bugs.
**Learning:** `asyncio.run()` cannot be called when an event loop is already running. For unified API endpoints needing sync wrappers that might be called within existing asyncio event loops, standard practice is to use a ThreadPoolExecutor wrapper (`pool.submit(asyncio.run, coro).result()`) to isolate the new loop from the running one, thus preventing `RuntimeError: asyncio.run() cannot be called from a running event loop`.
**Prevention:** Avoid split sync/async codebase logic if async wrappers or pure async calls are sufficient. Always test sync-wrapper methods in an event loop environment (e.g., using `pytest.mark.asyncio`) to catch runtime boundary errors.

## 2026-03-10 - Optimized Hash Digest to Integer Conversion

**Learning:** When extracting integer values from hashlib digests in Python, using `int.from_bytes(digest(), 'big')` instead of `int(hexdigest(), 16)` significantly avoids string allocation and parsing overhead. This is especially impactful in tight loops or hashing-heavy operations (e.g., LSH shingling, feature flags deterministic assignment, consistent hashing).
**Action:** When integer conversions from hashes are needed, always use the `.digest()` method along with `int.from_bytes` rather than intermediate `.hexdigest()` hex strings.
