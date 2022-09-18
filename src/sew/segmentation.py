import os

import numpy as np
from astropy.io import fits
from scipy import ndimage

from . import load_logger, sextractor

__all__ = ["sextractor_object_mask", "sextractor_sky_model", "create_source_map"]

DEFAULT_NAMES = dict(x="X_IMAGE", y="Y_IMAGE", flux="FLUX_AUTO")
logger = load_logger()


def sextractor_object_mask(
    path_or_pixels,
    tmp_path="/tmp",
    run_label=None,
    mask_fn=None,
    dilate_npix=5,
    dtype=bool,
    **sextractor_options,
):
    label = "" if run_label is None else "_" + run_label

    if mask_fn is not None:
        created_tmp = False
    else:
        mask_fn = os.path.join(tmp_path, f"obj_msk{label}.fits")
        created_tmp = True

    cfg = dict(
        CHECKIMAGE_TYPE="OBJECTS",
        CHECKIMAGE_NAME=mask_fn,
        tmp_path=tmp_path,
        run_label=run_label,
    )
    cfg.update(sextractor_options)
    sextractor.run(path_or_pixels, **cfg)
    mask = fits.getdata(mask_fn)

    if dilate_npix > 0:
        logger.debug(f"Dilating object mask with dilate_npix = {dilate_npix}")
        size = (dilate_npix, dilate_npix)
        mask = ndimage.morphology.grey_dilation(mask, size)

    mask = (mask > 0).astype(dtype)

    if created_tmp:
        os.remove(mask_fn)

    return mask


def sextractor_sky_model(
    path_or_pixels, run_label=None, tmp_path="/tmp", sky_fn=None, **sextractor_options
):
    label = "" if run_label is None else "_" + run_label

    if sky_fn is not None:
        created_tmp = False
    else:
        sky_fn = os.path.join(tmp_path, f"skymodel{label}.fits")
        created_tmp = True

    options = {}
    for k, v in sextractor_options.items():
        options[k.upper()] = v

    cfg = dict(
        CHECKIMAGE_TYPE="BACKGROUND",
        CHECKIMAGE_NAME=sky_fn,
        tmp_path=tmp_path,
        run_label=run_label,
    )
    cfg["DETECT_THRESH"] = options.pop("DETECT_THRESH", 2)
    cfg.update(options)

    sextractor.run(path_or_pixels, **cfg)
    sky = fits.getdata(sky_fn)

    if created_tmp:
        os.remove(sky_fn)

    return sky


def create_source_map(catalog, image_shape, max_num_sources=1e5, names=DEFAULT_NAMES):
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
    names : dict (optional)
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
    max_num_sources = int(max_num_sources)
    source_map = np.zeros(image_shape)
    flux = catalog[names["flux"]]
    flux_sort = np.argsort(-flux)
    x = np.array(catalog[names["x"]].astype(int))[flux_sort] - 1
    y = np.array(catalog[names["y"]].astype(int))[flux_sort] - 1
    source_map[y[:max_num_sources], x[:max_num_sources]] = 1
    return source_map
