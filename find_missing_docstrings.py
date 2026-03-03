import ast
import os

def check_file(filepath):
    with open(filepath, 'r') as f:
        source = f.read()

    tree = ast.parse(source)
    missing = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if not node.name.startswith('_'):
                if not ast.get_docstring(node):
                    missing.append(node.name)

    if missing:
        print(f"{filepath}: {missing}")

for root, _, files in os.walk('src/codomyrmex/cerebrum'):
    for file in files:
        if file.endswith('.py'):
            check_file(os.path.join(root, file))
