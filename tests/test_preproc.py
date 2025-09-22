import os
from pathlib import Path

import geopandas as gpd
from click.testing import CliRunner
from geopandas import testing

from exseas_explorer.preproc.preproc import update_patches


def test_update_patches():

    test_path = os.path.abspath("tests/data")

    runner = CliRunner()
    result = runner.invoke(
        update_patches,
        ["-w", test_path, "-p", "patches_T2M_jja_ProbHot.nc"],
    )
    assert result.exit_code == 0

    # Check if a file was generated
    out_path = os.path.join(test_path, "patches_T2M_jja_ProbHot.geojson")
    out_file = Path(out_path)
    assert out_file.is_file()

    # Check if file is same as test file
    generated_patches = gpd.read_file(out_path, engine="fiona")
    expected_path = os.path.join(test_path, "patches_T2M_jja_ProbHot_test.geojson")
    test_patches = gpd.read_file(expected_path, engine="fiona")
    testing.assert_geodataframe_equal(generated_patches, test_patches)

    # Delete the test file again
    os.remove(out_path)
