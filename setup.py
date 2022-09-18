from setuptools import find_packages, setup

install_requires = [
    "astropy>=5.1",
    "numpy>=1.23.2",
    "scipy>=1.9.1",
]

linting_deps = [
    "black>=22.6.0",
    "flake8>=5.0.4",
    "mypy>=0.971",
    "isort>=5.10.1",
    "pre-commit>=2.20.0",
]

testing_deps = [
    "ipykernel>=6.15.2",
    "pytest>=7.1.2",
]

extras_require = {"dev": linting_deps + testing_deps}

setup(
    name="SEW",
    version="0.0.0",
    author="Johnny Greco",
    url="https://github.com/DragonflyTelescope/SEW",
    python_requires=">=3.8",
    description="A super simple wrapper for SExtractor.",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    package_data={"sew": ["input/*"]},
    install_requires=install_requires,
    extras_require=extras_require,
)
