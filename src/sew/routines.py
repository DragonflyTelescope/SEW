"""Pre-cooked source detection routines."""
from astropy.table import Table

from . import sextractor
from .log import load_logger

logger = load_logger()

DEFAULT_STAR_QUERY = "FLAGS == 0 and ISOAREA_IMAGE > 10 and ISOAREA_IMAGE < 100 \
                      and FWHM_IMAGE > 1 and FWHM_IMAGE < 5"


__all__ = ["extract_bright_stars"]


def extract_bright_stars(path_or_pixels, query=DEFAULT_STAR_QUERY, **kwargs) -> Table:
    """_summary_

    Args:
        path_or_pixels: _description_
        query: _description_. Defaults to DEFAULT_STAR_QUERY.

    Returns:
        _description_
    """
    logger.debug("Running SExtractor to extract bright stars.")
    cat = sextractor.run(
        path_or_pixels,
        DETECT_MINAREA=kwargs.pop("DETECT_MINAREA", 5),
        DETECT_THRESH=kwargs.pop("DETECT_THRESH", 10),
        ANALYSIS_THRESH=1.5,
        **kwargs
    )
    cat = cat[cat.to_pandas().query(query).index.values]
    return cat
