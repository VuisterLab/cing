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
                nTmessage('%-4s %-10s' % (resDef.name, dihedral.name))
    # end if
    if 1: # DEFAULT 1
        for resDef in NTdb:
            NTmessageNoEOL("('%s')," % resDef.name)
    # end if
    
    # For completeness lib.
    if 0: # DEFAULT 0
        for resDef in NTdb:
#            if resDef.name != 'HIS':
#                continue
            for atomDef in resDef.atoms:
                cyana1AtomName = getDeepByKeysOrAttributes(atomDef.nameDict, CYANA) 
                cyana2AtomName = getDeepByKeysOrAttributes(atomDef.nameDict, CYANA2)
                if cyana1AtomName == cyana2AtomName:
                    continue
                msg = '%-4s %-10s %-10s %-10s' % (resDef.name, atomDef.name, cyana1AtomName, cyana2AtomName)
                nTdebug("Difference at: " + msg)
#                if not isHeavy(atomDef):
#    #                nTdebug("Skipping: " + msg)      
#                    continue
#                nTmessage(msg)
            # end for
        # end for
    # end if
# end def

if __name__ == '__main__':
    createStarUserLib()        
        