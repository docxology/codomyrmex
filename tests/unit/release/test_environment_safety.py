"""Suite-level gate: no test may rebuild the environment it is running in.

`uv run` re-resolves the project environment against `.python-version`. When the
running interpreter differs, that resolution **deletes and recreates `.venv`**:
a probe on a 3.12 environment replaced 970 site-packages entries with 165 and
left `lib/python3.12` gone. A test that does this from `cwd=REPO_ROOT` destroys
the environment every other test in the session imports from, and the failures
land in unrelated modules as `ModuleNotFoundError` long after the destructive
test has passed. The 3.11 leg was immune only because a matching environment
makes `uv run` a no-op, which is why the symptom looked version-specific.

Two shapes are refused:

- a subprocess `uv` invocation whose argv lacks `--no-sync` (and, for `run`,
  `--python`, since an unnamed interpreter falls back to `.python-version`);
- a subprocess invocation of a bare interpreter name (`python`, `python3`,
  `python3.12`, …), which runs whatever `PATH` resolves rather than the
  interpreter under test.

The scan parses each module with `ast`, so a comment or a docstring that
mentions `--no-sync` cannot satisfy it, and the controls below prove the gate
still refuses known-bad argv. The controls are part of the test: a gate that has
never been shown to fail is a gate nobody has evidence about.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

TESTS_ROOT = Path(__file__).resolve().parents[2]

SUBPROCESS_FUNCTIONS = frozenset({"run", "Popen", "check_output", "check_call", "call"})
MUTATING_VERBS = frozenset({"add", "remove", "lock", "sync"})
BARE_INTERPRETERS = frozenset({"python", "python3", "py"})
EXECUTABLE_TOKEN = "@sys.executable"


@dataclass(frozen=True)
class Finding:
    """One unsafe subprocess invocation, named by source position and argv."""

    path: Path
    line: int
    argv: tuple[str, ...]
    reason: str

    def describe(self) -> str:
        return f"{self.path}:{self.line}: {self.reason}\n    argv = {list(self.argv)}"


def _element_token(element: ast.expr) -> str | None:
    """Read one argv element, or None when it is not statically knowable."""
    if isinstance(element, ast.Constant) and isinstance(element.value, str):
        return element.value
    if (
        isinstance(element, ast.Attribute)
        and element.attr == "executable"
        and isinstance(element.value, ast.Name)
        and element.value.id == "sys"
    ):
        return EXECUTABLE_TOKEN
    return None


def _argv_elements(node: ast.expr) -> list[ast.expr] | None:
    if isinstance(node, ast.List | ast.Tuple):
        return list(node.elts)
    return None


def _literal_argv(node: ast.expr) -> tuple[str, ...] | None:
    """Return the argv when every element is statically knowable, else None.

    `sys.executable` is kept as a token rather than discarded, so a pinned
    interpreter still reads as pinned instead of turning the call unreadable.
    """
    elements = _argv_elements(node)
    if elements is None:
        return None
    parts = [_element_token(element) for element in elements]
    if any(part is None for part in parts):
        return None
    return tuple(part for part in parts if part is not None)


def _known_prefix(node: ast.expr) -> tuple[str, ...]:
    """Read the statically knowable leading tokens of an argv."""
    elements = _argv_elements(node)
    if not elements:
        return ()
    tokens: list[str] = []
    for element in elements:
        token = _element_token(element)
        if token is None:
            break
        tokens.append(token)
    return tuple(tokens)


def _is_subprocess_call(node: ast.Call) -> bool:
    func = node.func
    name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
    return name in SUBPROCESS_FUNCTIONS


def _judge_unknown_tail(known: tuple[str, ...]) -> list[str]:
    """Reasons an argv with an unreadable tail is still refused."""
    if not known:
        return []
    name = Path(known[0]).name
    if name == "uv":
        # `uv build`/`uv pip` do not resolve the project environment, so only a
        # run/sync verb — or a prefix too short to rule one out — is refused.
        verb_visible = "run" in known or "sync" in known
        if verb_visible or len(known) == 1:
            return [
                "`uv` invocation whose argv is not a literal list, so the gate "
                "cannot prove `--no-sync` is present"
            ]
        return []
    if _is_bare_python(name):
        return [
            f"`{name}` runs whatever PATH resolves; use `sys.executable` "
            "for the interpreter under test"
        ]
    return []


def _is_bare_python(program: str) -> bool:
    return program in BARE_INTERPRETERS or (
        program.startswith("python3.") and program[8:].isdigit()
    )


def _verb(argv: tuple[str, ...]) -> str:
    for token in argv[1:]:
        if not token.startswith("-"):
            return token
    return ""


def _judge(argv: tuple[str, ...]) -> list[str]:
    """Return the reasons this argv is unsafe; empty when it is safe."""
    reasons: list[str] = []
    program = Path(argv[0]).name if argv else ""

    if program == "uv" and _verb(argv) in MUTATING_VERBS:
        reasons.append(
            f"`uv {_verb(argv)}` rewrites pyproject.toml and the lockfile and "
            "re-resolves the shared environment; no test may run it"
        )

    if program == "uv" and ("run" in argv or "sync" in argv):
        if "--no-sync" not in argv:
            reasons.append(
                "`uv run`/`uv sync` without `--no-sync` re-resolves the project "
                "environment and rebuilds .venv when .python-version differs"
            )
        if "run" in argv and "--python" not in argv:
            reasons.append(
                "`uv run` without `--python` lets .python-version choose the "
                "interpreter instead of `sys.executable`"
            )

    if _is_bare_python(program):
        reasons.append(
            f"`{program}` runs whatever PATH resolves; use `sys.executable` "
            "for the interpreter under test"
        )
    return reasons


def scan_source(source: str, path: Path) -> list[Finding]:
    """Find unsafe subprocess invocations in one module's source."""
    tree = ast.parse(source, filename=str(path))

    assignments: dict[str, tuple[str, ...]] = {}
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            argv = _literal_argv(node.value)
            if argv is not None:
                assignments[node.targets[0].id] = argv

    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not _is_subprocess_call(node):
            continue
        if not node.args:
            continue
        argv = _literal_argv(node.args[0])
        if argv is None and isinstance(node.args[0], ast.Name):
            argv = assignments.get(node.args[0].id)
        if argv is None:
            known = _known_prefix(node.args[0])
            for reason in _judge_unknown_tail(known):
                findings.append(Finding(path, node.lineno, (*known, "…"), reason))
            continue
        for reason in _judge(argv):
            findings.append(Finding(path, node.lineno, argv, reason))
    return findings


def _test_modules() -> list[Path]:
    return sorted(
        path
        for path in TESTS_ROOT.rglob("test_*.py")
        if ".venv" not in path.parts and "__pycache__" not in path.parts
    )


def test_no_test_module_mutates_the_project_environment() -> None:
    findings = [
        finding
        for path in _test_modules()
        for finding in scan_source(path.read_text(encoding="utf-8"), path)
    ]
    assert not findings, (
        "unsafe subprocess invocations in the suite:\n\n"
        + "\n\n".join(finding.describe() for finding in findings)
    )


def test_the_runtime_guard_classifies_the_same_shapes(tmp_path: Path) -> None:
    """The spawn-time guard must refuse what the static gate refuses.

    The static scan cannot see a spawn production code performs on a test's
    behalf (`HermesClient._heal_environment` runs `uv add <pkg>` in the process
    working directory), so `tests/support/uv_spawns.py` re-checks at the spawn.
    Its classifier is pure, so the shapes are testable without spawning uv.
    """
    from tests.support.uv_spawns import violation_for

    repo = tmp_path / "repo"
    (repo / ".venv").mkdir(parents=True)
    inside = repo
    outside = tmp_path / "elsewhere"
    outside.mkdir()

    refused = [
        (("uv", "add", "requests"), inside),
        (("uv", "remove", "requests"), inside),
        (("uv", "sync"), inside),
        (("uv", "lock"), outside),
        (("uv", "run", "pytest"), inside),
    ]
    for argv, cwd in refused:
        assert violation_for(argv, cwd, repo) is not None, argv

    allowed = [
        (("uv", "run", "--no-sync", "--python", "x", "pytest"), inside),
        (("uv", "run", "pytest"), outside),
        (("uv", "build", "--out-dir", "dist"), inside),
        (("uv", "init"), inside),
        (("uv", "--version"), inside),
        (("git", "status"), inside),
    ]
    for argv, cwd in allowed:
        assert violation_for(argv, cwd, repo) is None, argv


def test_the_gate_scans_the_real_population() -> None:
    """A gate over an empty or wrong population would pass for the wrong reason."""
    modules = _test_modules()
    assert len(modules) > 1000
    relative = {path.relative_to(TESTS_ROOT).as_posix() for path in modules}
    assert "unit/colony_kernel/test_manuscript_consistency.py" in relative
    assert "unit/examples/test_example_execution.py" in relative


@pytest.mark.parametrize(
    ("source", "expected_reasons"),
    [
        # The defect that produced ~130 failures per 3.12+ leg.
        (
            'subprocess.run(["uv", "run", "--locked", "--group", "docs", "mkdocs"])',
            2,
        ),
        # A comment carrying the flag must not satisfy the gate.
        (
            'subprocess.run(["uv", "run", "pytest"])  # --no-sync --python\n',
            2,
        ),
        # `sync` is refused for the same reason.
        ('subprocess.run(["uv", "sync", "--locked"])', 2),
        ('subprocess.run(["uv", "add", "requests"])', 1),
        ('subprocess.run(["uv", "lock", "--check"])', 1),
        # argv assembled in a variable is still read.
        (
            'cmd = ["uv", "run", "pytest"]\nsubprocess.run(cmd)',
            2,
        ),
        # A bare interpreter is the same defect wearing different clothes.
        ('subprocess.check_output(["python3.12", "script.py"])', 1),
        ('subprocess.run(["python", "script.py"])', 1),
        # argv with a computed element is still read by its program name.
        ('subprocess.run(["python", str(script_path)])', 1),
        ('subprocess.run(["uv", "run", *extra_args])', 1),
        ('subprocess.run(["uv", *extra_args])', 1),
    ],
)
def test_the_gate_refuses_known_bad_invocations(
    source: str, expected_reasons: int, tmp_path: Path
) -> None:
    findings = scan_source(source, tmp_path / "sample.py")
    assert len(findings) == expected_reasons, [f.reason for f in findings]


@pytest.mark.parametrize(
    "source",
    [
        'subprocess.run(["uv", "run", "--no-sync", "--python", sys.executable, "pytest"])',
        'subprocess.run([sys.executable, "-m", "pytest", "tests/unit"])',
        'subprocess.run(["git", "-C", path, "status"])',
        'subprocess.run(["uv", "build", "--out-dir", out])',
    ],
)
def test_the_gate_accepts_safe_invocations(source: str, tmp_path: Path) -> None:
    findings = scan_source(source, tmp_path / "sample.py")
    assert findings == [], [f.reason for f in findings]
