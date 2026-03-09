
## 2024-05-24 - Pre-compiling fnmatch wildcards saves CPU
**Learning:** `fnmatch.fnmatch()` under the hood translates the glob pattern to a regex and compiles it. While `fnmatch` has an internal LRU cache, repeatedly calling `fnmatch.fnmatch` within high-throughput event loops causes severe overhead in function calls and cache lookups. O(1) matching of exact literal string topics is significantly faster.
**Action:** When evaluating topic matching (like in `EventBus` and `IntegrationBus`), partition exact string patterns from glob patterns containing `*`, `?`, `[`, `]`. Use a `set` for instant lookup of exact strings, and pre-compile the translated glob patterns manually (`re.compile(fnmatch.translate(pattern))`) to perform `.match()` checks during routing loops.
