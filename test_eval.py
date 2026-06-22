import ast
import operator

_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def _safe_eval(node, variables, functions):
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body, variables, functions)
    elif isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError(f"Unsupported constant type: {type(node.value)}")
    elif isinstance(node, ast.Name):
        if node.id in variables:
            return variables[node.id]
        raise ValueError(f"Unknown variable: {node.id}")
    elif isinstance(node, ast.BinOp):
        op = type(node.op)
        if op not in _ALLOWED_OPS:
            raise ValueError(f"Unsupported operator: {op}")
        left = _safe_eval(node.left, variables, functions)
        right = _safe_eval(node.right, variables, functions)
        return _ALLOWED_OPS[op](left, right)
    elif isinstance(node, ast.UnaryOp):
        op = type(node.op)
        if op not in _ALLOWED_OPS:
            raise ValueError(f"Unsupported unary operator: {op}")
        operand = _safe_eval(node.operand, variables, functions)
        return _ALLOWED_OPS[op](operand)
    elif isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Only simple function calls are supported")
        func_name = node.func.id
        if func_name not in functions:
            raise ValueError(f"Unknown function: {func_name}")
        func = functions[func_name]
        args = [_safe_eval(arg, variables, functions) for arg in node.args]
        return func(*args)
    else:
        raise ValueError(f"Unsupported expression node: {type(node)}")

print(_safe_eval(ast.parse("relu(x * 2 + y)", mode='eval'), {"x": 3.0, "y": -1.0}, {"relu": lambda x: max(0, x)}))
print(_safe_eval(ast.parse("-x", mode='eval'), {"x": 3.0}, {}))
print(_safe_eval(ast.parse("x**2", mode='eval'), {"x": 3.0}, {}))
