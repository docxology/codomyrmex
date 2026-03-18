"""
Tests for the SAIR Mathematics Distillation submodule.
Follows the zero-mock policy — uses real components and real JSONL data where available.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Add repo root to sys.path so 'scripts' package is importable.
repo_root = Path(__file__).resolve().parents[6]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

# ---------- evaluate --------------------------------------------------------
from scripts.sair.evaluate import parse_llm_response, OFFICIAL_TEMPLATE
from jinja2 import Template

# ---------- generate_cheatsheet ---------------------------------------------
from scripts.sair.generate_cheatsheet import (
    build_cheatsheet,
    validate_size,
    trim_to_budget,
    refine_from_results,
    STRATEGY_BUNDLES,
    TECHNIQUE_LIBRARY,
    MAX_BYTES,
)

# ---------- utils -----------------------------------------------------------
from scripts.sair.utils import (
    compute_hash,
    load_jsonl,
    save_jsonl,
    save_json,
    load_json,
    summarize_results,
    compare_runs,
    format_timestamp,
)

# ---------- download_data ---------------------------------------------------
from scripts.sair.download_data import verify_dataset_integrity, list_local_datasets


# ===========================================================================
# evaluate.py tests
# ===========================================================================

class TestParseLLMResponse:
    def test_true_verdict(self):
        resp = "VERDICT: TRUE\nREASONING: L0 is reflexive.\nPROOF: x*y = x*y.\nCOUNTEREXAMPLE:"
        parsed = parse_llm_response(resp)
        assert parsed["VERDICT"] == "TRUE"
        assert "reflexive" in parsed["REASONING"]
        assert "x*y" in parsed["PROOF"]

    def test_false_verdict(self):
        resp = "VERDICT: FALSE\nREASONING: Counterexample exists.\nPROOF:\nCOUNTEREXAMPLE: Magma {0,1}, a*b=b."
        parsed = parse_llm_response(resp)
        assert parsed["VERDICT"] == "FALSE"
        assert "Counterexample" in parsed["REASONING"]
        assert "Magma" in parsed["COUNTEREXAMPLE"]

    def test_unknown_verdict(self):
        resp = "VERDICT: MAYBE\nREASONING: Unclear."
        parsed = parse_llm_response(resp)
        assert parsed["VERDICT"] == "MAYBE"

    def test_multiline_reasoning(self):
        resp = "VERDICT: TRUE\nREASONING:\nLine 1.\nLine 2.\nPROOF: Done.\nCOUNTEREXAMPLE:"
        parsed = parse_llm_response(resp)
        assert "Line 1" in parsed["REASONING"]
        assert "Line 2" in parsed["REASONING"]


class TestTemplateRendering:
    def test_renders_equations(self):
        template = Template(OFFICIAL_TEMPLATE)
        rendered = template.render(equation1="x*y=y*x", equation2="x=x", cheatsheet=None)
        assert "x*y=y*x" in rendered
        assert "x=x" in rendered
        assert "VERDICT:" in rendered

    def test_cheatsheet_injected_when_set(self):
        template = Template(OFFICIAL_TEMPLATE)
        rendered = template.render(equation1="E1", equation2="E2", cheatsheet="Hint: left-zero.")
        assert "Hint: left-zero" in rendered

    def test_cheatsheet_omitted_when_none(self):
        template = Template(OFFICIAL_TEMPLATE)
        rendered = template.render(equation1="E1", equation2="E2", cheatsheet=None)
        assert "Hint" not in rendered


# ===========================================================================
# generate_cheatsheet.py tests
# ===========================================================================

class TestCheatsheetGeneration:
    def test_build_with_bundle(self):
        cs = build_cheatsheet(bundles=["baseline"])
        assert "STRATEGIES" in cs
        # Each baseline technique key should appear
        for key in STRATEGY_BUNDLES["baseline"]:
            assert key in cs

    def test_build_with_explicit_technique(self):
        cs = build_cheatsheet(techniques=["left_zero_magma"])
        assert "left_zero_magma" in cs
        assert TECHNIQUE_LIBRARY["left_zero_magma"][:20] in cs

    def test_build_with_rules(self):
        cs = build_cheatsheet(rules=["Rule A", "Rule B"])
        assert "Rule A" in cs
        assert "Rule B" in cs

    def test_validate_size_within(self):
        cs = build_cheatsheet(bundles=["baseline"])
        assert validate_size(cs) is True

    def test_validate_size_exceeded(self):
        large = "X" * (MAX_BYTES + 1)
        assert validate_size(large) is False

    def test_trim_to_budget(self):
        large = "\n".join(["Line " + str(i) for i in range(2000)])
        trimmed = trim_to_budget(large)
        assert len(trimmed.encode("utf-8")) <= MAX_BYTES

    def test_refine_from_results_uses_failure_patterns(self):
        """refine_from_results should activate counterexample strategies for missed FALSE problems."""
        run_data = {
            "summary": {"run_id": "test001", "accuracy": 0.5, "correct": 1, "evaluated": 2},
            "results": [
                {
                    "problem_id": "p1",
                    "equation1": "x=y",
                    "equation2": "y=x",
                    "ground_truth": "TRUE",
                    "verdict": "FALSE",
                    "is_correct": False,
                },
                {
                    "problem_id": "p2",
                    "equation1": "x*x=x",
                    "equation2": "x=y",
                    "ground_truth": "FALSE",
                    "verdict": "FALSE",
                    "is_correct": True,
                },
            ],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(run_data, f)
            tmp_path = f.name
        try:
            refined = refine_from_results(tmp_path, base_bundles=["baseline"])
            # Should include substitution_chain because of missed TRUE
            assert "substitution_chain" in refined
            assert len(refined.encode("utf-8")) <= MAX_BYTES
        finally:
            os.unlink(tmp_path)


# ===========================================================================
# utils.py tests
# ===========================================================================

class TestUtils:
    def test_compute_hash_deterministic(self):
        h1 = compute_hash("hello world")
        h2 = compute_hash("hello world")
        assert h1 == h2
        assert len(h1) == 12  # truncated to 12 chars

    def test_compute_hash_differs(self):
        assert compute_hash("a") != compute_hash("b")

    def test_save_and_load_jsonl(self, tmp_path):
        data = [{"id": "p1", "eq": "x=y"}, {"id": "p2", "eq": "y=x"}]
        fp = str(tmp_path / "test.jsonl")
        save_jsonl(data, fp)
        loaded = load_jsonl(fp)
        assert loaded == data

    def test_load_jsonl_missing_file_returns_empty(self, tmp_path):
        result = load_jsonl(str(tmp_path / "nonexistent.jsonl"))
        assert result == []

    def test_save_and_load_json(self, tmp_path):
        data = {"summary": {"accuracy": 0.8}, "results": []}
        fp = str(tmp_path / "run.json")
        save_json(data, fp)
        loaded = load_json(fp)
        assert loaded["summary"]["accuracy"] == 0.8

    def test_summarize_results_all_correct(self):
        results = [
            {"problem_id": "p1", "ground_truth": "TRUE", "verdict": "TRUE", "is_correct": True,
             "latency": 1.0, "usage": {"total_tokens": 100}},
            {"problem_id": "p2", "ground_truth": "FALSE", "verdict": "FALSE", "is_correct": True,
             "latency": 2.0, "usage": {"total_tokens": 200}},
        ]
        s = summarize_results(results)
        assert s["accuracy"] == 1.0
        assert s["correct"] == 2
        assert s["true_accuracy"] == 1.0
        assert s["false_accuracy"] == 1.0
        assert s["missed_problems"] == []
        assert s["total_tokens"] == 300

    def test_summarize_results_with_errors(self):
        results = [
            {"problem_id": "p1", "error": "Timeout"},
            {"problem_id": "p2", "ground_truth": "TRUE", "verdict": "TRUE", "is_correct": True,
             "latency": 1.0, "usage": {"total_tokens": 100}},
        ]
        s = summarize_results(results)
        assert s["errors"] == 1
        assert s["evaluated"] == 1

    def test_compare_runs(self):
        run_a = {"summary": {"accuracy": 0.5, "avg_latency_sec": 2.0, "model": "m1", "cheatsheet_hash": "abc"}}
        run_b = {"summary": {"accuracy": 0.7, "avg_latency_sec": 1.5, "model": "m2", "cheatsheet_hash": "def"}}
        delta = compare_runs(run_a, run_b)
        assert delta["accuracy_delta"] == pytest.approx(0.2, abs=0.001)
        assert delta["improved"] is True
        assert delta["latency_delta_sec"] == pytest.approx(-0.5, abs=0.001)

    def test_format_timestamp(self):
        ts = format_timestamp()
        assert len(ts) == 15  # YYYYMMDDTHHmmss
        assert "T" in ts


# ===========================================================================
# download_data.py tests
# ===========================================================================

class TestDownloadData:
    def test_verify_integrity_valid_jsonl(self, tmp_path):
        fp = tmp_path / "test.jsonl"
        fp.write_text('{"id": "1", "eq": "x=y"}\n{"id": "2", "eq": "y=x"}\n')
        assert verify_dataset_integrity(str(fp)) is True

    def test_verify_integrity_empty_file(self, tmp_path):
        fp = tmp_path / "empty.jsonl"
        fp.write_text("")
        assert verify_dataset_integrity(str(fp)) is False

    def test_verify_integrity_invalid_json(self, tmp_path):
        fp = tmp_path / "bad.jsonl"
        fp.write_text("{invalid json line}\n")
        assert verify_dataset_integrity(str(fp)) is False

    def test_verify_integrity_missing_file(self, tmp_path):
        assert verify_dataset_integrity(str(tmp_path / "nonexistent.jsonl")) is False

    def test_list_local_datasets_empty_dir(self, tmp_path):
        result = list_local_datasets(str(tmp_path))
        assert result == {}

    def test_list_local_datasets_finds_jsonl(self, tmp_path):
        sub = tmp_path / "data"
        sub.mkdir()
        (sub / "normal.jsonl").write_text('{"id": "p1"}\n')
        result = list_local_datasets(str(tmp_path))
        assert len(result) == 1
        assert list(result.values())[0]["valid"] is True
