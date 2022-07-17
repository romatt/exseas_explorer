# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

from curses.textpad import rectangle
import os

import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from dash_extensions.javascript import Namespace
from importlib_metadata import NullFinder

from util import (
    filter_patches,
    generate_cbar,
    generate_table,
    load_patches,
    generate_dl,
    generate_poly,
)

ns = Namespace("myNamespace", "mySubNamespace")

# OPTIONS
MIN_YEAR = 1950
MAX_YEAR = 2020
MIN_NUM_EVENTS = 1
MAX_NUM_EVENTS = 20
lon_range = [-180, 180]
lat_range = [-90, 90]
DATA_DIR = "/var/www/exseas_explorer/exseas_explorer/data/"
DEFAULT_SETTING = "patches_T2M_djf_ProbCold"
PARAMETER_LIST = [
    {"label": "2m Temperature", "value": "T2M"},
    {"label": "Total Precipitation", "value": "RTOT"},
    {"label": "10m Win", "value": "WG10"},
]
PARAMETER_OPTIONS = {
    "T2M": {
        "options": [
            {"label": "Hot", "value": "ProbHot"},
            {"label": "Cold", "value": "ProbCold"},
        ]
    },
    "RTOT": {
        "options": [
            {"label": "Wet", "value": "ProbWet"},
            {"label": "Dry", "value": "ProbDry"},
        ]
    },
    "WG10": {
        "options": [
            {"label": "Windy", "value": "ProbWindy"},
            {"label": "Calm", "value": "ProbCalm"},
        ]
    },
}
SEASON_LIST = [
    {"label": "DJF", "value": "djf"},
    {"label": "MAM", "value": "mam"},
    {"label": "JJA", "value": "jja"},
    {"label": "SON", "value": "son"},
]
LOCATION_LIST = [
    {"label": "All Objects", "value": "all_patches_"},
    {"label": "Land Objects Only", "value": "land_patches_"},
]
RANKING_LIST = [
    {"label": "Area", "value": 1},
    {"label": "Area over Land", "value": 2},
    {"label": "Mean Anomaly", "value": 3},
    {"label": "Mean Anomaly over Land", "value": 4},
    {"label": "Integrated Anomaly", "value": 5},
    {"label": "Integrated Anomaly over Land", "value": 6},
]
REGION_LIST = [
    {"label": "World", "value": "world"},
    {"label": "Northern Hemisphere", "value": "nh"},
    {"label": "Southern Hemisphere", "value": "sh"},
    {"label": "Europe", "value": "europe"},
    {"label": "North America", "value": "na"},
    {"label": "Asia", "value": "asia"},
]

# LOAD DEFAULT PATCHES
default_patches = load_patches(os.path.join(DATA_DIR, f"{DEFAULT_SETTING}.geojson"))
default_patches = filter_patches(default_patches)
classes = list(default_patches["Label"])
colorscale = generate_cbar(list(default_patches["Year"]))
poly_table = generate_table(default_patches, colorscale, classes)
poly_download = generate_dl(default_patches, DEFAULT_SETTING)

# POLYGON STYLE DEFINITIONS
style = dict(fillOpacity=0.5, weight=2)
hideout_dict = dict(
    colorscale=colorscale, classes=classes, style=style, colorProp="Label"
)

# Header row
header = html.Div(
    [
        dbc.Row(
            className="title",
            children=[
                dbc.Col(
                    [
                        dbc.NavbarBrand(
                            "INTEXseas Extreme Season Explorer",
                            className="ml-1",
                            style={
                                "font-size": "x-large",
                                "padding": "10px",
                                "line-height": "60px",
                                "color": "white",
                            },
                        )
                    ]
                ),
                dbc.Col(
                    [
                        html.Img(
                            src="/assets/eth_logo.png",
                            height="60px",
                            style={"padding": "10px", "float": "right"},
                        ),
                        html.Img(
                            src="/assets/iac_logo.png",
                            height="60px",
                            style={"padding": "10px", "float": "right"},
                        ),
                    ]
                ),
            ],
        )
    ],
    className="navbar-expand-lg navbar-light bg-primary",
)

# Navigation row
navbar = html.Div(
    [
        dbc.Row(
            children=[
                dbc.Col(
                    [
                        "Parameter:",
                        dcc.Dropdown(
                            PARAMETER_LIST,
                            "T2M",
                            id="parameter-selector",
                            clearable=False,
                            searchable=False,
                        ),
                    ],
                    className="nav_column_top",
                ),
                dbc.Col(
                    [
                        "Type of extreme:",
                        dcc.Dropdown(
                            PARAMETER_OPTIONS["T2M"]["options"],
                            "ProbCold",
                            id="option-selector",
                            clearable=False,
                            searchable=False,
                        ),
                    ],
                    className="nav_column_top",
                ),
                dbc.Col(
                    [
                        "Season:",
                        dcc.Dropdown(
                            SEASON_LIST,
                            "djf",
                            id="season-selector",
                            clearable=False,
                            searchable=False,
                        ),
                    ],
                    className="nav_column_top",
                ),
                dbc.Col(
                    [
                        "Sort by:",
                        dcc.Dropdown(
                            RANKING_LIST,
                            1,
                            id="ranking-selector",
                            clearable=False,
                            searchable=False,
                        ),
                    ],
                    className="nav_column_top",
                ),
                dbc.Col(
                    [
                        "Region:",
                        dcc.Dropdown(
                            REGION_LIST,
                            "world",
                            id="region-selector",
                            clearable=False,
                            searchable=False,
                        ),
                    ],
                    className="nav_column_top",
                ),
                dbc.Col(
                    [
                        "Number of events:",
                        html.Br(),
                        dcc.Input(
                            value=10,
                            id="nval-selector",
                            type="number",
                            min=MIN_NUM_EVENTS,
                            max=MAX_NUM_EVENTS,
                            step=1,
                        ),
                    ],
                    className="nav_column_top",
                ),
            ]
        ),
        dbc.Row(
            children=[
                dbc.Col(
                    [
                        "Longitude:",
                        dcc.RangeSlider(
                            min=-180,
                            max=180,
                            step=0.5,
                            marks={
                                -180: "-180",
                                -90: "-90",
                                0: "0",
                                90: "90",
                                180: "180",
                            },
                            value=lon_range,
                            tooltip={"placement": "top", "always_visible": True},
                            id="longitude-selector",
                        ),
                    ],
                    className="nav_column_bottom",
                ),
                dbc.Col(
                    [
                        "Latitude:",
                        dcc.RangeSlider(
                            min=-90,
                            max=90,
                            step=0.5,
                            marks={-90: "-90", -45: "-45", 0: "0", 45: "45", 90: "90"},
                            value=lat_range,
                            tooltip={"placement": "top", "always_visible": True},
                            id="latitude-selector",
                        ),
                    ],
                    className="nav_column_bottom",
                ),
                dbc.Col(
                    [
                        "Time period:",
                        dcc.RangeSlider(
                            min=1950,
                            max=2020,
                            step=1,
                            marks={
                                1950: "1950",
                                1960: "1960",
                                1970: "1970",
                                1980: "1980",
                                1990: "1990",
                                2000: "2000",
                                2010: "2010",
                                2020: "2020",
                            },
                            value=[1950, 2020],
                            tooltip={"placement": "top", "always_visible": True},
                            id="year-selector",
                        ),
                    ],
                    className="nav_column_bottom",
                ),
            ]
        ),
    ],
    className="navbar-light bg-light",
)

# Map row
maprow = html.Div(
    [
        dbc.Row(
            id="maprow",
            children=[
                dbc.Col(
                    [
                        dl.Map(
                            center=[0, 0],
                            zoom=2,
                            worldCopyJump=True,
                            minZoom=2,
                            zoomSnap=0.25,
                            children=[
                                dl.TileLayer(),
                                dl.GeoJSON(
                                    data=generate_poly(lon_range, lat_range),
                                    id="aio",
                                    options=dict(
                                        fill=False,
                                        dashArray="7",
                                        color="gray",
                                        weight=2,
                                    ),
                                ),
                                dl.GeoJSON(
                                    data=default_patches.__geo_interface__,
                                    id="patches",
                                    options=dict(
                                        style=ns("color_polys"),
                                        onEachFeature=ns("bindPopup"),
                                    ),
                                    hideout=hideout_dict,
                                ),
                                dl.LayerGroup(id="cbar", children=[]),
                            ],
                            id="map",
                        )
                    ],
                    id="map_column",
                    style={
                        "width": "calc(100vw - 250px)",
                        "height": "calc(100vh - 240px)",
                        "display": "block",
                        "flex": "none",
                    },
                ),
                dbc.Button(
                    children=["❯"],
                    color="primary",
                    id="toggle-sidebar",
                    n_clicks=0,
                    style={"right": "260px"},
                ),
                dbc.Col(
                    [
                        html.Div(
                            title="Polygon details",
                            children=[
                                html.Div(
                                    children=[poly_table],
                                    id="polygon-table",
                                    style={"height": "calc(100vh - 350px)"},
                                ),
                                html.Div(
                                    [
                                        html.A(
                                            "Download NetCDF (all)",
                                            className="btn btn-danger btn-download",
                                            id="btn-netcdf",
                                        ),
                                        dcc.Download(id="netcdf-download"),
                                    ],
                                    className="download_button",
                                ),
                                html.Div(
                                    [
                                        html.A(
                                            "Download GeoJSON (sel)",
                                            className="btn btn-danger btn-download",
                                            id="btn-geojson",
                                        ),
                                        dcc.Download(id="geojson-download"),
                                    ],
                                    className="download_button",
                                ),
                            ],
                            id="right-collapse",
                        )
                    ],
                    id="sidebar_column",
                    style={
                        "width": "250px",
                        "display": "block",
                        "flex": "none",
                        "position": "absolute",
                        "right": "0px",
                    },
                ),
            ],
        )
    ]
)

hidden = html.Div([html.Div(id="file_name", children=[], style=dict(display="none"))])

# Definition of app layout
app = Dash(
    __name__,
    update_title=None,
    title="INTEXseas Extreme Season Explorer",
    external_stylesheets=[dbc.themes.BOOTSTRAP, "assets/style.css"],
    external_scripts=["assets/color.js"],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.layout = html.Div([header, navbar, maprow, hidden])


@app.callback(
    Output("longitude-selector", "value"),
    Output("latitude-selector", "value"),
    Input("region-selector", "value"),
)
def subset_region(region_value):

    if region_value == "world":
        longitude_range = [-180, 180]
        latitude_range = [-90, 90]
    elif region_value == "nh":
        longitude_range = [-180, 180]
        latitude_range = [0, 90]
    elif region_value == "sh":
        longitude_range = [-180, 180]
        latitude_range = [-90, 0]
    elif region_value == "europe":
        longitude_range = [-20, 30]
        latitude_range = [30, 80]
    elif region_value == "asia":
        longitude_range = [40, 180]
        latitude_range = [10, 80]
    elif region_value == "na":
        longitude_range = [-170, -50]
        latitude_range = [20, 80]
    else:
        longitude_range = [-180, 180]
        latitude_range = [-90, 90]

    return longitude_range, latitude_range


@app.callback(
    Output("patches", "data"),
    Output("patches", "hideout"),
    Output("option-selector", "options"),
    Output("option-selector", "value"),
    Output("cbar", "children"),
    Output("polygon-table", "children"),
    Output("aio", "data"),
    Output("file_name", "children"),
    Input("parameter-selector", "value"),
    Input("option-selector", "value"),
    Input("season-selector", "value"),
    Input("nval-selector", "value"),
    Input("ranking-selector", "value"),
    Input("longitude-selector", "value"),
    Input("latitude-selector", "value"),
    Input("year-selector", "value"),
)
def draw_patches(
    parameter_value,
    parameter_option,
    season_value,
    nval_value,
    ranking_option,
    longitude_values,
    latitude_values,
    year_values,
):

    parameter_options = PARAMETER_OPTIONS[f"{parameter_value}"]["options"]

    # Check if parameter_option is contained in parameter_options
    if parameter_option in [d["value"] for d in parameter_options]:
        option_selected = parameter_option
    # Otherwise, use the first parameter option
    else:
        option_selected = parameter_options[0]["value"]

    # Load patches
    selected_patch = f"patches_{parameter_value}_{season_value}_{option_selected}"
    patches = load_patches(os.path.join(DATA_DIR, f"{selected_patch}.geojson"))
    patches = filter_patches(
        patches,
        ranking_option,
        nval_value,
        longitude_values,
        latitude_values,
        year_values,
    )

    classes = list(patches["Label"])
    labels = list(patches["Year"])

    # Update area of interest
    aio = generate_poly(longitude_values, latitude_values)

    # Update and create colorbar
    colorscale = generate_cbar(labels)
    cbar_height = nval_value * 32
    colorbar = dlx.categorical_colorbar(
        categories=[str(y) for y in labels],
        colorscale=colorscale,
        width=20,
        height=cbar_height,
        position="bottomleft",
    )

    hideout_dict = dict(
        colorscale=colorscale,
        classes=classes,
        style=style,
        colorProp="Label",
        parameter=parameter_value,
    )

    # Generate table
    poly_table = generate_table(
        patches, colorscale, classes, ranking_option, parameter_value, parameter_option
    )

    return (
        patches.__geo_interface__,
        hideout_dict,
        parameter_options,
        option_selected,
        [colorbar],
        poly_table,
        aio,
        selected_patch,
    )


# @app.callback(
#     Output("netcdf-download", "data"),
#     Input("btn-netcdf", "n_clicks"),
#     Input("file_name", "children"),
#     prevent_initial_call=True,
# )
# def dl_netcdf(n_clicks, file_name):

#     print(f"Sending ./data/{file_name}.nc")
#     return dcc.send_file(f"./data/{file_name}.nc")


# @app.callback(
#     Output("geojson-download", "data"),
#     Input("btn-geojson", "n_clicks"),
#     Input("patches", "data"),
#     prevent_initial_call=True,
# )
# def dl_geojson(n_clicks, patches):
#     return None
#     # return dcc.send_string(patches, "patches.geojson")


@app.callback(
    Output("map_column", "style"),
    Output("sidebar_column", "style"),
    Output("toggle-sidebar", "style"),
    Output("toggle-sidebar", "children"),
    Input("toggle-sidebar", "n_clicks"),
    Input("map_column", "style"),
    Input("sidebar_column", "style"),
    Input("toggle-sidebar", "style"),
    Input("toggle-sidebar", "children"),
)
def toggle_sidebar(n_clicks, map_style, sidebar_style, toggle_style, button):
    if n_clicks:
        if sidebar_style["display"] == "none":
            sidebar_style["display"] = "block"
            toggle_style["right"] = "260px"
            map_style["width"] = "calc(100vw - 250px)"
            button = ["❯"]
        else:
            sidebar_style["display"] = "none"
            toggle_style["right"] = "10px"
            map_style["width"] = "100%"
            button = ["❮"]
        return map_style, sidebar_style, toggle_style, button

    return map_style, sidebar_style, toggle_style, button


server = app.server

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
