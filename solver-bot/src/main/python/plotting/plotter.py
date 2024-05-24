import matplotlib.pyplot as plt
import io

def plot_solution(x_values, y_values):
    plt.clf()

    plt.grid(True)
    plt.plot(x_values, y_values)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', bbox_inches="tight")

    plt.close()

    buffer.seek(0)
    
    return buffer
