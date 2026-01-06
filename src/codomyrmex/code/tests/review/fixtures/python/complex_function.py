"""
Complex Python function for testing high complexity analysis.
"""

def highly_complex_function(data, config, options):
    """
    A highly complex function that should trigger complexity warnings.

    This function has multiple nested conditions, loops, and edge cases
    to test cyclomatic complexity calculation.
    """
    result = []

    if not data:
        return result

    if config.get('enabled', False):
        for item in data:
            if isinstance(item, dict):
                if 'type' in item:
                    if item['type'] == 'special':
                        if options.get('process_special', False):
                            if len(item.get('values', [])) > 0:
                                for value in item['values']:
                                    if value is not None:
                                        if isinstance(value, str):
                                            if len(value) > 10:
                                                result.append(value.upper())
                                            else:
                                                result.append(value.lower())
                                        elif isinstance(value, (int, float)):
                                            if value > 100:
                                                result.append(value * 2)
                                            elif value < 0:
                                                result.append(abs(value))
                                            else:
                                                result.append(value)
                                        else:
                                            result.append(str(value))
                                    else:
                                        result.append("NULL")
                            else:
                                result.append("EMPTY_SPECIAL")
                        else:
                            result.append("SKIPPED_SPECIAL")
                    elif item['type'] == 'normal':
                        if options.get('process_normal', True):
                            result.append(item.get('data', 'default'))
                        else:
                            result.append("SKIPPED_NORMAL")
                    else:
                        result.append("UNKNOWN_TYPE")
                else:
                    result.append("NO_TYPE")
            elif isinstance(item, list):
                if len(item) > 0:
                    for i, sub_item in enumerate(item):
                        if i % 2 == 0:
                            result.append(sub_item)
                        else:
                            result.append(sub_item * 2)
                else:
                    result.append("EMPTY_LIST")
            else:
                result.append(str(item))
    else:
        result.append("CONFIG_DISABLED")

    return result


def unreachable_code_example():
    """Function with unreachable code for dead code detection."""
    return "This function always returns"


def unused_variable_example():
    """Function with unused variables."""
    used_variable = "I am used"

    print(used_variable)
    return used_variable
