"script to save NTdb to convention"
from cing import cingPythonCingDir
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.database import NTdb
from cing.core.database import saveToSML

cing.verbosity = cing.verbosityDebug

if __name__ == '__main__':
    if 1: # DEFAULT: 1 disable only when needed.
        nTwarning("Don't execute this script %s by accident. It damages CING." % getCallerFileName())
        sys.exit(1)
    # end if
    
    convention = INTERNAL_1
    
    rootPath = os.path.realpath(os.path.join(cingPythonCingDir, 'Database' , convention) )
    if not os.path.exists( rootPath ):
        os.makedirs(  rootPath )
    saveToSML( NTdb, rootPath, convention )

