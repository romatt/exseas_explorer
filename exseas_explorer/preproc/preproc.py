"""
Sub-module containing pre-processing functionality
"""

import logging
import sys

import click
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from geopandas import GeoDataFrame
from pyproj import CRS
from rasterio import features
from rasterio.transform import Affine
from shapely.geometry import shape

level = logging.INFO
fmt = '[%(levelname)s] %(asctime)s - %(message)s'
logging.basicConfig(stream=sys.stdout, level=level, format=fmt)
logger = logging.getLogger('__NAME__')


def affine_transform(array) -> Affine:
    """Returns the transform operator relating index coordinates to
    geographical coordinates of the dataset
    
    Returns
    -------
    rasterio.transform.Affine
        transform operator for georeferencing guidance data
    """

    mean_grid_spacing: float = (np.gradient(array.lon).mean() +
                                np.gradient(array.lat).mean()) / 2

    return Affine.translation(array.lon.values[0]
                                    - 0.5 * mean_grid_spacing,
                                    array.lat.values[0]
                                    - 0.5 * mean_grid_spacing) \
        * Affine.scale(mean_grid_spacing, mean_grid_spacing)


def extract_contours(array: xr.DataArray):
    """
    Extract contours

    Parameters
    ----------
    array : xr.DataArray
        Input data array (do not pass a dataset!)

    Returns
    -------
    GeoDataFrame
        Polygons of input array in a geodataframe
    """

    # List holding all and land only contours
    polygons = []

    # Compute affine transformer (relating x-y to coordiantes)
    affine = affine_transform(array)

    # Iterate over years
    for year in array.year:

        # Contour object generator
        contours = features.shapes(array.sel(year=year).values,
                                   transform=affine,
                                   connectivity=4)

        # Iterate over object generator
        for geom, val in contours:

            # Avoid passing entire domain as final polygon
            if val != 0:

                # Extract geometry and save to large list
                geometry = shape(geom)

                # Buffer polygon to make it smooth
                geometry = geometry.buffer(0.5,
                                           join_style=3).buffer(-0.5,
                                                                join_style=2)

                # Save polygon to list of polygons
                polygons.append([int(val), geometry])

    # Convert list to GeoDataFrame
    gdf = GeoDataFrame(data=polygons,
                       columns=['lab', 'geometry'],
                       crs=CRS.from_epsg(4326))

    return gdf


@click.command()
@click.option('-w',
              '--work_dir',
              default='/net/thermo/atmosdyn/maxibo/intexseas/webpage/')
@click.option('-p',
              '--patch_file',
              default='patches_40y_era5_RTOT_djf_ProbDry.nc')
def update_patches(work_dir='/ytpool/data/ETH/INTEXseas/',
                   patch_file='patches_40y_era5_RTOT_djf_ProbDry.nc'):
    """Read extreme season patches from NetCDF file, convert to polygons, and
    save as GeoJSON files

    Parameters
    ----------
    work_dir : str
        Working directory
    patch_file : str
        Input file to process

    Examples
    --------

    >>> files=*.nc
    >>> for file in $files; do python /home/roman/projects/exseas_explorer/exseas_explorer/preproc/preproc.py -w /ytpool/data/ETH/INTEXseas/ -p $file; done
    """

    logger.info(f'Processing {work_dir}{patch_file}')

    # Read NetCDF file
    in_file = xr.open_dataset(work_dir + patch_file)

    # Re-name key xarray and change data-type to work with shapes features
    in_file = in_file.rename({'key': 'year'}).astype(np.float32)

    # Read dataframe with additional data on patches
    list_file = patch_file.replace("patches",
                                   "list").replace(".nc",
                                                   ".txt").replace("Prob", "")
    patch_data = pd.read_csv(work_dir + list_file, na_values='-999.99')
    patch_data = patch_data.astype({'lab': 'int32', 'key': 'int32'})

    # Read dataframe with literature information
    lit_file = patch_file.replace("patches", "lit").replace(".nc", ".txt").replace("Prob","")
    lit_data = pd.read_csv(work_dir + lit_file, na_values='-999.99', skip_blank_lines=True, sep=";")
    lit_data = lit_data.astype({'Label': 'int32', 'Year': 'int32'})
    lit_data = lit_data.drop(columns=['Year', 'Season'])
    # Some labels have multiple citations, need to aggreate  those into lists
    lit_data = lit_data.groupby('Label').agg(dict)

    # Extract contours
    patch = extract_contours(in_file.lab)

    # Merge contour data with geodataframe
    patch_out = patch.merge(patch_data, on='lab')
    patch_out = patch_out.rename(columns={"lab": "Label", "key": "Year"})

    # Merge literature data with DF
    patch_out = patch_out.merge(lit_data, on='Label', how='left')

    # Drop unused columns
    patch_out = patch_out.drop(columns=['ngp', 'land_ngp', 'median_prob', 'land_median_prob', 'median_ano', 'land_median_ano'])

    # Combine polygons with same label
    patch_out = patch_out.dissolve(by='Label').reset_index(level=0)

    # Save geometries to file
    file_end = patch_file.replace("nc", "geojson")
    patch_out.to_file(f'{work_dir}/{file_end}', driver='GeoJSON', index=False)


if __name__ == '__main__':
    update_patches()
