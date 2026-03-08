# Text-to-SQL Engine -- Agent Coordination

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Provides schema-aware natural language to SQL query generation. Accepts a database schema definition and converts natural language questions into SQL queries with confidence scoring and validation.

## MCP Tools

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `text_to_sql_generate` | Generate a SQL query from a natural language question against a schema | Standard | text_to_sql |
| `text_to_sql_validate` | Validate a SQL query for safety and basic syntax | Standard | text_to_sql |


## PAI Integration

| Algorithm Phase | Agent Role | Primary Operations |
|----------------|-----------|-------------------|
| EXECUTE | Engineer Agent | Convert natural language questions to SQL queries |
| VERIFY | QA Agent | Validate generated SQL for syntax correctness and safety |


## Agent Instructions

1. Provide tables as a dict mapping table names to column lists
2. text_to_sql_validate checks for SQL injection patterns and basic syntax issues


## Navigation

- [Source README](../../src/codomyrmex/text_to_sql/README.md) | [SPEC.md](SPEC.md)
