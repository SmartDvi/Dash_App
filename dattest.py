import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import dash_daq as daq
import pandas as pd

# Importing and cleaning of dataset
# ********************************************************************************
# Replace the following line with the path to your CSV file
df = pd.read_csv("C:\\Users\\Moritus Peters\\Documents\\navy\\loan_themes_by_region.csv")

df['mpi_region'] = df['mpi_region'].str.split(',').str[0]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

# Navbar
navbar = dbc.NavbarSimple(
    children=[
        html.Div([
            html.H1('Kiva Loan Distribution', className='text-center text-primary mb-4 me-1'),
            html.P("Kiva facilitates financial inclusion globally by crowdfunding loans, improving financial services, and overcoming barriers, enabling individuals to access education, start businesses, invest in farming, and afford emergency care."),
            dbc.NavItem(dbc.NavLink('Home', href='https://www.kiva.org/', className='text-light ml-auto'), className='ml-auto', ),
            dbc.NavItem(dbc.NavLink('Make a difference today', href='https://www.kiva.org/lend-by-category', className='text-light ml-auto'),className='ml-auto', ),
        ]),
    ],
    brand_href="https://www.kiva.org/impact",
    color='dark',
    dark=True,
    className='text-center text-primary mb-4'
)

# Cards
sector_card = dbc.Card(
    dbc.CardBody([
        html.H5('Sector',className='text-primary me-1 mt-9 px-3'),
        dcc.Dropdown(
            id='sector_dropdown',
            multi=False,
            options=[{'label': x, 'value': x} for x in sorted(df['sector'].unique())],
            style={'color': 'black'}
        )
    ], className='me-1 mt-5 px-3')
)

indicator_card = dbc.Card(
    dbc.CardBody([
        html.H5('Loan Amount Indicator', className='text-primary me-1 mt-9 px-3'),
        dcc.Graph(
            id='indicator',
            figure=go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=df[df['sector'] == df['sector'].iloc[0]]['amount'].sum(),
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Loan Amount", 'font': {'size': 24}},
                delta={'reference': df['amount'].mean() , "valueformat": ".0f", "prefix": "$", "suffix": "m"},
                gauge={
                    'axis': {'range': [0, df['amount'].sum()]},
                    'bar': {'color': "darkblue"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, df['amount'].sum() * 0.25], 'color': 'cyan'},
                        {'range': [df['amount'].sum() * 0.25, df['amount'].sum() * 0.75], 'color': 'royalblue'},
                        {'range': [df['amount'].sum() * 0.75, df['amount'].sum()], 'color': 'red'}],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': df['amount'].sum() * 0.75}
                }
            )),
            config={'displayModeBar': False}  # Hide the plotly toolbar
        ),
    ]) #className='me-1 px-3', style={'height': '250px'})
)

loan_theme_card = dbc.Card(
    dbc.CardBody([
        html.H5('Loan Theme Type Distribution', className='text-primary me-1 mt-9 px-3'),
        dcc.Graph(id='barChart_Loan_Theme_Type_Distribution', figure={})
    ], className='me-1 mt-5 px-3')
)

mpi_analysis_card = dbc.Card(
    dbc.CardBody([
        html.H5('MPI (Multidimensional Poverty Index) Analysis:',
                className='text-primary me-1 mt-9 px-3'),
        dcc.Graph(id='scatterchart_MPI_Analysis', figure={})
    ], className='me-1 mt-5 px-3')
)

geographical_distribution_card = dbc.Card(
    dbc.CardBody([
        html.H5('Geographical Distribution of Loans', className='text-center text-primary me-1 mt-9 px-3'),
        dcc.Graph(id='map', figure={})
    ], className='me-1 mt-5 px-3')
)

# Layout
app.layout = dbc.Container([
    navbar,
    dbc.Row([
        dbc.Col(sector_card, className="mt-3 mb-3 px-3"),
        dbc.Col(indicator_card, className="mt-3 mb-1 "),
    ]),
    dbc.Row([
        dbc.Col(loan_theme_card),
        dbc.Col(mpi_analysis_card, className="mt-3 mb-3"),
    ]),
    dbc.Row([
        dbc.Col(geographical_distribution_card)
    ])
])

# Callbacks
@app.callback(
    [Output('indicator', 'figure'),
     Output('scatterchart_MPI_Analysis', 'figure'),
     Output('barChart_Loan_Theme_Type_Distribution', 'figure'),
     Output('map', 'figure')],
    [Input('sector_dropdown', 'value')],
    [State('barChart_Loan_Theme_Type_Distribution', 'clickData'),
     State('scatterchart_MPI_Analysis', 'clickData'),
     State('map', 'selectedData')]
)
def update_visualizations(selected_sector, bar_chart_click_data, scatter_chart_click_data, map_selected_data):
    try:
        # Update indicator figure based on the selected sector
        indicator_value = df[df['sector'] == selected_sector]['amount'].sum()
        indicator_color = {
            "gradient": True,
            "ranges": {"green": [0, df['amount'].sum() * 0.25],
                       "yellow": [df['amount'].sum() * 0.25, df['amount'].sum() * 0.75],
                       "red": [df['amount'].sum() * 0.75, df['amount'].sum()]},
        }

        indicator_figure = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=indicator_value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Loan Amount", 'font': {'size': 24}},
            delta={'reference': df['amount'].mean() ,"valueformat": ".0f" ,"prefix": "$", "suffix": "M"},
            gauge={
                'axis': {'range': [0, df['amount'].sum()]},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, df['amount'].sum() * 0.25], 'color': 'cyan'},
                    {'range': [df['amount'].sum() * 0.25, df['amount'].sum() * 0.75], 'color': 'royalblue'},
                    {'range': [df['amount'].sum() * 0.75, df['amount'].sum()], 'color': 'red'}],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': df['amount'].sum() * 0.75}
            }
        ))

        # Update bar chart based on clicked data
        if bar_chart_click_data is not None:
            clicked_loan_theme_type = bar_chart_click_data['points'][0]['x']
            filtered_df = df[(df['sector'] == selected_sector) & (df['Loan Theme Type'] == clicked_loan_theme_type)]
            bar_chart_figure = px.bar(filtered_df['Loan Theme Type'].value_counts(),
                                      x=filtered_df['Loan Theme Type'].value_counts().index,
                                      y=filtered_df['Loan Theme Type'].value_counts().values,
                                      title=f'Loan Theme Type Distribution for {selected_sector}',
                                      labels={"x": "Loan Theme Type", "y": "Total County by Loan Theme Type"})
        else:
            bar_chart_figure = px.bar(df[df['sector'] == selected_sector]['Loan Theme Type'].value_counts(),
                                      x=df[df['sector'] == selected_sector]['Loan Theme Type'].value_counts().index,
                                      y=df[df['sector'] == selected_sector]['Loan Theme Type'].value_counts().values,
                                      title=f'Loan Theme Type Distribution for {selected_sector}',
                                      labels={"x": "Loan Theme Type", "y": "Total County by Loan Theme Type"})

        # Update scatter chart based on clicked data
        if scatter_chart_click_data is not None:
            clicked_data = scatter_chart_click_data['points'][0]['customdata']
            filtered_df_scatter = df[df['some_column'] == clicked_data]
            scatter_chart_figure = px.scatter(filtered_df_scatter, x='mpi_region', y='amount',
                                              color='Loan Theme Type', hover_name='Loan Theme Type',
                                              title=f'MPI Analysis for {selected_sector}')
        else:
            scatter_chart_figure = px.scatter(df[df['sector'] == selected_sector], x='mpi_region', y='amount',
                                              color='Loan Theme Type', hover_name='Loan Theme Type',
                                              title=f'MPI Analysis for {selected_sector}')

        # Update map based on selected data
        if map_selected_data is not None:
            # Extract relevant information from selectedData
            selected_points = map_selected_data['points']
            # Your logic to update the map based on the selected data
            # For example, you can filter the DataFrame based on selected points and create a new map

            filtered_df_map = df[df.index.isin([point['pointIndex'] for point in selected_points])]
            map_figure = px.scatter_mapbox(filtered_df_map, lat='lat', lon='lon', color='amount',
                                           size='amount', hover_name='Loan Theme Type',
                                           title=f'Geographical Distribution of Loans for {selected_sector}',
                                           mapbox_style="open-street-map")
            map_figure.update_layout(mapbox=dict(center={'lat': filtered_df_map['lat'].mean(),
                                                        'lon': filtered_df_map['lon'].mean()},
                                                zoom=3))
        else:
            map_figure = px.scatter_mapbox(df[df['sector'] == selected_sector], lat='lat', lon='lon', color='amount',
                                           size='amount', hover_name='Loan Theme Type',
                                           hover_data=['country', 'region', 'LocationName', 'names'],
                                           title=f'Geographical Distribution of Loans for {selected_sector}',
                                           mapbox_style="open-street-map")
            map_figure.update_layout(mapbox=dict(center={'lat': df[df['sector'] == selected_sector]['lat'].mean(),
                                                        'lon': df[df['sector'] == selected_sector]['lon'].mean()},
                                                zoom=3))

        return indicator_figure, scatter_chart_figure, bar_chart_figure, map_figure

    except Exception as e:
        print(f"Error in callback: {e}")
        # You can add further error handling or logging here
        return go.Figure(), px.scatter(), px.bar(), px.scatter_mapbox()

if __name__ == "__main__":
    app.run_server(debug=True, port=5000)
