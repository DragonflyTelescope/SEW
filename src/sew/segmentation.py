import os
from pathlib import Path
from typing import Dict, Optional

import numpy as np
from astropy.io import fits
from astropy.table import Table
from scipy import ndimage

from . import sextractor
from .log import load_logger
from .utils import ListLike, make_keys_uppercase, PathLike, PathOrPixels

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
    """Create an object mask using SExtractor's OBJECTS CHECKIMAGE.

    Args:
        path_or_pixels: Path to fits file or its pixels in a numpy array.
        tmp_path: Temporary path for files created by SExtractor.
        run_label: Unique file label for this function call (useful when running in parallel).
        mask_file_name: Name of OBJECTS CHECKIMAGE file written by SExtractor. If None,
            a generic name (plus the optional run label) will be used.
        dilate_npix: Apply grey dilation with structuring element of dimension
            (dilate_npix, dilate_npix).
        **sextractor_options: Any SExtractor configuration option passed as a keyword.

    Returns:
        The dilated object mask as a numpy array.
    """

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
        **make_keys_uppercase(sextractor_options),
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
) -> np.ndarray:
    """Create a model of the sky using SExtractor's BACKGROUND CHECKIMAGE.

    Args:
        path_or_pixels: Path to fits file or its pixels in a numpy array.
        run_label: Unique file label for this function call (useful when running in parallel).
        tmp_path: Temporary path for files created by SExtractor.
        sky_file_name: Name of BACKGROUND CHECKIMAGE file written by SExtractor. If None,
            a generic name (plus the optional run label) will be used.
        **sextractor_options: Any SExtractor configuration option passed as a keyword.

    Returns:
        The sky model as a numpy array.
    """

    if sky_file_name is not None:
        created_tmp = False
    else:
        label = "" if run_label is None else "_" + run_label
        sky_file_name = Path(tmp_path) / f"skymodel{label}.fits"
        created_tmp = True

    cfg = dict(
        CHECKIMAGE_TYPE="BACKGROUND",
        CHECKIMAGE_NAME=sky_file_name,
        tmp_path=tmp_path,
        run_label=run_label,
        **make_keys_uppercase(sextractor_options),
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
    """Make source map image based on the input catalog.

    The source map will have ones where there are detected sources and zeros
    everywhere else.

    Note:
        This function was written for double-star detection.

    Args:
        catalog: Catalog of sources with their image positions and fluxes.
        image_shape: Shape of the image from which the sources were detected.
        max_num_sources: Maximum number of sources to include in the source map.
            Sources will be sorted by flux and fainter sources will be dropped first.
        xy_flux_column_names: Names of the columns in the catalog. Must be a dictionary
            with values for keys = 'x', 'y', and 'flux'. For example:
            {'x': 'x_col', 'y': y_col', 'flux': 'flux_col'}.

    Returns:
        Source map with ones at the locations of sources from the input
        catalog and zeros everywhere else.
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
