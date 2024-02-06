import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from gtts import gTTS
import pandas as pd
#from chatterbot import ChatBot
import base64
from dash import callback

# Importing and cleaning of dataset
# ********************************************************************************

# Replace 'YOUR_FILE_ID' with the actual file ID
#url_csv = 'https://raw.githubusercontent.com/SmartDvi/Dash_App/main/loan_themes_by_region.csv'

# Read the CSV file directly from the Google Drive link
#df = pd.read_csv(url_csv)
df = pd.read_csv("C:\\Users\\Moritus Peters\\Documents\\Datasets\\kiva dataset\\loan_themes_by_region.csv")


# contains the data from your CSV file
#print(df)

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
        ),
        dcc.Textarea(id='user-input',
                     placeholder='Ask a question...', rows=4, className='mb-6'),
        html.Button("SUBMIT", id='ask_button', n_clicks=0, className='btn btn-primary mx-2'),
        html.Button("", id='voice-button', n_clicks=0, className='btn btn-secondary'),
        html.Div(id='Output-Area', className='mt-3')


    ], className='me-1  px-3')
)

indicator_card = dbc.Card(
    dbc.CardBody([
        html.H5('Loan Amount Indicator', className='text-primary me-1 mt-9 px-3'),
        dcc.Graph(id='indicator',
                  figure= go.Figure(go.Indicator(
        mode = 'gauge+number+delta',
        value = df[df['sector'] == df['sector'].unique()[0]]['amount'].sum(),
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': 'Loan Amount Distribution by Sector', 'font': {'size': 22} },
        delta = {'reference': df['amount'].mean(), 'valueformat': '.0f', 'prefix': '$', 'suffix': 'M'},
        gauge ={
            'axis': {'range': [None, 400000000], 'tickwidth':1, 'tickcolor': 'darkblue'},
            'bar' : {'color': 'darkblue'},
            'bgcolor' : 'white',
            'borderwidth': 2,
            'bordercolor' : 'gray',
            'steps' : [
                {'range': [None, 78836994], 'color': 'cyan'},
                {'range': [78836994, 236510982], 'color': 'royalblue'},
                {'range': [236510982, 315347975], 'color': 'red'}],
            'threshold' : {
                'line' : {'color': 'red', 'width' : 4},
                'thickness' : 0.75,
                'value' : df['amount'].sum() * 0.75
            }
        }
                  )),
            #config={'displayModeBar': False}  # Hide the plotly toolbar
                  ),
        ])
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
        dbc.Col(indicator_card, className="mt-3 mb-1 "), #className='me-1 px-3', style={'height': '250px'}
    ]),
    dbc.Row([
        dbc.Col(loan_theme_card),
        dbc.Col(mpi_analysis_card, className="mt-3 mb-3"),
    ]),
    dbc.Row([
        dbc.Col(geographical_distribution_card)
    ])
])

# making the gauge indicator interactive with the dropdown
@callback(
        Output('indicator', 'figure'),
        [Input('sector_dropdown', 'value')]
)

def update_indicator(selected_sector):
    indicator_value = df[df['sector'] == selected_sector]['amount'].sum()
    indicator_color ={
        'gradient': True,
        'ranges' : {
            'green': [None, 78836994],
            'yellow' : [78836994, 236510982],
            'red' : [236510982, 315347975]},
    }

    indicator_figure = go.Figure(go.Indicator(
        mode = 'gauge+number+delta',
        value = indicator_value,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': 'Loan Amount Distribution by Sector', 'font': {'size': 22} },
        delta = {'reference': df['amount'].mean(), 'valueformat': '.0f', 'prefix': '$', 'suffix': 'M'},
        gauge ={
            'axis': {'range': [None, 315347975], 'tickwidth':1, 'tickcolor': 'darkblue'},
            'bar' : {'color': 'darkblue'},
            'bgcolor' : 'white',
            'borderwidth': 2,
            'bordercolor' : 'gray',
            'steps' : [
                {'range': [None, 78836994], 'color': 'cyan'},
                {'range': [78836994, 236510982], 'color': 'royalblue'},
                {'range' : [236510982, 315347975], 'color' : 'red'}],
            'threshold' : {
                'line' : {'color': 'red', 'width' : 4},
                'thickness' : 0.75,
                'value' : df['amount'].sum() * 0.75
            }
        }
    ))

    return indicator_figure

# updating the Loan Theme Type Distribution

@callback(
    Output('barChart_Loan_Theme_Type_Distribution', 'figure'),
    [Input('sector_dropdown', 'value')])

def update_Loan_Theme(selected_sector):
    if selected_sector is None:
        selected_sector = df['sector'].iloc[1]

    data = df[df['sector'] == selected_sector] # linking the sector drop tot eh chart
    # developing the chart for loan Theme distribution
    fig1 = px.bar(data,
                  x = 'Loan Theme Type',
                  y = 'amount',
                  title = f' Loan Theme Type Distribution for {selected_sector} sector',
                  color = 'Loan Theme Type' )
    
    return fig1

# callback to update the mpi analysis scatter chart

@callback(
    Output('scatterchart_MPI_Analysis', 'figure'),
    [Input('sector_dropdown', 'value')]

)

def update_MPI_chart(selected_sector):
    if selected_sector is None:
        selected_sector = df['sector'].iloc[1]

    filter_df = df[df['sector'] == selected_sector]
    fig2 = px.scatter(
        filter_df,
        x = 'mpi_region',
        y = 'amount',
        color = 'Loan Theme Type',
        title= f'MPI Region for {selected_sector} Sector')
    return fig2

# callback to update the geographical Distribution of Loan accross countries and sectors

@callback(
    Output('map', 'figure'),
    [Input('sector_dropdown', 'value')]
)

def update_geographical_distribution(selected_sector):
    if selected_sector is None:
        selected_sector = df['sector'].iloc[1]

    filter_df = df[df['sector'] == selected_sector]
    fig3 = px.scatter_mapbox(filter_df,
                             lat='lat',
                             lon='lon',
                             color='amount',
                             hover_name='Loan Theme Type',
                             hover_data=['country', 'region', 'LocationName', 'names'],
                             title = f'Geographical Distribution of Loan For {selected_sector}',
                             mapbox_style= 'open-street-map',
                             zoom = 2
                             )
    return fig3


if __name__ == "__main__":
    app.run_server(debug=True, port=8570)