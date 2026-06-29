from codomyrmex.coding import ExecutionLimits, execute_with_limits

limits = ExecutionLimits(
    time_limit=5,
    memory_limit=64,
    cpu_limit=0.5,
    max_output_chars=1000,
)

safe_code = """
def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True

print(is_prime(17))
print(is_prime(20))
"""

execution_result = execute_with_limits(
    language="python", code=safe_code, limits=limits
)
print(execution_result)
