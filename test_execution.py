from codomyrmex.coding.execution.executor import execute_code
result = execute_code(
    language="python",
    code="""
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)

print(f"Factorial of 5 is: {factorial(5)}")
"""
)
print("Result:")
print(result)
