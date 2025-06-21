import io
from pathlib import Path

import matplotlib.pyplot as plt
import plotly.graph_objs as go
import plotly.io as pio
from jinja2 import Template
from printing.printer import get_variable_name

PY_DIR = Path(__file__).parent


def plot_solution_save(x_values, y_values, order):
    variable_names = ["y"] + [get_variable_name(i) for i in range(1, order)]
    fig = go.Figure()

    if isinstance(y_values[0], (list, tuple)):
        for i, name in enumerate(variable_names):
            fig.add_trace(
                go.Scatter(
                    x=x_values, y=[y[i] for y in y_values], mode="lines", name=name
                )
            )
    else:
        fig.add_trace(
            go.Scatter(x=x_values, y=y_values, mode="lines", name=variable_names[0])
        )

    fig.update_layout(
        legend=dict(x=0, y=1),
        margin=dict(l=20, r=20, t=40, b=40),
    )

    html_str = pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs="cdn",
        config={
            "responsive": True,
            "scrollZoom": True,
            "displayModeBar": True,
        },
    )

    with open(PY_DIR / "template.html", "r", encoding="utf-8") as f:
        template = Template(f.read())

    full_html = template.render(plot_div=html_str)

    buffer = io.BytesIO()
    buffer.write(full_html.encode("utf-8"))
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
