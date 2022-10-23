import os
from pathlib import Path

import geopandas as gpd
from click.testing import CliRunner
from geopandas import testing

from exseas_explorer.preproc.preproc import update_patches


def test_update_patches():

    runner = CliRunner()
    result = runner.invoke(update_patches, ['-w', os.path.abspath('tests/data'), '-p', 'patches_T2M_jja_ProbHot.nc'])
    assert result.exit_code == 0

    # Check if a file was generated
    out_path = os.path.join(os.path.abspath('tests/data'),'patches_T2M_jja_ProbHot.geojson')
    out_file = Path(out_path)
    assert out_file.is_file()

    # Check if file is same as test file
    generated_patches = gpd.read_file(out_path)
    test_patches = gpd.read_file(os.path.join(os.path.abspath('tests/data'),'patches_T2M_jja_ProbHot_test.geojson'))
    testing.assert_geodataframe_equal(generated_patches, test_patches)

    # Delete the test file again
    os.remove(out_path)


