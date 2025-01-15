# -*- coding: utf-8 -*-
"""
    Setup file for tsfresh.
    Use setup.cfg to configure your project.

    Part of this file was generated with PyScaffold 3.2.3.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
import sys

import numpy as np
from Cython.Build import cythonize
from pkg_resources import VersionConflict, require
from setuptools import Extension, setup

try:
    require("setuptools>=38.3")
except VersionConflict:
    print("Error: version of setuptools is too old (<38.3)!")
    sys.exit(1)

extensions = [
    Extension(
        name="tsfresh.feature_extraction.cython_ext.approx_entropy",
        sources=["tsfresh/feature_extraction/cython_ext/approx_entropy.pyx"],
        extra_compile_args=["-O3", "-funroll-loops", "-flto"],
        include_dirs=[np.get_include()],
    ),
]

if __name__ == "__main__":
    setup(
        use_pyscaffold=True,
        ext_modules=cythonize(extensions),
        include_dirs=[np.get_include()],
    )
