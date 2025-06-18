import io
import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.io as pio

from printing.printer import get_variable_name


def plot_solution_save(x_values, y_values, order):
    variable_names = ["y"] + [get_variable_name(i) for i in range(1, order)]
    fig = go.Figure()

    if isinstance(y_values[0], (list, tuple)):
        for i, name in enumerate(variable_names):
            fig.add_trace(go.Scatter(
                x=x_values,
                y=[y[i] for y in y_values],
                mode='lines',
                name=name
            ))
    else:
        fig.add_trace(go.Scatter(
            x=x_values,
            y=y_values,
            mode='lines',
            name=variable_names[0]
        ))

    fig.update_layout(
        legend=dict(x=0, y=1),
        width=900,
        height=600,
    )

    html_str = pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

    buffer = io.BytesIO()
    buffer.write(html_str.encode('utf-8'))
    buffer.seek(0)

    return buffer


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
