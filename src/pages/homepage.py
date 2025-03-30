import dash
from dash import dcc, html, dash_table, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd

dash.register_page(__name__, path='/')

filteringoptions = dbc.Container([
    dcc.Dropdown(id='year_dropdown', multi=True, placeholder="Select Year", className="m-3"),
    dcc.Dropdown(id='month_dropdown', multi=True, placeholder="Select Month", className="m-3"),
    dcc.Dropdown(
        id='status_dropdown',
        options=[
            {"label": "To Be Read", "value": "To Be Read"},
            {"label": "Reading", "value": "Reading"},
            {"label": "Complete", "value": "Complete"}
        ],
        multi=True,
        placeholder="Select Status",
        className="m-3"
    )
])

table_main = dash_table.DataTable(
    id="MainBookTable",
    columns=[
        {"name": "Status", "id": "Status"},
        {"name": "Book", "id": "Book"},
        {"name": "Author", "id": "Author"},
        {"name": "Rating", "id": "Rating"},
        {"name": "Recommended By", "id": "Recommended By"},
        {"name": "Start Date", "id": "Start Date"},
        {"name": "End Date", "id": "End Date"},
        {"name": "More Info", "id": "Book Link", "presentation": "markdown"},

    ],
    style_data={"fontFamily": "Arial, sans-serif", "fontSize": "14px", "fontWeight": "bold", "textAlign": "center"},
    style_header={"fontFamily": "Arial, sans-serif", "fontSize": "22px", "fontWeight": "bold", "backgroundColor": "#f4f4f4", "textAlign": "center", "padding": "10px"},
    style_data_conditional=[
        {"if": {"column_id": "Status", "filter_query": '{Status} = "Complete"'}, "color": "green", "fontWeight": "bold", "fontStyle": "italic"},
        {"if": {"column_id": "Status", "filter_query": '{Status} = "To Be Read"'}, "color": "#8B0000", "fontWeight": "bold", "fontStyle": "italic"},
        {"if": {"column_id": "Status", "filter_query": '{Status} = "Reading"'}, "color": "orange", "fontWeight": "bold", "fontStyle": "italic"},
        {   
            "if": {"column_id": "Author"},  # Clips only the "Book" column
            "whiteSpace": "nowrap",
            "overflowX": "auto",
            # "textOverflow": "ellipsis",
            "maxWidth": "165px",  # Adjust as needed
        }
        ],
    filter_action='native',
    sort_action='native',
)

layout = dbc.Container([
    dbc.Row([filteringoptions]),
    
    dbc.Row([
        dbc.Col(
            html.Div(table_main, style={"overflowX": "auto", "width": "100%", }),
            width=12
        )
    ], className="m-3", justify="center"),
    
], fluid=True)


@callback(
    [
        Output("MainBookTable", "data"),
        Output("year_dropdown", "options"),
        Output("month_dropdown", "options"),
    ],
    [
        Input("year_dropdown", "value"),
        Input("month_dropdown", "value"),
        Input("status_dropdown", "value"),
        Input("store", "data"),  # Load data from `dcc.Store`
    ]
)
def update_table(selected_years, selected_months, status_values, stored_data):
    if stored_data is None:
        return [], [], []  # If no data is stored, return empty values

    dff = pd.DataFrame(stored_data)  # Convert stored JSON back to DataFrame

    # Create dropdown options dynamically
    year_options = [{"label": str(int(year)), "value": int(year)} for year in sorted(dff["Start Year"].dropna().unique())]
    month_options = [{"label": month, "value": month} for month in dff["End Month"].dropna().unique()]

    # Apply filters
    if selected_years:
        dff = dff[dff["End Year"].isin(selected_years)]
    if selected_months:
        dff = dff[dff["End Month"].isin(selected_months)]
    if status_values:
        dff = dff[dff["Status"].isin(status_values)]
    
    dff["Book Link"] = dff["Book Link"].apply(lambda x: f"[More Info]({x})") 
    return dff.to_dict("records"), year_options, month_options