__version__ = '0.0.1'

try:
    __SEW_SETUP__
except NameError:
    __SEW_SETUP__ = False

if not __SEW_SETUP__:
    import os
    src_dir = os.path.dirname(os.path.dirname(__file__))
    package_dir = os.path.join(src_dir, 'sew')
    from .sextractor import *
    from . import routines
    from . import segmentation

