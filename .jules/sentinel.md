## 2025-03-05 - [Critical] SQL Injection in SQLite PRAGMA table_info via Unescaped Identifier
**Vulnerability:** Found an unescaped identifier (`table_name`) formatted directly into a `PRAGMA table_info` query (`f"PRAGMA table_info({table_name})"`) in `db_manager.py`'s `get_table_info` function.
**Learning:** SQLite's `PRAGMA` statements do not support standard prepared statement query parameterization. This often leads to developers falling back to string formatting, which introduces SQL injection vulnerabilities if the identifier is attacker-controlled.
**Prevention:** Since parameterized identifiers are not supported in `PRAGMA`, dynamically constructed queries using identifiers must be escaped manually. This is done by doubling interior double quotes (e.g. `"` -> `""`) and wrapping the entire identifier in double quotes (e.g., `f'"{table_name.replace('"', '""')}"'`) to ensure it's safely treated as a schema identifier and not executable SQL.

## 2024-03-08 - Command Line Password Exposure in MySQL Backup
**Vulnerability:** MySQL password was being passed directly to `mysqldump` via command-line arguments (`-p<password>`).
**Learning:** Passing credentials in command line arguments exposes them to anyone on the system via the process list (e.g. `ps aux`), which is a significant information disclosure risk. This was explicitly handled correctly for pg_dump but missed for mysqldump.
**Prevention:** Always use environment variables (like `MYSQL_PWD` for MySQL or `PGPASSWORD` for PostgreSQL) when calling external database tools via `subprocess.run` to prevent process-list exposure.
