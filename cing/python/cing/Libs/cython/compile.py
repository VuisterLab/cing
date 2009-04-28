# usage: python compile.py build_ext --inplace
# TODO automate this from CING setup script.
from distutils.core import setup
#from Cython.Distutils.extension import Extension # absent in fink install of cython-py25_0.9.6.10b-1_darwin-i386.deb
from distutils.extension import Extension # absent in fink install of cython-py25_0.9.6.10b-1_darwin-i386.deb
from Cython.Distutils.build_ext import build_ext #@UnresolvedImport


setup(
  name = 'Superpose',
  ext_modules=[
    Extension("superpose",       ["superpose.pyx"])
    ],
  cmdclass = {'build_ext': build_ext}
)
