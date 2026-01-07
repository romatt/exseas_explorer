import functools
from typing import Any

import dash_ag_grid
import dash_leaflet as dl
import geopandas
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from dash import html
from geojson import Feature, FeatureCollection, Polygon


def filter_patches(
    df: geopandas.GeoDataFrame,
    criterion: int = 1,
    nvals: int = 10,
    lon_range: list[float] = [-180, 180],
    lat_range: list[float] = [-90, 90],
    year_range: list[float] = [1950, 2020],
) -> tuple[geopandas.GeoDataFrame, str]:
    """
    Filter patches

    Parameters
    ----------
    df : GeoDataFrame
        Unfiltered dataframe
    criterion : int, default: 1
        Criterion used to filter dataframe
    nvals : int, default: 10
        Number of most intense events to filter by
    lon_range : list, default: [-180, 180]
        List of longitude range
    lat_range : list, default: [-90, 90]
        List of latitude range
    year_range : list, default: [1950, 2020]
        List of year range

    Returns
    -------
    df : GeoDataFrame
        Filtered dataframe with the `nvals` most intense events
    """

    # Filter for coordinate
    df = df[(df["lonmean"] >= lon_range[0]) & (df["lonmean"] <= lon_range[1])]
    df = df[(df["latmean"] >= lat_range[0]) & (df["latmean"] <= lat_range[1])]

    # Filter for years
    df = df[(df["year"] >= year_range[0]) & (df["year"] <= year_range[1])]

    # Check if the resulting number of events is still larger than nvals, otherwise change it
    available_events = len(df)

    if available_events < nvals:
        nvals = available_events
        title = f"Only {available_events} events in this selection:"
    else:
        title = "Number of events:"

    # Catch situations where no events remain
    if nvals == 0:
        df = geopandas.GeoDataFrame()
    else:
        # Filter for criterion and number of values
        if criterion == 1:
            df = df[df["area"] >= np.sort(df["area"])[-nvals]]
        elif criterion == 2:
            # Remove instances where land_area is NAN
            df = df[~np.isnan(df["land_area"])]
            df = df[df["land_area"] >= np.sort(df["land_area"])[-nvals]]
        elif criterion == 3:
            df = df[np.abs(df["mean_ano"]) >= np.sort(np.abs(df["mean_ano"]))[-nvals]]
        elif criterion == 4:
            df = df[~np.isnan(df["land_mean_ano"])]
            df = df[
                np.abs(df["land_mean_ano"])
                >= np.sort(np.abs(df["land_mean_ano"]))[-nvals]
            ]
        elif criterion == 5:
            df = df[
                np.abs(df["integrated_ano"])
                >= np.sort(np.abs(df["integrated_ano"]))[-nvals]
            ]
        elif criterion == 6:
            df = df[~np.isnan(df["land_integrated_ano"])]
            df = df[
                np.abs(df["land_integrated_ano"])
                >= np.sort(np.abs(df["land_integrated_ano"]))[-nvals]
            ]

    return df, title


@functools.cache
def load_patches(path: str) -> geopandas.GeoDataFrame:
    """
    Load selected patches and return geopandas object with patches

    Parameters
    ----------
    path : str
        Path to the GeoJSON file

    Returns
    -------
    df : geopandas.GeoDataFrame
        Geopandas geodataframe
    """

    # Load data
    in_file = open(path)
    df = geopandas.read_file(in_file, engine="fiona")

    return df


def generate_cbar(labels: list[int]) -> dl.Colorbar:
    """
    Generate colorbar for provided year labels

    Test years
    labels = [1952, 1963, 1964, 1966, 1969, 1971, 1979, 1983, 1987, 2010]

    Parameters
    ----------
    labels : list
        List of years to process
    """

    # Define colors
    cmap = plt.get_cmap("nipy_spectral", len(labels))
    colors = [matplotlib.colors.to_hex(cmap(x)) for x in range(len(labels))]

    return colors


def generate_table(
    df: pd.DataFrame,
    colors: list,
    labels: list[int],
    criterion: int = 1,
    parameter: str = "T2M",
    option: str = "ProbCold",
) -> dash_ag_grid.AgGrid:
    """
    Generate table for provided years

    Parameters
    ----------
    df : pandas.DataFrame
        Filtered input dataframe
    colors : list
        List of colors for each row
    labels : list
        List of labels
    criterion : int, default: 1
        Criterion used to filter dataframe
    parameter : str, default: 'T2M'
        Parameter selected

    Returns
    -------
    dash_table.DataTable
        Table with relevant columns
    """

    pd.options.mode.chained_assignment = None  # type: ignore[assignment]
    df.rename(columns={"year": "Year"}, inplace=True)

    if parameter == "T2M":
        units = "K"
    elif parameter == "RTOT":
        units = "m^3"
    elif parameter == "WG10":
        units = "m/s"

    ascending = False
    if option in ["ProbCold", "ProbDry", "ProbCalm"]:
        ascending = True

    # thousand-separator and no values after comma for large numbers
    format_specifier = ",.0f"

    if criterion == 1:
        column = "area"
        long_name = "Area (km^2)"
        ascending = False
    elif criterion == 2:
        column = "land_area"
        long_name = "Land Area (km^2)"
        ascending = False
    elif criterion == 3:
        column = "mean_ano"
        long_name = f"Mean Anom. ({units})"
        format_specifier = ",.2f"
    elif criterion == 4:
        column = "land_mean_ano"
        long_name = f"Mean Land Anom. ({units})"
        format_specifier = ",.2f"
    elif criterion == 5:
        column = "integrated_ano"
        long_name = f"Int. Anom. ({units})"
    elif criterion == 6:
        column = "land_integrated_ano"
        long_name = f"Int. Land Anom. ({units})"

    # Only return relevant columns
    df = df[["label", "Year", column]]
    df[column] = df[column].round(2)
    df = df.sort_values(by=column, ascending=ascending)
    df = df.rename(columns={column: long_name})

    # Generate dict with colors for table
    style = []

    # Convert dataframe year to list
    df_label = df["label"].tolist()

    for ind, label in enumerate(labels):
        row = df_label.index(label)

        cond = {
            "condition": f"params.rowIndex == {row}",
            "style": {
                "backgroundColor": str(colors[ind]),
                "color": "white",
            },
        }

        style.append(cond)

    # Drop label column before showing
    df = df.drop(columns=["label"])

    locale = """d3.formatLocale({"thousands": "'", "grouping": [3]})"""

    columnDefs = [
        {
            "field": "Year",
            "cellStyle": {
                "styleConditions": style,
            },
        },
        {
            "field": df.columns[1],
            "type": "rightAligned",
            "valueFormatter": {
                "function": f"{locale}.format('{format_specifier}')(params.value)"
            },
        },
    ]

    defaultColDef = {"resizable": False, "suppressMovable": True}

    table = dash_ag_grid.AgGrid(
        rowData=df.to_dict("records"),
        columnDefs=columnDefs,
        defaultColDef=defaultColDef,
        columnSize="autoSize",
        dashGridOptions={
            # otherwise cannot have . in column name
            "suppressFieldDotNotation": True,
            "animateRows": False,
            "rowHeight": 30,
        },
        style={"height": "100%"},
        # compact to reduce padding
        className="ag-theme-alpine compact",
    )
    return table


def generate_poly(lon_range: list[float], lat_range: list[float]) -> FeatureCollection:
    """
    Generate a GeoJSON polygon with extensions of currently selected lon/lat restrictions
    """

    rect = FeatureCollection(
        [
            Feature(
                id="aio",
                geometry=Polygon(
                    [
                        [
                            (lon_range[0], lat_range[0]),
                            (lon_range[0], lat_range[1]),
                            (lon_range[1], lat_range[1]),
                            (lon_range[1], lat_range[0]),
                            (lon_range[0], lat_range[0]),
                        ]
                    ]
                ),
            )
        ]
    )

    return rect


def generate_details(feature: dict[str, Any]) -> html.Div:
    """ """

    if feature is not None:
        if feature["properties"]["Link"] is not None:
            literature = html.P("Literature")
        else:
            literature = html.P("No literature for this feature")

        details = html.Div(
            [
                html.P(f"Statistics on patch {feature['id']}"),
                html.P(f"Year {feature['properties']['year']}"),
                html.P(f"Area {feature['properties']['area']}"),
                html.P(f"Land area {feature['properties']['land_area']}"),
                literature,
            ]
        )
    else:
        details = html.Div([html.P("You have not clicked on anything yet!")])
    return details
