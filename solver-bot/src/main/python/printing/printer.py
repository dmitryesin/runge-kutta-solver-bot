def print_solution(result, order, rounding):
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
