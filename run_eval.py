from codomyrmex.coding.execution.executor import execute_code
result = execute_code(
    code="print('Hello from documentation test')", language="python", timeout=10
)
print("RESULT:", result)
