import pytest
from astropy.io import fits

from sew import REPO_PATH


@pytest.fixture
def dwarf_path():
    return REPO_PATH / "tests" / "data" / "img-cutout-i.fits"


@pytest.fixture
def dwarf_pixels(dwarf_path):
    return fits.getdata(dwarf_path)
