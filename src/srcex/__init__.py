__version__ = '0.0.1'

try:
    __SRCEX_SETUP__
except NameError:
    __SRCEX_SETUP__ = False

if not __SRCEX_SETUP__:
    import os
    project_dir = os.path.dirname(os.path.dirname(__file__))
    package_dir = os.path.join(project_dir, 'srcex')
    package_data_dir = os.path.join(project_dir, 'data')
    from .sextractor import *
    from .routines import *
    from .segmentation import *

