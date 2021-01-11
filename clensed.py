import dash
from dash.dependencies import Input, Output
import pandas as pd
import re
import plotly.express as px
import plotly.graph_objects as go
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from itertools import cycle

# ------------------------------------------------------------------------------
# Set Plotly as our defauly plotting backend
# ------------------------------------------------------------------------------
pd.options.plotting.backend = 'plotly'

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
# Import TEST RACA Data /Prepare the RACA Data
# ------------------------------------------------------------------------------
# Test data
APP_DATA = "clensed.xlsx"

# import TEST dataframe and do some column renames
raca_df = pd.read_excel(APP_DATA)

# ------------------------------------------------------------------------------
# Rename our column headers
# ------------------------------------------------------------------------------

raca_df.rename(columns={'Process (Title)': 'process_title',
                        'Process description': 'process_description',
                        'Risk ID': 'risk_id',
                        'Risk Owner': 'risk_owner',
                        'Risk(Title)': 'risk_title',
                        'Risk Description': 'risk_description',
                        'Risk Category 1': 'risk_types',
                        'Risk Category 2': 'risk',
                        'Risk Category 3': 'level3',
                        'Associated KRIs': 'associated_kris',
                        'I': 'gross_impact',
                        'L': 'gross_likelihood',
                        'Control ID': 'control_id',
                        'Control Owner': 'control_owner',
                        'Control (Title)': 'control_title',
                        'Control Description': 'control_description',
                        'Control Activity': 'control_activity',
                        'Control Type': 'control_type',
                        'Control Frequency': 'control_frequency',
                        'DE & OE?': 'de_oe',
                        'Commentary on DE & OE assessment': 'de_oe_commentary',
                        'I.1': 'net_impact',
                        'L.1': 'net_likelihood',
                        'Commentary on Net Risk Assessment':
                            'net_risk_assesment_commentary',
                        'Risk Decision': 'risk_decision',
                        'Issue Description (if applicable)':
                            'issue_description',
                        'Action Description': 'action_description',
                        'Action Owner': 'action_owner',
                        'Action Due Date': 'action_due_date',
                        'Completion Date': 'completion_date',
                        'Action ID': 'action_id'
                        }, inplace=True)

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
    prefix_search = re.compile(r'^[a-zA-Z]+')

    dff = raca_df

    for e in dff['risk_id']:
        zz = prefix_search.findall(str(e))
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
    value='All',
    clearable=False,
    searchable=True,
    persistence=True,
    persistence_type='session',
    style={"width": "100%"},

    options=[{'label': k, 'value': k}
             for k in sorted(raca_df['risk_types'].astype(str).unique())] +
            [{'label': 'All', 'value': 'All'}],
)

# Risk Category 2
risk_dropdown = dcc.Dropdown(
    id='risk',
    multi=False,
    value='All',
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
    value='All',
    clearable=False,
    searchable=True,
    placeholder='Select...',
    persistence=True,
    persistence_type='session',
    style={"width": "100%"},

    options=[],

)

# Dropdown containing business units
# This can be used to just report on the RACAs from the particular business
# unit.
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
             for k in sorted(raca_df['business_unit'].astype(str).unique())] +
            [{'label': 'All', 'value': 'All'}],
)

# ------------------------------------------------------------------------------
# Define the table for the Risk Colour Legend
# ------------------------------------------------------------------------------
table_header = [
    html.Thead(html.Tr([html.Th("Legend")]))
]

row1 = html.Tr([html.Td("Very High")],
               style={'backgroundColor': 'rgb(255, 0 ,0)'})
row2 = html.Tr([html.Td("High")],
               style={'backgroundColor': 'rgb(255, 165 ,0)'})
row3 = html.Tr([html.Td("Medium")],
               style={'backgroundColor': 'rgb(255, 255 ,0)'})
row4 = html.Tr([html.Td("Low")],
               style={'backgroundColor': 'rgb(154, 205 ,50)'})
row5 = html.Tr([html.Td("Very Low")],
               style={'backgroundColor': 'rgb(127,255, 0)'})

table_body = [html.Tbody([row1, row2, row3, row4, row5])]

# ------------------------------------------------------------------------------
# Define overview options card
# ------------------------------------------------------------------------------
overview_options_card = dbc.Card(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(id='overview-container', children=[
                            dbc.Row([dbc.Label("Level 1 Risks")]),
                            dbc.Row([risk_types_dropdown]),
                            html.Br(),
                        ], style={'display': 'block', 'marginBottom': 50}),
                        html.Div(id='dropdown-container', children=[
                            dbc.Row([dbc.Label("Level 2 Risks")]),
                            dbc.Row([risk_dropdown]),
                            html.Br(),
                            dbc.Row([dbc.Label("Level 3 Risks")]),
                            dbc.Row([level3_dropdown]),
                            # This is the line that shows or hides the sliders
                        ], style={'display': 'block', 'marginBottom': 50}),
                        html.Br(),
                        html.Br(),
                        html.Div(id='business-unit-container', children=[
                            dbc.Row([
                                dbc.Label("Or Select a Business Unit Below")]),
                            html.Br(),
                            dbc.Row([dbc.Label("Select Business Unit")]),
                            dbc.Row([business_unit_dropdown]),
                        ], style={'display': 'block', 'marginBottom': 50}),
                    ], style={"width": "100%", 'marginBottom': 50},
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.Div(id='legend-container', children=[
                                    dbc.Table(table_header + table_body,
                                              bordered=True),
                                ], style={'display': 'block',
                                          'marginBottom': 50}),
                            ]
                        ),

                    ], style={"width": "100%", 'marginBottom': 50},
                )
            ], style={"width": "100%"},
        ),
    ],
    body=True,
    style={"width": "100%"},
)

#------------------------------------------------------------------------------
# Define our cards
# ------------------------------------------------------------------------------
card_monthly_reporting = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H5("Issues/Actions logged against a Business Unit",
                        className="card-title"),

                # html.H6("Number of Actions against a Business Unit",
                #         className="card-subtitle"),

                html.P(
                    "Number of Actions against a Business Unit",
                    className="card-text",
                ),

                dash_table.DataTable(
                    id = 'dt_card_mr',
                    columns=[
                            {'name': 'RACA Business Unit', 'id':'business_unit',
                             'type': 'text','editable': False},
                            {'name': 'Open RACA issues/Actions', 'id':
                                'count',
                         'type': 'text', 'editable': False},

                    ],
                    style_cell = {
                                 'overflow': 'hidden',
                                 'textOverflow': 'ellipsis',
                                 'maxWidth': 40,
                                 'textAlign': 'left',
                                 'fontSize': 12,
                                 'font-family': 'sans-serif',
                             },

                    style_header={'backgroundColor': 'rgb(7,22,51)',
                                  'color': 'white',
                                  'font_size': '12px'},

                )
            ]

        )
    ],
    color="light",   # https://bootswatch.com/default/ for more card colors
    inverse=False,   # change color of text (black or white)
    outline=True,  # True = remove the block colors from the background and
    # header
    style={"width": "30rem"}
)

card_monthly_reporting_2 = dbc.Card(
    [
        dbc.CardBody(
            [
                html.H5("RACA Actions Summary",
                        className="card-title"),

                html.P(
                    "Action status tracked against time",
                    className="card-text",
                ),
                dash_table.DataTable(
                    id = 'dt_card_mr_1',
                    columns=[
                            {'name': 'RACA Business Unit', 'id':'business_unit',
                             'type': 'text','editable': False},
                            {'name': 'Overdue more than 3 Months', 'id':'gt-3',
                             'type': 'numeric','editable': False},
                            {'name': 'Overdue between 1 & 3 Months',
                             'id':'lteq-3', 'type': 'numeric',
                             'editable': False},
                            {'name': 'Due within 1 Month', 'id':'lteq-13',
                             'type': 'numeric','editable': False},
                            {'name': 'Due between 1 & 3 months', 'id':'lteq13',
                             'type': 'numeric','editable': False},
                            {'name': 'Due min more than 3 momnths', 'id':'gt3',
                             'type': 'numeric','editable': False},
                            {'name': 'Due date to be confirmed', 'id':'ddtbc',
                             'type': 'numeric','editable': False},
                            {'name': 'Total Open Actions', 'id':'toa',
                             'type': 'numeric','editable': False},
                            {'name': 'Total Actions', 'id':'ta',
                             'type': 'numeric','editable': False},
                            {'name': 'total', 'id':'total', 'type': 'numeric',
                             'editable': False},
                    ],
                    style_cell = {
                                 'overflow': 'hidden',
                                 'textOverflow': 'ellipsis',
                                 'maxWidth': 40,
                                 'textAlign': 'left',
                                 'fontSize': 12,
                                 'font-family': 'sans-serif',
                             },

                    style_header={'backgroundColor': 'rgb(7,22,51)',
                                  'color': 'white',
                                  'font_size': '12px'},

                )
            ]

        )
    ],
    color="light",   # https://bootswatch.com/default/ for more card colors
    inverse=False,   # change color of text (black or white)
    outline=True,  # True = remove the block colors from the background and
    style={"width": "70rem"}
    # header
    #className="w-100 mb-3"
)
# ------------------------------------------------------------------------------
# Define Risk Datatable
# ------------------------------------------------------------------------------
data_table = dash_table.DataTable(
    id='table',
    # This line reads in all the columns in our dataframe raca_df
    # columns=[{"name": i, "id": i} for i in raca_df.columns],
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
    data=[],
    filter_action="native",
    sort_action="native",
    style_cell={
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
        'maxWidth': 0,
        'textAlign': 'left',
        'fontSize': 12,
        'font-family': 'sans-serif',
    },

    # Allow exports to CSV files
    export_format="csv",

    # ----------------------------------------------------------------
    # Overflow cells' content into multiple lines
    # ----------------------------------------------------------------
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
         'width': '7%'},
        {'if': {'column_id': 'gross_risk'},
         'width': '7%'},
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
            'border': '1px solid rgb(7, 22, 51)',
            'backgroundColor': 'rgb(212, 248, 255)'
        },
        {
            'if': {
                'column_editable': False  # True | False
            },
        },

        # Format Gross and Net Risk ***************************
        # Cells dependant on risk score ***********************
        # |------------|------------------|---------|------------|
        # | Priority   | RGB Colour Value | Hex     |  Range     |
        # |------------+------------------+---------+------------|
        # | Very High  | 255, 0, 0        | #FF0000 | > 18       |
        # | High       | 255, 165, 0      | #FFA500 | > 11 < 17  |
        # | Medium     | 255, 255, 0      | #FFFF00 | > 7 < 11   |
        # | Low        | 154, 205, 50     | #9ACD32 | > 3 < 7    |
        # | Very Low   | 127, 255, 0      | #7FFF00 | <= 3       |
        # | Blank      | 255, 255, 255    | #FFFFFF | " "        |
        # |------------|------------------|---------|------------|

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

    # ------------------------------------------------------------------
    # Freeze Rows - digit represents number of rows frozen 0 being header
    # row
    # ------------------------------------------------------------------
    fixed_rows={'headers': True, 'data': 0},

    style_header={
        # Style the table header row with Ink colour
        'backgroundColor': 'rgb(7, 22, 51)',
        'fontWeight': 'bold',
        'color': 'white'
    },

)

oprisk_fig_table = dash_table.DataTable(
    # ormr - OpRisk Monthly Reporting
    id = 'ormr',

# This line reads in all the columns in our dataframe raca_df
    # columns=[{"name": i, "id": i} for i in raca_df.columns],
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
    data=[],
    filter_action="native",
    sort_action="native",
    style_cell={
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
        'maxWidth': 0,
        'textAlign': 'left',
        'fontSize': 12,
        'font-family': 'sans-serif',
    },

    # Allow exports to CSV files
    export_format="csv",
)

all_raca_table = dash_table.DataTable(
    # All Raca
    id = 'allraca',

# This line reads in all the columns in our dataframe raca_df
    # columns=[{"name": i, "id": i} for i in raca_df.columns],
    columns=[
        {'name': 'Process (Title)', 'id': 'process_title', 'type': 'text',
         'editable': False},
        {'name': 'Process description', 'id': 'process_description',
         'type': 'text', 'editable': False},
        {'name': 'Risk ID', 'id': 'risk_id', 'type': 'text', 'editable': False},
        {'name': 'Risk Owner', 'id': 'risk_owner', 'type': 'text',
         'editable': False},
        {'name': 'Risk(Title)', 'id': 'risk_title', 'type': 'text',
         'editable': False},
        {'name': 'Risk Description', 'id': 'risk_description', 'type': 'text',
         'editable': False},
        {'name': 'Risk Category 1', 'id': 'risk_types', 'type': 'text',
         'editable': False},
        {'name': 'Risk Category 2', 'id': 'risk', 'type': 'text',
         'editable': False},
        {'name': 'Risk Category 3', 'id': 'level3', 'type': 'text',
         'editable': False},
        {'name': 'Associated KRIs', 'id': 'associated_kris', 'type': 'text',
         'editable': False},
        {'name': 'Gross Impact', 'id': 'gross_impact', 'type': 'numeric',
         'editable': False},
        {'name': 'Gross Likelihood', 'id': 'gross_likelihood',
         'type': 'numeric', 'editable': False},
        {'name': 'Control ID', 'id': 'control_id', 'type': 'text',
         'editable': False},
        {'name': 'Control Owner', 'id': 'control_owner', 'type': 'text',
         'editable': False},
        {'name': 'Control (Title)', 'id': 'control_title', 'type': 'text',
         'editable': False},
        {'name': 'Control Description', 'id': 'control_description',
         'type': 'text', 'editable': False},
        {'name': 'Control Activity', 'id': 'control_activity', 'type': 'text',
         'editable': False},
        {'name': 'Control Type', 'id': 'control_type', 'type': 'text',
         'editable': False},
        {'name': 'Control Frequency', 'id': 'control_frequency', 'type': 'text',
         'editable': False},
        {'name': 'DE & OE?', 'id': 'de_oe', 'type': 'text', 'editable': False},
        {'name': 'Commentary on DE & OE assessment', 'id': 'de_oe_commentary',
         'type': 'text', 'editable': False},
        {'name': 'Net Impact', 'id': 'net_impact', 'type': 'numeric',
         'editable': False},
        {'name': 'Net Likelihood', 'id': 'net_likelihood', 'type': 'numeric',
         'editable': False},
        {'name': 'Commentary on Net Risk Assessment', 'id':
            'net_risk_assesment_commentary', 'type': 'text', 'editable': False},
        {'name': 'Risk Decision', 'id': 'risk_decision', 'type': 'text',
         'editable': False},
        {'name': 'Issue Description (if applicable)', 'id': 'issue_description',
         'type': 'text', 'editable': False},
        {'name': 'Action Description', 'id': 'action_description',
         'type': 'text', 'editable': False},
         {'name': 'Action Owner', 'id': 'action_owner', 'type': 'text',
          'editable': False},
        {'name': 'Action Due Date', 'id': 'action_due_date', 'type': 'text',
         'editable': False},
        {'name': 'Completion Date', 'id': 'completion_dat', 'type': 'text',
         'editable': False},
        {'name': 'Action ID', 'id': 'action_id', 'type': 'text',
         'editable': False}
    ],
    data=[],
    filter_action="native",
    sort_action="native",
    style_cell={
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
        'maxWidth': 0,
        'textAlign': 'left',
        'fontSize': 12,
        'font-family': 'sans-serif',
    },
        # ------------------------------------------------------------------
        # Freeze Rows - digit represents number of rows frozen 0 being header
        # row
        # ------------------------------------------------------------------
    fixed_rows = {'headers': True, 'data': 0},
    style_header = {'backgroundColor': 'rgb(7, 22, 51)',
                    'fontWeight': 'bold',
                    'color': 'white'},

    # Allow exports to CSV files
    export_format="csv",

    # ----------------------------------------------------------------
    # Overflow cells' content into multiple lines
    # ----------------------------------------------------------------
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
         'width': '7%'},
        {'if': {'column_id': 'gross_risk'},
         'width': '7%'},
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
            'border': '1px solid rgb(7, 22, 51)',
            'backgroundColor': 'rgb(212, 248, 255)'
        },
        {
            'if': {
                'column_editable': False  # True | False
            },
        },
    ]
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

        ], ),
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
        ], className="mb-3"
        ),
        dbc.Card(data_table, body=False)

    ]
)

# Data table showing Monthly reporting section
tab3_content = dbc.Row([
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

                ],className="mb-3"
                ),
                dbc.Row([
                    dbc.Col(
                        [
                            dbc.Card(card_monthly_reporting, body=True),
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Card(card_monthly_reporting_2, body=True),
                        ]
                    )
                ]
            )
    ]
)


# Data table showing Monthly reporting section
tab4_content = dbc.Col(
    [
        html.Div([
            html.Br(),
            html.Span('All RACA Data', style={
                "font-size": 22,
                "color": color_2,
                'font-weight': 'bold'}),

            html.Br(),
            html.Span('This is all the data that is used in this application ',
                      style={
                          "font-size": 14,
                          "color": color_2}),
        ],className="mb-3"
        ),
        dbc.Card(all_raca_table, body=True)
    ],
)

tabs = dbc.Tabs(
    [
        dbc.Tab(tab1_content,
                tab_id="tab_map",
                label="Overview"
                ),  # style={"width": "100%"}),

        dbc.Tab(tab2_content,
                tab_id="tab_total",
                label="Risk Table"),
        # style={"width": "100%"}),

        dbc.Tab(tab3_content,
                tab_id="tab_oprisk_fig",
                label="Monthly Reporting"),
                #style={"width": "50%"}),

        dbc.Tab(tab4_content,
                tab_id="tab_alldata",
                label="All RACA Data"),
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
                dbc.Col(
                    [
                        tabs
                    ]
                ),
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
    elif id_tab == "tab_oprisk_fig":
        return False, True, "0%", 6, 5, 4, 3, 2
    elif id_tab == "tab_alldata":
        return False, True, "0%", 6, 5, 4, 3, 2

# # ------------------------------------------------------------------------------
# # Callback to hide L1 dropdown boxes if we are on teh risk table tab
# # ------------------------------------------------------------------------------
# @app.callback(
#     Output('overview-container', 'style'),
#     [Input("tabs", "active_tab")])
# def show_hide_element(id_tab):
#     if id_tab == 'tab_tab':
#         return {'display': 'block'}
#     else:
#         return {'display': 'none'}

# ------------------------------------------------------------------------------
# Callback to hide L2 and L3 dropdown boxes if risk_type == 'ALL'
# ------------------------------------------------------------------------------
# https://stackoverflow.com/questions/62788398/
# hide-show-dash-slider-component-by-updating-different-dropdown-component
@app.callback(
    Output('dropdown-container', 'style'),
    [Input('risk_types', 'value')])
def show_hide_element(visibility_state):
    if visibility_state == 'All':
        return {'display': 'none'}
    else:
        return {'display': 'block'}

# ------------------------------------------------------------------------------
# Only Show the Legend when we are on the Risk Table tab
# ------------------------------------------------------------------------------
# https://stackoverflow.com/questions/62788398/
# hide-show-dash-slider-component-by-updating-different-dropdown-component
@app.callback(
    Output('legend-container', 'style'),
    [Input("tabs", "active_tab")])
def show_hide_element(id_tab):
    if id_tab == 'tab_total':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# ------------------------------------------------------------------------------
# Only Show Select Business unit on Overview page
# ------------------------------------------------------------------------------
# https://stackoverflow.com/questions/62788398/
# hide-show-dash-slider-component-by-updating-different-dropdown-component
@app.callback(
    Output('business-unit-container', 'style'),
    [Input("tabs", "active_tab")])
def show_hide_element(id_tab):
    if id_tab == 'tab_map':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# ------------------------------------------------------------------------------
# Set Callback to define our dropdown boxes
# ------------------------------------------------------------------------------
@app.callback(
    Output('risk', 'options'),
    Input('risk_types', 'value'))
def set_tl2_options(tl1_options):
    if tl1_options != 'All':
        raca_options = raca_df[raca_df['risk_types'] == tl1_options]
        # print(f'DEBUG1: TL 1 Not equal to all: {raca_options}')
        print(f'DEBUG 1.1: L1 options "NOT ALL": {raca_options}')
    else:
        raca_options = raca_df
        # print(f'DEBUG2: TL1 equal to all: {raca_options}')
        print(f'DEBUG 1.2: L1 options "ALL": {raca_options}')
    return [{'label': i, 'value': i}
            for i in sorted(raca_options['risk'].astype(str).unique())]


@app.callback(
    Output('level3', 'options'),
    Input('risk', 'value'))
def set_tl3_options(tl2_options):
    if tl2_options != 'All':
        raca_options = raca_df[raca_df['risk'] == tl2_options]
        print(f'DEBUG 2.1: TL2 Not equal to all: {raca_options}')
    else:
        raca_options = raca_df
        print(f'DEBUG 2.2: TL2 equal to all: {raca_options}')
    return [{'label': i, 'value': i}
            for i in sorted(raca_options['level3'].astype(str).unique())]


# ------------------------------------------------------------------------------
# Define Callback to update data_table  on tab_1 id = table
# ------------------------------------------------------------------------------
@app.callback(
    Output('table', 'data'),
    Input('level3', 'value'))
def output_dataframe(data):
    print(f'DEBUG 3.1: Level 3 value {data}')
    
    
    table_df = raca_df
    table_df.drop_duplicates(subset=['risk_id'],inplace=True)
    return table_df.to_dict('records')


# ------------------------------------------------------------------------------
# Barchart 1 - Total Number of Risks by Business Function
# ------------------------------------------------------------------------------
@app.callback(Output('barchart1', 'figure'),
              [Input('level3', 'value'),
               Input('risk', 'value'),
               Input('risk_types', 'value')])
def update_figure(risk_types, risk, level3):
    # Create a copy of our dataframe so we are not working on the original
    df_copy = raca_df

    print(risk_types)

    if risk_types == 'All':

        # Display all risks grouped by business unit
        group1 = df_copy.groupby('business_unit')
        df2 = group1.apply(lambda x: x['risk_id'].sort_values().nunique())

        # Build our graph
        fig = df2.plot.bar(
            title='<b>Total Number of Risks by Business Function<b>')
        fig.update_layout(showlegend=False,
                          title_x=0.5,
                          height=800,
                          paper_bgcolor='rgba(0,0,0,0)',
                          plot_bgcolor='rgba(0,0,0,0)')

        # Set the bar colour
        fig.update_traces(marker_color='#00DEFF')

        # Set text angle on x axes
        fig.update_xaxes(tickangle=45,
                         categoryorder='total ascending',
                         title_text='<b>Business Function<b>')

        # Set Y axis text
        fig.update_yaxes(title_text='<b>Number of Risks<b>')

        return fig

    else: # risk_types != 'All'

        df_filtered = raca_df[['gross_risk', 'business_unit']]

        fig = px.line(df_filtered, x='business_unit', y='gross_risk')
        fig.update_xaxes(tickangle=45,
                         categoryorder='total ascending',
                         title_text='<b>Business Function<b>')

        # Set Y axis text
        fig.update_yaxes(title_text='<b>Number of Risks<b>')

        return fig

# ------------------------------------------------------------------------------
# Barchart 2 - Graph showing both Gross and Net risk by business function
# ------------------------------------------------------------------------------
@ app.callback(Output('piechart1', 'figure'),
               [Input('level3', 'value'),
                Input('risk', 'value'),
                Input('risk_types', 'value')])
def update_figure(risk_types, risk, selected_scale):
    group = raca_df.groupby('business_unit')
    # Get our Gross risk by business unit
    df3 = (group.apply(lambda x: x['gross_risk'].dropna().sum()) /
           group.apply(lambda x: x['risk_id'].sort_values().nunique()))

    # Display all risks grouped by business unit
    #group = df.groupby('business_unit')
    df4 = (group.apply(lambda x: x['net_risk'].dropna().sum()) /
           group.apply(lambda x: x['risk_id'].sort_values().nunique()))
    df4.astype(int)

    fig = go.Figure(data=[
        go.Bar(name='Gross Risk', x=df3.index, y=df3, marker_color='#00DEFF'),
        go.Bar(name='Net Risk', x=df4.index, y=df4, marker_color='#0082FF')
    ])
    # Change the bar mode
    fig.update_layout(barmode='group')

    # Build our graph
    fig.update_layout(title='<b>Comparison of Gross and Net Risk by Business'
                            ' Function</b>)',
                      showlegend=True,
                      title_x=0.5,
                      height=800,
                      paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)'
                      )

    fig.update_layout(xaxis_categoryorder='total ascending')
    fig.update_xaxes(tickangle=45,
                     title_text='<b>Business Function<b>'
                     )

    fig.update_yaxes(title_text='<b>Risk Score<b>'
                     )

    return fig

# ------------------------------------------------------------------------------
# Pie Chart 1 - Graph showing Total Number of Risks by Business Function
# ------------------------------------------------------------------------------
@ app.callback(Output('barchart2', 'figure'),
               [Input('level3', 'value'),
                Input('risk', 'value'),
                Input('risk_types', 'value')]
               )
def update_figure(risk_types, risk, selected_scale):
    # Display all risks grouped by business unit
    group = raca_df.groupby('business_unit')
    df2 = group.apply(lambda x: x['risk_id'].sort_values().nunique())
    #df2

    # Build our graph
    fig = px.pie(df2, values=df2,
                 names=df2.index,
                 title='<b>Total Number of Risks by Business Function<b>'
                 )

    fig.update_layout(showlegend=True,
                      title_x=0.5,
                      height=800
                      )
    fig.update_traces(hole=.4,
                      textinfo='value+label+percent',
                      hoverinfo="percent+name",
                      textposition='inside',
                      insidetextorientation='radial')

    return fig


# ------------------------------------------------------------------------------
# Pie Chart 2 - Graph showing Total Number of Risks by Business Function
# ------------------------------------------------------------------------------
@ app.callback(Output('piechart2', 'figure'),
               [Input('level3', 'value'),
                Input('risk', 'value'),
                Input('risk_types', 'value')]
               )
def update_figure(risk_types, risk, selected_scale):
    group = raca_df.groupby('business_unit')
    df3 = (group.apply(lambda x: x['gross_risk'].dropna().sum()) /\
    group.apply(lambda x: x['risk_id'].sort_values().nunique()))
    df4 = (group.apply(lambda x: x['net_risk'].dropna().sum()) /\
    group.apply(lambda x: x['risk_id'].sort_values().nunique()))

    fig = px.pie(df4, values=df3,
                 names=df4.index,
                 title='<b>Net Risk Score by Business Function<b>'
                 )

    fig.update_layout(showlegend=True,
                      title_x=0.5,
                      height = 800
                      )

    fig.update_traces(hole=.4,
                      textinfo='value+label',
                      hoverinfo="percent+name",
                      textposition='inside',
                      insidetextorientation='radial')

    return fig

# ------------------------------------------------------------------------------
# Tab 3 - Update Monthly reporting figures for Actions outstanding by
# business unit
# Calculate the number of actions logged against each business unit
# 1 Look at raca_df['action_id'] and if not a null value note the business
# function add to the count for the business function.
# Report data by unique business unit.
# ------------------------------------------------------------------------------
# @app.callback(
#     [Output('dt_card_mr', 'data')],
#     [Input('', component_property='n_clicks_timestamp')])
# def display_tweets(submit_button, screen_names):
#     temp_df = raca_df[['business_unit', 'action_id']]
#     temp_df = temp_df.dropna()
#     action_figs = temp_df.count()
#     data = action_figs.to_dict(orient='records')
#     print(data)
#     return data



# ------------------------------------------------------------------------------
# Run app and display the result
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    app.run_server(debug=True)