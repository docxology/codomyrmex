# Bolt Journal

## 2026-03-10 - Refactored Synchronous API Wrappers for asyncio Completeness

**Vulnerability/Performance Issue:** Synchronous blocking `time.sleep` calls were present in retry loops during API interaction logic. When the framework executes in an event loop environment, these synchronous blocking calls could stall the event loop. Furthermore, maintaining split implementation blocks (sync vs async) introduced duplication and bugs.
**Learning:** `asyncio.run()` cannot be called when an event loop is already running. For unified API endpoints needing sync wrappers that might be called within existing asyncio event loops, standard practice is to use a ThreadPoolExecutor wrapper (`pool.submit(asyncio.run, coro).result()`) to isolate the new loop from the running one, thus preventing `RuntimeError: asyncio.run() cannot be called from a running event loop`.
**Prevention:** Avoid split sync/async codebase logic if async wrappers or pure async calls are sufficient. Always test sync-wrapper methods in an event loop environment (e.g., using `pytest.mark.asyncio`) to catch runtime boundary errors.

## 2024-07-10 - Avoid inline dictionaries for type mapping

**Learning:** Recreating static dictionaries on every function call (e.g. `type_map = {"int": int, ...}` inside `deserialize`) adds significant overhead in frequently called code paths.
**Action:** Move static mapping dictionaries to class-level or module-level constants (e.g. `_TYPE_MAP`) to initialize them once and eliminate per-call allocation overhead.

## 2024-05-24 - O(1) Cache Eviction using OrderedDict

**Learning:** The `InMemoryCache` was implementing eviction by calling `min()` across all cache keys to find the oldest entry, causing $O(N)$ behavior on every cache insertion once it was full. This creates severe performance degradation for large caches.
**Action:** Use `collections.OrderedDict` to maintain insertion order, enabling $O(1)$ eviction via `.popitem(last=False)`, and pair it with `.move_to_end(key)` for existing updates. Use `time.monotonic()` for robust timestamp tracking over `time.time()`.
## 2026-09-11 - Session hygiene: dedupe before optimizing

**Failure mode:** The 2026-09 triage closed 200+ duplicate Bolt PRs. The
dominant pattern: the same optimization (O(1) InMemoryCache eviction,
`_TYPE_MAP` hoisting, regex precompilation) was re-proposed daily even after a
representative was merged, because sessions never checked open PRs or recent
merge history.

**Action (mandatory, in order):**
1. `gh pr list --state open --search "<symbol or file>"` — an open PR on the
   same file/intent blocks a new PR.
2. `git log --oneline -50 -- <target-file>` + read the file on `main` — if
   the optimization is already applied (module-level map, compiled regex,
   `move_to_end`, frozenset, batching), the task is DONE. Do not open a PR.
3. One logical change = one PR. No formatter churn, no unrelated files, no
   CI/workflow edits, no `.jules/` journal-only diffs.
4. Cite `file:line` on `main` in the PR body proving the hot path still
   allocates/compiles today.

**Retired topics (do not re-propose; representative already merged):**
InMemoryCache OrderedDict eviction (merged #488, applied via #283 stats fix),
`cache/policies.py` monotonic clocks (#483 family), TTLPolicy O(1) (#470),
InferenceCache LRU (#485), `validation.py` `_TYPE_MAP` (#410), module-level
type maps in the config/metrics/validation trio (#420 + applied #441/#425),
templating regex precompile (#397/#402 family), `config_loader` env regex
(#401/#381), safety scanner regexes (#379), MinHash int extraction (#219),
EventBus pattern precompile (#151), ConsistentHash rebuild (#146).
## 2024-09-12 - Eliminate per-call allocation overhead in factory functions

**Learning:** Dynamically creating mapping dictionaries inside frequently called factory functions like `create_serializer` adds measurable overhead due to repeated memory allocation on every call.
**Action:** Always extract static mapping dictionaries (like registry maps) to module-level or class-level constants to initialize them exactly once.
