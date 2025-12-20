"""
Tab for scraping and displaying swimmer results
Save this as: tabs/results_tab.py
"""
import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from shared_data import data_store
from scraper import scrape_all_swimmers

# Tab layout
layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H3("Swimmer Results", className="mb-3"),
            
            # Year selection and scrape button
            dbc.Row([
                dbc.Col([
                    dbc.Label("Select Year:"),
                    dcc.Dropdown(
                        id='year-dropdown',
                        options=[{'label': str(y), 'value': str(y)} for y in range(2020, 2026)],
                        value='2025',
                        clearable=False
                    )
                ], width=3),
                dbc.Col([
                    html.Br(),
                    dbc.Button("🔍 Scrape Results", id="scrape-button", color="primary", className="w-100")
                ], width=3)
            ], className="mb-3"),
            
            # Progress and status
            html.Div(id='scrape-status'),
            dcc.Interval(id='progress-interval', interval=500, disabled=True),
            
            # Results visualization
            html.Div(id='results-visualization', className="mt-4")
        ], width=12)
    ])
])

# Callback to scrape results
@callback(
    [Output('scrape-status', 'children'),
     Output('progress-interval', 'disabled'),
     Output('results-visualization', 'children')],
    Input('scrape-button', 'n_clicks'),
    State('year-dropdown', 'value'),
    prevent_initial_call=True
)
def scrape_results(n_clicks, year):
    if not data_store.has_swimmers_data():
        return dbc.Alert("⚠️ Please upload swimmer data first!", color="warning"), True, ""
    
    swimmers_df = data_store.get_swimmers_data()
    mswa_ids = swimmers_df['MSWA number'].tolist()
    
    try:
        # Show scraping message
        status = dbc.Alert("🔄 Scraping in progress...", color="info")
        
        # Scrape results
        results_df = scrape_all_swimmers(mswa_ids, year)
        
        if results_df.empty:
            return dbc.Alert("❌ No results found", color="danger"), True, ""
        
        # Store results
        data_store.set_results_data(results_df)
        
        # Create visualizations
        viz = create_visualizations(results_df)
        
        success_msg = dbc.Alert([
            html.H5("✅ Scraping Complete!", className="alert-heading"),
            html.P(f"Total swims found: {len(results_df)}")
        ], color="success")
        
        return success_msg, True, viz
        
    except Exception as e:
        return dbc.Alert(f"❌ Error: {str(e)}", color="danger"), True, ""

def create_visualizations(df):
    """Create visualizations from results data"""
    
    # Convert data types
    df["Date"] = pd.to_datetime(df["Date"], format='%d.%m.%Y')
    df["Point"] = pd.to_numeric(df["Point"])
    df = df.sort_values(["Name", "Date"])
    df['Agg Points'] = df.groupby("Name")["Point"].cumsum()
    
    # Points by swimmer histogram
    fig1 = px.histogram(
        df,
        x="Name",
        y="Point",
        hover_name="Name",
        color="Stroke",
        histfunc="sum",
        title="EM1000 Points per Swimmer"
    )
    fig1.update_traces(hovertemplate="<b>Name: %{x}</b><br>Points: %{y}")
    fig1.update_layout(yaxis=dict(title=dict(text="Points")))
    
    # Cumulative points line chart
    fig2 = px.line(
        df,
        x="Date",
        y="Agg Points",
        color="Name",
        title="Cumulative Points Over Time"
    )
    fig2.update_layout(
        xaxis_title="Date",
        yaxis_title="Cumulative Points"
    )
    
    return html.Div([
        dbc.Row([
            dbc.Col([dcc.Graph(figure=fig1)], width=12)
        ]),
        dbc.Row([
            dbc.Col([dcc.Graph(figure=fig2)], width=12)
        ])
    ])