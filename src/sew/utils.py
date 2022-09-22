from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

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
    header: Optional[fits.Header] = None,
    run_label: Optional[str] = None,
    tmp_path: PathLike = "/tmp",
) -> Tuple[Path, bool]:
    """Helper function for optionally writing fits files for input to SExtractor.

    Note:
        This purpose of this function is to enable the user to pass either a
        path or pixels to the sextractor.run function. If pixels are given,
        a temporary file is created (as required for SExtractor input). If a
        Path is given, it is simply returned and no temporary file is created.

    Args:
        path_or_pixels: Path to fits file or its pixels in a numpy array.
        header: Astropy fits header object. If not None, this header will take precedent.
        run_label: Unique file label for this function call (useful when running in parallel).
        tmp_path: Temporary path for files created by SExtractor. Defaults to "/tmp".

    Returns:
        Path object pointing to the fits file that contains the pixels and a boolean
        that is True if a temporary file was created.
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


def is_list_like(check: Any) -> bool:
    """Return True if an object is list-like (i.e., list, ndarray, or tuple)."""
    return isinstance(check, (list, np.ndarray, tuple))


def list_of_strings(str_or_list: Union[str, List[str]]) -> List[str]:
    """Return a list of strings when given a variety of inputs.

    Args:
        str_or_list: Single string of comma-separated values or a list of strings.
            If it's the latter, then the input list is simply returned.

    Returns:
        A list of strings, where each element represents a single piece of
        information (e.g., a parameter or flag name)

    Examples:
                INPUT                                 OUTPUT
        'flag_1,flag_2,flag_3'         --> ['flag_1', 'flag_2', 'flag_3']
        'flag_1, flag_2, flag_3'       --> ['flag_1', 'flag_2', 'flag_3']
        ['flag_1', 'flag_2', 'flag_3'] --> ['flag_1', 'flag_2', 'flag_3']
    """
    if is_list_like(str_or_list):
        ls_str = list(str_or_list)
    elif isinstance(str_or_list, str):
        ls_str = str_or_list.replace(" ", "").split(",")
    else:
        Exception(f"{str_or_list} is not correct type for list of str")
    return ls_str


def make_keys_uppercase(dictionary: dict) -> dict:
    """Make all key names in dictionary uppercase.

    Args:
        dictionary: Make keys of this dict uppercase.

    Returns:
        A new dictionary (i.e., the input dictionary is not modified) with
        all uppercase keys.
    """
    d = {}
    for k, v in dictionary.items():
        d[k.upper()] = v
    return d
