from codomyrmex.coding.execution.executor import execute_code

generated_code = '''
def factorial(n):
    """Calculate factorial of n using recursion."""
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n - 1)

# Test the function
result = factorial(5)
print(f"Factorial of 5 is: {result}")
'''

print(execute_code(language="python", code=generated_code, timeout=10))
