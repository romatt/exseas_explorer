import dash_leaflet as dl
import geopandas
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm, ListedColormap

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
                   criterion: int,
                   nvals: int = 10) -> geopandas.GeoDataFrame:
    """
    Filter patches by selected criterion

    Parameters
    ----------
    df : GeoDataFrame
        Unfiltered dataframe
    criterion : int
        Criterion used to filter dataframe
    nvals : int, default: 10
        Number of most intense events to filter by

    Returns
    -------
    df : GeoDataFrame
        Filtered dataframe with the `nvals` most intense events 
    """

    if criterion == 1:
        df = df[df['area'] >= np.sort(df['area'])[-nvals]]
    if criterion == 2:
        # Remove instances where land_area is NAN
        df = df[~np.isnan(df['land_area'])]
        df = df[df['land_area'] >= np.sort(df['land_area'])[-nvals]]

    return df

def load_patches(path: str) -> geopandas.GeoDataFrame:
    """
    Load selected patches and return geopandas object with patches
    """

    # Load data
    in_file = open(path)
    df = geopandas.read_file(in_file)

    return df

def generate_cbar(labels: list) -> dl.Colorbar:
    """
    Generate colorbar for provided year labels

    Test years
    years = [1952,1963,1964,1966,1969,1971,1979,1983,1987,2010]

    Parameters
    ----------
    labels : list
        List of years to process
    """

    # Define colors
    colors = [matplotlib.colors.to_hex(cols(norm(x))) for x in labels]

    return colors