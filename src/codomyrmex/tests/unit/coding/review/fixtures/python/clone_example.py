"""
Example file with code clones for testing duplicate detection.
"""

def calculate_statistics_v1(data):
    """Calculate basic statistics for a list of numbers."""
    if not data:
        return {'count': 0, 'sum': 0, 'mean': 0, 'min': None, 'max': None}

    total = 0
    minimum = data[0]
    maximum = data[0]

    for value in data:
        total += value
        if value < minimum:
            minimum = value
        if value > maximum:
            maximum = value

    count = len(data)
    mean = total / count

    return {
        'count': count,
        'sum': total,
        'mean': mean,
        'min': minimum,
        'max': maximum
    }


def calculate_statistics_v2(numbers):
    """Calculate basic statistics for a list of numbers - similar to v1."""
    if not numbers:
        return {'count': 0, 'sum': 0, 'mean': 0, 'min': None, 'max': None}

    total = 0
    minimum = numbers[0]
    maximum = numbers[0]

    for value in numbers:
        total += value
        if value < minimum:
            minimum = value
        if value > maximum:
            maximum = value

    count = len(numbers)
    mean = total / count

    return {
        'count': count,
        'sum': total,
        'mean': mean,
        'min': minimum,
        'max': maximum
    }


class DataProcessor:
    """A class that might have similar methods."""

    def process_data_v1(self, items):
        """Process data with validation."""
        if not items:
            return []

        result = []
        for item in items:
            if item is not None:
                if isinstance(item, str):
                    result.append(item.strip())
                elif isinstance(item, (int, float)):
                    result.append(item)
                else:
                    result.append(str(item))

        return result

    def process_data_v2(self, items):
        """Process data with validation - similar to v1."""
        if not items:
            return []

        result = []
        for item in items:
            if item is not None:
                if isinstance(item, str):
                    result.append(item.strip())
                elif isinstance(item, (int, float)):
                    result.append(item)
                else:
                    result.append(str(item))

        return result

