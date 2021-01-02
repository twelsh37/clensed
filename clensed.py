import dash
from dash.dependencies import Input, Output
import pandas as pd
import re
import plotly.express as px
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from itertools import cycle


# ------------------------------------------------------------------------------
# Set Plotly as our defauly plotting backend
# ------------------------------------------------------------------------------
pd.options.plotting.backend='plotly'

# ------------------------------------------------------------------------------
# Setup our Colour Choices
# ------------------------------------------------------------------------------
# Blue
color_1 = "#3498db"
# Ink
color_2 = "#071633"
# Black
color_3 = "#000000"


palette = cycle(px.colors.qualitative.Dark24)

# ------------------------------------------------------------------------------
# Import RACA Data /Prepare the RACA Data
# ------------------------------------------------------------------------------

APP_DATA = "clensed.csv"

# import dataframe and do some column renames
raca_df = pd.read_csv(APP_DATA)

raca_df.rename(columns={'Process (Title)' : 'process_title',
                   'Process description' : 'process_description',
                   'Risk ID' : 'risk_id',
                   'Risk Owner' : 'risk_owner',
                   'Risk(Title)' : 'risk_title',
                   'Risk Description' : 'risk_description',
                   'Risk Category 1' : 'risk_types',
                   'Risk Category 2' : 'risk',
                   'Risk Category 3' : 'level3',
                   'Associated KRIs' : 'associated_kris',
                   'I' : 'gross_impact',
                   'L' : 'gross_likelihood',
                   'Control ID' : 'control_id',
                   'Control Owner' : 'control_owner',
                   'Control (Title)' : 'control_title',
                   'Control Description' : 'control_description',
                   'Control Activity' : 'control_activity',
                   'Control Type' : 'control_type',
                   'Control Frequency' : 'control_frequency',
                   'DE & OE?':'de_oe',
                   'Commentary on DE & OE assessment': 'de_oe_commentary',
                   'I.1' : 'net_impact',
                   'L.1' : 'net_likelihood',
                   'Commentary on Net Risk Assessment' :
                            'net_risk_assesment_commentary',
                   'Risk Decision' : 'risk_decision',
                   'Issue Description (if applicable)' : 'issue_description',
                   'Action Description' : 'action_description',
                   'Action Owner' : 'action_owner',
                   'Action Due Date' : 'action_due_date',
                   'Completion Date' : 'completion_date',
                   'Action ID' : 'action_id'
                  },inplace = True)

# calculate our gross and net risk scores
# it does this by multiplying the impact and likelihood columns
# the results are appended to teh df dataframe under columns
# gross_risk and net_risk respectivly
raca_df['gross_risk'] = raca_df['gross_impact'] * raca_df['gross_likelihood']
raca_df['net_risk'] = raca_df['net_impact'] * raca_df['net_likelihood']

# convert the two new columns to numeric fields
raca_df['gross_risk'].apply(pd.to_numeric)
raca_df['net_risk'].apply(pd.to_numeric)

# create our function to work through df['risk_id'] and just extract
# the alpha prefix from the risk_id. E.g 'GMBH-P01-R01' becomes 'GMBH'
# 'GMBH' is then appended to the list prefix[]
prefix = []
def business_unit():
    prefix_search=re.compile(r'^[a-zA-Z]+')

    for value in raca_df['risk_id']:
        zz = prefix_search.findall(str(value))
        prefix.append(zz)
    return prefix

business_unit()

# This takes our list of lists, 'prefix', from the function above and pulls out
# all its members into one list 'extract'
extract = [item[0] for item in prefix]

# Insert a new column to hold our business unit and populate it with Business
# Unit Names. We get the business unit names from the 'extract[]' list in the
# step above
result = []
for value in extract:
    if value == 'DP':
        result.append('Data Privacy')
    elif value == 'AP':
        result.append('Accounts Payable')
    elif value == 'BP':
        result.append('British Petroleum')
    elif value == 'CP':
        result.append('Client Profile')
    else:
        print(f"Business Unit {value} has not been added to the function yet")
    #print(f'DEBUG1: Results just in {result}')

# Apply reuslts to 'business_unit' to create the column in the dataframe
raca_df['business_unit'] = result

# ------------------------------------------------------------------------------
# Build app
# ------------------------------------------------------------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Clensed"
server = app.server

# ------------------------------------------------------------------------------
# Define graphs
# ------------------------------------------------------------------------------
graph_bar = dcc.Graph(id="graph-bar",
                      figure={},
                      style={"height": "80vh", "width": "100%"}
                      )

graph_map = dcc.Graph(id="graph-map",
                      figure={},
                      style={"height": "80vh", "width": "100%"}
                      )

graph_line = dcc.Graph(id="graph-line",
                       figure={},
                       style={"height": "75vh", "width": "100%"}
                       )

# ------------------------------------------------------------------------------
# Define Navbar
# ------------------------------------------------------------------------------
# Logo
LOGO = "assets/raca.png"
navbar = dbc.Navbar(
    [
        html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Col(html.Img(src=LOGO, height="40px"), width="106px"),
                    dbc.Col(dbc.NavbarBrand("Risk and Controls Assesments",
                                            className="ml-10",
                                            style={
                                                'font-size': 40
                                            }
                                            )
                            ),
                ],
                align="center",
                no_gutters=True,
            ),
        ),
        dbc.NavbarToggler(id="navbar-toggler"),
    ],
    color=color_2,
    dark=True,
)

# ------------------------------------------------------------------------------
# Define dropdowns
# ------------------------------------------------------------------------------
# Risk Category 1
risk_types_dropdown = dcc.Dropdown(
    id='risk_types',
    multi=False,
    value = 'All',
    clearable=False,
    searchable=True,
    persistence=True,
    persistence_type='session',
    style={"width": "100%"},

    options=[{'label': k, 'value': k}
             for k in sorted(raca_df['risk_types'].astype(str).unique())]
            + [{'label': 'All', 'value': 'All'}],
)

# Risk Category 2
risk_dropdown = dcc.Dropdown(
    id='risk',
    multi=False,
    value ='All',
    clearable=False,
    searchable=True,
    placeholder='Select...',
    persistence=True,
    persistence_type='session',
    style={"width": "100%"},

    options=[{'label': k, 'value': k}
             for k in sorted(raca_df['risk'].astype(str).unique())]
)

# Risk Category 2
level3_dropdown = dcc.Dropdown(
    id='level3',
    multi=False,
    value ='All',
    clearable=False,
    searchable=True,
    placeholder='Select...',
    persistence=True,
    persistence_type='session',
    style={"width": "100%"},

    options=[],

)

# Dropdown containing business units
# This can be used to just report on the RACAs from the particular business unit.
business_unit_dropdown = dcc.Dropdown(
    id="business_unit_dropdown",
    multi=False,
    value='All',
    clearable=False,
    searchable=True,
    placeholder='Select ...',
    persistence=True,
    persistence_type='session',
    style={"width": "100%"},

    options=[{'label': k, 'value': k}
             for k in sorted(raca_df['business_unit'].astype(str).unique())]
            + [{'label': 'All', 'value': 'All'}],
)

# ------------------------------------------------------------------------------
# Define overview options card
# ------------------------------------------------------------------------------
overview_options_card = dbc.Card(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row([dbc.Label("Level 1 Risks")]),
                        dbc.Row([risk_types_dropdown]),
                        html.Br(),
                        dbc.Row([dbc.Label("Level 2 Risks")]),
                        dbc.Row([risk_dropdown]),
                        html.Br(),
                        dbc.Row([dbc.Label("Level 3 Risks")]),
                        dbc.Row([level3_dropdown]),
                        html.Br(),
                        html.Br(),
                        dbc.Row([dbc.Label("Or Select a Business Unit Below")]),
                        html.Br(),
                        dbc.Row([dbc.Label("Select Business Unit")]),
                        dbc.Row([business_unit_dropdown]),
                    ], style={"width": "100%"},
                )
            ], style={"width": "100%"},
        ),
    ],
    body=True,
    style={"width": "100%"},
)

# ------------------------------------------------------------------------------
# Define Risk Datatable
# ------------------------------------------------------------------------------
data_table = dash_table.DataTable(
    id='table',
    # This line reads in all the columns in our dataframe raca_df
    #columns=[{"name": i, "id": i} for i in raca_df.columns],
    columns=[
        {'name': 'Risk description', 'id': 'risk_description', 'type': 'text',
         'editable': False},
        {'name': 'Risk ID', 'id': 'risk_id', 'type': 'text', 'editable': False},
        {'name': 'Risk Owner', 'id': 'risk_owner', 'type': 'text',
         'editable': False},
        {'name': 'Risk(Title)', 'id': 'risk_title', 'type': 'text',
         'editable': False},
        {'name': 'Risk Category 1', 'id': 'risk_types', 'type': 'text',
         'editable': False},
        {'name': 'Risk Category 2', 'id': 'risk', 'type': 'text',
         'editable': False},
        {'name': 'Risk Category 3', 'id': 'level3', 'type': 'text',
         'editable': False},
        {'name': 'Gross Risk', 'id': 'gross_risk', 'type': 'numeric',
         'editable': False},
        {'name': 'Net Risk', 'id': 'net_risk', 'type': 'numeric',
         'editable': False},

    ],
    data=raca_df.to_dict('records'),
    filter_action="native",
    sort_action="native",
    style_cell={
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
        'maxWidth': 0,
        'textAlign': 'left',
        'fontSize': 12,
        'font-family':'sans-serif',
    },

    #----------------------------------------------------------------
    # Overflow cells' content into multiple lines
    #----------------------------------------------------------------
    style_data={
        'whiteSpace': 'normal',
        'height': 'auto'
    },

    style_cell_conditional=[
        {'if': {'column_id': 'risk_description'},
         'width': '40%', 'textAlign': 'left'},
        {'if': {'column_id': 'risk_id'},
         'width': '5%', 'textAlign': 'left'},
        {'if': {'column_id': 'risk_owner'},
         'width': '5%', 'textAlign': 'left'},
        {'if': {'column_id': 'risk_title'},
         'width': '10%', 'textAlign': 'left'},
        {'if': {'column_id': 'risk_type'},
         'width': '10%', 'textAlign': 'left'},
        {'if': {'column_id': 'risk'},
         'width': '10%', 'textAlign': 'left'},
        {'if': {'column_id': 'level3'},
         'width': '10%', 'textAlign': 'left'},
        {'if': {'column_id': 'gross_risk'},
         'width': '5%'},
        {'if': {'column_id': 'gross_risk'},
         'width': '5%'},
    ],
    style_data_conditional=[
        # Set up alternating line colourings for ease of reading
        {
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(235, 239, 240)'
        },

        # Align text to the left ******************************
        {
            'if': {
                'column_type': 'numeric'
                # 'text' | 'any' | 'datetime' | 'numeric'
            },
            'textAlign': 'right'
        },

        # Format active cells *********************************
        {
            'if': {
                'state': 'active'  # 'active' | 'selected'
            },
            'border': '3px solid rgb(0, 116, 217)'
        },
        {
            'if': {
                'column_editable': False  # True | False
            },
         },

        # Format Gross and Net Risk ***************************
        # Cells dependant on risk score ***********************
        #|------------|------------------|---------|------------|
        #| Priority   | RGB Colour Value | Hex     |  Range     |
        #|------------+------------------+---------+------------|
        #| Very High  | 255, 0, 0        | #FF0000 | > 18       |
        #| High       | 255, 165, 0      | #FFA500 | > 11 < 17  |
        #| Medium     | 255, 255, 0      | #FFFF00 | > 7 < 11   |
        #| Low        | 154, 205, 50     | #9ACD32 | > 3 < 7    |
        #| Very Low   | 127, 255, 0      | #7FFF00 | <= 3       |
        #| Blank      | 255, 255, 255    | #FFFFFF | " "        |
        #|------------|------------------|---------|------------|

        # Very High - Gross Risk
        {
            'if': {
                'column_id': 'gross_risk',
                'filter_query': '{gross_risk} gt 16'
            },
            'backgroundColor': 'rgb(255, 0, 0)',
            'color': 'black',
            'font-size': 22,
            'textAlign': 'center',
        },

        # Very High - Net Risk
        {
            'if': {
                'column_id': 'net_risk',
                'filter_query': '{net_risk} gt 16'
            },
            'backgroundColor': 'rgb(255, 0, 0)',
            'color': 'black',
            'font-size': 22,
            'textAlign': 'center',
        },

        # High - Gross Risk
        {
            'if': {
                'column_id': 'gross_risk',
                'filter_query': '{gross_risk} gt 11 && {gross_risk} lt 17'
            },
            'backgroundColor': 'rgb(255, 165, 0)',
            'color': 'black',
            'font-size': 22,
            'textAlign': 'center',
        },

        # High - Net Risk
        {
            'if': {
                'column_id': 'net_risk',
                'filter_query': '{net_risk} gt 11 && {net_risk} lt 17'
            },
            'backgroundColor': 'rgb(255, 165, 0)',
            'color': 'black',
            'font-size': 22,
            'textAlign': 'center',
        },

        # Medium - Gross Risk
        {
            'if': {
                'column_id': 'gross_risk',
                'filter_query': '{gross_risk} gt 7 && {gross_risk} lt 11'
            },
            'backgroundColor': 'rgb(255, 255, 0)',
            'color': 'black',
            'font-size': 22,
            'textAlign': 'center',
        },

        # Medium - Net Risk
        {
            'if': {
                'column_id': 'net_risk',
                'filter_query': '{net_risk} gt 7 && {net_risk} lt 11'
            },
            'backgroundColor': 'rgb(255, 255, 0)',
            'color': 'black',
            'font-size': 22,
            'textAlign': 'center',
        },

        # Low - Gross Risk
        {
            'if': {
                'column_id': 'gross_risk',
                'filter_query': '{gross_risk} gt 3 && {gross_risk} lt 7'
            },
            'backgroundColor': 'rgb(154, 205, 50)',
            'color': 'black',
            'font-size': 22,
            'textAlign': 'center',
        },

        # Low - Net Risk
        {
            'if': {
                'column_id': 'net_risk',
                'filter_query': '{net_risk} gt 3 && {net_risk} lt 7'
            },
            'backgroundColor': 'rgb(154, 205, 50)',
            'color': 'black',
            'font-size': 22,
            'textAlign': 'center',
        },

        # Very Low - Gross Risk
        {
            'if': {
                'column_id': 'gross_risk',
                'filter_query': '{gross_risk} gt 0 && {gross_risk} lt 4'
            },
            'backgroundColor': 'rgb(127, 255, 0)',
            'color': 'black',
            'font-size': 22,
            'textAlign': 'center',
        },

        # Very Low - Net Risk
        {
            'if': {
                'column_id': 'net_risk',
                'filter_query': '{net_risk} gt 0 &&  {net_risk} lt 4'
            },
            'backgroundColor': 'rgb(127, 255, 0)',
            'color': 'black',
            'font-size': 22,
            'textAlign': 'center',
        },
    ],

    #------------------------------------------------------------------
    # Freeze Rows - digit represents number of rows frozen 0 being header
    # row
    #------------------------------------------------------------------
    fixed_rows={'headers': True, 'data': 0},

    style_header={
        # Style the table header row with Ink colour
        'backgroundColor': 'rgb(7, 22, 51)',
        'fontWeight': 'bold',
        'color': 'white'
    },

)

# ------------------------------------------------------------------------------
# Define tabs
# ------------------------------------------------------------------------------
tab1_content = dbc.Row(
    [
        html.Div([
            html.Br(),
            # Setup our Headings on the Overview Tab
            html.Span('RACA Overview',
                      style={
                          "font-size": 22,
                          "color": color_2,
                          'font-weight': 'bold'}),
            html.Br(),
            html.Span('Overall RACA Statistics',
                      style={
                          "font-size": 14,
                          "color": color_2}),
        ]
        ),

        html.Br(),
        # Setup our initial 4 Charts/Tables
        html.Div([
            # Chart 1
            html.Div([
                dcc.Graph(id='barchart1'),
            ], className='six columns'),

            # Chart 2
            html.Div([
                dcc.Graph(id='barchart2'),
            ], className='six columns'),

        ], ),

        html.Div([
            # Chart 3
            html.Div([
                dcc.Graph(id='piechart1'),
            ], className='six columns'),

            # Chart 4
            html.Div([
                dcc.Graph(id='piechart2'),
            ], className='six columns'),

        ],),
    ],
    no_gutters=True,
)

# Data table showing Risk section of RACA
tab2_content = dbc.Col(
    [
        html.Div([
            html.Br(),
            html.Span('Risk Data', style={
                "font-size": 22,
                "color": color_2,
                'font-weight': 'bold'}),

            html.Br(),
            html.Span('Initial Risk data as well as a cumulative Gross and Net'
                      ' risk score arrived at by multiplying '
                      'Gross Impact x Gross Likelihood, and similar for Net',
                      style={
                          "font-size": 14,
                          "color": color_2}),
        ]
        ),
        dbc.Card(data_table, body=True)
    ]
)

tabs = dbc.Tabs(
    [
        dbc.Tab(tab1_content,
                tab_id="tab_map",
                label="Overview"
                ),  # style={"width": "100%"}),

        dbc.Tab(tab2_content,
                tab_id="tab_total",
                label="Data Table"),
        # style={"width": "100%"}),

    ],
    id="tabs",
    active_tab="tab_map",
    style={"width": "100%"}
    # style={"height": "auto", "width": "auto"},
)

# ------------------------------------------------------------------------------
# Define layout
# ------------------------------------------------------------------------------
app.layout = html.Div(
    [
        navbar,
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Collapse(
                            overview_options_card,
                            id="menu_1",
                        )
                    ], id="menu_col_1", width=6, xs=6, sm=5, md=4, lg=3, xl=2
                ),
                dbc.Col([tabs]),
            ], style={"height": "auto", "width": "99%"},
        )
    ],
    # style={"height": "auto", "width": "auto"},
)


# ------------------------------------------------------------------------------
# Define callback to toggle tabs
# ------------------------------------------------------------------------------
@app.callback(
    [Output("business_unit_dropdown", "disabled"),
     Output("menu_1", "is_open"),
     Output("menu_col_1", "width"),
     Output("menu_col_1", "xs"),
     Output("menu_col_1", "sm"),
     Output("menu_col_1", "md"),
     Output("menu_col_1", "lg"),
     Output("menu_col_1", "xl")],
    [Input("tabs", "active_tab")],
)
def toggle_tabs(id_tab):
    if id_tab == "tab_time" or id_tab == "tab_table":
        return False, False, "0%", 0, 0, 0, 0, 0
    elif id_tab == "tab_map":
        return True, True, "0%", 6, 5, 4, 3, 2
    elif id_tab == "tab_total":
        return False, True, "0%", 6, 5, 4, 3, 2


# ------------------------------------------------------------------------------
# Set Callback to define our dropdown boxes
# ------------------------------------------------------------------------------
@app.callback(
    Output('risk', 'options'),
    Input('risk_types', 'value'))
def set_tl2_options(tl1_options):
    if tl1_options != 'All':
        raca_options = raca_df['risk_types'] == tl1_options
        #print(f'DEBUG1: TL 1 Not equal to all: {raca_options}')
    else:
        raca_options = raca_df
        #print(f'DEBUG2: TL1 equal to all: {raca_options}')

    return [{'label': i, 'value': i}
            for i in sorted(raca_options['risk'].astype(str).unique())]

@app.callback(
    Output('level3', 'options'),
    Input('risk', 'value'))
def set_tl3_options(tl2_options):
    if tl2_options != 'All':
        raca_options = raca_df[raca_df['risk'] == tl2_options]
        #print(f'DEBUG3: TL2 Not equal to all: {raca_options}')
    else:
        raca_options = raca_df
        #print(f'DEBUG4: TL2 equal to all: {raca_options}')
    return [{'label': i, 'value': i}
            for i in sorted(raca_options['level3'].astype(str).unique())]

# ------------------------------------------------------------------------------
# Define callback to update graph
#------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Define Callback to update data_table  on tab_1 id = table
#------------------------------------------------------------------------------

# ------------------------------------------------------------------------------
# Run app and display the result
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=True)
