"""Real Ruff runners preserve diagnostics without creating workspace caches."""

from pathlib import Path

import pytest

from codomyrmex.coding.review.mixins.traditional import TraditionalMixin
from codomyrmex.coding.static_analysis.tool_runners import ToolRunner


@pytest.mark.unit
@pytest.mark.parametrize("runner_kind", ["static_analysis", "review"])
def test_ruff_diagnostics_do_not_create_cache(
    runner_kind: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    source = tmp_path / "example.py"
    source.write_text("import os\n", encoding="utf-8")
    (tmp_path / "ruff.toml").write_text('[lint]\nselect = ["F"]\n', encoding="utf-8")
    if runner_kind == "static_analysis":
        results = ToolRunner({"ruff": True}, str(tmp_path)).run_ruff(str(source))
    else:
        results = TraditionalMixin()._run_ruff(str(source))

    assert any(result.rule_id == "F401" for result in results)
    assert sorted(path.name for path in tmp_path.iterdir()) == [
        "example.py",
        "ruff.toml",
    ]
