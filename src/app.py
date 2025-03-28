from dash import Dash, html, dash_table, dcc, callback, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import gspread
from google.oauth2.service_account import Credentials
import json

import dash_bootstrap_components as dbc
from flask import Flask

# NOTE THERE IS A BUG WHERE THE MORE INFO DOESNT WORK FOR PARENTHESIS IN BOOK NAME (EG RAM CHANDRA)


load_dotenv()

width1 = '80%'
width2 = '60%'


# Path to your downloaded JSON key file
key_path = os.getenv("GOOGLE_SHEET_KEY_PATH")
spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")

# Scopes for Google Sheets API access
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]

import json

# Load credentials from environment variable
service_account_info = json.loads(os.getenv("GOOGLE_SHEET_CREDENTIALS"))
creds = Credentials.from_service_account_info(service_account_info, scopes=scopes)

# Authenticate with gspread
gc = gspread.authorize(creds)

sheet = gc.open_by_key(spreadsheet_id).sheet1

# Get all values from the sheet
data = sheet.get_all_values()

# Convert to Pandas DataFrame
columns = data[0]  # First row as column headers
rows = data[1:]    # Remaining rows as data
df = pd.DataFrame(rows, columns=columns)

# df = pd.read_excel('GIT Local Book Tracker/Book Log.xlsx')

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table, callback, Input, Output
import plotly.express as px
import pandas as pd
import pandas_datareader.data as web
import datetime

# df = pd.read_excel('Past_Projects/GIT Local Book Tracker/Book Log.xlsx')

"""
==================================================
1. DATA PREPROCESSING
==================================================
"""

# Load and preprocess data
df = df.iloc[:, 0:25] # Takes in the first 25 columns 
df = df.dropna(how="all") # Drops rows where values are NaN
df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce") 
df["Book Link"] = df["Book"].apply(lambda book: f"/book/{book.replace(' ', '_')}") # Creates a link to the book
df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce") 
df["End Date"] = pd.to_datetime(df["End Date"], errors="coerce")
df["Start Year"] = df["Start Date"].dt.year
df["Start Month"] = df["Start Date"].dt.month_name()
df["End Year"] = df["End Date"].dt.year
df["End Month"] = df["End Date"].dt.month_name()
df['month_year'] = df['End Date'].dt.strftime('%Y-%m')


# Create options for dropdowns
year_options = [{"label": str(int(year)), "value": int(year)} for year in sorted(df["Start Year"].dropna().unique())]

month_options = [{"label": month, "value": month} for month in [
    "January", "February", "March", "April", "May", "June", "July", "August", 
    "September", "October", "November", "December"
]]

unique_genres = sorted(set(df["Genre"].dropna().str.split(", ").explode()))
genre_options = [{"label": str(genre), "value": str(genre)} for genre in unique_genres]

values_list = df.groupby(["month_year"]).size().reset_index(name="Book Count")
values_list.columns = ['Date', 'Books Read']
values_list["Date"] = pd.to_datetime(values_list["Date"])

# Converting dates back to readable format
df["Start Date"] = df["Start Date"].dt.strftime('%b %d, %Y')  
df["End Date"] = df["End Date"].dt.strftime('%b %d, %Y')  


app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.LITERA],
                meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}])

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Visualizations", href="/visualizations")),
        dbc.NavItem(dbc.NavLink("Book Info", href="/")),
    ],
    brand="Vedant's Book Tracker",
    brand_href="/",
    color="primary",
    dark=True,
)

app.layout = html.Div([
    navbar,
    dash.page_container,  # This automatically loads the correct page layout
    dcc.Store(id='store', data=df.to_dict("records"), storage_type='memory'),  # Store component to hold data
])


if __name__ == '__main__':
    app.run_server(debug=True)

    
