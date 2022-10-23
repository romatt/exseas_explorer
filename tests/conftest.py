import os

import pytest

from exseas_explorer.util import filter_patches, load_patches


@pytest.fixture(scope="session")
def default_patches():
    dir = os.path.abspath('tests/data')
    patch_geojson = 'patches_T2M_jja_ProbHot_test.geojson'
    default_patches = load_patches(os.path.join(dir, patch_geojson))
    yield default_patches

@pytest.fixture(scope="session")
def test_file_netcdf():
    dir = os.path.abspath('tests/data')
    patch_geojson = 'patches_T2M_jja_ProbHot_test.nc'
    yield os.path.join(dir, patch_geojson)
