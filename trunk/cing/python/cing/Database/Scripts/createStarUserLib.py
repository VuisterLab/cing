"""
Unit test execute as:
python $CINGROOT/python/cing/Database/Scripts/createStarUserLib.py
"""
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.database import NTdb
from cing.core.database import isHeavy

cing.verbosity = cing.verbosityDebug

def createStarUserLib():
    if 0:
        for resDef in NTdb:
            for dihedral in resDef.dihedrals:
                NTmessage('%-4s %-10s' % (resDef.name, dihedral.name))
    # end if
    
    # For completeness lib.
    if 1:
        for resDef in NTdb:
            for atomDef in resDef.atoms:
                msg = '%-4s %-10s' % (resDef.name, atomDef.name)
    #            NTdebug("Looking at: " + msg)
                if not isHeavy(atomDef):
    #                NTdebug("Skipping: " + msg)      
                    continue  
                NTmessage(msg)
            # end for
        # end for
    # end if
# end def

if __name__ == '__main__':
    createStarUserLib()        
        