# usage: python compile.py build_ext --inplace
# TODO automate this from CING setup script.
from distutils.core import setup
from Cython.Distutils.extension import Extension
from Cython.Distutils.build_ext import build_ext


setup(
  name = 'Superpose',
  ext_modules=[ 
    Extension("vector",       ["vector.pyx"]),
    Extension("matrix",       ["matrix.pyx"])
    ],
  cmdclass = {'build_ext': build_ext}
)
