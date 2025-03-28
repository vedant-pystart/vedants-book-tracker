import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

dash.register_page(__name__, path='/visualizations')

layout = dbc.Container([
    html.H3("Books Read Per Month", className='m-3'),
    dcc.Graph(id="books_per_month_graph", config={
        'displayModeBar': False,  # Hide the toolbar
        'scrollZoom': False,  # Disable zooming with scroll
        'doubleClick': False,  # Disable double-click zoom reset
        'showTips': False  # Disable tooltips
    }),
], fluid=True)


@callback(
    Output("books_per_month_graph", "figure"),
    Input("store", "data")  # Get stored data from dcc.Store
)
def update_visualization(stored_data):
    if stored_data is None:
        return px.line(title="No Data Available")  # Handle case where data isn't loaded

    dff = pd.DataFrame(stored_data)  # Convert JSON to DataFrame

    # Create values_list dynamically
    values_list = dff.groupby(["month_year"]).size().reset_index(name="Book Count")
    values_list.columns = ['Date', 'Books Read']
    values_list["Date"] = pd.to_datetime(values_list["Date"])

    # Create the line chart
    fig = px.line(values_list, x='Date', y='Books Read', markers=True)

    fig.update_layout(
        yaxis=dict(title="Books Read"),
        xaxis=dict(linecolor="black"),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode="closest",
    )

    fig.update_traces(line=dict(width=7, color='navy'), marker=dict(size=15, symbol='circle'))
    fig.update_traces(hovertemplate='%{x|%B %Y}<br>Books Read: %{y}<extra></extra>')

    return fig