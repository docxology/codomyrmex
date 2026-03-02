"""
MCP tools for the text_to_sql module.

Exposes text-to-SQL conversion capabilities through the Model Context
Protocol so that AI agents can generate SQL queries from natural language.
"""

from __future__ import annotations

from codomyrmex.model_context_protocol.decorators import mcp_tool

from .engine import SQLSchema, TextToSQLEngine


@mcp_tool(category="text_to_sql")
def text_to_sql_generate(question: str, tables: dict, primary_keys: dict = None) -> dict:
    """Generate a SQL query from a natural language question.

    Args:
        question: Natural language question about the data
        tables: Schema dict mapping table names to column lists,
            e.g. {"users": ["id", "name", "email"]}
        primary_keys: Optional dict mapping table names to primary key columns

    Returns:
        dict with keys: query (str), confidence (float), tables_used (list),
        valid (bool), error (str|None)
    """
    schema = SQLSchema(
        tables=tables,
        primary_keys=primary_keys or {},
    )
    engine = TextToSQLEngine(schema)
    result = engine.generate(question)
    return {
        "query": result.query,
        "confidence": result.confidence,
        "tables_used": result.tables_used,
        "valid": result.valid,
        "error": result.error,
    }


@mcp_tool(category="text_to_sql")
def text_to_sql_validate(sql: str) -> dict:
    """Validate a SQL query for safety and basic syntax.

    Args:
        sql: SQL query string to validate

    Returns:
        dict with keys: valid (bool), error (str|None)
    """
    from .engine import SQLValidator

    is_valid, error = SQLValidator.validate(sql)
    return {
        "valid": is_valid,
        "error": error,
    }
