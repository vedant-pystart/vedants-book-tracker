import dash
from dash import dcc, html, callback, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd

dash.register_page(__name__, path_template="/book/<book_name>")

layout = dbc.Container([
    dcc.Location(id="url"), 
    html.H1(id="book_title", className="text-center mt-4"),
    html.P(id="book_author", className="text-muted text-center"),
    html.P(id="book_description", className="mt-3"),
], fluid=True)


@callback(
    [Output("book_title", "children"),
     Output("book_author", "children"),
     Output("book_description", "children")],
    [Input("store", "data"), Input("url", "pathname")]  
)
def load_book_details(stored_data, pathname):
    if stored_data is None:
        return "Book Not Found", "", ""

    dff = pd.DataFrame(stored_data)
    book_name = pathname.split("/")[-1].replace("_", " ")  

    book_info = dff[dff["Book"] == book_name]
    if book_info.empty:
        return "Book Not Found", "", ""

    title = book_info["Book"].values[0]
    author = f'Author: {book_info["Author"].values[0]}'
    description = f'Rating: {book_info["Rating"].values[0]}\nStatus: {book_info["Status"].values[0]}'

    return title, author, description