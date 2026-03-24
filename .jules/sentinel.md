## 2025-03-05 - [Critical] SQL Injection in SQLite PRAGMA table_info via Unescaped Identifier
**Vulnerability:** Found an unescaped identifier (`table_name`) formatted directly into a `PRAGMA table_info` query (`f"PRAGMA table_info({table_name})"`) in `db_manager.py`'s `get_table_info` function.
**Learning:** SQLite's `PRAGMA` statements do not support standard prepared statement query parameterization. This often leads to developers falling back to string formatting, which introduces SQL injection vulnerabilities if the identifier is attacker-controlled.
**Prevention:** Since parameterized identifiers are not supported in `PRAGMA`, dynamically constructed queries using identifiers must be escaped manually. This is done by doubling interior double quotes (e.g. `"` -> `""`) and wrapping the entire identifier in double quotes (e.g., `f'"{table_name.replace('"', '""')}"'`) to ensure it's safely treated as a schema identifier and not executable SQL.

## 2025-03-05 - [CRITICAL] Process-List Credential Exposure in External Tools
**Vulnerability:** Found `mysqldump` being executed with the password passed directly in the command line arguments (`-p...`).
**Learning:** Passing credentials via command-line arguments to external subprocesses (like `mysqldump` or `pg_dump`) exposes them to any user on the system who can view the process list (e.g., via `ps` or `/proc`).
**Prevention:** Always pass credentials to external database tools via environment variables (like `MYSQL_PWD` or `PGPASSWORD`) using the `env` parameter in `subprocess.run`, as these are not exposed in the process list.
