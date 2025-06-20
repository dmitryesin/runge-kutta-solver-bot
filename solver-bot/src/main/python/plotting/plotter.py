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
        margin=dict(l=20, r=20, t=40, b=40),
    )

    html_str = pio.to_html(
        fig,
        full_html=False,
        include_plotlyjs='cdn',
        config={'responsive': True}
    )

    responsive_wrapper = f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            html, body {{
                margin: 0;
                padding: 0;
                height: 100%;
                width: 100%;
            }}
            .plotly-graph-div {{
                height: 100% !important;
                width: 100% !important;
            }}
        </style>
    </head>
    <body>
        {html_str}
    </body>
    </html>
    """

    buffer = io.BytesIO()
    buffer.write(responsive_wrapper.encode('utf-8'))
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
