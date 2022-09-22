# 🪡 Source Extractor Wrapper (SEW)

[![tests](https://github.com/DragonflyTelescope/SEW/actions/workflows/tests.yml/badge.svg)](https://github.com/DragonflyTelescope/SEW/actions/workflows/tests.yml)

# Overview

`SEW` provides a simple user interface for running Source Extractor from python.

# Basic Usage

`SEW` seamlessly works with both `numpy` arrays and fits files, which is
Source Extractor's required input format.

```python
import sew

image = function_that_returns_image_as_numpy_array()

catalog = sew.run(image)
```

The Source Extractor catalog is returned as an astropy `Table` object.

If instead you have a fits file path, the function call looks identical:

```python
catalog = sew.run(path_to_fits_file)
```

You can specify any Source Extractor configuration parameter as a keyword in the `run` function:

```python
catalog = sew.run(path_to_fits_file, DETECT_THRESH=3, MAG_ZEROPOINT=27)
```

By default, a small number of measurement parameters are returned in the catalog:

```
    X_IMAGE
    Y_IMAGE
    FLUX_AUTO
    FLUX_RADIUS
    FWHM_IMAGE
    A_IMAGE
    B_IMAGE
    THETA_IMAGE
    ISOAREA_IMAGE
    FLAGS
```

To add additional measurement parameters, use the `extra_params` keyword:

```python
catalog = sew.run(path_to_fits_file, extra_params=["ISO0", "ISO1", "ISO2"])
```

# Installation

### 🐍 Create an environment (Optional)

If you don't have one already, create a python environment for `SEW`. Here, we'll use `conda` to create
a new development environment:

```shell
conda create -n sew-env python=3.8
```

Don't forget to activate the environment:

```shell
conda activate sew-env
```

### 🐑 🐑 Clone this repository

Using SSH:

```shell
git clone git@github.com:DragonflyTelescope/SEW.git
```

or

Using HTTPS:

```shell
git clone https://github.com/DragonflyTelescope/SEW.git
```

### 💿 Install SEW and its dependencies

Install the package using `pip`:

```shell
cd sew
python -m pip install .
```

This will install `SEW` and the dependencies listed in `setup.py`.

If you plan to develop the package, `pip` install in editable mode with the `[dev]` option:

```shell
python -m pip install -e '.[dev]'
```

In addition to the main package dependencies, this will install extra packages that are used
for development (e.g., `black` and `pytest`).

### 🌌 Source Extractor

Now comes the fun part – installing [Source Extractor](https://sextractor.readthedocs.io/en/latest/Installing.html)!

Assuming you have Source Extractor installed, you must create an environment variable called `SE_EXECUTABLE` that points
to the SExtractor executable.

For example, if you are running `bash` and the executable `sextractor` is in your path, you can append your
`.bashrc` file like this:

```shell
echo 'export SE_EXECUTABLE="sextractor"' >> ~/.bashrc
```

Be sure to either open a new terminal or source your `.bashrc` file to save the environment variable.

### 🚀 Let's Go!

If all the above steps worked without any errors, you should be ready to SEW it up 🪡!
