## 2025-03-05 - [Critical] SQL Injection in SQLite PRAGMA table_info via Unescaped Identifier
**Vulnerability:** Found an unescaped identifier (`table_name`) formatted directly into a `PRAGMA table_info` query (`f"PRAGMA table_info({table_name})"`) in `db_manager.py`'s `get_table_info` function.
**Learning:** SQLite's `PRAGMA` statements do not support standard prepared statement query parameterization. This often leads to developers falling back to string formatting, which introduces SQL injection vulnerabilities if the identifier is attacker-controlled.
**Prevention:** Since parameterized identifiers are not supported in `PRAGMA`, dynamically constructed queries using identifiers must be escaped manually. This is done by doubling interior double quotes (e.g. `"` -> `""`) and wrapping the entire identifier in double quotes (e.g., `f'"{table_name.replace('"', '""')}"'`) to ensure it's safely treated as a schema identifier and not executable SQL.
## 2025-05-23 - [Critical] AST parsing replaces arbitrary eval()

**Vulnerability:** A critical command injection vulnerability was discovered in the `autograd` module. The `autograd_compute` MCP tool used `compile()` and `eval()` directly on user-provided strings. This allowed arbitrary code execution because AI agents or users could pass malicious Python code strings instead of math expressions.

**Learning:** Mathematical evaluators often misuse `eval()` because it natively supports expressions. The fix involved migrating to an AST-based parser (`ast.parse`) combined with a strict recursive evaluator (`_safe_eval`). A unique edge case in AST evaluation is that negative numbers are parsed as `ast.UnaryOp` (with `ast.USub`) rather than primitive `ast.Constant` nodes, requiring specific handler logic to extract values securely when an exponent is passed.

**Prevention:** Never use `eval()` on strings sourced outside of fully trusted codebase origins. For dynamic math, always build a whitelist-based AST evaluator or use safer functions like `ast.literal_eval`. Make sure to account for AST quirks like `ast.UnaryOp` wrapping constants.
