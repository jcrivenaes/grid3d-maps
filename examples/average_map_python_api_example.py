#!/usr/bin/env python
"""Example of using the average_map Python API.

This demonstrates how to use the new Python function interface
instead of YAML configuration files.
"""

from grid3d_maps.avghc import average_map

# Example 1: Basic usage with explicit zone ranges
def example_basic():
    """Basic example with all parameters specified."""
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
        title='Reek Field',
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
        mapfolder='/tmp/maps',
        plotfolder='/tmp/plots',
        tag='example1',
        prefix='demo',
    )
    print("✓ Example 1 completed: Basic usage")


# Example 2: Using external YAML file for zonation
def example_with_yaml_zonation():
    """Example using external YAML file for zone definitions."""
    average_map(
        eclroot='tests/data/reek/REEK',
        grid='$eclroot.EGRID',
        properties={
            'PORO': '$eclroot.INIT',
        },
        zonation_yamlfile='tests/yaml/avg1a_zone.yml',
        title='Reek Field',
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
        mapfolder='/tmp/maps',
        tag='example2',
    )
    print("✓ Example 2 completed: Using external YAML zonation")


# Example 3: Auto map settings (estimated from grid)
def example_auto_mapsettings():
    """Example with automatic map settings estimation."""
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
        ],
        compute_zone=True,
        compute_all=False,
        mapfolder='/tmp/maps',
        tag='example3',
    )
    print("✓ Example 3 completed: Auto map settings")


# Example 4: Date difference properties
def example_date_diff():
    """Example with pressure difference between dates."""
    average_map(
        eclroot='tests/data/reek/REEK',
        grid='$eclroot.EGRID',
        properties={
            'PORO': '$eclroot.INIT',
            'PRESSURE--20030101-19991201': '$eclroot.UNRST',  # Difference between two dates
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
        mapfolder='/tmp/maps',
        tag='example4',
    )
    print("✓ Example 4 completed: Date difference")


# Example 5: Super ranges (combining multiple zones)
def example_super_ranges():
    """Example with super ranges combining zones."""
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
            {'Z1+Z3': ['Z1', 'Z3']},  # Combine Z1 and Z3
            {'AllZones': ['Z1', 'Z2', 'Z3']},  # Combine all zones
        ],
        compute_zone=True,
        mapsettings={
            'xori': 457000,
            'xinc': 50,
            'yori': 5927000,
            'yinc': 50,
            'ncol': 200,
            'nrow': 250,
        },
        mapfolder='/tmp/maps',
        tag='example5',
    )
    print("✓ Example 5 completed: Super ranges")


# Example 6: Multiple properties
def example_multiple_properties():
    """Example with multiple properties to average."""
    average_map(
        eclroot='tests/data/reek/REEK',
        grid='$eclroot.EGRID',
        properties={
            'PORO': '$eclroot.INIT',
            'PERMX': '$eclroot.INIT',
            'PRESSURE--19991201': '$eclroot.UNRST',
            'PRESSURE--20030101': '$eclroot.UNRST',
        },
        zranges=[
            {'Z1': [1, 5]},
            {'Z2': [6, 10]},
        ],
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
        mapfolder='/tmp/maps',
        tag='example6',
    )
    print("✓ Example 6 completed: Multiple properties")


if __name__ == '__main__':
    print("Grid3D Average Map - Python API Examples")
    print("=" * 50)
    print()

    # Uncomment the examples you want to run:
    # example_basic()
    # example_with_yaml_zonation()
    # example_auto_mapsettings()
    # example_date_diff()
    # example_super_ranges()
    # example_multiple_properties()

    print()
    print("Examples ready to run. Uncomment the function calls in __main__.")
