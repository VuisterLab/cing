# usage: python setup.py build_ext --inplace
# TODO automate this from CING setup script.

# adapted from http://docs.cython.org/src/tutorial/cython_tutorial.html

from distutils.core import setup
from Cython.Build import cythonize 

setup(
  ext_modules = cythonize("superpose.pyx")
)
