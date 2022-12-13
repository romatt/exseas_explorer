import geojson
import numpy as np
import pytest

from exseas_explorer.util import (
    filter_patches,
    generate_cbar,
    generate_poly,
    generate_table,
)


def test_load_patches(default_patches):
    assert len(default_patches) == 19
    assert default_patches["year"].unique()[0] == 1988


def test_filter_patches(default_patches):
    filtered_patches = filter_patches(default_patches)
    assert len(filtered_patches) == 10
    filtered_patches = filter_patches(default_patches, nvals=1)
    assert len(filtered_patches) == 1
    filtered_patches = filter_patches(default_patches, criterion=2)
    assert not any(np.isnan(filtered_patches["land_area"]))


@pytest.fixture
def filtered_patches(default_patches):
    filtered_patches = filter_patches(default_patches)
    yield filtered_patches


def test_generate_cbar(filtered_patches):
    colorscale = generate_cbar(list(filtered_patches["year"]))
    assert len(colorscale) == 10
    assert colorscale[0] == "#000000"
    assert colorscale[-1] == "#cccccc"


@pytest.fixture
def colorscale(filtered_patches):
    colorscale = generate_cbar(list(filtered_patches["year"]))
    yield colorscale


def test_generate_table(filtered_patches, colorscale):
    poly_table = generate_table(
        filtered_patches, colorscale, list(filtered_patches["label"])
    )
    assert poly_table.data[0] == {"year": 1988, "Area (km^2)": 7957515.04}
    assert poly_table.data[-1] == {"year": 1988, "Area (km^2)": 617857.55}


def test_generate_poly():
    polygon = generate_poly([-180, 180], [0, 90])
    assert type(polygon) == geojson.feature.FeatureCollection
    assert len(polygon.features) == 1
    assert polygon.features[0].geometry.coordinates[0][0] == [-180, 0]
    assert len(polygon.features[0].geometry.coordinates[0]) == 5
