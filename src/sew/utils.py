import numpy as np
from astropy.io import fits


__all__ = ['is_list_like', 'list_of_strings', 'temp_fits_file']


def is_list_like(check):
    """
    Check if an object is list-like (i.e., list, ndarray, or tuple).
    """
    return isinstance(check, (list, np.ndarray, tuple))


def list_of_strings(str_or_list):
    """
    Return a list of strings from a single string of comma-separated values.

    Parameters
    ----------
    str_or_list : str or list-like
        Single string of comma-separated values or a list of strings. If it's
        the latter, then the inpits list is simply returned.

    Examples
    --------

            INPUT                                 OUTPUT
    'flag_1,flag_2,flag_3'         --> ['flag_1', 'flag_2', 'flag_3']
    'flag_1, flag_2, flag_3'       --> ['flag_1', 'flag_2', 'flag_3']
    ['flag_1', 'flag_2', 'flag_3'] --> ['flag_1', 'flag_2', 'flag_3']
    """
    if is_list_like(str_or_list):
        ls_str = str_or_list
    elif type(str_or_list) == str:
        ls_str = str_or_list.replace(' ', '').split(',')
    else:
        Exception('{} is not correct type for list of str'.format(str_or_list))
    return ls_str


def temp_fits_file(path_or_pixels, tmp_path='/tmp', run_label=None,
                   prefix='tmp',  header=None):
    """
    Save temporary fits files if necessary. If a numpy array is given as input,
    the temporary file isn't necessary.
    """
    is_str = type(path_or_pixels) == str or type(path_or_pixels) == np.str_
    if is_str and header is None:
        path = path_or_pixels
        created_tmp = False
    else:
        if is_str:
            path_or_pixels = fits.getdata(path_or_pixels)
        label = '' if run_label is None else '_' + run_label
        fn = '{}{}.fits'.format(prefix, label)
        path = os.path.join(tmp_path, fn)
        logger.debug('Writing temporary fits file {}'.format(path))
        fits.writeto(path, path_or_pixels, header=header, overwrite=True)
        created_tmp = True
    return path, created_tmp
