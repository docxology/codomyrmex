"""Real Z3 models and subprocess-isolated capability rejection regressions."""

import json
import subprocess
import sys

import pytest

pytest.importorskip("z3")

from codomyrmex.formal_verification.backends.z3_backend import Z3Backend


@pytest.mark.unit
@pytest.mark.parametrize(
    "item",
    [
        "z3.os.system('exit 1')",
        "z3.sys.modules['os'].system('exit 1')",
        "z3.z3core.ctypes.CDLL(None)",
        "z3.open_log('forbidden.log')",
        "z3.parse_smt2_file('secret.smt2')",
        "solver.from_file('secret.smt2')",
        "optimizer.from_file('secret.smt2')",
        "z3.Z3_open_log('forbidden.log')",
        "z3.Context()",
        "Solver(logFile='forbidden.log')",
        "z3.Solver(logFile='forbidden.log')",
        "s = z3.Solver; s(None, None, 'forbidden.log')",
        "Optimize()",
        "solver.ctx.ref()",
        "solver.ctx_ref()",
        "solver.set(timeout=0)",
        "solver.check()",
        "z3.set_param('timeout', 0)",
        "x = Int('x'); x.ctx.ref()",
        "x = Int('x'); x.as_ast()",
        "z3.__dict__",
        "import os",
        "f = z3.open_log; f('forbidden.log')",
    ],
)
def test_forbidden_capabilities_in_subprocess(item, tmp_path):
    code = (
        "import json, sys\n"
        "from codomyrmex.formal_verification.backends.z3_backend import Z3Backend\n"
        "from codomyrmex.formal_verification.exceptions import ModelBuildError\n"
        "backend = Z3Backend()\n"
        "backend.add_item(json.loads(sys.argv[1]))\n"
        "try:\n"
        "    backend.solve_model()\n"
        "except ModelBuildError:\n"
        "    sys.exit(0)\n"
        "sys.exit(3)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code, json.dumps(item)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert not (tmp_path / "forbidden.log").exists()


@pytest.mark.unit
@pytest.mark.parametrize(
    "items",
    [
        ["x, y = Ints('x y')", "solver.add(x + y == 12, x > 5, y < 10)"],
        ["x = z3.Int('x')", "s = solver; add = s.add", "add(x == 42)"],
        [
            "a = Array('a', IntSort(), IntSort())",
            "solver.add(Select(Store(a, 1, 2), 1) == 2)",
        ],
        ["x = BitVec('x', 8)", "solver.add(ULT(x, BitVecVal(10, 8)))"],
        ["f = Function('f', IntSort(), IntSort())", "solver.add(f(1) == 2)"],
        ["x = Int('x')", "optimizer.add(x >= 1, x <= 10)", "optimizer.maximize(x)"],
        ["x = Int('x')", "solver.add(ForAll([x], x + 1 > x))"],
    ],
)
def test_supported_model_building(items):
    backend = Z3Backend()
    for item in items:
        backend.add_item(item)
    result = backend.solve_model()
    assert result.status.value == "sat"
