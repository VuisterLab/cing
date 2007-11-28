"""
To be executed before the Test routines are called
"""
from cing import cingRoot

import os

cingDirTests       = os.path.join( cingRoot,            "Tests")
cingDirTestsData   = os.path.join( cingDirTests,        "data")
cingDirTestsTmp    = os.path.join( cingDirTestsData,    "tmp")


