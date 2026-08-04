## 2026-03-10 - Refactored Synchronous API Wrappers for asyncio Completeness

**Vulnerability/Performance Issue:** Synchronous blocking `time.sleep` calls were present in retry loops during API interaction logic. When the framework executes in an event loop environment, these synchronous blocking calls could stall the event loop. Furthermore, maintaining split implementation blocks (sync vs async) introduced duplication and bugs.
**Learning:** `asyncio.run()` cannot be called when an event loop is already running. For unified API endpoints needing sync wrappers that might be called within existing asyncio event loops, standard practice is to use a ThreadPoolExecutor wrapper (`pool.submit(asyncio.run, coro).result()`) to isolate the new loop from the running one, thus preventing `RuntimeError: asyncio.run() cannot be called from a running event loop`.
**Prevention:** Avoid split sync/async codebase logic if async wrappers or pure async calls are sufficient. Always test sync-wrapper methods in an event loop environment (e.g., using `pytest.mark.asyncio`) to catch runtime boundary errors.

## 2024-07-10 - Avoid inline dictionaries for type mapping

**Learning:** Recreating static dictionaries on every function call (e.g. `type_map = {"int": int, ...}` inside `deserialize`) adds significant overhead in frequently called code paths.
**Action:** Move static mapping dictionaries to class-level or module-level constants (e.g. `_TYPE_MAP`) to initialize them once and eliminate per-call allocation overhead.
## 2024-07-10 - Avoid shared mutable state when hoisting static dictionaries
**Learning:** When hoisting static mapping dictionaries to module-level constants to avoid per-call overhead, if the values in the dictionary are mutable objects (like nested dicts ), they can be accidentally modified by callers, leading to bugs. This happened when returning a schema dict that was later mutated with additional properties.
**Action:** Store immutable primitive types (like strings) in the static dictionary, and construct the mutable objects freshly at the usage site (e.g. ).

## 2024-07-10 - Avoid shared mutable state when hoisting static dictionaries
**Learning:** When hoisting static mapping dictionaries to module-level constants to avoid per-call overhead, if the values in the dictionary are mutable objects (like nested dicts `{"type": "string"}`), they can be accidentally modified by callers, leading to bugs. This happened when returning a schema dict that was later mutated with additional properties.
**Action:** Store immutable primitive types (like strings) in the static dictionary, and construct the mutable objects freshly at the usage site (e.g. `{"type": _TYPE_MAPPING.get(field.type, "string")}`).

## 2026-08-04 - Classify overlayfs mount failures as Docker setup errors
**Learning:** In certain CI environments, Docker containers fail to start with `error response from daemon: failed to mount ... invalid argument` due to kernel and overlayfs compatibility issues. Previously, the framework classified this as a generic `execution_error`, causing tests that should have gracefully skipped to fail.
**Action:** Add `"error response from daemon"` to `_DOCKER_SETUP_ERROR_MARKERS` in `codomyrmex/coding/sandbox/container.py` so that environment-specific container initialization failures correctly yield a `setup_error`.
