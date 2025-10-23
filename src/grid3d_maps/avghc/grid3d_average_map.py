"""Script to make average maps directly from 3D grids.

A typical scenario is to create average maps directly from Eclipse
simulation files (or eventually other similators), but ROFF files
are equally supported.
"""

import logging
import sys

from . import (
    _compute_avg,
    _configparser,
    _get_grid_props,
    _get_zonation_filters,
    _mapsettings,
)

try:
    from grid3d_maps.version import __version__
except ImportError:
    __version__ = "0.0.0"

APPNAME = "grid3d_average_map"

# Module variables for ERT hook implementation:
DESCRIPTION = (
    "Make average property maps directly from 3D grids. Docs:\n"
    + "https://fmu-docs.equinor.com/docs/grid3d-maps/"
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def do_parse_args(args):
    """Parse command line arguments that will override config."""
    return _configparser.parse_args(args, APPNAME, DESCRIPTION)


def yamlconfig(inputfile, args):
    """Read from YAML file and modify/override"""

    config = _configparser.yconfig(inputfile)
    config = _configparser.prepare_metadata(config)
    config = _configparser.propformatting(config)

    # override with command line args
    config = _configparser.yconfig_override(config, args, APPNAME)

    config = _configparser.yconfig_set_defaults(config, APPNAME)

    # in case of YAML input (e.g. zonation from file)
    config = _configparser.yconfig_addons(config, APPNAME)

    if args.dumpfile:
        _configparser.yconfigdump(config, args.dumpfile)

    return config


def get_grid_props_data(config):
    """Collect the relevant Grid and props data (but not do the import)."""

    gfile, initlist, restartlist, dates = _get_grid_props.files_to_import(
        config, APPNAME
    )

    logger.info("Grid file is {}".format(gfile))

    logger.info("Getting INIT file data")
    for initpar, initfile in initlist.items():
        logger.info("%s file is %s", initpar, initfile)

    logger.info("Getting RESTART file data")
    for restpar, restfile in restartlist.items():
        logger.info("%s file is %s", restpar, restfile)

    logger.info("Getting dates")
    for date in dates:
        logger.info("Date is %s", date)

    return gfile, initlist, restartlist, dates


def import_pdata(config, gfile, initlist, restartlist, dates):
    """Import the data, and represent datas as numpies"""

    grd, initobjects, restobjects, dates = _get_grid_props.import_data(
        APPNAME, gfile, initlist, restartlist, dates
    )
    specd, averaged = _get_grid_props.get_numpies_avgprops(
        config, grd, initobjects, restobjects
    )

    # returns also dates since dates list may be updated after import
    return grd, specd, averaged, dates


def import_filters(config, grd):
    """Import the filter data properties, process and return a filter mask"""

    return _get_grid_props.import_filters(config, APPNAME, grd)


def get_zranges(config, grd):
    """Get the zonation names and ranges based on the config file.

    The zonation input has several variants; this is processed
    here. The config['zonation']['zranges'] is a list like

        - Tarbert: [1, 10]
        - Ness: [11,13]

    Args:
        config: The configuration dictionary
        grd (Grid): The XTGeo grid object

    Returns:
        A numpy zonation 3D array (zonation) + a zone dict)
    """
    zonation, zoned = _get_zonation_filters.zonation(config, grd)

    return zonation, zoned


def compute_avg_and_plot(
    config, grd, specd, propd, dates, zonation, zoned, filterarray
):
    """A dict of avg (numpy) maps, with zone name as keys."""

    if config["mapsettings"] is None:
        config = _mapsettings.estimate_mapsettings(config, grd)
    else:
        logger.info("Check map settings vs grid...")
        status = _mapsettings.check_mapsettings(config, grd)
        if status >= 10:
            logger.critical("STOP! Mapsettings defined is outside the 3D grid!")

    # This is done a bit different here than in the HC thickness. Here the
    # mapping and plotting is done within _compute_avg.py

    avgd = _compute_avg.get_avg(
        config, specd, propd, dates, zonation, zoned, filterarray
    )

    if config["output"]["plotfolder"] is not None:
        _compute_avg.do_avg_plotting(config, avgd)


def _build_config_from_kwargs(
    eclroot=None,
    folderroot=None,
    grid=None,
    properties=None,
    zonation_yamlfile=None,
    zonation_zonefile=None,
    zonation_zname=None,
    zranges=None,
    superranges=None,
    title=None,
    compute_zone=True,
    compute_all=True,
    mask_zeros=False,
    mapsettings=None,
    mapfolder=None,
    plotfolder=None,
    tag=None,
    prefix=None,
    lowercase=True,
    **kwargs
):
    """Build internal config dictionary from keyword arguments.

    This helper function converts Python keyword arguments into the internal
    config dictionary format that the rest of the pipeline expects.

    Args:
        eclroot (str): Eclipse root path (e.g., 'path/to/REEK')
        folderroot (str): Alternative folder root for input data
        grid (str): Grid file path (can use $eclroot variable)
        properties (dict): Dictionary of properties to average, e.g.,
            {'PORO': '$eclroot.INIT', 'PRESSURE--19991201': '$eclroot.UNRST'}
        zonation_yamlfile (str): Path to YAML file with zonation definition
        zonation_zonefile (str): Path to zone file
        zonation_zname (str): Zone name (default: 'all')
        zranges (list): List of zone ranges, e.g., [{'Z1': [1, 5]}, {'Z2': [6, 10]}]
        superranges (list): List of super ranges combining zones
        title (str): Project title
        compute_zone (bool): Compute per-zone averages (default: True)
        compute_all (bool): Compute overall average (default: True)
        mask_zeros (bool): Mask zero values in output (default: False)
        mapsettings (dict): Map settings with keys: xori, xinc, yori, yinc, ncol, nrow
        mapfolder (str): Output folder for maps
        plotfolder (str): Output folder for plots
        tag (str): Tag to add to output filenames
        prefix (str): Prefix for output filenames
        lowercase (bool): Use lowercase in output filenames (default: True)
        **kwargs: Additional settings passed to tuning or other config sections

    Returns:
        dict: Configuration dictionary compatible with the pipeline
    """
    # Build the nested config structure
    config = {
        'title': title or 'SomeField',
        'input': {},
        'zonation': {},
        'computesettings': {
            'zone': compute_zone,
            'all': compute_all,
            'mask_zeros': mask_zeros,
            'tuning': {},
        },
        'mapsettings': mapsettings,
        'output': {
            'mapfolder': mapfolder or 'fmu-dataio',
            'plotfolder': plotfolder,
            'tag': tag,
            'prefix': prefix,
            'lowercase': lowercase,
        }
    }

    # Add input section
    if eclroot:
        config['input']['eclroot'] = eclroot
    if folderroot:
        config['input']['folderroot'] = folderroot
    if grid:
        config['input']['grid'] = grid

    # Add properties to input
    if properties:
        config['input'].update(properties)

    # Add zonation settings
    if zonation_yamlfile:
        config['zonation']['yamlfile'] = zonation_yamlfile
    if zonation_zonefile:
        config['zonation']['zonefile'] = zonation_zonefile
    if zonation_zname:
        config['zonation']['zname'] = zonation_zname
    if zranges:
        config['zonation']['zranges'] = zranges
    if superranges:
        config['zonation']['superranges'] = superranges

    # Add any additional tuning parameters
    for key, value in kwargs.items():
        if key.startswith('tuning_'):
            config['computesettings']['tuning'][key[7:]] = value
        else:
            # Try to place in appropriate section
            config['computesettings'][key] = value

    return config


def average_map(
    eclroot=None,
    folderroot=None,
    grid=None,
    properties=None,
    zonation_yamlfile=None,
    zonation_zonefile=None,
    zonation_zname=None,
    zranges=None,
    superranges=None,
    title=None,
    compute_zone=True,
    compute_all=True,
    mask_zeros=False,
    mapsettings=None,
    mapfolder=None,
    plotfolder=None,
    tag=None,
    prefix=None,
    lowercase=True,
    **kwargs
):
    """Create average property maps from 3D grids using Python API.

    This function provides a Python-native alternative to the YAML-based
    configuration. It creates average maps directly from 3D Eclipse or ROFF grids.

    Args:
        eclroot (str): Eclipse root path (e.g., 'tests/data/reek/REEK'). This will
            be used to construct full paths using $eclroot variable substitution.
        folderroot (str, optional): Alternative folder root for input data.
        grid (str): Grid file path. Can use $eclroot variable, e.g., '$eclroot.EGRID'
        properties (dict): Dictionary mapping property identifiers to file paths.
            Examples:
                {'PORO': '$eclroot.INIT'}
                {'PRESSURE--19991201': '$eclroot.UNRST'}
                {'PRESSURE--20030101-19991201': '$eclroot.UNRST'}  # diff between dates
        zonation_yamlfile (str, optional): Path to YAML file with zone definitions.
        zonation_zonefile (str, optional): Path to zone property file.
        zonation_zname (str, optional): Zone property name (default: 'all').
        zranges (list, optional): List of dictionaries defining zone ranges.
            Example: [{'Z1': [1, 5]}, {'Z2': [6, 10]}, {'Z3': [11, 14]}]
        superranges (list, optional): List of dictionaries defining combined zones.
            Example: [{'Z1+3': ['Z1', 'Z3']}]
        title (str, optional): Project title (default: 'SomeField').
        compute_zone (bool): Whether to compute per-zone averages (default: True).
        compute_all (bool): Whether to compute overall average (default: True).
        mask_zeros (bool): Whether to mask zero values in output (default: False).
        mapsettings (dict, optional): Map settings dictionary with keys:
            - xori (float): Map origin X coordinate
            - xinc (float): Map increment in X direction
            - yori (float): Map origin Y coordinate
            - yinc (float): Map increment in Y direction
            - ncol (int): Number of columns
            - nrow (int): Number of rows
            If None, settings will be estimated from the 3D grid.
        mapfolder (str, optional): Output folder for maps (default: 'fmu-dataio').
        plotfolder (str, optional): Output folder for plots (default: None = no plots).
        tag (str, optional): Tag added to output filenames for identification.
        prefix (str, optional): Prefix for output filenames.
        lowercase (bool): Use lowercase in output filenames (default: True).
        **kwargs: Additional parameters passed to computesettings.

    Returns:
        None. Maps are written to disk in the specified output folders.

    Examples:
        Basic usage with Eclipse data:

        >>> from grid3d_maps.avghc.grid3d_average_map import average_map
        >>> average_map(
        ...     eclroot='tests/data/reek/REEK',
        ...     grid='$eclroot.EGRID',
        ...     properties={
        ...         'PORO': '$eclroot.INIT',
        ...         'PRESSURE--19991201': '$eclroot.UNRST',
        ...     },
        ...     zranges=[
        ...         {'Z1': [1, 5]},
        ...         {'Z2': [6, 10]},
        ...     ],
        ...     mapsettings={
        ...         'xori': 457000, 'xinc': 50,
        ...         'yori': 5927000, 'yinc': 50,
        ...         'ncol': 200, 'nrow': 250,
        ...     },
        ...     mapfolder='/tmp/maps',
        ...     tag='myrun',
        ... )

        Using external zonation file:

        >>> average_map(
        ...     eclroot='tests/data/reek/REEK',
        ...     grid='$eclroot.EGRID',
        ...     properties={'PORO': '$eclroot.INIT'},
        ...     zonation_yamlfile='zones.yml',
        ...     mapfolder='/tmp/maps',
        ... )
    """
    logger.info(f"Starting {APPNAME} via Python API (version {__version__})")

    # Build config from keyword arguments
    config = _build_config_from_kwargs(
        eclroot=eclroot,
        folderroot=folderroot,
        grid=grid,
        properties=properties,
        zonation_yamlfile=zonation_yamlfile,
        zonation_zonefile=zonation_zonefile,
        zonation_zname=zonation_zname,
        zranges=zranges,
        superranges=superranges,
        title=title,
        compute_zone=compute_zone,
        compute_all=compute_all,
        mask_zeros=mask_zeros,
        mapsettings=mapsettings,
        mapfolder=mapfolder,
        plotfolder=plotfolder,
        tag=tag,
        prefix=prefix,
        lowercase=lowercase,
        **kwargs
    )

    # Process config through the standard pipeline
    config = _configparser.prepare_metadata(config)
    config = _configparser.propformatting(config)
    config = _configparser.yconfig_set_defaults(config, APPNAME)
    config = _configparser.yconfig_addons(config, APPNAME)

    # Execute the pipeline
    logger.info("Collect files...")
    gfile, initlist, restartlist, dates = get_grid_props_data(config)

    logger.info("Import files...")
    grd, specd, propd, dates = import_pdata(config, gfile, initlist, restartlist, dates)

    # Get the filter array
    filterarray = import_filters(config, grd)
    logger.info("Filter mean value: %s", filterarray.mean())
    if filterarray.mean() < 1.0:
        logger.info("Property filters are active")

    for prop, val in propd.items():
        logger.info("Key is %s, avg value is %s", prop, val.mean())

    # Get the zonations
    logger.info("Get zonation info")
    zonation, zoned = get_zranges(config, grd)

    logger.info("Compute average properties")
    compute_avg_and_plot(config, grd, specd, propd, dates, zonation, zoned, filterarray)

    logger.info(f"{APPNAME} completed successfully")


def main(args=None):
    """Main routine."""
    logger.info(f"Starting {APPNAME} (version {__version__})")
    logger.info("Parse command line")
    args = do_parse_args(args)

    config = None
    if not args.config:
        logger.error("Config file is missing")
        sys.exit(1)

    logger.debug("--config option is applied, reading YAML ...")

    # get the configurations
    logger.info("Parse YAML file")
    config = yamlconfig(args.config, args)

    # get the files
    logger.info("Collect files...")
    gfile, initlist, restartlist, dates = get_grid_props_data(config)

    # import data from files and return relevant numpies
    logger.info("Import files...")

    grd, specd, propd, dates = import_pdata(config, gfile, initlist, restartlist, dates)

    # get the filter array
    filterarray = import_filters(config, grd)
    logger.info("Filter mean value: %s", filterarray.mean())
    if filterarray.mean() < 1.0:
        logger.info("Property filters are active")

    for prop, val in propd.items():
        logger.info("Key is %s, avg value is %s", prop, val.mean())

    # Get the zonations
    logger.info("Get zonation info")
    zonation, zoned = get_zranges(config, grd)

    logger.info("Compute average properties")
    compute_avg_and_plot(config, grd, specd, propd, dates, zonation, zoned, filterarray)


if __name__ == "__main__":
    main()
