"""Z3 SMT solver backend.

Wraps the z3-solver pip package to provide constraint solving over
booleans, integers, reals, bitvectors, and arrays with quantifier support.

References:
    - Z3 Prover: https://github.com/Z3Prover/z3
    - mcp-solver Z3 mode: https://github.com/szeider/mcp-solver
"""

from __future__ import annotations

import ast
import contextlib
from typing import Any

# Deliberately exclude file parsers, logging/configuration, native bindings,
# contexts, and imported Python modules. A callable's origin is not a sandbox.
_MODEL_NAMES = frozenset(
    [
        "Int",
        "Ints",
        "IntVal",
        "Real",
        "Reals",
        "RealVal",
        "Bool",
        "Bools",
        "BoolVal",
        "BitVec",
        "BitVecs",
        "BitVecVal",
        "Array",
        "Const",
        "Consts",
        "Function",
        "IntSort",
        "RealSort",
        "BoolSort",
        "BitVecSort",
        "ArraySort",
        "And",
        "Or",
        "Not",
        "Implies",
        "If",
        "Xor",
        "ForAll",
        "Exists",
        "Sum",
        "Product",
        "Distinct",
        "Abs",
        "ToReal",
        "ToInt",
        "IsInt",
        "Select",
        "Store",
        "K",
        "Concat",
        "Extract",
        "ZeroExt",
        "SignExt",
        "ULT",
        "ULE",
        "UGT",
        "UGE",
        "LShR",
        "RotateLeft",
        "RotateRight",
        "sat",
        "unsat",
        "unknown",
    ]
)
_SOLVER_METHODS = frozenset(
    {"add", "assert_and_track", "push", "pop", "reset", "assertions"}
)
_OPTIMIZER_METHODS = frozenset(
    {"add", "add_soft", "minimize", "maximize", "push", "pop", "assertions"}
)
_EXPRESSION_METHODS = frozenset(
    {"sort", "size", "as_long", "as_fraction", "as_decimal", "sexpr"}
)


def _model_attribute(obj: Any, name: str) -> Any:
    """Resolve only model-building capabilities, never arbitrary attributes."""
    if name.startswith("_"):
        raise AttributeError("Access to private attributes is forbidden")
    allowed: frozenset[str] = frozenset()
    if obj is z3:
        allowed = _MODEL_NAMES
    elif isinstance(obj, z3.Solver):
        allowed = _SOLVER_METHODS
    elif isinstance(obj, z3.Optimize):
        allowed = _OPTIMIZER_METHODS
    elif isinstance(obj, z3.ExprRef):
        allowed = _EXPRESSION_METHODS
    if name not in allowed:
        raise AttributeError(f"Model attribute {name!r} is not allowed")
    return getattr(obj, name)


def _model_callable(func: Any) -> bool:
    """Accept approved constructors, symbolic declarations, and bound methods."""
    if any(func is getattr(z3, name, None) for name in _MODEL_NAMES):
        return callable(func)
    if isinstance(func, z3.FuncDeclRef):
        return True
    owner = getattr(func, "__self__", None)
    name = getattr(func, "__name__", "")
    if owner is None:
        return False
    try:
        return func == _model_attribute(owner, name)
    except AttributeError:
        return False


def _safe_exec(code: str, namespace: dict[str, Any]) -> None:
    """Execute python statements safely by manually traversing the AST.

    This replaces `exec()` to prevent arbitrary code execution, only allowing
    variable assignments, basic function calls, array subscripts, math and
    comparison operations, and boolean logic necessary for Z3 model building.
    """
    tree = ast.parse(code, mode="exec")

    def _eval(node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Load):
                if node.id in namespace:
                    return namespace[node.id]
                raise NameError(f"Name {node.id!r} is not defined")
            if isinstance(node.ctx, ast.Store):
                return node.id
            raise TypeError(f"Unsupported Name context: {type(node.ctx)}")
        if isinstance(node, ast.Attribute):
            obj = _eval(node.value)
            return _model_attribute(obj, node.attr)
        if isinstance(node, ast.Call):
            func = _eval(node.func)
            if not _model_callable(func):
                raise TypeError("Only approved model-building calls are allowed")
            if any(kw.arg is None for kw in node.keywords):
                raise TypeError("Expanded keyword arguments are not allowed")
            args = [_eval(arg) for arg in node.args]
            kwargs = {
                kw.arg: _eval(kw.value) for kw in node.keywords if kw.arg is not None
            }
            return func(*args, **kwargs)
        if isinstance(node, ast.BinOp):
            left = _eval(node.left)
            right = _eval(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.Mod):
                return left % right
            if isinstance(node.op, ast.Pow):
                return left**right
            if isinstance(node.op, ast.BitXor):
                return left ^ right
            if isinstance(node.op, ast.BitOr):
                return left | right
            if isinstance(node.op, ast.BitAnd):
                return left & right
            if isinstance(node.op, ast.LShift):
                return left << right
            if isinstance(node.op, ast.RShift):
                return left >> right
            if isinstance(node.op, ast.FloorDiv):
                return left // right
            raise TypeError(f"Unsupported binary operator: {type(node.op)}")
        if isinstance(node, ast.UnaryOp):
            operand = _eval(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            if isinstance(node.op, ast.USub):
                return -operand
            if isinstance(node.op, ast.Not):
                return not operand
            if isinstance(node.op, ast.Invert):
                return ~operand
            raise TypeError(f"Unsupported unary operator: {type(node.op)}")
        if isinstance(node, ast.Compare):
            if len(node.ops) > 1:
                raise ValueError("Chained comparisons not fully supported")
            op = node.ops[0]
            left = _eval(node.left)
            right = _eval(node.comparators[0])
            if isinstance(op, ast.Eq):
                return left == right
            if isinstance(op, ast.NotEq):
                return left != right
            if isinstance(op, ast.Lt):
                return left < right
            if isinstance(op, ast.LtE):
                return left <= right
            if isinstance(op, ast.Gt):
                return left > right
            if isinstance(op, ast.GtE):
                return left >= right
            if isinstance(op, ast.Is):
                return left is right
            if isinstance(op, ast.IsNot):
                return left is not right
            if isinstance(op, ast.In):
                return left in right
            if isinstance(op, ast.NotIn):
                return left not in right
            raise TypeError(f"Unsupported comparison operator: {type(op)}")
        if isinstance(node, ast.List):
            return [_eval(elt) for elt in node.elts]
        if isinstance(node, ast.Tuple):
            return tuple(_eval(elt) for elt in node.elts)
        if isinstance(node, ast.Dict):
            return {
                _eval(k): _eval(v)
                for k, v in zip(node.keys, node.values, strict=False)
                if k is not None
            }
        if isinstance(node, ast.Subscript):
            value = _eval(node.value)
            slice_val = _eval(node.slice)
            return value[slice_val]
        if isinstance(node, ast.Slice):
            lower = _eval(node.lower) if node.lower else None
            upper = _eval(node.upper) if node.upper else None
            step = _eval(node.step) if node.step else None
            return slice(lower, upper, step)
        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                res = _eval(node.values[0])
                for v in node.values[1:]:
                    res = res and _eval(v)
                return res
            if isinstance(node.op, ast.Or):
                res = _eval(node.values[0])
                for v in node.values[1:]:
                    res = res or _eval(v)
                return res
            raise TypeError(f"Unsupported boolean operator: {type(node.op)}")
        raise TypeError(f"Unsupported AST node type: {type(node)}")

    for stmt in tree.body:
        if isinstance(stmt, ast.Assign):
            value = _eval(stmt.value)
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    namespace[target.id] = value
                elif isinstance(target, ast.Tuple):
                    for i, elt in enumerate(target.elts):
                        if isinstance(elt, ast.Name):
                            namespace[elt.id] = value[i]
                        else:
                            raise TypeError(
                                "Only simple assignments to variables are allowed"
                            )
                else:
                    raise TypeError("Only simple assignments to variables are allowed")
        elif isinstance(stmt, ast.Expr):
            _eval(stmt.value)
        else:
            raise TypeError(f"Unsupported statement type: {type(stmt)}")


z3 = None
with contextlib.suppress(ImportError):
    import z3

from codomyrmex.formal_verification.exceptions import (
    BackendNotAvailableError,
    ModelBuildError,
    SolverTimeoutError,
)

from .base import SolverBackend, SolverResult, SolverStatus


def _require_z3() -> None:
    """require Z3 ."""
    if z3 is None:
        raise BackendNotAvailableError(
            "z3-solver is not installed. Install with: pip install z3-solver"
        )


class Z3Backend(SolverBackend):
    """Z3 SMT solver backend implementing the mcp-solver 6-tool interface.

    Items are a restricted subset of Z3 Python expressions interpreted by an
    AST evaluator. Only approved constructors and model-building methods are
    reachable; solver timeouts do not isolate native code or model building.
    """

    def __init__(self) -> None:
        _require_z3()
        self._items: list[str] = []

    def clear_model(self) -> None:
        self._items.clear()

    def add_item(self, item: str, index: int | None = None) -> int:
        if index is None:
            self._items.append(item)
            return len(self._items) - 1
        self._items.insert(index, item)
        return index

    def delete_item(self, index: int) -> str:
        if not self._items:
            raise ModelBuildError(f"Cannot delete index {index}: model is empty")
        if not 0 <= index < len(self._items):
            raise ModelBuildError(
                f"Index {index} out of range (0-{len(self._items) - 1})"
            )
        return self._items.pop(index)

    def replace_item(self, index: int, new_item: str) -> str:
        if not self._items:
            raise ModelBuildError(f"Cannot replace index {index}: model is empty")
        if not 0 <= index < len(self._items):
            raise ModelBuildError(
                f"Index {index} out of range (0-{len(self._items) - 1})"
            )
        old = self._items[index]
        self._items[index] = new_item
        return old

    def get_model(self) -> list[tuple[int, str]]:
        return list(enumerate(self._items))

    def solve_model(self, timeout_ms: int = 30000) -> SolverResult:
        _require_z3()

        # Build a namespace with z3 imports for executing model items
        namespace: dict[str, Any] = {"z3": z3}
        # Pre-populate common z3 types for convenience
        for name in _MODEL_NAMES:
            if hasattr(z3, name):
                namespace[name] = getattr(z3, name)

        # Execute all items to build the model
        solver = z3.Solver()
        solver.set("timeout", timeout_ms)
        # Enable unsat core extraction by labeling assertions if needed
        solver.set("unsat_core", True)
        namespace["solver"] = solver

        # Provide an optimizer engine for optimization-oriented models.
        optimizer = z3.Optimize()
        optimizer.set("timeout", timeout_ms)
        namespace["optimizer"] = optimizer

        try:
            for idx, item in enumerate(self._items):
                try:
                    _safe_exec(item, namespace)
                except Exception as exc:
                    raise ModelBuildError(
                        f"Error executing item {idx}: {item!r}: {exc}"
                    ) from exc

            # If optimizer has assertions, use it; otherwise use solver
            engine = optimizer if optimizer.assertions() else solver
            result = engine.check()

            if result == z3.sat:
                z3_model = engine.model()
                model_dict = {}
                for decl in z3_model.decls():
                    val = z3_model[decl]
                    model_dict[str(decl)] = str(val)

                stats = {
                    "num_constraints": len(engine.assertions()),
                    "engine": "Optimize" if engine is optimizer else "Solver",
                }
                if engine is solver:
                    stats["num_scopes"] = solver.num_scopes()

                return SolverResult(
                    status=SolverStatus.SAT,
                    model=model_dict,
                    statistics=stats,
                )
            if result == z3.unsat:
                unsat_core = solver.unsat_core()
                core_labels = [str(c) for c in unsat_core]
                return SolverResult(
                    status=SolverStatus.UNSAT,
                    statistics={
                        "num_constraints": len(solver.assertions()),
                        "unsat_core": core_labels,
                    },
                )
            return SolverResult(
                status=SolverStatus.UNKNOWN,
                statistics={"num_constraints": len(solver.assertions())},
            )

        except ModelBuildError:
            raise
        except z3.Z3Exception as exc:
            if "timeout" in str(exc).lower():
                raise SolverTimeoutError(f"Z3 timeout after {timeout_ms}ms") from exc
            return SolverResult(
                status=SolverStatus.ERROR,
                error_message=str(exc),
            )

    def push(self) -> None:
        self._items.append("solver.push()")

    def pop(self, n: int = 1) -> None:
        self._items.append(f"solver.pop({n})")

    def backend_name(self) -> str:
        return "Z3 SMT Solver"
