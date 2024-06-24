import re
import json

PY_DIR = "solver-bot/src/main/python/"

MATH_FUNCTIONS = json.load(open(
    PY_DIR + "mathematics/function_list.json", "r"))


def replace_math_functions(equation):
    """
    The function accepts an equation
    and checks if there are trigonometric functions there,
    if there are, it converts them.
    """
    for func, replacement in MATH_FUNCTIONS.items():
        if func in ['coth', 'cth']:
            equation = re.sub(rf'\b{func}\((.*?)\)',
                              r'(cosh(\1) / sinh(\1))',
                              equation)
        elif func in ['acot', 'actg', 'arccot', 'arcctg']:
            equation = re.sub(rf'\b{func}\((.*?)\)',
                              r'(atan(1 / \1))',
                              equation)
        else:
            equation = re.sub(rf'\b{func}\b',
                              f'{replacement}',
                              equation)

    return equation
