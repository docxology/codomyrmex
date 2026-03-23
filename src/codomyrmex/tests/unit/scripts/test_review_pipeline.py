"""Smoke and integration tests for scripts/review (subprocess, real git, real SARIF files)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[5]
REVIEW_DIR = REPO_ROOT / "scripts" / "review"
FIXTURES = REPO_ROOT / "src" / "codomyrmex" / "tests" / "fixtures" / "review"


def _run_script(
    name: str, args: list[str], cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    script = REVIEW_DIR / name
    cmd = [sys.executable, str(script), *args]
    return subprocess.run(
        cmd,
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.unit
def test_sarif_merge_dedupes(tmp_path: Path) -> None:
    out = tmp_path / "merged.sarif"
    r = _run_script(
        "sarif_merge.py",
        [
            str(FIXTURES / "sample_a.sarif"),
            str(FIXTURES / "sample_b.sarif"),
            "-o",
            str(out),
        ],
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    results = []
    for run in data["runs"]:
        results.extend(run.get("results") or [])
    rule_ids = [x["ruleId"] for x in results]
    assert "rule-a" in rule_ids
    assert "rule-b" in rule_ids
    assert len(results) == 2


@pytest.mark.unit
def test_sarif_utils_summarize() -> None:
    sys.path.insert(0, str(REVIEW_DIR))
    try:
        from sarif_utils import load_sarif, summarize_sarif

        data = load_sarif(FIXTURES / "sample_a.sarif")
        s = summarize_sarif(data)
        assert s["total_results"] == 1
        assert s["by_level"].get("error") == 1
    finally:
        sys.path.remove(str(REVIEW_DIR))


@pytest.mark.unit
def test_pr_analyzer_git_repo(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "review@test.local"],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(["git", "config", "user.name", "review"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("# base\n", encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init", "--no-verify"],
        cwd=tmp_path,
        check=True,
    )
    subprocess.run(["git", "checkout", "-b", "feature"], cwd=tmp_path, check=True)
    (tmp_path / "new.py").write_text(
        "api_key = 'notreallysecret123456'\n", encoding="utf-8"
    )
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "commit", "-m", "add secret-like line", "--no-verify"],
        cwd=tmp_path,
        check=True,
    )
    r = _run_script(
        "pr_analyzer.py",
        [str(tmp_path), "--base", "main", "--head", "feature", "--json"],
        cwd=tmp_path,
    )
    assert r.returncode == 0, r.stderr
    payload = json.loads(r.stdout)
    assert payload["findings_count"] >= 1
    assert any(f["category"] == "hardcoded_secret" for f in payload["findings"])


@pytest.mark.unit
def test_code_quality_checker_long_function(tmp_path: Path) -> None:
    body = "\n".join(["    pass"] * 55)
    src = f"def long_one():\n{body}\n"
    p = tmp_path / "mod.py"
    p.write_text(src, encoding="utf-8")
    r = _run_script(
        "code_quality_checker.py", [str(p), "--language", "python", "--json"]
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(r.stdout)
    assert any(i["kind"] == "long_function" for i in data["issues"])


@pytest.mark.unit
def test_bandit_json_to_sarif(tmp_path: Path) -> None:
    out = tmp_path / "out.sarif"
    r = _run_script(
        "bandit_json_to_sarif.py",
        [str(FIXTURES / "bandit_min.json"), str(out)],
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    results = data["runs"][0]["results"]
    assert len(results) == 1
    assert results[0]["ruleId"] == "B105"
    assert results[0]["level"] == "error"
    assert results[0]["locations"][0]["physicalLocation"]["region"]["startLine"] == 7


@pytest.mark.unit
def test_review_report_generator_markdown(tmp_path: Path) -> None:
    pr_path = tmp_path / "pr.json"
    pr_path.write_text(
        json.dumps({"risk": "low", "findings_count": 0, "complexity_score": 2}),
        encoding="utf-8",
    )
    out = tmp_path / "out.md"
    r = _run_script(
        "review_report_generator.py",
        [
            str(tmp_path),
            "--pr-analysis",
            str(pr_path),
            "--format",
            "markdown",
            "--output",
            str(out),
        ],
        cwd=tmp_path,
    )
    assert r.returncode == 0, r.stderr
    text = out.read_text(encoding="utf-8")
    assert "Verdict" in text
    assert "approve" in text.lower() or "suggestions" in text.lower()
