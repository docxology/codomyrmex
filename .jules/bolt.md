## 2025-03-09 - Faster hash digest integer parsing
**Learning:** Parsing an integer from the raw `digest()` bytes via `int.from_bytes(..., "big")` is slightly faster (and avoids string allocation overhead) compared to hex-encoding it and using `int(..., 16)`.
**Action:** Use `digest()` directly instead of `.hexdigest()` when a numeric representation of a hash is needed and the algorithm allows modifying the parsing approach.
