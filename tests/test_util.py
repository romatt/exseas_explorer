
import pytest
import numpy as np

from exseas_explorer.util import (filter_patches, generate_cbar, generate_table)

def test_load_patches(default_patches):
    assert len(default_patches)==19
    assert default_patches['year'].unique()[0]==1950

def test_filter_patches(default_patches):
    filtered_patches = filter_patches(default_patches)
    assert len(filtered_patches)==10
    filtered_patches = filter_patches(default_patches, nvals=1)
    assert len(filtered_patches)==1
    filtered_patches = filter_patches(default_patches, criterion=2)
    assert any(np.isnan(filtered_patches["land_area"]))==False

@pytest.fixture
def filtered_patches(default_patches):
    filtered_patches = filter_patches(default_patches)
    yield filtered_patches

def test_generate_cbar(filtered_patches):
    colorscale = generate_cbar(list(filtered_patches["year"]))
    assert len(colorscale)==10
    assert colorscale[0]=='#000000'
    assert colorscale[-1]=='#cccccc'

@pytest.fixture
def colorscale(filtered_patches):
    colorscale = generate_cbar(list(filtered_patches["year"]))
    yield colorscale

def test_generate_table(filtered_patches, colorscale):
    poly_table = generate_table(filtered_patches, colorscale, list(filtered_patches["label"]))
    assert poly_table.data[0]=={'year': 1950, 'Area (km^2)': 2639429.64}
    assert poly_table.data[-1]=={'year': 1950, 'Area (km^2)': 326450.42}
