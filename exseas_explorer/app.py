# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import hashlib
import importlib.resources as pkg_resources
import pathlib

import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_leaflet.express as dlx
import flask
import geopandas
from dash import Dash, Input, Output, State, dcc, html, no_update
from dash_extensions.javascript import Namespace

from exseas_explorer.util import (
    filter_patches,
    generate_cbar,
    generate_poly,
    generate_table,
    load_patches,
)

# allow arbitrary locations if exseas_explorer is installed and
# default to /var/www otherwise
DATA_DIR = pathlib.Path("/data/exseas_explorer_data/")

if not DATA_DIR.is_dir():
    try:
        DATA_DIR = pkg_resources.files("exseas_explorer") / "data"  # type: ignore[assignment]
    except ModuleNotFoundError as e:
        raise ValueError("Install exseas_explorer or fix data path") from e

ns = Namespace("myNamespace", "mySubNamespace")

# OPTIONS
MIN_YEAR = 1950
MAX_YEAR = 2020
MIN_NUM_EVENTS = 1
MAX_NUM_EVENTS = 20
lon_range: list[float] = [-180, 180]
lat_range: list[float] = [-90, 90]
DEFAULT_SETTING = "patches_T2M_djf_ProbCold"
PARAMETER_LIST = [
    {"label": "2m Temperature", "value": "T2M"},
    {"label": "Total Precipitation", "value": "RTOT"},
    {"label": "10m Wind", "value": "WG10"},
]
PARAMETER_OPTIONS = {
    "T2M": [
        {"label": "Hot", "value": "ProbHot"},
        {"label": "Cold", "value": "ProbCold"},
    ],
    "RTOT": [
        {"label": "Wet", "value": "ProbWet"},
        {"label": "Dry", "value": "ProbDry"},
    ],
    "WG10": [
        {"label": "Stormy", "value": "ProbWindy"},
        {"label": "Calm", "value": "ProbCalm"},
    ],
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
MODAL_TITLE = [html.P("Additional Information")]
MODAL_CONTENT = [
    html.P(
        [
            "This Web-Application allows visualizing and accessing the ERA5 extreme season catalogue of Böttcher et al., (2023). A very brief explanation of the available types of extreme seasons as well as filters for extreme season object selection is provided below. For a more in-depth documentation of the extreme season catalogue please refer to ",
            html.A(
                "Böttcher et al. (2023)",
                target="_blank",
                href="https://journals.ametsoc.org/view/journals/bams/104/3/BAMS-D-21-0348.1.xml",
            ),
            " as well as to their ",
            html.A(
                "Supplemental Material",
                target="_blank",
                href="https://journals.ametsoc.org/supplemental/journals/bams/104/3/BAMS-D-21-0348.1.xml/10.1175_BAMS-D-21-0348.2.pdf",
            ),
            ".",
        ]
    ),
    html.H5("Available filters"),
    html.P(
        "'Parameters' and 'Type of Extreme' sets one of the six available types of extreme seasons"
    ),
    html.Li(
        "'2m Temperature' is the de-trended 2-metre temperature for which there are 'Cold' and 'Hot' extreme events"
    ),
    html.Li(
        "'Total Precipitation' is the total precipitation for which there are 'Wet' and 'Dry' extreme events"
    ),
    html.Li(
        "'10m Wind' is the 10-metre wind speed for which there are 'Stormy' or 'Calm' extreme events"
    ),
    html.Br(),
    html.P("'Season'"),
    html.Li("'DJF' represents the months December-January-February"),
    html.Li("'MAM' represents the months March-April-May"),
    html.Li("'JJA' represents the months June-July-August"),
    html.Li("'SON' represents the months September-October-November"),
    html.Br(),
    html.P("'Sort by' allows to sort extreme events by different criteria"),
    html.Li("'Area' filters for the spatially largest events"),
    html.Li(
        "'Area over Land' also filters for the spatially largest events, but considers only the land-area"
    ),
    html.Li("'Mean Anomaly' filters for the mean anomaly of the event"),
    html.Li(
        "'Mean Anomaly over Land' also filter for the mean anomaly of the event, but considers only the part of the event that is over land"
    ),
    html.Li(
        "'Integrated Anomaly' filters for the area integrated anomaly of the respective variable"
    ),
    html.Li(
        "'Integrated Anomaly over Land' filters for the area integrated anomaly of the respective variable but only considers the part of each object that covers a land area"
    ),
]

# LOAD DEFAULT PATCHES
default_patches = load_patches(str(DATA_DIR / f"{DEFAULT_SETTING}.geojson"))
default_patches, event_title = filter_patches(default_patches)
classes = list(default_patches["label"])
colorscale = generate_cbar(list(default_patches["year"]))
poly_table = generate_table(default_patches, colorscale, classes)

# POLYGON STYLE DEFINITIONS
style = dict(fillOpacity=0.5, weight=2)
hideout_dict = dict(
    colorscale=colorscale, classes=classes, style=style, colorProp="label"
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
                                "fontSize": "x-large",
                                "padding": "10px",
                                "lineHeight": "60px",
                                "color": "white",
                            },
                        )
                    ],
                    className="title_column",
                ),
                dbc.Col(
                    [
                        html.Img(
                            id="eth_logo",
                            src="/assets/eth_logo.png",
                            height="60px",
                            style={"padding": "10px", "float": "right"},
                        ),
                        html.Img(
                            id="iac_logo",
                            src="/assets/iac_logo.png",
                            height="60px",
                            style={"padding": "10px", "float": "right"},
                        ),
                    ],
                    className="logo_column",
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
                            # https://github.com/plotly/dash/issues/3487
                            PARAMETER_LIST,  # type:ignore[arg-type]
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
                            PARAMETER_OPTIONS["T2M"],  # type:ignore[arg-type]
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
                            SEASON_LIST,  # type:ignore[arg-type]
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
                            RANKING_LIST,  # type:ignore[arg-type]
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
                            REGION_LIST,  # type:ignore[arg-type]
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
                        html.Div(
                            children=["Number of events:"],
                            id="event-title",
                        ),
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
                            zoom=2.5,
                            worldCopyJump=True,
                            minZoom=2,
                            zoomSnap=0.25,
                            style={"height": "100%"},
                            children=[
                                dl.TileLayer(),
                                dl.GeoJSON(
                                    data=generate_poly(lon_range, lat_range),
                                    id="aio",
                                    style=dict(
                                        fill=False,
                                        dashArray="7",
                                        color="gray",
                                        weight=2,
                                    ),
                                    zoomToBounds=True,
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
                                ),
                                html.Div(
                                    [
                                        dbc.Button(
                                            "Information \u2753", id="open", n_clicks=0
                                        ),
                                        dbc.Modal(
                                            [
                                                dbc.ModalHeader(
                                                    dbc.ModalTitle(MODAL_TITLE)
                                                ),
                                                dbc.ModalBody(MODAL_CONTENT),
                                                dbc.ModalFooter(
                                                    dbc.Button(
                                                        "Close",
                                                        id="close",
                                                        className="ms-auto",
                                                        n_clicks=0,
                                                    )
                                                ),
                                            ],
                                            id="modal",
                                            is_open=False,
                                        ),
                                    ]
                                ),
                                html.Div(
                                    id="download-netcdf",
                                    className="download_button",
                                    children=[
                                        html.A(
                                            "Download raw data as netCDF",
                                            href=f"data/{DEFAULT_SETTING}.nc",
                                            className="btn btn-success btn-download",
                                            id="download-netcdf-anchor",
                                        ),
                                    ],
                                ),
                                html.Div(
                                    id="download-json",
                                    className="download_button",
                                    children=[
                                        html.Div(
                                            [
                                                html.Button(
                                                    "Download current selection as GeoJSON",
                                                    id="btn-json-download",
                                                    className="btn btn-success btn-download",
                                                ),
                                                dcc.Download(
                                                    id="download-json-component"
                                                ),
                                            ]
                                        )
                                    ],
                                ),
                            ],
                            id="right-collapse",
                        )
                    ],
                    id="sidebar_column",
                    style={
                        "width": "249px",
                        "display": "block",
                        "flex": "none",
                        "right": "0px",
                    },
                    className="bg-light",
                ),
            ],
        )
    ]
)

# Definition of app layout
app = Dash(
    __name__,
    title="INTEXseas Extreme Season Explorer",
    external_stylesheets=[dbc.themes.BOOTSTRAP, "assets/style.css"],
    external_scripts=["assets/color.js"],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.layout = html.Div([header, navbar, maprow])


@app.callback(
    Output("longitude-selector", "value"),
    Output("latitude-selector", "value"),
    Input("region-selector", "value"),
)
def subset_region(region_value: str):
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
    Output("nval-selector", "max"),
    Output("event-title", "children"),
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
    parameter_options = PARAMETER_OPTIONS[parameter_value]

    # Check if parameter_option is contained in parameter_options
    if parameter_option in [d["value"] for d in parameter_options]:
        option_selected = parameter_option
    # Otherwise, use the first parameter option
    else:
        option_selected = parameter_options[0]["value"]

    # Load patches
    selected_patch = f"patches_{parameter_value}_{season_value}_{option_selected}"
    patches = load_patches(str(DATA_DIR / f"{selected_patch}.geojson"))

    patches, event_title = filter_patches(
        patches,
        ranking_option,
        nval_value,
        longitude_values,
        latitude_values,
        year_values,
    )

    # Check if number of values was modified due to filtering
    if len(patches) < nval_value:
        max_events = len(patches)
    else:
        max_events = MAX_NUM_EVENTS

    # Catch situations where no events remain
    if max_events == 0:
        return (
            {"type": "FeatureCollection", "features": []},
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            no_update,
            "NO EVENTS LEFT, PLEASE CHANGE SELECTION!",
        )

    classes = list(patches["label"])
    labels = list(patches["year"])

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
        colorProp="label",
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
        max_events,
        event_title,
    )


@app.callback(
    Output("download-netcdf-anchor", "href"),
    Input("parameter-selector", "value"),
    Input("option-selector", "value"),
    Input("season-selector", "value"),
    prevent_initial_call=True,
)
def show_netcdf_download(
    parameter_value,
    parameter_option,
    season_value,
):
    selected_patch = f"patches_{parameter_value}_{season_value}_{parameter_option}.nc"
    # NOTE: this is a route (not a path)
    uri = f"data/{selected_patch}"
    return uri


@app.callback(
    Output("download-json-component", "data"),
    State("patches", "data"),
    State("parameter-selector", "value"),
    State("option-selector", "value"),
    State("season-selector", "value"),
    Input("download-json", "n_clicks"),
    prevent_initial_call=True,
)
def download_geojson(patches, parameter_value, parameter_option, season_value, _):
    gdf = geopandas.GeoDataFrame.from_features(patches)
    gdf = gdf.drop(columns=["visited on", "what"])
    geojson = gdf.to_json()

    # the filename should be the same, given the same patches
    hash = hashlib.sha1(geojson.encode("utf-8")).hexdigest()[:8]

    filename = (
        f"patches_{parameter_value}_{season_value}_{parameter_option}_{hash}.geojson"
    )

    return dcc.send_string(geojson, filename=filename)


@app.callback(
    Output("sidebar_column", "style"),
    Output("toggle-sidebar", "style"),
    Output("toggle-sidebar", "children"),
    Input("toggle-sidebar", "n_clicks"),
    Input("sidebar_column", "style"),
    Input("toggle-sidebar", "style"),
    Input("toggle-sidebar", "children"),
)
def toggle_sidebar(n_clicks, sidebar_style, toggle_style, button):
    if n_clicks:
        if sidebar_style["display"] == "none":
            sidebar_style["display"] = "block"
            toggle_style["right"] = "260px"
            button = ["❯"]
        else:
            sidebar_style["display"] = "none"
            toggle_style["right"] = "10px"
            button = ["❮"]
        return sidebar_style, toggle_style, button

    return sidebar_style, toggle_style, button


@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.server.route("/data/<path:path>")
def serve_static(path):
    return flask.send_from_directory(DATA_DIR, path)


server = app.server

if __name__ == "__main__":
    app.run(debug=True, port=8050)
