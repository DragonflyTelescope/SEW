import os
from pathlib import Path
from typing import Dict, Optional

import numpy as np
from astropy.io import fits
from astropy.table import Table
from scipy import ndimage

from . import sextractor
from .log import load_logger
from .utils import ListLike, PathLike, PathOrPixels

__all__ = [
    "create_sextractor_object_mask",
    "create_sextractor_sky_model",
    "create_source_map",
]

logger = load_logger()
DEFAULT_XY_FLUX_NAMES = dict(x="X_IMAGE", y="Y_IMAGE", flux="FLUX_AUTO")


def create_sextractor_object_mask(
    path_or_pixels: PathOrPixels,
    tmp_path: PathLike = "/tmp",
    run_label: Optional[str] = None,
    mask_file_name: Optional[PathLike] = None,
    dilate_npix: int = 5,
    **sextractor_options,
) -> np.ndarray:

    if mask_file_name is not None:
        created_tmp = False
    else:
        label = "" if run_label is None else "_" + run_label
        mask_file_name = Path(tmp_path) / f"obj_msk{label}.fits"
        created_tmp = True

    cfg = dict(
        CHECKIMAGE_TYPE="OBJECTS",
        CHECKIMAGE_NAME=mask_file_name,
        tmp_path=tmp_path,
        run_label=run_label,
        **sextractor_options,
    )
    sextractor.run(path_or_pixels, **cfg)
    mask = fits.getdata(mask_file_name)

    if dilate_npix > 0:
        logger.debug(f"Dilating object mask with dilate_npix = {dilate_npix}")
        size = (dilate_npix, dilate_npix)
        mask = ndimage.morphology.grey_dilation(mask, size)

    mask = (mask > 0).astype(bool)

    if created_tmp:
        os.remove(mask_file_name)

    return mask


def create_sextractor_sky_model(
    path_or_pixels: PathOrPixels,
    run_label: Optional[str] = None,
    tmp_path: PathLike = "/tmp",
    sky_file_name: Optional[PathLike] = None,
    **sextractor_options,
):
    label = "" if run_label is None else "_" + run_label

    if sky_file_name is not None:
        created_tmp = False
    else:
        sky_file_name = Path(tmp_path) / f"skymodel{label}.fits"
        created_tmp = True

    options = {}
    for k, v in sextractor_options.items():
        options[k.upper()] = v

    cfg = dict(
        CHECKIMAGE_TYPE="BACKGROUND",
        CHECKIMAGE_NAME=sky_file_name,
        tmp_path=tmp_path,
        run_label=run_label,
        **options,
    )
    sextractor.run(path_or_pixels, **cfg)
    sky = fits.getdata(sky_file_name)

    if created_tmp:
        os.remove(sky_file_name)

    return sky


def create_source_map(
    catalog: Table,
    image_shape: ListLike,
    max_num_sources: int = 100_000,
    xy_flux_column_names: Optional[Dict[str, str]] = None,
):
    """
    Make source map image based on the input catalog with ones where there
    are detected sources and zeros everywhere else.

    Parameters
    ----------
    catalog : structured ndarray, astropy.table.Table, or pandas.DataFrame
        Catalog of sources with their image positions and fluxes.
    image_shape : list-like
        Shape of the image from which the sources were detected.
    max_num_sources : int (optional)
        Maximum number of sources to include in the source map.
    xy_flux_column_names : dict (optional)
        Names of the columns in the catalog. The name dictionary must have
        values for keys = x, y, and flux.

    Returns
    -------
    source_map : ndarray
        Source map with ones at the locations of sources from the input
        catalog and zeros at non-source pixels.

    Notes
    -----
    This function was written for double-star detection.
    """
    if xy_flux_column_names is None:
        xy_flux_column_names = DEFAULT_XY_FLUX_NAMES
    max_num_sources = int(max_num_sources)
    source_map = np.zeros(image_shape)
    flux = catalog[xy_flux_column_names["flux"]]
    flux_sort = np.argsort(-flux)
    x = np.array(catalog[xy_flux_column_names["x"]].astype(int))[flux_sort] - 1
    y = np.array(catalog[xy_flux_column_names["y"]].astype(int))[flux_sort] - 1
    source_map[y[:max_num_sources], x[:max_num_sources]] = 1
    return source_map
