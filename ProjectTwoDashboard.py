from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import dash_leaflet as dl
import plotly.express as px
import pandas as pd
import base64

# Import CRUD module
from animal_shelter import AnimalShelter

###########################
# Data Manipulation / Model
###########################

username = "spencerbelknap_db"
password = "SpBossman2002!"

# Connect to database via CRUD Module
db = AnimalShelter(username, password)

# Load all data initially
df = pd.DataFrame.from_records(db.read({}))
if "_id" in df.columns:
    df.drop(columns=['_id'], inplace=True)

#########################
# Dashboard Layout / View
#########################

app = Dash(__name__)

# Load Grazioso Salvare logo
image_filename = 'assets/Grazioso_Salvare_Logo.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

app.layout = html.Div([

    html.Center([
        html.Img(
            src='data:image/png;base64,{}'.format(encoded_image.decode()),
            style={'height': '100px'}
        ),
        html.H3("Dashboard by Spencer Belknap")
    ]),

    html.Center(html.B(html.H1('CS-340 Dashboard'))),
    html.Hr(),

    # FILTER OPTIONS
    html.Div([
        dcc.Dropdown(
            id='filter-type',
            options=[
                {'label': 'Water Rescue', 'value': 'water'},
                {'label': 'Mountain/Wilderness Rescue', 'value': 'mountain'},
                {'label': 'Disaster/Individual Tracking', 'value': 'disaster'},
                {'label': 'Reset', 'value': 'reset'}
            ],
            placeholder="Select Rescue Type",
            value='reset'
        )
    ]),

    html.Hr(),

    # DATA TABLE
    dash_table.DataTable(
        id='datatable-id',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        page_size=10,
        sort_action='native',
        filter_action='native',
        row_selectable='single',
        style_table={'overflowX': 'auto'}
    ),

    html.Br(),
    html.Hr(),

    # CHART + MAP SIDE BY SIDE
    html.Div(style={'display': 'flex'}, children=[
        html.Div(id='graph-id', style={'width': '50%'}),
        html.Div(id='map-id', style={'width': '50%'})
    ])
])

#############################################
# Interaction Between Components / Controller
#############################################

# FILTERING CALLBACK (FIXED)
@app.callback(
    Output('datatable-id', 'data'),
    [Input('filter-type', 'value')]
)
def update_dashboard(filter_type):

    if filter_type == 'water':
        query = {
            "animal_type": "Dog",
            "breed": {"$in": ["Labrador Retriever Mix", "Chesapeake Bay Retriever", "Newfoundland"]},
            "sex_upon_outcome": "Intact Female"
        }

    elif filter_type == 'mountain':
        query = {
            "animal_type": "Dog",
            "breed": {"$in": ["German Shepherd", "Alaskan Malamute", "Old English Sheepdog",
                              "Siberian Husky", "Rottweiler"]},
            "sex_upon_outcome": "Intact Male"
        }

    elif filter_type == 'disaster':
        query = {
            "animal_type": "Dog",
            "breed": {"$in": ["Doberman Pinscher", "German Shepherd", "Golden Retriever",
                              "Bloodhound", "Rottweiler"]},
            "sex_upon_outcome": "Intact Male"
        }

    else:
        query = {}

    results = db.read(query)

    # Prevent crash if no results
    if not results:
        return []

    dff = pd.DataFrame.from_records(results)

    if "_id" in dff.columns:
        dff.drop(columns=['_id'], inplace=True)

    return dff.to_dict('records')


# PIE CHART CALLBACK (ENHANCED)
@app.callback(
    Output('graph-id', "children"),
    [Input('datatable-id', "derived_virtual_data")]
)
def update_graphs(viewData):
    if not viewData:
        dff = df
    else:
        dff = pd.DataFrame(viewData)

    if dff.empty or "breed" not in dff.columns:
        return [html.Div("No data available for chart")]

    fig = px.pie(dff, names='breed', title='Breed Distribution')
    return [dcc.Graph(figure=fig)]


# MAP CALLBACK (ENHANCED)
@app.callback(
    Output('map-id', "children"),
    [
        Input('datatable-id', "derived_virtual_data"),
        Input('datatable-id', "derived_virtual_selected_rows")
    ]
)
def update_map(viewData, selected_rows):

    if not viewData:
        return html.Div("No data available")

    dff = pd.DataFrame(viewData)

    row = selected_rows[0] if selected_rows else 0

    lat = dff.loc[row, "location_lat"]
    lon = dff.loc[row, "location_long"]

    return [
        dl.Map(
            style={'width': '100%', 'height': '500px'},
            center=[lat, lon],
            zoom=12,
            children=[
                dl.TileLayer(id="base-layer-id"),
                dl.Marker(
                    position=[lat, lon],
                    children=[
                        dl.Tooltip(dff.loc[row, "breed"]),
                        dl.Popup([
                            html.H1("Animal Name"),
                            html.P(dff.loc[row, "name"])
                        ])
                    ]
                )
            ]
        )
    ]


# Run app
if __name__ == '__main__':
    app.run(debug=True)
