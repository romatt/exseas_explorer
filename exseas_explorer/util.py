import dash_leaflet as dl
import geopandas
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, Colormap, ListedColormap
from dash import dash_table

# COLORMAP DEFINITON
greys = plt.cm.Greys  # 1950er
pinks = plt.cm.RdPu  # 1960er
purp = plt.cm.Purples  # 1970er
blues = plt.cm.Blues  # 1980er
greens = plt.cm.Greens  # 1990er
ylors = plt.cm.Oranges  #YlOrBr   # 2000er
reds = plt.cm.Reds  # 2010er
cols=ListedColormap([greys(20),greys(40),greys(60),greys(80),greys(100),greys(120),greys(140),greys(160),greys(180),greys(200),   \
             pinks(20),pinks(40),pinks(60),pinks(80),pinks(100),pinks(120),pinks(140),pinks(160),pinks(180),pinks(200),   \
                     purp(20),purp(40),purp(60),purp(80),purp(100),purp(120),purp(140),purp(160),purp(180),purp(200),   \
                     blues(20),blues(40),blues(60),blues(80),blues(100),blues(120),blues(140),blues(160),blues(180),blues(200),   \
                     greens(20),greens(40),greens(60),greens(80),greens(100),greens(120),greens(140),greens(160),greens(180),greens(200),\
                     ylors(20),ylors(40),ylors(60),ylors(80),ylors(100),ylors(120),ylors(140),ylors(160),ylors(180),ylors(200),\
                    reds(20),reds(40),reds(60),reds(80),reds(100),reds(120),reds(140),reds(160),reds(180),reds(200),\
                     plt.cm.YlOrRd(60)])
norm = BoundaryNorm(np.arange(1950, 2020 + 1, 1), cols.N)


def filter_patches(df: geopandas.GeoDataFrame,
                   criterion: int = 1,
                   nvals: int = 10,
                   lon_range: list = [-180, 180],
                   lat_range: list = [-90, 90],
                   year_range: list = [1950, 2020]) -> geopandas.GeoDataFrame:
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
    df = df[(df['lonmean'] >= lon_range[0]) & (df['lonmean'] <= lon_range[1])]
    df = df[(df['latmean'] >= lat_range[0]) & (df['latmean'] <= lat_range[1])]

    # Filter for years
    df = df[(df['Year'] >= year_range[0]) & (df['Year'] <= year_range[1])]

    # Filter for criterion and number of values
    if criterion == 1:
        df = df[df['area'] >= np.sort(df['area'])[-nvals]]
    elif criterion == 2:
        # Remove instances where land_area is NAN
        df = df[~np.isnan(df['land_area'])]
        df = df[df['land_area'] >= np.sort(df['land_area'])[-nvals]]
    elif criterion == 3:
        df = df[
            np.abs(df['mean_ano']) >= np.sort(np.abs(df['mean_ano']))[-nvals]]
    elif criterion == 4:
        df = df[~np.isnan(df['land_mean_ano'])]
        df = df[np.abs(df['land_mean_ano']) >= np.sort(
            np.abs(df['land_mean_ano']))[-nvals]]
    elif criterion == 5:
        df = df[np.abs(df['integrated_ano']) >= np.sort(
            np.abs(df['integrated_ano']))[-nvals]]
    elif criterion == 6:
        df = df[~np.isnan(df['land_integrated_ano'])]
        df = df[np.abs(df['land_integrated_ano']) >= np.sort(
            np.abs(df['land_integrated_ano']))[-nvals]]

    return df


def load_patches(path: str) -> geopandas.GeoDataFrame:
    """
    Load selected patches and return geopandas object with patches
    """

    # Load data
    df = geopandas.read_file(path, encoding="utf8")

    return df


def generate_cbar(labels: list) -> dl.Colorbar:
    """
    Generate colorbar for provided year labels

    Test years
    labels = [1952,1963,1964,1966,1969,1971,1979,1983,1987,2010]

    Parameters
    ----------
    labels : list
        List of years to process
    """

    # Define colors
    colors = [matplotlib.colors.to_hex(cols(norm(x))) for x in labels]

    cmap = plt.get_cmap("turbo", len(labels))
    colors = [
        matplotlib.colors.to_hex(cmap(x)) for x in np.arange(len(labels))
    ]

    return colors


def generate_table(df: pd.DataFrame, colors: list, criterion: int = 1) -> pd.DataFrame:
    """
    Generate table for provided years

    Parameters
    ----------
    df : pandas.DataFrame
        Filtered input dataframe
    colors : list
        List of colors for each row
    criterion : int, default: 1
        Criterion used to filter dataframe

    Returns
    -------
    dash_table.DataTable
        Table with relevant columns
    """

    pd.options.mode.chained_assignment = None

    # Only return relevant columns
    if criterion == 1:
        df = df[['Year', 'area']]
        df['area'] = df['area'].round(2)
        df = df.rename(columns={"area": "Area (km^2)"})
    elif criterion == 2:
        df = df[['Year', 'land_area']]
        df['land_area'] = df['land_area'].round(2)
        df = df.rename(columns={"land_area": "Land Area (km^2)"})
    elif criterion == 3:
        df = df[['Year', 'mean_ano']]
        df['mean_ano'] = df['mean_ano'].round(2)
        df = df.rename(columns={"mean_ano": "Mean Anom. (XXX)"})
    elif criterion == 4:
        df = df[['Year', 'land_mean_ano']]
        df['land_mean_ano'] = df['land_mean_ano'].round(2)
        df = df.rename(columns={"land_mean_ano": "Mean Land Anom. (XXX)"})
    elif criterion == 5:
        df = df[['Year', 'integrated_ano']]
        df['integrated_ano'] = df['integrated_ano'].round(2)
        df = df.rename(columns={"integrated_ano": "Int. Anom. (XXX)"})
    elif criterion == 6:
        df = df[['Year', 'land_integrated_ano']]
        df['land_integrated_ano'] = df['land_integrated_ano'].round(2)
        df = df.rename(columns={"land_integrated_ano": "Int. Land Anom. (XXX)"})

    # Convert from m^2 to km^2
    # df['area'] = df['area'].div(1e+6)
    # df['land_area'] = df['land_area'].div(1e+6)

    # Sort by year in reverse order
    df = df.sort_values(by='Year', ascending=False)

    # Invert colors
    colors = colors[::-1]

    # Generate dict with colors for table
    list = []
    for i, color in enumerate(colors):
        list.append({
            'if': {
                'row_index': i,
                'column_id': 'Year',
            },
            'backgroundColor': str(color),
            'color': 'white'
        })

    table = dash_table.DataTable(data=df.to_dict('records'),
                                 columns=[{
                                     'id': c,
                                     'name': c
                                 } for c in df.columns],
                                 style_data_conditional=list,
                                 sort_action='native')

    return table


def generate_poly():
    """
    Generate a polygon with extensions of currently selected lon/lat restrictions
    """

    polygon = dl.Polygon(positions=[[57, 10], [57, 11], [56, 11], [57, 10]])

    return None
