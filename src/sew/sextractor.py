import os
from pathlib import Path
from subprocess import CalledProcessError, call, check_output
from typing import List, Optional, Union

import numpy as np
from astropy.io import ascii, fits
from astropy.table import Table

from . import errors, utils
from .constants import PACKAGE_PATH, SE_EXECUTABLE
from .log import load_logger
from .utils import PathLike, PathOrPixels

__all__ = [
    "run",
    "DEFAULT_OPTIONS",
    "OPTION_NAMES",
    "PARAM_NAMES",
    "SE_INPUT_FILE_PATH",
    "KERNEL_PATH",
]

logger = load_logger()

# default SExtractor paths and files
SE_INPUT_FILE_PATH = PACKAGE_PATH / "input"
KERNEL_PATH = SE_INPUT_FILE_PATH / "kernels"
DEFAULT_NNW = SE_INPUT_FILE_PATH / "default.nnw"
DEFAULT_CONFIG_PATH = SE_INPUT_FILE_PATH / "default.config"
DEFAULT_PARAM_FILE = SE_INPUT_FILE_PATH / "default.param"
DEFAULT_CONV = KERNEL_PATH / "default.conv"

try:
    lines_bytes = check_output(f"{SE_EXECUTABLE} -dd", shell=True)
except CalledProcessError:
    raise errors.SourceExtractorExecutableError(
        "SE_EXECUTABLE is not working correctly -> verify this env variable runs SExtractor as expected"
    )

# get list of all config options
lines = lines_bytes.decode("utf-8").split("\n")
cleaned = filter(
    lambda line: line.strip()[0] != "#", filter(lambda line: len(line) > 1, lines)
)
OPTION_NAMES = [line.split()[0] for line in cleaned]

# get list of all SExtractor measurement parameters
lines_bytes = check_output(f"{SE_EXECUTABLE} -dp", shell=True)
lines = lines_bytes.decode("utf-8").split("\n")
cleaned = filter(lambda line: len(line) > 1, lines)
PARAM_NAMES = [line.split()[0][1:] for line in cleaned]
DEFAULT_PARAMS = np.loadtxt(DEFAULT_PARAM_FILE, dtype=str).tolist()

# default non-standard options
DEFAULT_OPTIONS = dict(
    VERBOSE_TYPE="QUIET",
    PARAMETERS_NAME=DEFAULT_PARAM_FILE,
    FILTER_NAME=DEFAULT_CONV,
)


def run(
    path_or_pixels: PathOrPixels,
    config_path: Optional[PathLike] = DEFAULT_CONFIG_PATH,
    catalog_path: Optional[PathLike] = None,
    tmp_path: PathLike = "/tmp",
    run_label: Optional[str] = None,
    header: Optional[fits.Header] = None,
    extra_params: Optional[Union[str, List[str]]] = None,
    **sextractor_options,
) -> Table:
    """Run Source Extractor.

    Args:
        path_or_pixels: _description_
        catalog_path: _description_. Defaults to None.
        config_path: _description_. Defaults to None.
        tmp_path: _description_. Defaults to "/tmp".
        run_label: _description_. Defaults to None.
        header: _description_. Defaults to None.
        extra_params: _description_. Defaults to None.
        **sextractor_options: Any SExtractor configuration option passed as a keyword.

    Returns:
        _description_


    Notes:
        You must have SExtractor installed to run this function.

        Default measured parameters (add extra parameters using the extra_params argument):
            X_IMAGE
            Y_IMAGE
            FLUX_AUTO
            FLUX_RADIUS
            FWHM_IMAGE
            A_IMAGE
            B_IMAGE
            THETA_IMAGE
            ISOAREA_IMAGE
            FLAGS

    Example:
        # run like this
        cat = sextractor.run(image_file_name, FILTER='N', DETECT_THRESH=10)

        # or like this
        options = dict(FILTER='N', DETECT_THRESH=10)
        cat = sextractor.run(image_file_name, **options)

        # extra_params can be given in the following formats
        # (it is case-insensitive)
        extra_params = 'FLUX_RADIUS'
        extra_params = 'FLUX_RADIUS,ELLIPTICITY'
        extra_params = 'FLUX_RADIUS, ELLIPTICITY'
        extra_params = ['FLUX_RADIUS', 'ELLIPTICITY']

        cat = sextractor.run(image_file_name, extra_params=extra_params)
    """
    image_path, created_tmp = utils.create_temp_fits_file_if_necessary(
        path_or_pixels,
        tmp_path=tmp_path,
        run_label=run_label,
        header=header,
    )

    logger.debug(f"Running SExtractor on {image_path}")

    # update config options
    final_options = DEFAULT_OPTIONS.copy()
    for k, v in sextractor_options.items():
        k = k.upper()
        if k not in OPTION_NAMES:
            logger.warning(
                f"{k} is not a valid SExtractor option -> we will ignore it!"
            )
        else:
            logger.debug(f"SExtractor config update: {k} = {v}")
            final_options[k] = v

    # create catalog path if necessary
    if catalog_path is not None:
        cat_name = catalog_path
        save_cat = True
    else:
        label = "" if run_label is None else "_" + run_label
        cat_name = Path(tmp_path) / "se{}.cat".format(label)
        save_cat = False

    # create and write param file if extra params were given
    param_file_name = None
    if extra_params is not None:
        extra_params_list = utils.list_of_strings(extra_params)
        params = DEFAULT_PARAMS.copy()
        for par in extra_params_list:
            p = par.upper()
            _p = p[: p.find("(")] if p.find("(") > 0 else p
            if _p not in PARAM_NAMES:
                logger.warning(
                    f"{p} is not a valid SExtractor param -> we will ignore it!"
                )
            elif _p in DEFAULT_PARAMS:
                logger.warning(f"{p} is a default parameter -> No need to add it!")
            else:
                params.append(p)
        if len(params) > len(DEFAULT_PARAMS):
            label = "" if run_label is None else "_" + run_label
            param_file_name = Path(tmp_path) / "params{label}.se"
            with open(param_file_name, "w") as f:
                logger.debug(f"writing parameter file to {param_file_name}")
                f.write("\n".join(params))
            final_options["PARAMETERS_NAME"] = param_file_name

    # build shell command
    cmd = f"{SE_EXECUTABLE} -c {config_path} {image_path} -CATALOG_NAME {cat_name}"
    for k, v in final_options.items():
        cmd += f" -{k.upper()} {v}"
    if param_file_name is not None:
        cmd += f" -PARAMETERS_NAME {param_file_name}"

    # run it
    logger.debug(f">> {cmd}")
    call(cmd, shell=True)

    # convert detection catalog into astropy table
    if "CATALOG_TYPE" not in final_options.keys():
        catalog = ascii.read(cat_name)
    elif final_options["CATALOG_TYPE"] == "ASCII_HEAD":
        catalog = ascii.read(cat_name)
    else:
        raise errors.SEWError(
            f"{final_options['CATALOG_TYPE']} is an invalid CATALOG_TYPE"
        )

    # clean up the mess of temporary files
    if created_tmp:
        logger.debug(f"deleting temporary file {image_path}")
        os.remove(image_path)
    if param_file_name is not None:
        logger.debug(f"deleting temporary file {param_file_name}")
        os.remove(param_file_name)
    if not save_cat:
        logger.debug(f"deleting temporary file {cat_name}")
        os.remove(cat_name)

    return catalog
