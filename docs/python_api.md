# Python API for grid3d_average_map

This document describes the new Python API for creating average maps from 3D grids, which provides an alternative to the YAML-based configuration.

## Overview

The `average_map()` function allows you to create average property maps directly from Python code using keyword arguments, eliminating the need for YAML configuration files in many cases.

## Basic Usage

```python
from grid3d_maps.avghc import average_map

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
    mapsettings={
        'xori': 457000,
        'xinc': 50,
        'yori': 5927000,
        'yinc': 50,
        'ncol': 200,
        'nrow': 250,
    },
    mapfolder='/tmp/maps',
    tag='myrun',
)
```

## Parameters

### Input Data Parameters

- **`eclroot`** (str, optional): Eclipse root path (e.g., `'path/to/REEK'`). Used for `$eclroot` variable substitution.
- **`folderroot`** (str, optional): Alternative folder root for input data.
- **`grid`** (str, required): Grid file path. Can use `$eclroot` variable (e.g., `'$eclroot.EGRID'`).
- **`properties`** (dict, required): Dictionary mapping property names to file paths.

### Zonation Parameters

You can specify zonation in multiple ways:

- **`zranges`** (list, optional): Direct zone definition as list of dicts:
  ```python
  zranges=[
      {'Z1': [1, 5]},
      {'Z2': [6, 10]},
      {'Z3': [11, 14]},
  ]
  ```

- **`zonation_yamlfile`** (str, optional): Path to YAML file with zone definitions.
- **`zonation_zonefile`** (str, optional): Path to zone property file.
- **`zonation_zname`** (str, optional): Zone property name (default: `'all'`).
- **`superranges`** (list, optional): List of combined zones:
  ```python
  superranges=[
      {'Z1+3': ['Z1', 'Z3']},
  ]
  ```

### Compute Settings

- **`compute_zone`** (bool): Compute per-zone averages (default: `True`).
- **`compute_all`** (bool): Compute overall average (default: `True`).
- **`mask_zeros`** (bool): Mask zero values in output (default: `False`).

### Map Settings

- **`mapsettings`** (dict, optional): Map configuration with keys:
  - `xori` (float): Map origin X coordinate
  - `xinc` (float): Map increment in X direction
  - `yori` (float): Map origin Y coordinate
  - `yinc` (float): Map increment in Y direction
  - `ncol` (int): Number of columns
  - `nrow` (int): Number of rows

  If `None`, settings are automatically estimated from the 3D grid.

### Output Parameters

- **`mapfolder`** (str, optional): Output folder for maps (default: `'fmu-dataio'`).
- **`plotfolder`** (str, optional): Output folder for plots (default: `None` = no plots).
- **`tag`** (str, optional): Tag added to output filenames.
- **`prefix`** (str, optional): Prefix for output filenames.
- **`lowercase`** (bool): Use lowercase in filenames (default: `True`).

### Other Parameters

- **`title`** (str, optional): Project title (default: `'SomeField'`).
- **`**kwargs`**: Additional parameters for advanced settings.

## Property Specifications

Properties are specified as a dictionary where:
- **Key**: Property identifier
- **Value**: Source file path (can use `$eclroot` variable)

### Property Name Formats

1. **Static properties** (from INIT files):
   ```python
   'PORO': '$eclroot.INIT'
   ```

2. **Dynamic properties at specific date** (from UNRST files):
   ```python
   'PRESSURE--19991201': '$eclroot.UNRST'
   ```

3. **Date difference properties**:
   ```python
   'PRESSURE--20030101-19991201': '$eclroot.UNRST'
   ```
   This computes the difference: PRESSURE(20030101) - PRESSURE(19991201)

## Examples

### Example 1: Basic Usage

```python
from grid3d_maps.avghc import average_map

average_map(
    eclroot='tests/data/reek/REEK',
    grid='$eclroot.EGRID',
    properties={
        'PORO': '$eclroot.INIT',
    },
    zranges=[
        {'Z1': [1, 5]},
        {'Z2': [6, 10]},
    ],
    compute_zone=True,
    compute_all=True,
    mapsettings={
        'xori': 457000, 'xinc': 50,
        'yori': 5927000, 'yinc': 50,
        'ncol': 200, 'nrow': 250,
    },
    mapfolder='/tmp/maps',
    tag='run1',
)
```

### Example 2: Using External YAML for Zonation

```python
average_map(
    eclroot='tests/data/reek/REEK',
    grid='$eclroot.EGRID',
    properties={'PORO': '$eclroot.INIT'},
    zonation_yamlfile='zones.yml',  # External zone definition
    mapsettings={
        'xori': 457000, 'xinc': 50,
        'yori': 5927000, 'yinc': 50,
        'ncol': 200, 'nrow': 250,
    },
    mapfolder='/tmp/maps',
)
```

### Example 3: Auto Map Settings

Let the function estimate map settings from the grid:

```python
average_map(
    eclroot='tests/data/reek/REEK',
    grid='$eclroot.EGRID',
    properties={'PORO': '$eclroot.INIT'},
    zranges=[{'Z1': [1, 5]}],
    mapfolder='/tmp/maps',
    # mapsettings=None (default) - will be auto-estimated
)
```

### Example 4: Date Differences

Compute pressure change between dates:

```python
average_map(
    eclroot='tests/data/reek/REEK',
    grid='$eclroot.EGRID',
    properties={
        'PRESSURE--20030101-19991201': '$eclroot.UNRST',
    },
    zranges=[{'Z1': [1, 5]}],
    mapsettings={
        'xori': 457000, 'xinc': 50,
        'yori': 5927000, 'yinc': 50,
        'ncol': 200, 'nrow': 250,
    },
    mapfolder='/tmp/maps',
)
```

### Example 5: Super Ranges

Combine multiple zones:

```python
average_map(
    eclroot='tests/data/reek/REEK',
    grid='$eclroot.EGRID',
    properties={'PORO': '$eclroot.INIT'},
    zranges=[
        {'Z1': [1, 5]},
        {'Z2': [6, 10]},
        {'Z3': [11, 14]},
    ],
    superranges=[
        {'Z1+Z3': ['Z1', 'Z3']},  # Combine zones 1 and 3
    ],
    mapsettings={
        'xori': 457000, 'xinc': 50,
        'yori': 5927000, 'yinc': 50,
        'ncol': 200, 'nrow': 250,
    },
    mapfolder='/tmp/maps',
)
```

### Example 6: Multiple Properties

Process multiple properties at once:

```python
average_map(
    eclroot='tests/data/reek/REEK',
    grid='$eclroot.EGRID',
    properties={
        'PORO': '$eclroot.INIT',
        'PERMX': '$eclroot.INIT',
        'PRESSURE--19991201': '$eclroot.UNRST',
        'SGAS--19991201': '$eclroot.UNRST',
    },
    zranges=[
        {'Z1': [1, 5]},
        {'Z2': [6, 10]},
    ],
    mapsettings={
        'xori': 457000, 'xinc': 50,
        'yori': 5927000, 'yinc': 50,
        'ncol': 200, 'nrow': 250,
    },
    mapfolder='/tmp/maps',
    plotfolder='/tmp/plots',  # Also create plots
    tag='multiprops',
)
```

## Comparison: YAML vs Python API

### YAML Configuration (traditional)

```yaml
# config.yml
title: Reek
input:
  eclroot: tests/data/reek/REEK
  grid: $eclroot.EGRID
  PORO: $eclroot.INIT
  PRESSURE--19991201: $eclroot.UNRST

zonation:
  zranges:
    - Z1: [1, 5]
    - Z2: [6, 10]

computesettings:
  zone: Yes
  all: Yes

mapsettings:
  xori: 457000
  xinc: 50
  yori: 5927000
  yinc: 50
  ncol: 200
  nrow: 250

output:
  mapfolder: /tmp
  tag: myrun
```

```python
# Usage
from grid3d_maps.avghc.grid3d_average_map import main
main(['--config', 'config.yml'])
```

### Python API (new)

```python
from grid3d_maps.avghc import average_map

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
    compute_all=True,
    mapsettings={
        'xori': 457000, 'xinc': 50,
        'yori': 5927000, 'yinc': 50,
        'ncol': 200, 'nrow': 250,
    },
    mapfolder='/tmp',
    tag='myrun',
)
```

## Benefits of Python API

1. **No external files needed**: Everything in one script
2. **Type hints and IDE support**: Better autocomplete and error checking
3. **Dynamic configuration**: Easily parameterize with loops, conditions, etc.
4. **Integration**: Easier to integrate into existing Python workflows
5. **Programmatic control**: Can be called from other Python code

## When to Use YAML vs Python API

### Use YAML when:
- Working with ERT workflows
- Configuration should be separate from code
- Non-programmers need to modify settings
- Configuration is reused across multiple runs

### Use Python API when:
- Building automated workflows
- Integrating with existing Python code
- Parameterizing runs programmatically
- Rapid prototyping and experimentation

## Notes

- The Python API internally converts keyword arguments to the same configuration dictionary format used by YAML
- All the same features and options are available in both interfaces
- You can still use `zonation_yamlfile` parameter to reference external YAML files for zone definitions
- Variable substitution (like `$eclroot`) works the same way in both interfaces
