# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import base64
import os

# import plotly.express as px
# import pandas as pd
import dash
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_leaflet.express as dlx
import geopandas
import matplotlib
import numpy as np
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

# OPTIONS
DATA_DIR = '/ytpool/data/ETH/INTEXseas'
PARAMETER_LIST = [
    {
        'label': '2m Temperature',
        'value': 'T2M'
    },
    {
        'label': 'Total Precipitation',
        'value': 'RTOT'
    },
    {
        'label': '10m Win',
        'value': 'WG10'
    },
]
PARAMETER_OPTIONS = {
    'T2M': {
        'options': [{
            'label': 'Hot',
            'value': 'ProbHot'
        }, {
            'label': 'Cold',
            'value': 'ProbCold'
        }]
    },
    'RTOT': {
        'options': [{
            'label': 'Wet',
            'value': 'ProbWet'
        }, {
            'label': 'Dry',
            'value': 'ProbDry'
        }]
    },
    'WG10': {
        'options': [{
            'label': 'Windy',
            'value': 'ProbWindy'
        }, {
            'label': 'Calm',
            'value': 'ProbCalm'
        }]
    }
}
SEASON_LIST = [{
    'label': 'Winter',
    'value': 'djf'
}, {
    'label': 'Spring',
    'value': 'mam'
}, {
    'label': 'Summer',
    'value': 'jja'
}, {
    'label': 'Autumn',
    'value': 'son'
}]
LOCATION_LIST = [{
    'label': 'All Objects',
    'value': 'all_patches_'
}, {
    'label': 'Land Objects Only',
    'value': 'land_patches_'
}]
RANKING_LIST = [{
    'label': 'area',
    'value': 1
}, {
    'label': 'return period mean',
    'value': 2
}]


# FUNCTION DEFINITONS
def load_patches(path: str) -> geopandas.GeoDataFrame:
    """
    Load selected patches and return geopandas object with patches
    """

    # Load data
    in_file = open(path)
    df = geopandas.read_file(in_file)

    return df


def filter_patches(df: geopandas.GeoDataFrame,
                   criterion: int) -> geopandas.GeoDataFrame:
    """
    Filter patches by selected criterion
    """

    if criterion == 1:
        df = df[df['area'] >= np.sort(df['area'])[-10]]
    if criterion == 2:
        df = df[df['mean_prob'] >= np.sort(df['mean_prob'])[-10]]

    return df


# By default load something?
default_patches = load_patches(
    os.path.join(DATA_DIR, "all_patches_40y_era5_WG10_djf_ProbWindy.geojson"))
default_patches = filter_patches(default_patches, 1)

def generate_cbar(labels: list) -> dl.Colorbar:
    """
    Generate colorbar for provided labels
    """

    # Define colors
    # classes = np.arange(np.nanmin(labels), np.nanmax(labels), 1)
    cmap = matplotlib.cm.get_cmap('Spectral', len(labels))
    colors = [cmap(x / np.max(labels))
              for x in labels]  # Assign colors to labels
    colors = [matplotlib.colors.to_hex(x)
              for x in colors]  # Convert colors to hex

    # Create colorbar.
    ctg = [
        "{}".format(cls, labels[i + 1]) for i, cls in enumerate(labels[:-1])
    ] + ["{}".format(labels[-1])]
    return dlx.categorical_colorbar(categories=ctg,
                                    colorscale=colors,
                                    width=400,
                                    height=30,
                                    position="bottomleft")

style = dict(weight=2,
             opacity=1,
             color='white',
             dashArray='3',
             fillOpacity=0.7)

# Header
header = html.Div([
    dbc.Row(className='title',
            children=[
                dbc.Col([
                    dbc.NavbarBrand("INTEXseas Extreme Season Explorer",
                                    className="ml-1",
                                    style={
                                        'font-size': 'x-large',
                                        'padding': '10px'
                                    })
                ],
                        width=8),
                dbc.Col([
                    html.Img(src='/assets/eth_logo.png',
                             height="100px",
                             style={
                                 'padding': '25px',
                                 'float': 'right'
                             })
                ],
                        width=4),
            ])
],
                  className="navbar-expand-lg navbar-light bg-light")

# Navigation pane
navbar = html.Div([
    dbc.Row(id='navbar',
            children=[
                dbc.Col([
                    "Parameter:",
                    dcc.Dropdown(PARAMETER_LIST,
                                 'T2M',
                                 id='parameter-selector',
                                 clearable=False,
                                 searchable=False)
                ],
                        width=2,
                        className='nav_column'),
                dbc.Col([
                    "Options:",
                    dcc.Dropdown(PARAMETER_OPTIONS['T2M']['options'],
                                 'ProbHot',
                                 id='option-selector',
                                 clearable=False,
                                 searchable=False)
                ],
                        width=2,
                        className='nav_column'),
                dbc.Col([
                    "Season:",
                    dcc.Dropdown(SEASON_LIST,
                                 'djf',
                                 id='season-selector',
                                 clearable=False,
                                 searchable=False)
                ],
                        width=2,
                        className='nav_column'),
                dbc.Col([
                    "Location:",
                    dcc.Dropdown(LOCATION_LIST,
                                 'all_patches_',
                                 id='location-selector',
                                 clearable=False,
                                 searchable=False)
                ],
                        width=2,
                        className='nav_column'),
                dbc.Col([
                    "Ranking criterion:",
                    dcc.Dropdown(RANKING_LIST,
                                 1,
                                 id='ranking-selector',
                                 clearable=False,
                                 searchable=False)
                ],
                        width=2,
                        className='nav_column'),
            ]),
],
                  className="navbar-light bg-light")

# Definition of app layout
app = Dash(__name__,
           update_title=None,
           title="INTEXseas Extreme Season Explorer",
           external_stylesheets=[dbc.themes.BOOTSTRAP, 'assets/style.css'])
app.layout = html.Div([
    header, navbar,
    dl.Map(center=[0, 0],
           zoom=2,
           children=[
               dl.TileLayer(),
               dl.GeoJSON(data=default_patches.__geo_interface__,
                          id="patches"),
               dl.LayerGroup(id="cbar", children=[])
           ],
           style={
               'padding-top': '2em',
               'width': '90%',
               'height': '70vh',
               'margin': "auto",
               "display": "block"
           },
           id="map")
])


@app.callback(Output(component_id='patches', component_property='data'),
              Output(component_id='option-selector',
                     component_property='options'),
              Output(component_id='option-selector',
                     component_property='value'),
              Output(component_id='cbar',
                     component_property='children'),
              Input(component_id='parameter-selector',
                    component_property='value'),
              Input(component_id='option-selector',
                    component_property='value'),
              Input(component_id='season-selector',
                    component_property='value'),
              Input(component_id='location-selector',
                    component_property='value'),
              Input(component_id='ranking-selector',
                    component_property='value'))
def draw_patches(parameter_value, parameter_option, season_value,
                 location_value, ranking_option):

    print(ranking_option)

    parameter_options = PARAMETER_OPTIONS[f'{parameter_value}']['options']

    # Check if parameter_option is contained in parameter_options
    if parameter_option in [d['value'] for d in parameter_options]:
        option_selected = parameter_option
    # Otherwise, use the first parameter option
    else:
        option_selected = parameter_options[0]["value"]

    # Load patches
    selected_file = f'{location_value}40y_era5_{parameter_value}_{season_value}_{option_selected}.geojson'
    patches = load_patches(os.path.join(DATA_DIR, selected_file))
    patches = filter_patches(patches, ranking_option)

    print(patches['lab'])

    # Update colorbar
    colorbar = generate_cbar(list(patches['lab']))

    return patches.__geo_interface__, parameter_options, option_selected, colorbar


if __name__ == '__main__':
    app.run_server(debug=True)
