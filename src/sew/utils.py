from pathlib import Path
from typing import Optional, Tuple, Union

import numpy as np
from astropy.io import fits

from . import errors
from .log import load_logger

__all__ = [
    "create_temp_fits_file_if_necessary",
    "is_list_like",
    "list_of_strings",
    "ListLike",
    "make_keys_uppercase",
    "PathLike",
    "PathOrPixels",
]

logger = load_logger()
ListLike = Union[list, tuple, np.ndarray]
PathLike = Union[Path, str, np.str_]
PathOrPixels = Union[PathLike, np.ndarray]


def create_temp_fits_file_if_necessary(
    path_or_pixels: PathOrPixels,
    tmp_path: PathLike = "/tmp",
    run_label: Optional[str] = None,
    header: Optional[fits.Header] = None,
) -> Tuple[Path, bool]:
    """_summary_

    Args:
        path_or_pixels: Path to fits file or its pixels in a numpy array.
        tmp_path: _description_. Defaults to "/tmp".
        run_label: _description_. Defaults to None.
        header: _description_. Defaults to None.

    Raises:
        errors.InvalidPathOrPixels: _description_

    Returns:
        _description_
    """
    is_path = isinstance(path_or_pixels, (Path, str, np.str_))
    if is_path and header is None:
        created_temp_file = False
        fits_file_path = Path(str(path_or_pixels))
    else:
        pixels: np.ndarray
        created_temp_file = True
        if is_path:
            pixels = fits.getdata(path_or_pixels)
        elif isinstance(path_or_pixels, np.ndarray):
            pixels = path_or_pixels
        else:
            raise errors.InvalidPathOrPixels(
                f"{type(path_or_pixels)} is not a valid path / numpy array"
            )
        label = "" if run_label is None else "_" + run_label
        fits_file_path = Path(tmp_path) / f"se_temp{label}.fits"
        logger.debug(f"Writing temporary fits file {fits_file_path}")
        fits.writeto(fits_file_path, pixels, header=header, overwrite=True)
    return fits_file_path, created_temp_file


def is_list_like(check):
    """Check if an object is list-like (i.e., list, ndarray, or tuple)."""
    return isinstance(check, (list, np.ndarray, tuple))


def list_of_strings(str_or_list):
    """
    Return a list of strings from a single string of comma-separated values.

    Parameters
    ----------
    str_or_list : str or list-like
        Single string of comma-separated values or a list of strings. If it's
        the latter, then the inputs list is simply returned.

    Examples
    --------

            INPUT                                 OUTPUT
    'flag_1,flag_2,flag_3'         --> ['flag_1', 'flag_2', 'flag_3']
    'flag_1, flag_2, flag_3'       --> ['flag_1', 'flag_2', 'flag_3']
    ['flag_1', 'flag_2', 'flag_3'] --> ['flag_1', 'flag_2', 'flag_3']
    """
    if is_list_like(str_or_list):
        ls_str = str_or_list
    elif type(str_or_list) == str:
        ls_str = str_or_list.replace(" ", "").split(",")
    else:
        Exception("{} is not correct type for list of str".format(str_or_list))
    return ls_str


def make_keys_uppercase(dictionary: dict) -> dict:
    d = {}
    for k, v in dictionary.items():
        d[k.upper()] = v
    return d
