import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
from dash import html
from dash import dcc

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv(r"C:\Users\Dell\Downloads\spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

launch_sites = spacex_df['Launch Site'].unique()

dropdown_options = [{'label':'All Sites','value':'ALL'}] + [{'label':site,'value':site} for site in launch_sites]
# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                dcc.Dropdown(id='site-dropdown',
                                                options=dropdown_options,
                                                value='ALL',
                                                placeholder="Select a Launch Site here",
                                                searchable=True
                                            ),
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    value=[min_payload,max_payload],
                                    marks={
                                        0:'0',
                                        2500:'2500',
                                        5000:'5000',
                                        7500:'7500',
                                        10000:'10000'
                                    }
                                ),
                                html.Br(),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart',component_property='figure'),
    Input(component_id='site-dropdown',component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        #If all sites selected,show total successful launches by site
        fig = px.pie(
            spacex_df.groupby('Launch Site')['class'].sum().reset_index(),
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        #If specifies site selected,show success vs failed counts
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        fig = px.pie(
            filtered_df['class'].value_counts().reset_index(),
            values='count',
            names=['Failed','Success'] if filtered_df['class'].value_counts().index[0] == 0 else ['Success','Failed'],
            title=f'Launch Outcomes for {entered_site}'
        )
    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart',component_property='figure'),
    [Input(component_id='site-dropdown',component_property='value'),
    Input(component_id='payload-slider',component_property='value')]
)
def get_scatter_chart(entered_site,payload_range):
    #Filter by payload range
    filtered_df= spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]

    #Filter by site if specific site selected
    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    #Create Sctter Plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f'Payload vs Launch Success ({entered_site if entered_site != "ALL" else "ALL Sites"})',
        labels = {'class':'Launch Outcome'},
        height=500
    )

    #Customize y-axis
    fig.update_layout(
        yaxis=dict(
            tickmode='array',
            tickvals=[0,1],
            ticktext=['Failed','Success']
        )
    )
    return fig
# Run the app
if __name__ == '__main__':
    app.run_server()
