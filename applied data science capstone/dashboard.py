import dash
from dash import dcc, html, Input, Output 
import plotly.express as px
import pandas as pd
import requests
import datetime

data=pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_2.csv")

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Layout del Dashboard
app.layout = html.Div([
    html.H1("SpaceX Launch Dashboard", style={'textAlign': 'center'}),

    # Filtros
    html.Div([
        html.Div([
            html.Label('Booster Version:'),
            dcc.Dropdown(
                id='booster-filter',
                options=[{'label': b, 'value': b} for b in data['BoosterVersion'].unique()],
                value=None,
                placeholder='All'
            )
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label('Launch Site:'),
            dcc.Dropdown(
                id='site-filter',
                options=[{'label': s, 'value': s} for s in data['LaunchSite'].unique()],
                value=None,
                placeholder='All'
            )
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),

        html.Div([
            html.Label('Orbit:'),
            dcc.Dropdown(
                id='orbit-filter',
                options=[{'label': o, 'value': o} for o in data['Orbit'].unique()],
                value=None,
                placeholder='All'
            )
        ], style={'width': '30%', 'display': 'inline-block', 'padding': '10px'}),
    ]),

    # KPIs
    html.Div([
        html.Div(id='total-launches', style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center'}),
        html.Div(id='success-rate', style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center'}),
        html.Div(id='avg-payload', style={'display': 'inline-block', 'width': '30%', 'textAlign': 'center'}),
    ], style={'padding': '20px'}),

    # Gráficos
    dcc.Graph(id='outcome-pie-chart'),
    dcc.Graph(id='payload-vs-flight-scatter'),
    dcc.Graph(id='launchsite-vs-flight-scatter'),
    dcc.Graph(id='launch-trend-line'),
    dcc.Graph(id='payload-histogram')
])

# Callback para actualizar dashboard
@app.callback(
    [Output('total-launches', 'children'),
     Output('success-rate', 'children'),
     Output('avg-payload', 'children'),
     Output('outcome-pie-chart', 'figure'),
     Output('payload-vs-flight-scatter', 'figure'),
     Output('launchsite-vs-flight-scatter', 'figure'),
     Output('launch-trend-line', 'figure'),
     Output('payload-histogram', 'figure')],
    [Input('booster-filter', 'value'),
     Input('site-filter', 'value'),
     Input('orbit-filter', 'value')]
)
def update_dashboard(selected_booster, selected_site, selected_orbit):
    # Filtrado de datos
    df_filtered = data.copy()
    if selected_booster:
        df_filtered = df_filtered[df_filtered['BoosterVersion'] == selected_booster]
    if selected_site:
        df_filtered = df_filtered[df_filtered['LaunchSite'] == selected_site]
    if selected_orbit:
        df_filtered = df_filtered[df_filtered['Orbit'] == selected_orbit]

    # KPIs
    total_launches = len(df_filtered)
    success_count = (df_filtered['Class'] == 1).sum()
    success_rate = (success_count / total_launches * 100) if total_launches > 0 else 0
    avg_payload = df_filtered['PayloadMass'].mean()

    total_launches_card = html.H3(f"Total Launches: {total_launches}")
    success_rate_card = html.H3(f"Success Rate: {success_rate:.1f}%")
    avg_payload_card = html.H3(f"Avg Payload: {avg_payload:.1f} kg" if not pd.isna(avg_payload) else "N/A")

    # Pie Chart Outcome
    outcome_counts = df_filtered['Outcome'].value_counts()
    pie_fig = px.pie(values=outcome_counts.values, names=outcome_counts.index, title='Launch Outcomes')

    df_filtered['LandingOutcome'] = df_filtered['Class'].apply(
    lambda x: 'Success' if '1' in str(x) else 'Failure'
)

    # Scatter Plot Payload vs FlightNumber
    payload_scatter = px.scatter(
        df_filtered,
        x='FlightNumber',
        y='PayloadMass',
        color= 'LandingOutcome',
        title='Payload Mass vs Flight Number',
        hover_data=['BoosterVersion']
    )

    # Scatter Plot LaunchSite vs FlightNumber
    site_scatter = px.scatter(
        df_filtered,
        x='FlightNumber',
        y='LaunchSite',
        color='LandingOutcome',
        title='Launch Site vs Flight Number'
    )

    # Trend Line of Launches per Year
    df_filtered['Year'] = pd.to_datetime(df_filtered['Date']).dt.year
    trend_df = df_filtered.groupby('Year').size().reset_index(name='Launches')
    trend_line = px.line(trend_df, x='Year', y='Launches', title='Launches Over Time')

    # Histogram of Payload Mass
    payload_hist = px.histogram(df_filtered, x='PayloadMass', nbins=20, title='Payload Mass Distribution')

    return total_launches_card, success_rate_card, avg_payload_card, pie_fig, payload_scatter, site_scatter, trend_line, payload_hist

if __name__ == '__main__':
    app.run(debug=True)
