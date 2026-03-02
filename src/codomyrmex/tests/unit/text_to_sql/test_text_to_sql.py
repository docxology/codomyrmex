"""
Unit tests for the text_to_sql module.

Tests cover:
- SQL generation from natural language
- Schema matching (table and column resolution)
- Aggregation detection (COUNT, AVG, MAX, MIN, SUM)
- SQL validation (safety and syntax)
- MCP tool interface
"""

import pytest

from codomyrmex.text_to_sql import SQLResult, SQLSchema, TextToSQLEngine
from codomyrmex.text_to_sql.engine import SQLValidator

# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_schema():
    """Standard test schema with users and orders tables."""
    return SQLSchema(
        tables={
            "users": ["id", "name", "email", "age"],
            "orders": ["id", "user_id", "total", "created_at"],
        },
        primary_keys={"users": "id", "orders": "id"},
    )


@pytest.fixture
def engine(sample_schema):
    """TextToSQLEngine with sample schema."""
    return TextToSQLEngine(sample_schema)


# ---------------------------------------------------------------------------
# SQL Validator
# ---------------------------------------------------------------------------


class TestSQLValidator:
    """SQL validation for safety and syntax."""

    @pytest.mark.unit
    def test_valid_select(self):
        valid, error = SQLValidator.validate("SELECT * FROM users;")
        assert valid is True
        assert error is None

    @pytest.mark.unit
    def test_valid_count(self):
        valid, error = SQLValidator.validate("SELECT COUNT(*) FROM orders;")
        assert valid is True

    @pytest.mark.unit
    def test_dangerous_drop_blocked(self):
        valid, error = SQLValidator.validate("DROP TABLE users;")
        assert valid is False
        assert "DROP" in error

    @pytest.mark.unit
    def test_dangerous_delete_blocked(self):
        valid, error = SQLValidator.validate("DELETE FROM users WHERE id = 1;")
        assert valid is False
        assert "DELETE" in error

    @pytest.mark.unit
    def test_dangerous_update_blocked(self):
        valid, error = SQLValidator.validate("UPDATE users SET name = 'x';")
        assert valid is False
        assert "UPDATE" in error

    @pytest.mark.unit
    def test_dangerous_insert_blocked(self):
        valid, error = SQLValidator.validate("INSERT INTO users VALUES (1, 'test');")
        assert valid is False
        assert "INSERT" in error

    @pytest.mark.unit
    def test_dangerous_truncate_blocked(self):
        valid, error = SQLValidator.validate("TRUNCATE TABLE users;")
        assert valid is False
        assert "TRUNCATE" in error

    @pytest.mark.unit
    def test_dangerous_alter_blocked(self):
        valid, error = SQLValidator.validate("ALTER TABLE users ADD COLUMN foo;")
        assert valid is False
        assert "ALTER" in error

    @pytest.mark.unit
    def test_dangerous_create_blocked(self):
        valid, error = SQLValidator.validate("CREATE TABLE evil (id INT);")
        assert valid is False
        assert "CREATE" in error

    @pytest.mark.unit
    def test_missing_select(self):
        valid, error = SQLValidator.validate("FROM users;")
        assert valid is False
        assert "SELECT" in error

    @pytest.mark.unit
    def test_missing_from(self):
        valid, error = SQLValidator.validate("SELECT *;")
        assert valid is False
        assert "FROM" in error

    @pytest.mark.unit
    def test_dangerous_keywords_blocked(self):
        """All dangerous keywords should be blocked."""
        for kw in SQLValidator.DANGEROUS_KEYWORDS:
            valid, error = SQLValidator.validate(f"{kw} something FROM table;")
            assert valid is False, f"Expected {kw} to be blocked"


# ---------------------------------------------------------------------------
# SQL Generation
# ---------------------------------------------------------------------------


class TestSQLGeneration:
    """SQL query generation from natural language."""

    @pytest.mark.unit
    def test_count_query_generated(self, engine):
        result = engine.generate("How many users are there?")
        assert "COUNT(*)" in result.query.upper()
        assert result.valid is True
        assert result.confidence >= 0.7

    @pytest.mark.unit
    def test_count_with_keyword(self, engine):
        result = engine.generate("count the number of orders")
        assert "COUNT(*)" in result.query.upper()

    @pytest.mark.unit
    def test_select_star_fallback(self, engine):
        """When no columns match, should fall back to SELECT *."""
        result = engine.generate("show me everything from users")
        assert "*" in result.query
        assert result.valid is True

    @pytest.mark.unit
    def test_avg_aggregation(self, engine):
        result = engine.generate("what is the average age of users")
        assert "AVG" in result.query.upper()

    @pytest.mark.unit
    def test_max_aggregation(self, engine):
        result = engine.generate("what is the maximum total in orders")
        assert "MAX" in result.query.upper()

    @pytest.mark.unit
    def test_min_aggregation(self, engine):
        result = engine.generate("what is the minimum total in orders")
        assert "MIN" in result.query.upper()

    @pytest.mark.unit
    def test_sum_aggregation(self, engine):
        result = engine.generate("what is the total sum of all orders total")
        assert "SUM" in result.query.upper()

    @pytest.mark.unit
    def test_limit_query(self, engine):
        result = engine.generate("show me the top 5 users")
        assert "LIMIT 5" in result.query.upper()

    @pytest.mark.unit
    def test_result_has_tables_used(self, engine):
        result = engine.generate("show me users")
        assert len(result.tables_used) >= 1

    @pytest.mark.unit
    def test_result_is_sqlresult(self, engine):
        result = engine.generate("show me users")
        assert isinstance(result, SQLResult)

    @pytest.mark.unit
    def test_query_ends_with_semicolon(self, engine):
        result = engine.generate("how many users")
        assert result.query.endswith(";")


# ---------------------------------------------------------------------------
# Schema Matching
# ---------------------------------------------------------------------------


class TestSchemaMatching:
    """Table and column resolution from question text."""

    @pytest.mark.unit
    def test_schema_matching_users_table(self, engine):
        result = engine.generate("show me all users")
        assert "users" in result.tables_used

    @pytest.mark.unit
    def test_schema_matching_orders_table(self, engine):
        result = engine.generate("list all orders with total")
        assert "orders" in result.tables_used

    @pytest.mark.unit
    def test_column_matching_boosts_confidence(self, engine):
        """Mentioning specific columns should increase confidence."""
        result_specific = engine.generate("show me the name of users")
        result_generic = engine.generate("show me something from users")
        assert result_specific.confidence >= result_generic.confidence

    @pytest.mark.unit
    def test_empty_schema_no_table(self):
        schema = SQLSchema(tables={})
        eng = TextToSQLEngine(schema)
        result = eng.generate("how many things")
        assert result.valid is False
        assert "No matching table" in result.error

    @pytest.mark.unit
    def test_single_table_fallback(self):
        """With one table and no keyword match, should still pick the table."""
        schema = SQLSchema(tables={"products": ["id", "price"]})
        eng = TextToSQLEngine(schema)
        result = eng.generate("what data exists")
        assert "products" in result.tables_used


# ---------------------------------------------------------------------------
# SQLSchema dataclass
# ---------------------------------------------------------------------------


class TestSQLSchema:
    """SQLSchema initialization and defaults."""

    @pytest.mark.unit
    def test_default_primary_keys(self):
        schema = SQLSchema(tables={"t": ["a"]})
        assert schema.primary_keys == {}

    @pytest.mark.unit
    def test_default_foreign_keys(self):
        schema = SQLSchema(tables={"t": ["a"]})
        assert schema.foreign_keys == []

    @pytest.mark.unit
    def test_explicit_keys(self):
        schema = SQLSchema(
            tables={"users": ["id", "name"]},
            primary_keys={"users": "id"},
            foreign_keys=[("orders", "user_id", "users", "id")],
        )
        assert schema.primary_keys["users"] == "id"
        assert len(schema.foreign_keys) == 1


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


class TestMCPTools:
    """MCP tool interface tests."""

    @pytest.mark.unit
    def test_generate_tool_returns_dict(self):
        from codomyrmex.text_to_sql.mcp_tools import text_to_sql_generate

        result = text_to_sql_generate(
            question="how many users",
            tables={"users": ["id", "name"]},
        )
        assert "query" in result
        assert "valid" in result
        assert "confidence" in result

    @pytest.mark.unit
    def test_validate_tool_valid_sql(self):
        from codomyrmex.text_to_sql.mcp_tools import text_to_sql_validate

        result = text_to_sql_validate(sql="SELECT * FROM users;")
        assert result["valid"] is True

    @pytest.mark.unit
    def test_validate_tool_dangerous_sql(self):
        from codomyrmex.text_to_sql.mcp_tools import text_to_sql_validate

        result = text_to_sql_validate(sql="DROP TABLE users;")
        assert result["valid"] is False
        assert result["error"] is not None
