import os
import numpy as np
from subprocess import call, check_output, CalledProcessError
from astropy.io import ascii, fits
from .log import logger
from . import package_dir, utils
EXECUTABLE = os.getenv('SE_EXE')


__all__ = [
    'run',
    'default_options',
    'input_file_path',
    'kernel_path',
    'default_params',
    'all_param_names',
    'EXECUTABLE'
]

# default SExtractor paths and files
input_file_path = os.path.join(package_dir, 'io')
kernel_path = os.path.join(input_file_path, 'kernels')
default_nnw = os.path.join(input_file_path, 'default.nnw')
default_config = os.path.join(input_file_path, 'default.config')
default_param_file = os.path.join(input_file_path, 'default.param')
default_conv = os.path.join(kernel_path, 'default.conv')


# get list of all config options
lines = check_output(f'{EXECUTABLE} -dd', shell=True)
lines = lines.decode('utf-8').split('\n')
cleaned = filter(lambda l: l.strip()[0] != '#',
          filter(lambda l: len(l) > 1, lines))
all_option_names = [l.split()[0] for l in cleaned]


# get list of all SExtractor measurement parameters
lines = check_output(f'{EXECUTABLE} -dp', shell=True)
lines = lines.decode('utf-8').split('\n')
cleaned = filter(lambda l: len(l) > 1, lines)
all_param_names = [l.split()[0][1:] for l in cleaned]
default_params = np.loadtxt(default_param_file, dtype=str).tolist()


# default non-standard options
default_options = dict(
    BACK_SIZE=128,
    GAIN=0.37,
    PIXEL_SCALE=2.85,
    SEEING_FWHM=2.5,
    VERBOSE_TYPE='QUIET',
    MEMORY_BUFSIZE=4096,
    MEMORY_OBJSTACK=30000,
    MEMORY_PIXSTACK=3000000,
    PARAMETERS_NAME=default_param_file,
    FILTER_NAME=default_conv
)


def run(path_or_pixels, catalog_path=None, config_path=default_config,
        tmp_path='/tmp', run_label=None, header=None,
        extra_params=None, **sextractor_options):
    """
    Run SExtractor.

    Parameters
    ----------
    path_or_pixels : str
        Full path file name to the fits image -- or -- The image pixels as
        a numpy array. In the latter case, a temporary fits file will be
        written in tmp_path with an optional run_label to make the temp file
        name unique (this is useful if you are running in parallel).
    catalog_path : str (optional)
        If not None, the full path file name of the output catalog. If None,
        a temporary catalog will be written in tmp_path with a
        run_label (if it's not None).
    config_path : str (optional)
        Full path SExtractor configuration file name.
    tmp_path : str (optional)
        Path for temporary fits files if you pass image pixels to
        this function.
    run_label : str (optional)
        A unique label for the temporary files.
    header : astropy.io.fits.Header (optional)
        Image header if you pass image pixels to this function and want
        SExtractor to have the header information.
    extra_params: str or list-like (optional)
        Additional SE measurement parameters. The default parameters, which
        are always in included, are the following:
        X_IMAGE, Y_IMAGE, FLUX_AUTO, FLUX_RADIUS, FWHM_IMAGE, A_IMAGE,
        B_IMAGE, THETA_IMAGE, FLAGS
    **sextractor_options: Keyword arguments
        Any SExtractor configuration option.

    Returns
    -------
    catalog : astropy.Table
        The SExtractor source catalog.

    Notes
    -----
    You must have SExtractor installed to run this function.

    The 'sextractor_options' keyword arguments may be passed one at a time or
    as a dictionary, exactly the same as **kwargs.

    Example:

    # like this
    cat = sextractor.run(image_fn, cat_fn, FILTER='N', DETECT_THRESH=10)

    # or like this
    options = dict(FILTER='N', DETECT_THRESH=10)
    cat = sextractor.run(image_fn, cat_fn, **options)

    # extra_params can be given in the following formats
    extra_params = 'FLUX_RADIUS'
    extra_params = 'FLUX_RADIUS,ELLIPTICITY'
    extra_params = 'FLUX_RADIUS, ELLIPTICITY'
    extra_params = ['FLUX_RADIUS', 'ELLIPTICITY']
    # (it is case-insensitive)
    """
    image_path, created_tmp = utils.temp_fits_file(path_or_pixels,
                                                   tmp_path=tmp_path,
                                                   run_label=run_label,
                                                   prefix='se_tmp',
                                                   header=header)

    logger.debug('Running SExtractor on ' + image_path)

    # update config options
    final_options = default_options.copy()
    for k, v in sextractor_options.items():
        k = k.upper()
        if k not in all_option_names:
            msg = '{} is not a valid SExtractor option -> we will ignore it!'
            logger.warning(msg.format(k))
        else:
            logger.debug('SExtractor config update: {} = {}'.format(k, v))
            final_options[k] = v

    # create catalog path if necessary
    if catalog_path is not None:
        cat_name = catalog_path
        save_cat = True
    else:
        label = '' if run_label is None else '_' + run_label
        cat_name = os.path.join(tmp_path, 'se{}.cat'.format(label))
        save_cat = False

    # create and write param file if extra params were given
    param_fn = None
    if extra_params is not None:
        extra_params = utils.list_of_strings(extra_params)
        params = default_params.copy()
        for par in extra_params:
            p = par.upper()
            _p = p[:p.find('(')] if p.find('(') > 0 else p
            if _p not in all_param_names:
                msg = '{} is not a valid SExtractor param -> we will ignore it!'
                logger.warning(msg.format(p))
            elif _p in default_params:
                msg = '{} is a default parameter -> No need to add it!'
                logger.warning(msg.format(p))
            else:
                params.append(p)
        if len(params) > len(default_params):
            label = '' if run_label is None else '_' + run_label
            param_fn = os.path.join(tmp_path, 'params{}.se'.format(label))
            with open(param_fn, 'w') as f:
                logger.debug('Writing parameter file to ' + param_fn)
                print('\n'.join(params), file=f)
        final_options['PARAMETERS_NAME'] = param_fn

    # build shell command
    cmd = EXECUTABLE + ' -c {} {}'.format(config_path, image_path)
    cmd += ' -CATALOG_NAME ' + cat_name
    for k, v in final_options.items():
        cmd += ' -{} {}'.format(k.upper(), v)
    if param_fn is not None:
        cmd += ' -PARAMETERS_NAME ' + param_fn

    # run it
    logger.debug(f'>> {cmd}')
    call(cmd, shell=True)

    if 'CATALOG_TYPE' not in final_options.keys():
        catalog = ascii.read(cat_name)
    elif final_options['CATALOG_TYPE'] == 'ASCII_HEAD':
        catalog = ascii.read(cat_name)
    else:
        catalog = None

    if created_tmp:
        logger.debug('Deleting temporary file ' + image_path)
        os.remove(image_path)
    if param_fn is not None:
        logger.debug('Deleting temporary file ' + param_fn)
        os.remove(param_fn)
    if not save_cat:
        logger.debug('Deleting temporary file ' + cat_name)
        os.remove(cat_name)

    return catalog
