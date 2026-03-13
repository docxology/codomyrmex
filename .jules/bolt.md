
## 2026-03-10 - Event Routing Performance
**Learning:** `fnmatch.fnmatch()` introduces significant overhead when called repeatedly in hot paths (like event buses). In this codebase, the EventBus and IntegrationBus rely heavily on pattern matching for every emitted event.
**Action:** Always pre-compile wildcard patterns (`*`, `?`, `[`) using `re.compile(fnmatch.translate(pattern))` and use O(1) set lookups for literal strings to optimize routing.
