"""Testing suite for average_map Python API."""

from pathlib import Path

import pytest
import xtgeo

from grid3d_maps.avghc.grid3d_average_map import average_map


def test_average_map_python_api_basic(datatree):
    """Test average_map using Python API instead of YAML config."""
    result = datatree / "map_pythonapi_basic"
    result.mkdir(parents=True)

    # Call the Python API instead of using YAML
    average_map(
        eclroot='tests/data/reek/REEK',
        grid='$eclroot.EGRID',
        properties={
            'PORO': '$eclroot.INIT',
            'PRESSURE--19991201': '$eclroot.UNRST',
        },
        zranges=[
            {'Z1': [1, 5]},
            {'Z2': [6, 10]},
            {'Z3': [11, 14]},
        ],
        title='Reek',
        compute_zone=True,
        compute_all=True,
        mask_zeros=True,
        mapsettings={
            'xori': 457000,
            'xinc': 50,
            'yori': 5927000,
            'yinc': 50,
            'ncol': 200,
            'nrow': 250,
        },
        mapfolder=str(result),
        plotfolder=str(result),
        tag='pythonapi',
        prefix='test',
    )

    # Verify output was created
    z1poro = xtgeo.surface_from_file(result / "z1--pythonapi_average_poro.gri")
    assert z1poro.values.mean() == pytest.approx(0.1598, abs=0.001)


def test_average_map_python_api_with_yamlfile(datatree):
    """Test average_map using Python API with external zonation YAML."""
    result = datatree / "map_pythonapi_yamlfile"
    result.mkdir(parents=True)

    # Call the Python API with zonation from file
    average_map(
        eclroot='tests/data/reek/REEK',
        grid='$eclroot.EGRID',
        properties={
            'PORO': '$eclroot.INIT',
        },
        zonation_yamlfile='tests/yaml/avg1a_zone.yml',
        title='Reek',
        compute_zone=True,
        compute_all=True,
        mapsettings={
            'xori': 457000,
            'xinc': 50,
            'yori': 5927000,
            'yinc': 50,
            'ncol': 200,
            'nrow': 250,
        },
        mapfolder=str(result),
        tag='yamlzone',
    )

    # Verify output was created
    z1poro = xtgeo.surface_from_file(result / "z1--yamlzone_average_poro.gri")
    assert z1poro.values.mean() == pytest.approx(0.1598, abs=0.001)


def test_average_map_python_api_auto_mapsettings(datatree):
    """Test average_map with automatic map settings estimation."""
    result = datatree / "map_pythonapi_auto"
    result.mkdir(parents=True)

    # Call without mapsettings - should auto-estimate from grid
    average_map(
        eclroot='tests/data/reek/REEK',
        grid='$eclroot.EGRID',
        properties={
            'PORO': '$eclroot.INIT',
        },
        zranges=[
            {'Z1': [1, 5]},
        ],
        compute_zone=True,
        compute_all=False,
        mapfolder=str(result),
        tag='auto',
    )

    # Verify output was created
    z1poro = xtgeo.surface_from_file(result / "z1--auto_average_poro.gri")
    # Should have reasonable values even with auto-estimated map settings
    assert z1poro.values.mean() > 0.1 and z1poro.values.mean() < 0.3


def test_average_map_python_api_superranges(datatree):
    """Test average_map with super ranges combining zones."""
    result = datatree / "map_pythonapi_super"
    result.mkdir(parents=True)

    average_map(
        eclroot='tests/data/reek/REEK',
        grid='$eclroot.EGRID',
        properties={
            'PORO': '$eclroot.INIT',
        },
        zranges=[
            {'Z1': [1, 5]},
            {'Z2': [6, 10]},
            {'Z3': [11, 14]},
        ],
        superranges=[
            {'Z1+3': ['Z1', 'Z3']},
        ],
        mapsettings={
            'xori': 457000,
            'xinc': 50,
            'yori': 5927000,
            'yinc': 50,
            'ncol': 200,
            'nrow': 250,
        },
        mapfolder=str(result),
        tag='super',
    )

    # Verify super range output was created
    superzone = xtgeo.surface_from_file(result / "z1+3--super_average_poro.gri")
    assert superzone.values.mean() > 0.1


def test_average_map_python_api_date_diff(datatree):
    """Test average_map with date difference property."""
    result = datatree / "map_pythonapi_datediff"
    result.mkdir(parents=True)

    average_map(
        eclroot='tests/data/reek/REEK',
        grid='$eclroot.EGRID',
        properties={
            'PRESSURE--20030101-19991201': '$eclroot.UNRST',
        },
        zranges=[
            {'Z1': [1, 5]},
        ],
        compute_zone=True,
        compute_all=False,
        mapsettings={
            'xori': 457000,
            'xinc': 50,
            'yori': 5927000,
            'yinc': 50,
            'ncol': 200,
            'nrow': 250,
        },
        mapfolder=str(result),
        tag='datediff',
    )

    # Verify date diff output was created
    pressure_diff = xtgeo.surface_from_file(
        result / "z1--datediff_average_pressure--20030101-19991201.gri"
    )
    # Pressure difference should exist
    assert pressure_diff is not None
