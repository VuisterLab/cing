#@PydevCodeAnalysisIgnore
from cing.core.database import saveToSML
from cing import *
import os

# script to save NTdb to convention
convention = INTERNAL_1

rootPath = os.path.realpath(os.path.join(cingPythonCingDir, 'Database' , convention) )
if not os.path.exists( rootPath ):
	os.makedirs(  rootPath )
saveToSML( NTdb, rootPath, convention )

