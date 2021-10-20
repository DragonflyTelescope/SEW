import os, sys
import builtins
from setuptools import setup, find_packages
sys.path.append('src')


def readme():
    with open("README.rst") as f:
        return f.read()


# HACK: fetch version
builtins.__SRCEX_SETUP__ = True
import srcex
version = srcex.__version__


# Publish the library to PyPI.
if "publish" in sys.argv[-1]:
    os.system("python setup.py sdist bdist_wheel")
    os.system(f"python3 -m twine upload dist/*{version}*")
    sys.exit()


# Push a new tag to GitHub.
if "tag" in sys.argv:
    os.system("git tag -a v{0} -m 'version {0}'".format(version))
    os.system("git push --tags")
    sys.exit()


setup(
    name='srcex',
    version=version,
    description='An easy peasy Source Extractor wrapper.',
    long_description=readme(),
    author='Johnny Greco',
    author_email='jgreco.astro@gmail.com',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    url='https://github.com/DragonflyTelescope/SrcEx',
    install_requires=[
        'numpy>=1.17',
        'scipy>=1',
        'astropy>=4'
     ],
     classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Astronomy",
      ],
    python_requires='>=3.6',
)
