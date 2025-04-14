import numpy as np
import requests

from equation.function_replacer import replace_math_functions

JAVA_SERVER_URL = "http://localhost:8080/api/solver"


def set_java_parameters(method, order, equation, initial_x, initial_y, reach_point, step_size):
    method_mapping = {
        "method_euler": 1,
        "method_modified_euler": 2,
        "method_runge_kutta": 4,
        "method_dormand_prince": 7
    }

    payload = {
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


def get_application_status(application_id):
    response = requests.get(f"{JAVA_SERVER_URL}/application/{application_id}/status",
                            timeout=10)
    response.raise_for_status()
    return response.json()


def get_application_creation_date(application_id):
    response = requests.get(f"{JAVA_SERVER_URL}/application/{application_id}/creation_date",
                            timeout=10)
    response.raise_for_status()
    return response.json()


def get_application_list(user_id):
    response = requests.get(f"{JAVA_SERVER_URL}/application/list/{user_id}",
                            timeout=10)
    response.raise_for_status()
    return response.json()


def get_solution(application_id):
    response = requests.get(f"{JAVA_SERVER_URL}/solution/{application_id}",
                            timeout=10)
    response.raise_for_status()
    return np.array(response.json())


def get_x_values(application_id):
    response = requests.get(f"{JAVA_SERVER_URL}/x-values/{application_id}",
                            timeout=10)
    response.raise_for_status()
    return np.array(response.json())


def get_y_values(application_id):
    response = requests.get(f"{JAVA_SERVER_URL}/y-values/{application_id}",
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
