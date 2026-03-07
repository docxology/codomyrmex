## 2025-03-05 - [Critical] SQL Injection in SQLite PRAGMA table_info via Unescaped Identifier
**Vulnerability:** Found an unescaped identifier (`table_name`) formatted directly into a `PRAGMA table_info` query (`f"PRAGMA table_info({table_name})"`) in `db_manager.py`'s `get_table_info` function.
**Learning:** SQLite's `PRAGMA` statements do not support standard prepared statement query parameterization. This often leads to developers falling back to string formatting, which introduces SQL injection vulnerabilities if the identifier is attacker-controlled.
**Prevention:** Since parameterized identifiers are not supported in `PRAGMA`, dynamically constructed queries using identifiers must be escaped manually. This is done by doubling interior double quotes (e.g. `"` -> `""`) and wrapping the entire identifier in double quotes (e.g., `f'"{table_name.replace('"', '""')}"'`) to ensure it's safely treated as a schema identifier and not executable SQL.
## 2024-05-24 - Process arguments password leak
**Vulnerability:** Passing passwords securely to subprocess tools via command-line arguments (like `mysqldump -p{password}`) is not secure. The arguments can be seen in the process list by any user.
**Learning:** External tools often have ways to accept credentials through environment variables which are not easily seen by other users.
**Prevention:** Avoid putting credentials in `subprocess.run` arguments. Always look for and use environment variables (e.g., `MYSQL_PWD` for MySQL or `PGPASSWORD` for PostgreSQL) and pass them securely using `env=os.environ.copy()`.
