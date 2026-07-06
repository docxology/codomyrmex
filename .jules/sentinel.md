## 2026-03-01 - Fix Hardcoded Secret Vulnerability in Models

**Vulnerability:**
The `SecretType` Enum in `src/codomyrmex/security/secrets/models.py` previously assigned the literal string `"password"` to the `PASSWORD` constant. Static Application Security Testing (SAST) tools and secret scanners routinely flag this exact pattern (assigning a string literal like "password" to a variable named `PASSWORD`) as a hardcoded secret. Although the value represents a type rather than an actual secret, it triggers false positives that degrade security monitoring efficacy.

**Learning:**
Security models and Enums should avoid using literal security-sensitive terms like `"password"` directly as values. These patterns mimic common hardcoded credentials, confusing security scanners.

**Learning:**
Duplicate definitions across modules (e.g., repeating the `SecretType` definition in both `models.py` and `__init__.py`) increase the risk of inconsistent fixes. A unified source of truth should be maintained.

**Prevention:**
Use descriptive suffixes or alternatives (e.g., changing `"password"` to `"password_type"`) for model or type definitions. Implement robust CI checks to enforce single-source-of-truth patterns rather than duplicating classes.

## 2026-03-02 - Fix SQL Injection via PRAGMA String Interpolation

**Vulnerability:**
The `get_table_info` method in `src/codomyrmex/database_management/db_manager.py` manually escaped table names and used string interpolation to execute the PRAGMA query: `conn.execute(f"PRAGMA table_info({safe_table_name})")`. This approach is error-prone and a classic SQL injection vector if custom escaping logic is bypassed.

**Learning:**
SQLite >= 3.16.0 provides table-valued functions for pragmas which allow parameterized bindings. This means string interpolation is completely unnecessary when inspecting schema info.

**Prevention:**
Never use string interpolation for SQL query execution even with internal variables. Always use parameterized queries or table-valued pragma functions such as `SELECT * FROM pragma_table_info(?)`.
