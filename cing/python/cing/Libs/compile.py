# usage: python compile.py build_ext --inplace

from distutils.core import setup
#from distutils.extension import Extension
from Pyrex.Distutils.extension import Extension #@UnresolvedImport
from Pyrex.Distutils import build_ext #@UnresolvedImport

setup(
  name = 'Superpose',
  ext_modules=[ 
    Extension("vector",       ["vector.pyx"]),
    Extension("matrix",       ["matrix.pyx"])
    ],
  cmdclass = {'build_ext': build_ext}
)
