import re
import json

MATH_FUNCTIONS = json.load(open("mathematics/function_list.json", "r"))


def check_alphabet(equation, order):
    """
    The function takes an equation
    and the order of the differential equation
    and checks if it is written correctly.
    """
    if order == "First":
        alphabet = ['x', 'y']
    elif order == "Second":
        alphabet = ['x', 'y', 'z']
    else:
        return False

    tokens = re.findall(r'[a-zA-Z]+|\d+|\S', equation)

    for token in tokens:
        if token.isalpha() and token not in alphabet and token not in MATH_FUNCTIONS:
            return False
    
    return True
