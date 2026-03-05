
## 2025-03-03 - Hoist `str.lower()` outside loops
**Learning:** Python's `str.lower()` has non-trivial overhead when called repeatedly inside loops on large text content. In `documentation.py`, doing `if pattern.lower() in content.lower():` across many iterations significantly degrades performance compared to pre-computing `content_lower = content.lower()`.
**Action:** When performing substring searches against a large payload in multiple conditions or loops, calculate `payload.lower()` once and store it. Additionally, precompute lists of lowercase query strings if they are static.
