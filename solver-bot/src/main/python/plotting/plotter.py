import io
import matplotlib.pyplot as plt

from printing.printer import get_variable_name


def plot_solution(x_values, y_values, order):
    plt.clf()

    plt.figure(figsize=(10, 6), dpi=200)

    plt.grid(True)

    variable_names = ["y"] + [get_variable_name(i) for i in range(1, order)]

    plt.plot(x_values, y_values, label=variable_names)

    plt.legend()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")

    plt.close()

    buffer.seek(0)

    return buffer
