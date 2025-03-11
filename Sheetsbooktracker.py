from dash import Dash, html, dash_table, dcc, callback, Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

load_dotenv()


# Path to your downloaded JSON key file
key_path = os.getenv("GOOGLE_SHEET_KEY_PATH")
spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")


# Scopes for Google Sheets API access
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]

# Authenticate using the service account credentials
creds = Credentials.from_service_account_file(key_path, scopes=scopes)

# Authenticate with gspread
gc = gspread.authorize(creds)


sheet = gc.open_by_key(spreadsheet_id).sheet1

# Get all values from the sheet
data = sheet.get_all_values()

# Convert to Pandas DataFrame
columns = data[0]  # First row as column headers
rows = data[1:]    # Remaining rows as data
df = pd.DataFrame(rows, columns=columns)


"""
==================================================
1. DATA PREPROCESSING
==================================================
"""

# Load and preprocess data
df = df.iloc[:, 0:25]  
df = df.dropna(how="all")  
df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
df["Book Link"] = df["Book"].apply(lambda book: f"/book/{book.replace(' ', '_')}")
df["Start Date"] = pd.to_datetime(df["Start Date"], errors="coerce")
df["End Date"] = pd.to_datetime(df["End Date"], errors="coerce")
df["Start Year"] = df["Start Date"].dt.year
df["Start Month"] = df["Start Date"].dt.month_name()
df["End Year"] = df["End Date"].dt.year
df["End Month"] = df["End Date"].dt.month_name()

year_options = [{"label": str(int(year)), "value": int(year)} for year in sorted(df["Start Year"].dropna().unique())]
month_options = [{"label": month, "value": month} for month in [
    "January", "February", "March", "April", "May", "June", "July", "August", 
    "September", "October", "November", "December"
]]

unique_genres = sorted(set(df["Genre"].dropna().str.split(", ").explode()))


genre_options = [{"label": str(genre), "value": str(genre)} for genre in unique_genres]

df['month_year'] = df['End Date'].dt.strftime('%Y-%m')

# print(df["month_year"])

values_list = df.groupby(["month_year"]).size().reset_index(name="Book Count")

values_list.columns = ['Date', 'Books Read']

values_list["Date"] = pd.to_datetime(values_list["Date"])

# print(unique_genres)


df["Start Date"] = df["Start Date"].dt.strftime('%b %d, %Y')  
df["End Date"] = df["End Date"].dt.strftime('%b %d, %Y')  

bookspermonth = px.line(values_list, x='Date', y='Books Read', title='Books Read Per Month', markers=True)

bookspermonth.update_layout(
    title={
        'text': 'Books Read Per Month',  # Title text
        'font': {
            'family': 'Arial, sans-serif',  # Font type
            'size': 24,  # Font size
            'color': 'black',  # Font color
            'weight': 'bold'  # Font weight
        },
        'x': 0.5,  # Center the title horizontally
        'xanchor': 'center'  # Align the title to the center
    },
    yaxis=dict(
        showticklabels=True,  # Show labels on the y-axis
        showgrid=False,  # Remove grid lines
        zeroline=False,  # Hide the zero line
        title="Books Read"  # Set y-axis title
    ),
    xaxis=dict(
        showgrid=True,  # Keep grid on the x-axis
        zeroline=True,  # Show the zero line
        linecolor="black"  # Change x-axis line color to black
    ),
    plot_bgcolor='white',  # Set the background color of the plot area
    paper_bgcolor='white',  # Set the background color of the entire figure
    hoverlabel=dict(
        bgcolor="rgba(255,255,255,0.7)",  # Slightly transparent background for hover
        font_size=14,  # Font size for hover label
        font_family="Arial, sans-serif",  # Font for hover label
        font_color="black"  # Hover label text color
    ),
    margin=dict(t=40, b=30, l=40, r=40),  # Adjust margins for compactness
    hovermode="closest",  # More responsive hover
    legend=dict(
        visible=False  # Hide the legend
    )
)

# Update the line thickness
bookspermonth.update_traces(line=dict(width=7, color = 'navy'), marker=dict(size=15, symbol = 'circle'))  # Line thickness and marker size

bookspermonth.update_traces(
    hovertemplate='%{x|%B %Y}<br>Books Read: %{y}<extra></extra>'  # Format x as Month Year and customize tooltip
)


"""
==================================================
2. DASH APPLICATION FEATURES
==================================================
"""

app = Dash(suppress_callback_exceptions=True)


app.layout = html.Div([
    dcc.Location(id="url", refresh=False),  # Tracks URL changes
    html.Div(id="page-content"),  # Placeholder for different pages (content changes here)
])

"""
==================================================
3. DASH CALLBACKS
==================================================
"""

# Callback to display the correct page based on the URL
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname")
)
def display_page(pathname):
    if pathname.startswith("/book/"):
        book_name = pathname.split("/book/")[1].replace("_", " ")
        book_data = df[df["Book"] == book_name]

        if book_data.empty:
            return html.H1("Book Not Found")

        book_info = book_data.iloc[0]
        
        return html.Div([
            html.H1(book_info["Book"], style={"textAlign": "center"}),
            html.Hr(),
            html.H3(f"Author: {book_info['Author']}"),
            html.H3(f"Status: {book_info['Status']}"),
            html.H3(f"Recommendation: {book_info['Rec?']}"),
            html.H3(f"Recommended By: {book_info['Recommended By']}"),
            html.H3(f"Start Date: {book_info['Start Date']}"),
            html.H3(f"End Date: {book_info['End Date']}"),
            html.P(f"Summary: {book_info['Summary']}"),
            html.P(f"Core Themes: {book_info['Core Themes']}"),
            html.P(f"Review: {book_info['Review']}"),
            html.P(f"What I Gained from Reading: {book_info['What I gained from reading']}"),
            html.P(f"Story Behind Finding the Book: {book_info['Story behind finding the book']}"),
            html.H3(f"Genre: {book_info['Genre']}"),
            html.H3(f"Personal Collection: {book_info['Personal Collection?']}"),
            html.H3(f"Series/Standalone: {book_info['Series/Standalone?']}"),
            html.H3(f"Page Count: {book_info['Page Ct.']}"),
            html.A("Back to Home", href="/"),
        ])

    else:
        return html.Div([
    html.H1("Local Book Tracking Analytics Dashboard", style={"textAlign": "center", "fontFamily": "Arial, sans-serif"}),  
    html.Hr(),  

# Book Status Label and Dropdown
    html.Div([
        html.Label("Book Status:", style={"fontFamily": "Arial, sans-serif", "fontWeight": "bold", "fontSize": "16px", "width": "150px"}),
        dcc.Dropdown(
            ["Complete", "Reading", "To Be Read"], 
            ["Complete"], 
            multi=True, 
            id="DropdownBookStatus", 
            style={"width": "75%", "fontFamily": "Arial, sans-serif"}
        )
    ], style={"width": "75%", "margin": "auto", "display": "flex", "alignItems": "center", "gap": "10px"}),

    # Recommendation Label and Dropdown
    html.Div([
        html.Label("Recommendation:", style={"fontSize": "16px", "fontFamily": "Arial, sans-serif", "fontWeight": "bold", "width": "150px"}),
        dcc.Dropdown(
            id="rec-dropdown",
            options=[
                {"label": "Yes", "value": "Yes"},
                {"label": "No", "value": "No"},
            ],
            value=["Yes"],  # Default to 'Yes'
            multi=True,  # Allow multiple selection
            style={"width": "75%", "fontFamily": "Arial, sans-serif"}
        ),
    ], style={"width": "75%", "margin": "auto", "display": "flex", "alignItems": "center", "gap": "10px"}),

    # Year Label
    html.Div([
        html.Label("Year:", style={"fontSize": "16px", "fontFamily": "Arial, sans-serif", "fontWeight": "bold", "width": "150px"}),
        dcc.Dropdown(
            id="year_dropdown",
            options= year_options,
            multi=True,
            style={"width": "75%", "fontFamily": "Arial, sans-serif"}
        ),
    ], style={"width": "75%", "margin": "auto", "display": "flex", "alignItems": "center", "gap": "10px"}),

    # Month Label

        html.Div([
        html.Label("Month:", style={"fontSize": "16px", "fontFamily": "Arial, sans-serif", "fontWeight": "bold", "width": "150px"}),
        dcc.Dropdown(
            id="month_dropdown",
            options= month_options,
            multi=True,
            style={"width": "75%", "fontFamily": "Arial, sans-serif"}
        ),
    ], style={"width": "75%", "margin": "auto", "display": "flex", "alignItems": "center", "gap": "10px"}),


    # # Genre Dropdown
    # html.Div([
    #     html.Label("Genre:", style={"fontFamily": "Arial, sans-serif", "fontWeight": "bold", "fontSize": "16px", "width": "150px"}),
    #     dcc.Dropdown(options = genre_options, 
    #         multi=True, 
    #         id="DropdownBookStatus", 
    #         style={"width": "75%", "fontFamily": "Arial, sans-serif"}
    #     )
    # ], style={"width": "75%", "margin": "auto", "display": "flex", "alignItems": "center", "gap": "10px"}),
    html.Hr(),

    # Table
    dash_table.DataTable(
                data=df.assign(**{"Book Link": df["Book Link"].apply(lambda x: f"[More Info]({x})")}).to_dict("records"),                columns=[
                    {"name": "Status", "id": "Status"},
                    {"name": "Book", "id": "Book"},
                    {"name": "Author", "id": "Author"},
                    {"name": "Rating", "id": "Rating"},
                    {"name": "Recommended By", "id": "Recommended By"},
                    {"name": "Start Date", "id": "Start Date"},
                    {"name": "End Date", "id": "End Date"},
                    {"name": "More Info", "id": "Book Link", "presentation": "markdown"},
                ],
        id="MainBookTable",
        style_table={"width": "80%", "margin": "auto"},  
        style_data={"fontFamily": "Arial, sans-serif", "fontSize": "14px", "fontWeight": "bold", "textAlign": "center"},
        style_header={"fontFamily": "Arial, sans-serif", "fontSize": "22px", "fontWeight": "bold", "backgroundColor": "#f4f4f4", "textAlign": "center", "padding": "10px"},
        style_data_conditional=[
            {"if": {"column_id": "Status", "filter_query": '{Status} = "Complete"'}, "color": "green", "fontWeight": "bold", "fontStyle": "italic"},
            {"if": {"column_id": "Status", "filter_query": '{Status} = "To Be Read"'}, "color": "#8B0000", "fontWeight": "bold", "fontStyle": "italic"},
            {"if": {"column_id": "Status", "filter_query": '{Status} = "Reading"'}, "color": "orange", "fontWeight": "bold", "fontStyle": "italic"}
        ]
    ),   
    html.Hr(),

    dcc.Graph(id="ratings_histogram"),
    html.Hr(),
    dcc.Graph(figure = bookspermonth)


  
])

@app.callback(
    Output("MainBookTable", "data"),
    [
        Input("DropdownBookStatus", "value"),
        Input("rec-dropdown", "value"),
        Input("year_dropdown", "value"),
        Input("month_dropdown", "value")
    ]
)
def update_table(status_values, rec_values, selected_years, selected_months,):
    # Filter by Status and Recommendation
    if not rec_values:  
        filtered_df = df[df["Status"].isin(status_values)]
    else:
        filtered_df = df[(df["Status"].isin(status_values)) & (df["Rec?"].isin(rec_values))]

    # Filter by Year (Optional)
    if selected_years:
        filtered_df = filtered_df.loc[
            (filtered_df["Start Year"].isin(selected_years)) | 
            (filtered_df["End Year"].isin(selected_years))
        ]

    # Filter by Month (Only if Years are Selected)
    if selected_months:
        if selected_years:  # Ensure that year filtering is applied
            filtered_df = filtered_df.loc[
                ((filtered_df["Start Year"].isin(selected_years)) & (filtered_df["Start Month"].isin(selected_months))) | 
                ((filtered_df["End Year"].isin(selected_years)) & (filtered_df["End Month"].isin(selected_months)))
            ]
        else:  # If no year selected, just filter by month alone
            filtered_df = filtered_df.loc[
                (filtered_df["Start Month"].isin(selected_months)) | 
                (filtered_df["End Month"].isin(selected_months))
            ]

    # # Filter by Genre (Handle NaN Values)
    # if selected_genres:
    #     filtered_df = filtered_df.dropna(subset=["Genre"])  # Drop NaNs before applying filter
    #     filtered_df = filtered_df[
    #         filtered_df["Genre"].apply(lambda x: any(genre in x.split(", ") for genre in selected_genres))
    #     ]

    # Format the Book Link as Markdown
    filtered_df["Book Link"] = filtered_df["Book Link"].apply(lambda x: f"[More Info]({x})")

    return filtered_df.to_dict("records")

# Update visualization based on recommendation filter
@callback(
    Output("ratings_histogram", "figure"),
    Input("rec-dropdown", "value"),
    Input("year_dropdown", "value"),  # Year filter
    Input("month_dropdown", "value")  # Month filter
)
def update_vis(rec_values, year_values, month_values):
    if "All" in rec_values or not rec_values:  
        dfvis1 = df
    else:
        # Filter based on selected values for 'Rec?'
        dfvis1 = df[df["Rec?"].isin(rec_values)]

    if not year_values or "All" in year_values:  # Check for None or empty
        dfvis1 = dfvis1  # No filtering on Year
    else:
        # Filter based on both Start Year and End Year
        dfvis1 = dfvis1[dfvis1["Start Year"].isin(year_values) | dfvis1["End Year"].isin(year_values)]

    if not month_values or "All" in month_values:  # Check for None or empty
        dfvis1 = dfvis1  # No filtering on Year
    else:
        # Filter based on both Start Year and End Year
        dfvis1 = dfvis1[dfvis1["Start Month"].isin(month_values) | dfvis1["End Month"].isin(month_values)]


    # Categorize the ratings into buckets (you can adjust ranges as needed)
    rating_bins = pd.cut(dfvis1['Rating'], bins=[0, 5, 7, 10], labels=["Low", "Medium", "High"])

    # Add a new column for the rating categories
    dfvis1['Rating Category'] = rating_bins

    # Create histogram
    vis = px.histogram(
        dfvis1, 
        x="Rating",  # Show rating distribution
        nbins=20,  # Adjust number of bins as necessary
        color="Rating Category",  # Color based on the rating category
        color_discrete_map={"Low": "#8B0000", "Medium": "orange", "High": "green"},  # Set color map
        title="Ratings Distribution"
    )
    # Update layout for custom title styling, axis removal, and no legend
    vis.update_layout(
        title={
            'text': 'Ratings Distribution',  # Title text
            'font': {
                'family': 'Arial, sans-serif',  # Font type
                'size': 24,  # Font size
                'color': 'black',  # Font color
                'weight': 'bold'  # Font weight
            },
            'x': 0.5,  # Center the title horizontally
            'xanchor': 'center'  # Align the title to the center
        },
        yaxis=dict(
            showticklabels=False,  # Hides the labels (numbers) on the y-axis
            showgrid=False,  # Removes the grid lines
            zeroline=False,  # Hides the zero line
            title=""  # Remove y-axis title
        ),
        xaxis=dict(
            showgrid=True,  # Keeps the grid on the x-axis
            zeroline = True, 
            linecolor = "black"
        ),
        legend=dict(
            visible=False  # Hides the legend
        ), 
        plot_bgcolor='white',  # Sets the background color of the plot area (the actual graph area)
        paper_bgcolor='white',  # Sets the background color of the entire figure (including title, margins)
        hoverlabel=dict(
        bgcolor="rgba(255,255,255,0.7)",  # Slightly transparent background for hover
        font_size=14,  # Font size for hover label
        font_family="Arial, sans-serif",  # Font for hover label
        font_color="black"  # Hover label text color
    ),
    bargap=0.01,  # Reduce the gap between bars for a more packed look
    margin=dict(t=40, b=30, l=40, r=40),  # Reduce margins for compactness
    hovermode="closest"  # More responsive hover
    )
    return vis

if __name__ == "__main__":
    app.run_server(debug=True, host='0.0.0.0', port=5000)

