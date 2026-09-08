import pytest

from codomyrmex.text_to_sql.engine import SQLSchema, TextToSQLEngine


def test_sql_injection_defense():
    schema = SQLSchema(tables={"users": ["id", "name"]})
    eng = TextToSQLEngine(schema)
    result = eng.generate("give me everything from users where name = o'brien")
    assert result.query == "SELECT name FROM users WHERE name = 'o''brien';"
