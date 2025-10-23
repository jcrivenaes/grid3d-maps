# Quick Start: Python API vs YAML

## Before (YAML-based approach)

### Step 1: Create config.yml
```yaml
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
  mapfolder: /tmp/maps
  tag: myrun
```

### Step 2: Run from command line
```bash
grid3d_average_map --config config.yml
```

### Or from Python
```python
from grid3d_maps.avghc.grid3d_average_map import main
main(['--config', 'config.yml'])
```

---

## After (New Python API)

### Single Python script
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
    mapfolder='/tmp/maps',
    tag='myrun',
)
```

---

## Key Advantages

✅ **No separate files needed** - Everything in one place
✅ **IDE support** - Autocomplete and type hints
✅ **Programmatic** - Easy to parameterize and loop
✅ **Less context switching** - Stay in Python
✅ **Easier debugging** - Stack traces point to your code

---

## Advanced Example: Parametric Study

```python
from grid3d_maps.avghc import average_map

# Easy to parameterize!
dates = ['19991201', '20000601', '20010101', '20020101']
zones = [
    {'Shallow': [1, 5]},
    {'Middle': [6, 10]},
    {'Deep': [11, 14]},
]

for date in dates:
    average_map(
        eclroot='tests/data/reek/REEK',
        grid='$eclroot.EGRID',
        properties={
            'PRESSURE--' + date: '$eclroot.UNRST',
        },
        zranges=zones,
        mapsettings={
            'xori': 457000, 'xinc': 50,
            'yori': 5927000, 'yinc': 50,
            'ncol': 200, 'nrow': 250,
        },
        mapfolder=f'/tmp/maps_{date}',
        tag=f'date_{date}',
    )
```

This would require 4 separate YAML files with the old approach!
