import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px

dash.register_page(__name__, path='/visualizations')

total_pages = "N/A"

# Check out DBC Card instead of Container. Easier to use and more visually appealing

information = html.Div([
    dbc.Row([
        dbc.Col(
            dbc.Container(
                [
                    html.H1(f"{total_pages}", className="display-5 fw-bold", id="total_pages_read"),
                    html.P("Cool Stat: To Be Added", className="lead"),
                ],
                fluid=True,
            ),
            className="p-3 bg-body-secondary rounded-3 mx-2",  # Adds margin on both sides
            width=2,
        ),
        dbc.Col(
            dbc.Container(
                [
                    html.H1(f"{total_pages}", className="display-5 fw-bold", id="total_pages_read"),
                    html.P("Pages Read", className="lead"),
                ],
                fluid=True,
            ),
            className="p-3 bg-body-secondary rounded-3 mx-2",  # Adds margin on both sides
            width=2,
        ),
    ],) 
])

layout = dbc.Container([
    dbc.Row(dbc.Col(information, className="m-4")),
    html.H3("Content Read Per Month", className='m-3'),
    dcc.RadioItems([' Books', ' Pages' ], ' Books', id='books_or_pages', className='m-3'),

    dcc.Graph(id="books_per_month_graph", config={
        'displayModeBar': False,  # Hide the toolbar
        'scrollZoom': False,  # Disable zooming with scroll
        'doubleClick': False,  # Disable double-click zoom reset
        'showTips': False  # Disable tooltips
    }),
], fluid=True)




@callback(
    Output("books_per_month_graph", "figure"),
    Input("store", "data"),  # Get stored data from dcc.Store
    Input("books_or_pages", "value")
)
def update_visualization(stored_data, books_or_pages):
    if stored_data is None:
        return px.line(title="No Data Available")  # Handle case where data isn't loaded

    dff = pd.DataFrame(stored_data)  # Convert JSON to DataFrame
    dff["Page Ct."] = pd.to_numeric(dff["Page Ct."], errors="coerce")

    if books_or_pages == ' Pages':
        values_list = dff.groupby(["month_year"])["Page Ct."].sum().reset_index(name="Pages Read")
        values_list.columns = ['Date', 'Pages Read']
        values_list["Date"] = pd.to_datetime(values_list["Date"])
        fig = px.line(values_list, x='Date', y='Pages Read', markers=True)
        yaxis=dict(title="Pages Read"),
        fig.update_traces(hovertemplate='%{x|%B %Y}<br>Pages Read: %{y}<extra></extra>')

    
    elif books_or_pages == ' Books':
        values_list = dff.groupby(["month_year"]).size().reset_index(name="Book Count")
        values_list.columns = ['Date', 'Books Read']
        values_list["Date"] = pd.to_datetime(values_list["Date"])
        fig = px.line(values_list, x='Date', y='Books Read', markers=True)
        yaxis=dict(title="Books Read"),
        fig.update_traces(hovertemplate='%{x|%B %Y}<br>Books Read: %{y}<extra></extra>')

    # Create the line chart

    fig.update_layout(
        xaxis=dict(linecolor="black"),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode="closest",
    )

    fig.update_traces(line=dict(width=7, color='navy'), marker=dict(size=15, symbol='circle'))

    return fig

@callback(
    Output("total_pages_read", "children"),
    Input("store", "data"),  # Get stored data from dcc.Store
)
def create_stats(stored_data):
    
    dff = pd.DataFrame(stored_data) 
    dff["Page Ct."] = pd.to_numeric(dff["Page Ct."], errors="coerce")

    if stored_data is None:
        total_pages = "No Data Available"
        return total_pages
       
    total_pages = dff["Page Ct."].sum()
    return total_pages