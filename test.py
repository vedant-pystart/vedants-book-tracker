from dash import Dash, html, dash_table, dcc, callback, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import gspread
from google.oauth2.service_account import Credentials
import json

load_dotenv()

# Load credentials from environment variable
service_account_info = json.loads(os.getenv("GOOGLE_SHEET_CREDENTIALS"))
creds = Credentials.from_service_account_info(service_account_info, scopes=[
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file"
])

# Authenticate with gspread
gc = gspread.authorize(creds)

# Google Sheet ID (from environment variable)
spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")

# Access the first sheet
sheet = gc.open_by_key(spreadsheet_id).sheet1