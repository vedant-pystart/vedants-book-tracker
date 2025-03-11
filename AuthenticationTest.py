import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# Path to your downloaded JSON key file
key_path = '/Users/vedant/Documents/sheets-book-tracker-ba6acadc4aa7.json'

# Scopes for Google Sheets API access
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]

# Authenticate using the service account credentials
creds = Credentials.from_service_account_file(key_path, scopes=scopes)

# Authenticate with gspread
gc = gspread.authorize(creds)

# Open the Google Sheets document by its ID
spreadsheet_id = "1w35c853BOj2Ewb4-Df0664Dt-QCH9DYIx6pbX1Vr4ho"

sheet = gc.open_by_key(spreadsheet_id).sheet1

# Get all values from the sheet
data = sheet.get_all_values()

# Convert to Pandas DataFrame
columns = data[0]  # First row as column headers
rows = data[1:]    # Remaining rows as data
df = pd.DataFrame(rows, columns=columns)

# Display the first few rows of the DataFrame
print(df.head())