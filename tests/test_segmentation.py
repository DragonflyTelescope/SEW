import numpy as np
from astropy.io import fits

import sew


def test_create_sextractor_object_mask_dilatation(dwarf_path):
    """Test that a SExtractor object mask is created and dilate_npix works as expected."""
    mask_1 = sew.segmentation.create_sextractor_object_mask(dwarf_path, dilate_npix=1)
    mask_10 = sew.segmentation.create_sextractor_object_mask(dwarf_path, dilate_npix=10)
    assert mask_1.sum() < mask_10.sum()


def test_create_sextractor_object_mask_mask_file(dwarf_path, tmp_path):
    """Test that a SExtractor object mask is created and saved to the given file."""
    mask_file_name = tmp_path / "mask.fits"
    mask = sew.segmentation.create_sextractor_object_mask(
        dwarf_path, mask_file_name=mask_file_name, dilate_npix=0
    )
    assert mask_file_name.is_file()
    assert np.allclose(mask.astype(int), (fits.getdata(mask_file_name) > 0).astype(int))
