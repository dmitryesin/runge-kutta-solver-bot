import numpy as np
import requests

from equation.function_replacer import replace_math_functions
from telegram.ext import (
    ContextTypes
)

JAVA_SERVER_URL = "http://localhost:8080/api/solver"


async def get_solution(context: ContextTypes.DEFAULT_TYPE):
    (user_id,
     method,
     order,
     equation,
     initial_x,
     initial_y,
     reach_point,
     step_size) = await extract_user_data(context)

    try:
        set_java_parameters(user_id,
                            method,
                            order,
                            equation,
                            initial_x,
                            initial_y,
                            reach_point,
                            step_size)
        response = requests.get(f"{JAVA_SERVER_URL}/solution",
                                timeout=10)
        response.raise_for_status()
        result = response.json()
    except (ValueError, requests.RequestException):
        return None

    return result


async def extract_user_data(context: ContextTypes.DEFAULT_TYPE):
    data = context.user_data

    return (
        context._user_id,
        data['method'],
        data['order'],
        data['equation'],
        data['initial_x'],
        data['initial_y'],
        data['reach_point'],
        data['step_size']
    )


def set_java_parameters(user_id, method, order, equation, initial_x, initial_y, reach_point, step_size):
    method_mapping = {
        "method_euler": 1,
        "method_modified_euler": 2,
        "method_runge_kutta": 4,
        "method_dormand_prince": 7
    }

    payload = {
        "userId": user_id,
        "method": method_mapping.get(method, 1),
        "order": int(order),
        "equation": replace_math_functions(equation),
        "initialX": float(initial_x),
        "initialY": list(map(float, initial_y.split())),
        "reachPoint": float(reach_point),
        "stepSize": float(step_size)
    }

    response = requests.post(f"{JAVA_SERVER_URL}/solve",
                             json=payload,
                             timeout=10)
    response.raise_for_status()


def set_user_settings(user_id, language, rounding, method):
    payload = {
        "language": language,
        "rounding": rounding,
        "method": method
    }

    response = requests.post(f"{JAVA_SERVER_URL}/user-settings/{user_id}",
                             params=payload,
                             timeout=10)
    response.raise_for_status()
    return response.text


def get_user_settings(user_id):
    response = requests.get(f"{JAVA_SERVER_URL}/user-settings/{user_id}",
                            timeout=10)
    response.raise_for_status()
    return response.json()


def get_x_values():
    response = requests.get(f"{JAVA_SERVER_URL}/x-values",
                            timeout=10)
    response.raise_for_status()
    return np.array(response.json())


def get_y_values():
    response = requests.get(f"{JAVA_SERVER_URL}/y-values",
                            timeout=10)
    response.raise_for_status()
    return np.array(response.json())


def get_result_info(result, order, rounding):
    try:
        order = int(order)
    except ValueError:
        return ""

    superscripts = "⁰¹²³⁴⁵⁶⁷⁸⁹"

    def get_variable_name(i):
        if i < 4:
            return f"y{chr(39) * i}"
        return f"y{"⁽"}{''.join(superscripts[int(d)] for d in str(i))}{"⁾"}"

    result_str = f"x: {result[0]:.2f}"
    variable_names = ["y"] + [get_variable_name(i) for i in range(1, int(order))]

    for i in range(1, order + 1):
        if i < len(result):
            result_str += f", {variable_names[i-1]}: {result[i]:.{rounding}f}"
        else:
            result_str += f", {variable_names[i-1]}: NaN"

    return result_str
