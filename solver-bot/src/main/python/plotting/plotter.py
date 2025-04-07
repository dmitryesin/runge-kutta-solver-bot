import matplotlib.pyplot as plt
import io

def plot_solution(x_values, y_values, order):
    plt.clf()

    plt.figure(figsize=(10, 6), dpi=200)

    plt.grid(True)

    superscripts = "⁰¹²³⁴⁵⁶⁷⁸⁹"

    def get_variable_name(i):
        if i < 4:
            return f"y{chr(39) * i}"
        return f"y{"⁽"}{''.join(superscripts[int(d)] for d in str(i))}{"⁾"}"

    variable_names = ["y"] + [get_variable_name(i) for i in range(1, int(order))]

    plt.plot(x_values, y_values, label=variable_names)

    plt.legend()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches="tight")

    plt.close()

    buffer.seek(0)

    return buffer
