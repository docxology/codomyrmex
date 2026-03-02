"""
Text-to-SQL engine using template matching and schema-aware generation.

Converts natural language questions into SQL queries by pattern matching
against common query structures and resolving table/column references
from a provided schema. Pure Python, no LLM dependency.
"""

import re
from dataclasses import dataclass


@dataclass
class SQLSchema:
    """Database schema for context-aware SQL generation."""

    tables: dict[str, list[str]]  # {table_name: [column_name, ...]}
    primary_keys: dict[str, str] = None  # {table_name: pk_column}
    foreign_keys: list[tuple] = None  # [(table, col, ref_table, ref_col), ...]

    def __post_init__(self):
        if self.primary_keys is None:
            self.primary_keys = {}
        if self.foreign_keys is None:
            self.foreign_keys = []


@dataclass
class SQLResult:
    """Result of a text-to-SQL conversion."""

    query: str
    confidence: float
    tables_used: list[str]
    valid: bool
    error: str | None = None


class SQLValidator:
    """Basic SQL syntax validator."""

    REQUIRED_KEYWORDS = ["SELECT", "FROM"]
    DANGEROUS_KEYWORDS = [
        "DROP",
        "DELETE",
        "UPDATE",
        "INSERT",
        "ALTER",
        "CREATE",
        "TRUNCATE",
    ]

    @classmethod
    def validate(cls, sql: str) -> tuple[bool, str | None]:
        """Returns (is_valid, error_message)."""
        sql_upper = sql.upper().strip()

        # Check for dangerous operations
        for kw in cls.DANGEROUS_KEYWORDS:
            if kw in sql_upper.split():
                return False, f"Dangerous SQL keyword '{kw}' not allowed"

        # Check required keywords
        for kw in cls.REQUIRED_KEYWORDS:
            if kw not in sql_upper:
                return False, f"Missing required keyword '{kw}'"

        # Check basic syntax: SELECT ... FROM ...
        if not re.search(r"SELECT\s+.+\s+FROM\s+\w+", sql_upper, re.DOTALL):
            return False, "Invalid SQL structure: expected SELECT ... FROM ..."

        return True, None


class TextToSQLEngine:
    """
    Text-to-SQL engine using template matching and schema-aware generation.

    This implementation uses pattern matching and templates rather than an LLM,
    demonstrating the core logic. In production, an LLM would handle generation.
    """

    # Query patterns for common SQL operations
    PATTERNS = [
        # Count queries
        (r"\bhow many\b|\bcount\b|\bnumber of\b", "COUNT"),
        # Aggregations
        (r"\baverage\b|\bavg\b|\bmean\b", "AVG"),
        (r"\bmaximum\b|\bmax\b|\bhighest\b|\blargest\b", "MAX"),
        (r"\bminimum\b|\bmin\b|\blowest\b|\bsmallest\b", "MIN"),
        (r"\bsum\b|\btotal\b", "SUM"),
        # Filtering
        (r"\bwhere\b|\bwith\b|\bhaving\b|\bthat have\b", "WHERE"),
        # Ordering
        (r"\border by\b|\bsort by\b|\branked by\b", "ORDER BY"),
        # Limits
        (r"\btop (\d+)\b|\bfirst (\d+)\b|\blimit\b", "LIMIT"),
    ]

    def __init__(self, schema: SQLSchema):
        self.schema = schema
        self.validator = SQLValidator()

    def _find_table(self, question: str) -> str | None:
        """Find the most relevant table based on question keywords."""
        question_lower = question.lower()
        best_match = None
        best_score = 0

        for table_name in self.schema.tables:
            # Score by table name mentions
            score = sum(
                1 for word in table_name.lower().split("_") if word in question_lower
            )
            # Score by column mentions
            for col in self.schema.tables[table_name]:
                if col.lower().replace("_", " ") in question_lower:
                    score += 2

            if score > best_score:
                best_score = score
                best_match = table_name

        # Fallback: first table
        if best_match is None and self.schema.tables:
            best_match = next(iter(self.schema.tables))

        return best_match

    def _find_columns(self, question: str, table: str) -> list[str]:
        """Find relevant columns from question."""
        question_lower = question.lower()
        relevant = []

        for col in self.schema.tables.get(table, []):
            if (
                col.lower() in question_lower
                or col.lower().replace("_", " ") in question_lower
            ):
                relevant.append(col)

        return relevant if relevant else ["*"]

    def generate(self, question: str) -> SQLResult:
        """
        Generate SQL from natural language question.

        Args:
            question: Natural language question about the data

        Returns:
            SQLResult with generated SQL and metadata
        """
        question_lower = question.lower()

        # Find relevant table
        table = self._find_table(question)
        if table is None:
            return SQLResult(
                query="",
                confidence=0.0,
                tables_used=[],
                valid=False,
                error="No matching table found in schema",
            )

        # Find columns
        columns = self._find_columns(question, table)

        # Determine aggregation
        agg_type = None
        for pattern, agg in self.PATTERNS:
            if re.search(pattern, question_lower):
                agg_type = agg
                break

        # Build SQL
        if agg_type == "COUNT":
            select_clause = "COUNT(*)"
        elif agg_type in ("AVG", "MAX", "MIN", "SUM") and columns != ["*"]:
            select_clause = f"{agg_type}({columns[0]})"
        else:
            select_clause = ", ".join(columns)

        sql = f"SELECT {select_clause} FROM {table}"

        # Add WHERE if mentioned
        if re.search(r"\bwhere\b.*=", question_lower):
            # Try to extract condition
            eq_match = re.search(r"(\w+)\s*=\s*['\"]?(\w+)['\"]?", question)
            if eq_match:
                col, val = eq_match.group(1), eq_match.group(2)
                if col in self.schema.tables.get(table, []):
                    sql += f" WHERE {col} = '{val}'"

        # Add ORDER BY
        if re.search(r"\border by\b|\bsort by\b", question_lower):
            if columns != ["*"]:
                sql += f" ORDER BY {columns[0]}"

        # Add LIMIT
        limit_match = re.search(
            r"\btop (\d+)\b|\blimit (\d+)\b|\bfirst (\d+)\b", question_lower
        )
        if limit_match:
            n = next(g for g in limit_match.groups() if g)
            sql += f" LIMIT {n}"

        sql = sql.strip() + ";"

        # Validate
        is_valid, error = self.validator.validate(sql)
        confidence = 0.7 if agg_type else 0.5
        if columns != ["*"]:
            confidence += 0.1

        return SQLResult(
            query=sql,
            confidence=round(confidence, 2),
            tables_used=[table],
            valid=is_valid,
            error=error,
        )
