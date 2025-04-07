import re
import json

PY_DIR = "solver-bot/src/main/python/"

MATH_FUNCTIONS = json.load(open(
    PY_DIR + "equation/functions.json", "r", encoding="utf-8"))


def validate_symbols(equation):
    allowed_vars = {'x', 'y', 'X', 'Y'}
    symbols = re.findall(r'[a-zA-Z]+|\d+|\S', equation)
    for symbol in symbols:
        if symbol.isalpha() and symbol not in allowed_vars and symbol not in MATH_FUNCTIONS:
            return False, symbol
    return True, None


def validate_parentheses(equation):
    stack = []
    for i, char in enumerate(equation):
        if char == '(':
            stack.append(i)
        elif char == ')':
            if not stack:
                return False
            start_index = stack.pop()
            # Check for empty parentheses
            if start_index + 1 == i:
                return False

    if stack:
        return False
    return True
