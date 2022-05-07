# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import os
from datetime import date

import dash
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from dash_extensions.javascript import assign

from exseas_explorer.util import (filter_patches, generate_cbar,
                                  generate_table, load_patches)

# OPTIONS
MIN_YEAR = 1950
MAX_YEAR = 2020
MIN_NUM_EVENTS = 1
MAX_NUM_EVENTS = 20
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
    'label': 'Area',
    'value': 1
}, {
    'label': 'Area over Land',
    'value': 2
}, {
    'label': 'Mean Anomaly',
    'value': 3
}, {
    'label': 'Mean Anomaly over Land',
    'value': 4
}, {
    'label': 'Integrated Anomaly',
    'value': 5
}, {
    'label': 'Integrated Anomaly over Land',
    'value': 6
}]

# LOAD DEFAULT PATCHES
default_patches = load_patches(
    os.path.join(DATA_DIR, "patches_40y_era5_T2M_djf_ProbCold.geojson"))
default_patches = filter_patches(default_patches)
classes = list(default_patches['Label'])
colorscale = generate_cbar(list(default_patches['Year']))
poly_table = generate_table(default_patches, colorscale)

# POLYGON STYLE DEFINITIONS
style = dict(fillOpacity=0.5, weight=2)

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
                    colorProp="Label")

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
                        width=3),
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
                              min=MIN_NUM_EVENTS,
                              max=MAX_NUM_EVENTS,
                              step=1)
                ],
                        xl=1,
                        xs=6,
                        className='nav_column'),
                dbc.Col([
                    "Filter by:",
                    dcc.Dropdown(RANKING_LIST,
                                 1,
                                 id='ranking-selector',
                                 clearable=False,
                                 searchable=False)
                ],
                        xl=2,
                        xs=6,
                        className='nav_column')
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
                        xl=3,
                        xs=7,
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
                        xl=3,
                        xs=7,
                        className='nav_column'),
                dbc.Col([
                    "Interval:",
                    dcc.RangeSlider(min=1950,
                                    max=2020,
                                    step=1,
                                    marks={1950:"1950",1960:"1960",1970:"1970",1980:"1980",1990:"1990",2000:"2000",2010:"2010",2020:"2020"},
                                    value=[1950, 2020],
                                    tooltip={"placement": "top", "always_visible": True},
                                    id="year-selector")
                        ],
                        xl=3,
                        xs=7,
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
                       worldCopyJump=True,
                       minZoom=2,
                       zoomSnap=0.25,
                       children=[
                           dl.TileLayer(),
                           dl.GeoJSON(data=default_patches.__geo_interface__,
                                      id="patches",
                                      options=dict(style=style_handle),
                                      hideout=hideout_dict),
                           dl.LayerGroup(id="cbar", children=[])
                       ],
                       id="map")
                    ],
                    id='map_column',
                    style={
                           'width': '80%',
                           'height': 'calc(100vh - 303px)',
                           'display': 'block',
                           'flex': 'none',
                       }
                    ),
            dbc.Button(children=["❯"],
                       color="primary",
                       id="toggle-sidebar",
                       n_clicks=0,
                       style={
                           'left': '75%'
                       }),
            dbc.Col([
                html.Div(
                        title="Polygon details",
                        children=[poly_table],
                        id="right-collapse",
                )
            ],
                    id='sidebar_column',
                    style={
                            'width': '20%',
                            'display': 'block',
                            'flex': 'none',
                        })
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
              Output("right-collapse", "children"),
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
                    component_property='value'),
              Input(component_id='year-selector',
                    component_property='value'))
def draw_patches(parameter_value, parameter_option, season_value, nval_value,
                 ranking_option, longitude_values, latitude_values, year_values):

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
    patches = filter_patches(patches, ranking_option, nval_value, longitude_values, latitude_values, year_values)

    classes = list(patches['Label'])
    labels = list(patches['Year'])
    # Update colorbar
    colorscale = generate_cbar(labels)

    # Create colorbar
    colorbar = dlx.categorical_colorbar(categories=[str(y) for y in labels],
                                        colorscale=colorscale,
                                        width=20,
                                        height=500,
                                        position="bottomleft")

    hideout_dict = dict(colorscale=colorscale,
                        classes=classes,
                        style=style,
                        colorProp="Label")

    # Generate table
    poly_table = generate_table(patches, colorscale)

    return patches.__geo_interface__, hideout_dict, parameter_options, option_selected, colorbar, [poly_table]

@app.callback(
    Output("map_column", "style"),
    Output("sidebar_column", "style"),
    Output("toggle-sidebar", "style"),
    Output("toggle-sidebar", "children"),
    Input("toggle-sidebar", "n_clicks"),
    Input("map_column", "style"),
    Input("sidebar_column", "style"),
    Input("toggle-sidebar", "style"),
    Input("toggle-sidebar", "children")
)
def toggle_sidebar(n_clicks, map_style, sidebar_style, toggle_style, button):
    if n_clicks:
        if sidebar_style['display'] == "none":
            sidebar_style['display'] = "block"
            toggle_style['left'] = "75%"
            map_style['width'] = "80%"
            button = ["❯"]
        else:
            sidebar_style['display'] = "none"
            toggle_style['left'] = "95%"
            map_style['width'] = "100%"
            button = ["❮"]
        return map_style, sidebar_style, toggle_style, button

    return map_style, sidebar_style, toggle_style, button

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
