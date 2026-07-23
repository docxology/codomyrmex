from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

from codomyrmex.manuscript.variables import (
    _canonical_sqlite_sha256,
    validate_variable_contract,
)


def test_pdf_margin_is_configured_and_injected() -> None:
    root = Path(__file__).resolve().parents[3]
    config_path = root / "docs" / "manuscript" / "config.yaml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    expected = str(config["paper"]["pdf_margin"])
    variables = json.loads(
        (root / "output" / "data" / "manuscript_variables.json").read_text(
            encoding="utf-8"
        )
    )
    preamble = (root / "docs" / "manuscript" / "preamble.md").read_text(
        encoding="utf-8"
    )

    assert "{{CONFIG_PDF_MARGIN}}" in preamble
    assert variables["CONFIG_PDF_MARGIN"] == expected
    assert re.fullmatch(r"(?:0|[0-9]+(?:\.[0-9]+)?)(?:in|cm|mm|pt)", expected)


def test_sqlite_artifact_digest_is_stable_across_temporary_paths(
    tmp_path: Path,
) -> None:
    import sqlite3

    database_paths = [tmp_path / "a.sqlite", tmp_path / "nested" / "b.sqlite"]
    for index, path in enumerate(database_paths):
        path.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(path)
        connection.execute(
            "CREATE TABLE pheromone_markers "
            "(key TEXT PRIMARY KEY, strength REAL NOT NULL, metadata_json TEXT NOT NULL)"
        )
        connection.execute(
            "INSERT INTO pheromone_markers (key, strength, metadata_json) "
            "VALUES (?, ?, ?)",
            (
                "failure",
                1.0,
                '{"last_reinforced": %s, "location": "fixture"}' % (100.0 + index),
            ),
        )
        connection.commit()
        connection.close()

    assert _canonical_sqlite_sha256(database_paths[0]) == _canonical_sqlite_sha256(
        database_paths[1]
    )


def test_variable_contract_reports_used_reserved_and_unused_values(tmp_path: Path):
    manuscript = tmp_path / "manuscript"
    manuscript.mkdir()
    (manuscript / "01_method.md").write_text(
        "Measured value {{RESULT_VALUE}}; figure {{FIGURE_FILENAME_MAIN}}.\n",
        encoding="utf-8",
    )
    (manuscript / "config.yaml").write_text(
        "figures:\n  main:\n    caption: 'Caption {{RESULT_VALUE}}'\n",
        encoding="utf-8",
    )
    figures = tmp_path / "figures"
    figures.mkdir()
    (figures / "main.py").write_text(
        "value = _var_float('RESULT_VALUE')\n",
        encoding="utf-8",
    )

    report = validate_variable_contract(
        manuscript,
        {
            "RESULT_VALUE": "1.0",
            "FIGURE_FILENAME_MAIN": "main.png",
            "CONFIG_HASH": "",
            "CONFIG_SCORE_MID": "0.5",
        },
        figure_source_dir=figures,
    )

    assert report["status"] == "valid"
    assert "RESULT_VALUE" in report["used_tokens"]
    assert report["reserved_variables"]["CONFIG_SCORE_MID"]
    assert report["unused_variables"] == []


def test_variable_contract_fails_on_undefined_and_unclassified_unused(tmp_path: Path):
    manuscript = tmp_path / "manuscript"
    manuscript.mkdir()
    (manuscript / "01_method.md").write_text(
        "Value {{DEFINED}} and {{MISSING}}.\n", encoding="utf-8"
    )
    report = validate_variable_contract(manuscript, {"DEFINED": "ok", "DRIFT": "1"})

    assert report["status"] == "invalid"
    assert "MISSING" in report["undefined_tokens"]
    assert "DRIFT" in report["unused_variables"]
