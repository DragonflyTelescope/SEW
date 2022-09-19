import sew


def test_run_from_path(dwarf_path):
    """Test sextractor.run from an image path."""
    cat = sew.run(dwarf_path)
    assert len(cat) == 233


def test_run_from_pixels(dwarf_pixels):
    """Test sextractor.run from image pixels."""
    cat = sew.run(dwarf_pixels)
    assert len(cat) == 233


def test_run_add_config_options(dwarf_pixels):
    """Test sextractor config options are added via kwargs."""
    assert len(sew.run(dwarf_pixels, DETECT_THRESH=1)) > len(
        sew.run(dwarf_pixels, DETECT_THRESH=1000)
    )


def test_run_add_extra_parameters(dwarf_pixels):
    """Test sextractor measurement parameters are added using extra_params."""
    n_params_initial = len(sew.run(dwarf_pixels).colnames)
    extra_params = ["ISO0", "ISO1", "ISO2"]
    cat = sew.run(dwarf_pixels, extra_params=extra_params)
    assert len(cat.colnames) - n_params_initial == len(extra_params)
    for p in extra_params:
        assert p in cat.colnames
