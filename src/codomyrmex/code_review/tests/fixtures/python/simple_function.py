"""
Simple Python function for testing basic complexity analysis.
"""

def simple_function(x, y):
    """A simple function with low complexity."""
    return x + y

def calculate_average(numbers):
    """Calculate average with basic conditional logic."""
    if not numbers:
        return 0
    return sum(numbers) / len(numbers)