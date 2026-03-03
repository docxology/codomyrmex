"""MCP tools for the database_management module.

Exposes adapter listing, database monitoring, and schema generation
as auto-discovered MCP tools. Zero external dependencies beyond the
database_management module itself.
"""

from __future__ import annotations

from codomyrmex.model_context_protocol.decorators import mcp_tool


@mcp_tool(
    category="database_management",
    description=(
        "List available database adapter names supported by the "
        "database_management module (e.g. sqlite, postgres, mysql, redis)."
    ),
)
def db_list_adapters() -> list[str]:
    """Return the list of supported database adapter identifiers."""
    return ["sqlite", "postgres", "mysql", "redis"]


@mcp_tool(
    category="database_management",
    description=(
        "Monitor database health and performance. Returns a dictionary "
        "with metrics such as connection count, query latency, and status."
    ),
)
def db_monitor(connection_string: str = "sqlite:///:memory:") -> dict:
    """Run a database health check and return metrics.

    Args:
        connection_string: Database connection URI (defaults to in-memory SQLite).

    Returns:
        Dictionary of health/performance metrics.

    """
    from codomyrmex.database_management import monitor_database

    return monitor_database(connection_string)


@mcp_tool(
    category="database_management",
    description=(
        "Generate a database schema from model definitions. "
        "models is a list of model dicts (e.g. [{'name': 'User', "
        "'fields': {'id': 'int', 'name': 'str'}}]). "
        "output_dir is the directory to write generated schema files."
    ),
)
def db_generate_schema(
    models: list[dict],
    output_dir: str = "/tmp/codomyrmex_schema",
) -> dict:
    """Generate database schema from model definitions.

    Args:
        models: List of model definition dicts.
        output_dir: Directory for generated schema output.

    Returns:
        Dictionary with schema generation results.

    """
    from codomyrmex.database_management import generate_schema

    result = generate_schema(models, output_dir)
    if isinstance(result, dict):
        return result
    if hasattr(result, "__dict__"):
        return {k: str(v) for k, v in result.__dict__.items()}
    return {"result": str(result)}
