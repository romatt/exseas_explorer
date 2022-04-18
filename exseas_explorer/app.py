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
# import geopandas
# import matplotlib
import numpy as np
from dash import Dash, dash_table, dcc, html
from dash.dependencies import Input, Output
from dash_extensions.javascript import assign

from exseas_explorer.util import filter_patches, generate_cbar, load_patches

# OPTIONS
MIN_YEAR = 1950
MAX_YEAR = 2020
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
    'label': 'DJF',
    'value': 'djf'
}, {
    'label': 'MAM',
    'value': 'mam'
}, {
    'label': 'JJA',
    'value': 'jja'
}, {
    'label': 'SON',
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
    'label': 'all area',
    'value': 1
}, {
    'label': 'land area',
    'value': 2
}]

# LOAD DEFAULT PATCHES
default_patches = load_patches(
    os.path.join(DATA_DIR, "patches_40y_era5_T2M_djf_ProbCold.geojson"))
default_patches = filter_patches(default_patches)
classes = list(default_patches['key'])
colorscale = generate_cbar(classes)

# POLYGON STYLE DEFINITIONS
style = dict(fillOpacity=0.7, weight=1)

# Geojson rendering logic, must be JavaScript as it is executed in clientside.
style_handle = assign("""function(feature, context){
    const {classes, colorscale, style, colorProp} = context.props.hideout;  // get props from hideout
    const value = feature.properties[colorProp];  // get value the determines the color
    for (let i = 0; i < classes.length; ++i) {
        if (value > classes[i]) {
            style.fillColor = colorscale[i];  // set the fill color according to the class
            style.color = colorscale[i];  // set the border color according to the class
        }
    }
    return style;
}""")

hideout_dict = dict(colorscale=colorscale,
                    classes=classes,
                    style=style,
                    colorProp="key")

# Header row
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

# Navigation row
navbar = html.Div([
    dbc.Row(children=[
                dbc.Col([
                    "Parameter:",
                    dcc.Dropdown(PARAMETER_LIST,
                                 'T2M',
                                 id='parameter-selector',
                                 clearable=False,
                                 searchable=False)
                ],
                        xl=1,
                        xs=6,
                        className='nav_column'),
                dbc.Col([
                    "Option:",
                    dcc.Dropdown(PARAMETER_OPTIONS['T2M']['options'],
                                 'ProbCold',
                                 id='option-selector',
                                 clearable=False,
                                 searchable=False)
                ],
                        xl=1,
                        xs=6,
                        className='nav_column'),
                dbc.Col([
                    "Season:",
                    dcc.Dropdown(SEASON_LIST,
                                 'djf',
                                 id='season-selector',
                                 clearable=False,
                                 searchable=False)
                ],
                        xl=1,
                        xs=6,
                        className='nav_column'),
                dbc.Col([
                    "# of events:",
                    dcc.Input(value=10,
                              id='nval-selector',
                              type='number',
                              min=5,
                              max=20,
                              step=1)
                ],
                        xl=1,
                        xs=6,
                        className='nav_column'),
                dbc.Col([
                    "Ranking:",
                    dcc.Dropdown(RANKING_LIST,
                                 1,
                                 id='ranking-selector',
                                 clearable=False,
                                 searchable=False)
                ],
                        xl=1,
                        xs=6,
                        className='nav_column'),
            ]),
    dbc.Row(children=[
                dbc.Col([
                    "Longitude:",
                    dcc.RangeSlider(min=-180,
                                    max=180,
                                    step=0.5,
                                    marks={-180:"-180",0:"0",180:"180"},
                                    value=[-180, 180],
                                    tooltip={"placement": "top", "always_visible": True},
                                    id="longitude-selector")
                ],
                        width=3,
                        className='nav_column'),
                dbc.Col([
                    "Latitude:",
                    dcc.RangeSlider(min=-90,
                                    max=90,
                                    step=0.5,
                                    marks={-90:"-90",0:"0",90:"90"},
                                    value=[-90, 90],
                                    tooltip={"placement": "top", "always_visible": True},
                                    id="latitude-selector")
                ],
                        width=3,
                        className='nav_column')
    ]),
],
                  className="navbar-light bg-light")

# Map row
maprow = html.Div([
    dbc.Row(
        id='maprow',
        children=[
            dbc.Col([
                dl.Map(center=[0, 0],
                       zoom=2,
                       children=[
                           dl.TileLayer(),
                           dl.GeoJSON(data=default_patches.__geo_interface__,
                                      id="patches",
                                      options=dict(style=style_handle),
                                      hideout=hideout_dict),
                           dl.LayerGroup(id="cbar", children=[])
                       ],
                       style={
                           'padding-top': '2em',
                           'width': '100%',
                           'height': '70vh',
                           "display": "block"
                       },
                       id="map")
            ],
                    width=9,
                    className='map_column'),
            dbc.Col([
                "Details:"
            ],
                    width=3,
                    className='sidebar_column')
        ])
])

# Definition of app layout
app = Dash(__name__,
           update_title=None,
           title="INTEXseas Extreme Season Explorer",
           external_stylesheets=[dbc.themes.BOOTSTRAP, 'assets/style.css'])
app.layout = html.Div([header, navbar, maprow])


@app.callback(Output(component_id='patches', component_property='data'),
              Output(component_id='patches', component_property='hideout'),
              Output(component_id='option-selector',
                     component_property='options'),
              Output(component_id='option-selector',
                     component_property='value'),
              Output(component_id='cbar', component_property='children'),
              Input(component_id='parameter-selector',
                    component_property='value'),
              Input(component_id='option-selector',
                    component_property='value'),
              Input(component_id='season-selector',
                    component_property='value'),
              Input(component_id='nval-selector', component_property='value'),
              Input(component_id='ranking-selector',
                    component_property='value'),
              Input(component_id='longitude-selector',
                    component_property='value'),
              Input(component_id='latitude-selector',
                    component_property='value'))
def draw_patches(parameter_value, parameter_option, season_value, nval_value,
                 ranking_option, longitude_values, latitude_values):

    parameter_options = PARAMETER_OPTIONS[f'{parameter_value}']['options']

    # Check if parameter_option is contained in parameter_options
    if parameter_option in [d['value'] for d in parameter_options]:
        option_selected = parameter_option
    # Otherwise, use the first parameter option
    else:
        option_selected = parameter_options[0]["value"]

    # Load patches
    selected_file = f'patches_40y_era5_{parameter_value}_{season_value}_{option_selected}.geojson'
    patches = load_patches(os.path.join(DATA_DIR, selected_file))
    patches = filter_patches(patches, ranking_option, nval_value, longitude_values, latitude_values)

    classes = list(patches['key'])
    # Update colorbar
    colorscale = generate_cbar(classes)

    # Create colorbar
    colorbar = dlx.categorical_colorbar(categories=[str(y) for y in classes],
                                        colorscale=colorscale,
                                        width=20,
                                        height=500,
                                        position="bottomleft")

    hideout_dict = dict(colorscale=colorscale,
                        classes=classes,
                        style=style,
                        colorProp="key")

    return patches.__geo_interface__, hideout_dict, parameter_options, option_selected, colorbar


if __name__ == '__main__':
    app.run_server(debug=True)
