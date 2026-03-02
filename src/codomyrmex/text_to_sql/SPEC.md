# Text-to-SQL -- Technical Specification

## Architecture

### Pattern Matching Engine

1. **Table resolution**: Score each table by keyword overlap with question (table name words + column name matches)
2. **Column resolution**: Find columns mentioned in the question text
3. **Aggregation detection**: Regex patterns match COUNT, AVG, MAX, MIN, SUM
4. **Clause generation**: Build SELECT, FROM, WHERE, ORDER BY, LIMIT clauses

### SQL Validator

- Rejects queries containing dangerous keywords (DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, TRUNCATE)
- Requires SELECT and FROM keywords
- Validates basic SELECT ... FROM ... structure

### Confidence Scoring

| Condition | Confidence |
|-----------|------------|
| Aggregation detected | +0.7 base |
| No aggregation | +0.5 base |
| Specific columns found | +0.1 |

## Dataclasses

### SQLSchema
- `tables: dict[str, list[str]]` -- table name to column list
- `primary_keys: dict[str, str]` -- table name to PK column
- `foreign_keys: list[tuple]` -- (table, col, ref_table, ref_col)

### SQLResult
- `query: str` -- generated SQL
- `confidence: float` -- 0.0 to 1.0
- `tables_used: list[str]`
- `valid: bool`
- `error: Optional[str]`

## Limitations

- Template-based, not LLM-based (limited natural language understanding)
- Single-table queries only (no JOINs)
- WHERE clause requires explicit "where column = value" format
- No subqueries or complex expressions
