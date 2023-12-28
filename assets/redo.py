import dash
from datetime import datetime, date
import numpy as np
from dash import dcc, html
from dash.dependencies import Output, Input, State
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
import pandas as pd
import pandas_datareader.data as web
import datetime

# importing and cleaning of dataset
# ********************************************************************************
df = pd.read_excel("C:\\Users\\Moritus Peters\\Downloads\\Adidas Sales.xlsx")
df[:3]

# Convert 'InvoiceNo' column to string
df['Price per Unit'] =  df['Price per Unit'].astype(str)

# Remove '/C/' from the 'InvoiceNo' column
df['Price per Unit'] =  df['Price per Unit'].str.replace('/C/', '', regex=True)

# Remove any remaining non-numeric characters (except for decimal points)
df['Price per Unit'] =  df['Price per Unit'].str.replace('[^0-9.]', '', regex=True)

# Convert 'InvoiceNo' to numeric
df['Price per Unit'] = pd.to_numeric( df['Price per Unit'])

# fetching invoice Month column from invoice Date
df['Month'] = pd.to_datetime(df['Invoice Date']).dt.month_name()
# fetching invoice day column from invoice Date
df['Day'] = pd.to_datetime(df['Invoice Date']).dt.day_name()
# fetching invoice year column from invoice Date
df['year'] = pd.to_datetime(df['Invoice Date']).dt.year

df['Revenue'] = df['Price per Unit'] * df['Units Sold']
# Calculate Total Revenue per City
product_revenue = df.groupby('City')['Revenue'].sum().sort_values(ascending=False)
gh = product_revenue.head().reset_index()
print(gh)
# Calculate Total Revenue per City
product_revenue = df.groupby('Product')['Revenue'].sum().sort_values(ascending=False)
PR = product_revenue.head().reset_index()
print(PR)
# Calculate Total Revenue per Month
Month_revenue = df.groupby('Month')['Revenue'].sum().sort_values(ascending=False)
MR = Month_revenue.head().reset_index()
# Calculate Total Sales per Region
Region_sales = df.groupby('Region')['Total Sales'].sum().sort_values(ascending=False)
RS = Region_sales.head().reset_index()
print(RS)
# Calculate Total Revenue per Product
product_TotalSales = df.groupby('Product')['Total Sales'].sum().sort_values(ascending=False)
PS = product_TotalSales.reset_index()
# Calculate Total Revenue per Region
Region_Revenue = df.groupby('Region')['Revenue'].sum().sort_values(ascending=False)
RR = Region_Revenue.head().reset_index()

# *******************************************************************************************
# https://www.bootstrapcdn.com/bootswatch/
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}]
                )

#Layout section: Bootstrap (https://hackerthemes.com/bootstrap-cheatsheet/)
# ************************************************************************

app.layout = dbc.Container([
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink('Home', href="https://www.adidas.com/us"))
        ], brand="Adidas Sales Dashboard",
        brand_href = "f",
        color='Primary',
        dark=False,
        className= 'me-1' "mt-2" 'px-3'
    ),
    dbc.Row([
        dbc.Col([
            html.H5('State', className= 'me-1' "mt-5" 'px-3'),
            dcc.Dropdown(
                id='State_dropdown',
                multi=False,
                options=[{'label': x, 'value': x} for x in sorted(df['State'].unique())],
            ),
            html.H5('Sales Method', className='card-title'),
            dcc.Checklist(
                id='id_checklist',
                options=[{'label': i, 'value': i} for i in sorted(df['Sales Method'].unique())],
                value=sorted(df['Sales Method'].unique()[0]),
                inline=True
            ),


        ]),
        dbc.Col([
            html.H5('Revenue Gauge ', className= 'me-1' "mt-5" 'px-3'),
            dcc.Graph(id='indicator', figure={}),

        ])
    ]),
    dbc.Row([
        dbc.Col([
            html.H5('Revenue Trend per Day',
                    className='text-center text-primary mb-4'),
            dcc.Graph(id='lineChart_Revenue_perday', figure={})

        ]),
        dbc.Col([
            html.H5('Revenue Trend Per Product',
                    className='text-center text-primary mb-4'),
            dcc.Graph(id='BarChart_Revenue_perProduct', figure={})

        ]),

]),
    dbc.Row([
        dbc.Col([
            html.H5('Revenue Trend Per State',
                    className='text-center text-primary mb-4'),
            dcc.Graph(id='Map_Revenue_per State', figure={})


        ])
    ])

])

# callback section: connection the components
#*************************************************************************************

@app.callback(
    Output(component_id='lineChart_Revenue_perday', component_property='figure'),
    Output(component_id='BarChart_Revenue_perProduct', component_property='figure'),
    Output(component_id='Map_Revenue_per State', component_property='figure'),
    Output(component_id='indicator', component_property='figure'),
    [Input(component_id='State_dropdown', component_property='value'),
     Input(component_id='id_checklist', component_property='value')],
    [State(component_id='Map_Revenue_per State', component_property='selectedData')]
)

def update_all_graphs(selected_state_dropdown, selected_methods_checklist, selected_state_map):
    # Your logic to update all graphs based on user interactions

    # Filter data based on selected_state_dropdown and selected_methods_checklist
    filtered_data = df[df['State'] == selected_state_dropdown]
    filtered_data = filtered_data[filtered_data['Sales Method'].isin(selected_methods_checklist)]

    # Create line chart
    line_chart = px.line(filtered_data, x='Day', y='Revenue', title=f'Revenue Trend per Day in {selected_state_dropdown}')

    # Create bar chart
    bar_chart = px.bar(filtered_data, x='Product', y='Revenue', title=f'Revenue Trend Per Product in {selected_state_dropdown}')

    # Create map chart
    map_chart = px.scatter_geo(filtered_data, locations='State', locationmode='USA-states', color='Revenue',
                               title=f'Revenue Trend Per State - {selected_state_dropdown}')

    # Create gauge chart (indicator)
    indicator_chart =go.Figure( go.Indicator(
        title='Revenue Gauge',
        value=df['Revenue'].sum(),
        domain={'x' : [0, 0.6], 'y': [0, 0.5]},
        mode="number+gauge+delta",
        gauge=dict(
            axis=dict(range=[None, df['Revenue'].sum() * 1.5]),

            steps=[
                dict(range=[0, df['Revenue'].sum() * 0.25], color="red"),
                dict(range=[df['Revenue'].sum() * 0.25, df['Revenue'].sum() * 0.75], color="yellow"),
                dict(range=[df['Revenue'].sum() * 0.75, df['Revenue'].sum() * 1.5], color="green"),
            ],
        )
    )
    )
    return line_chart, bar_chart, map_chart, indicator_chart

if __name__=="__main__":
    app.run_server(debug=True, port=7050)