# 2023-11-20 - [Compile Regex Patterns Once in API Routing]

**Learning:** Recompiling regular expressions on every incoming request for path parameter matching causes an unnecessary performance bottleneck. The `_path_to_regex` method in `APIRouter` was rebuilding and recompiling its parameter extraction regex for each endpoint evaluation loop.
**Action:** Always cache or memoize compiled regex patterns in high-traffic routing logic or request parsers, either via `functools.lru_cache` or by storing them in a dictionary keyed by the endpoint path.
