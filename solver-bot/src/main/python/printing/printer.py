def print_solution(result, order, rounding):
    try:
        order = int(order)
    except ValueError:
        return ""
    
    def format_value(value, rounding):
        formatted_value = f"{value:.{rounding}f}"
        if '.' in formatted_value:
            formatted_value = formatted_value.rstrip('0')
            if formatted_value.endswith('.'):
                formatted_value += '0'
        return formatted_value

    def get_variable_name(i):
        superscripts = "⁰¹²³⁴⁵⁶⁷⁸⁹"
        if i < 4:
            return f"y{chr(39) * i}"
        return f"y{"⁽"}{''.join(superscripts[int(d)] for d in str(i))}{"⁾"}"

    formatted_x = format_value(result[0], rounding)
    result_str = f"x: {formatted_x}"

    variable_names = ["y"] + [get_variable_name(i) for i in range(1, int(order))]

    for i in range(1, order + 1):
        if i < len(result):
            formatted_y = format_value(result[i], rounding)
            result_str += f", {variable_names[i-1]}: {formatted_y}"
        else:
            result_str += f", {variable_names[i-1]}: NaN"

    return result_str
