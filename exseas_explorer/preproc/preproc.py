"""
Sub-module containing pre-processing functionality
"""

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
# from shapely.geometry import Polygon
# from skimage import measure
from shapely.geometry import shape


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
                polygons.append([int(val), geometry])

    # Convert list to GeoDataFrame
    gdf = GeoDataFrame(data=polygons,
                       columns=['lab', 'geometry'],
                       crs=CRS.from_epsg(4326))

    return gdf

@click.command()
@click.option('-w', '--work_dir', default='/net/thermo/atmosdyn/maxibo/intexseas/webpage/')
@click.option('-p', '--patch_file', default='patches_40y_era5_RTOT_djf_ProbDry.nc')
def update_patches(work_dir='/net/thermo/atmosdyn/maxibo/intexseas/webpage/',
                   patch_file='patches_40y_era5_RTOT_djf_ProbDry.nc'):
    """Read extreme season patches from NetCDF file, convert to polygons, and
    save as GeoJSON files

    TODO
    - Combine geodataframe containing shapes with the one with additional information

    Parameters
    ----------
    work_dir : str
        Working directory
    patch_file : str
        Input file to process
    """

    # Read NetCDF file
    in_file = xr.open_dataset(work_dir + patch_file)

    # Re-name key xarray and change data-type to work with shapes features
    in_file = in_file.rename({'key': 'year'}).astype(np.float32)

    # Read dataframe with additional data on patches
    list_file = patch_file.replace("patches", "list").replace(".nc", ".txt")
    patch_data = pd.read_csv(work_dir + list_file, na_values='-999.99')
    patch_data = patch_data.astype({'lab':'int32', 'key':'int32'})

    # Extract contours
    patch_all = extract_contours(in_file.lab)
    patch_land = extract_contours(in_file.lab_land)

    # Merge DF data with geodataframe
    patch_all_out = patch_all.merge(patch_data, on='lab')
    patch_land_out = patch_land.merge(patch_data, on='lab')

    # Replace end of string
    file_end = patch_file.replace("nc", "geojson")

    # Save geometries to file
    patch_all_out.to_file(f'{work_dir}/all_{file_end}',
                          driver='GeoJSON',
                          index=False)
    patch_land_out.to_file(f'{work_dir}/land_{file_end}',
                           driver='GeoJSON',
                           index=False)

if __name__ == '__main__':
    update_patches()

# test = xr.where(
#     in_file.lab.sel(year=year) == 5073, in_file.lab.sel(year=year), 0)

# # Display the image and plot all contours found
# fig, ax = plt.subplots()
# ax.imshow(in_file.lab.sel(year=year), cmap="Spectral")

# for contour in test:
#     ax.plot(contour[:, 1], contour[:, 0], linewidth=2)

# ax.axis('image')
# ax.set_xticks([])
# ax.set_yticks([])
# plt.show()
