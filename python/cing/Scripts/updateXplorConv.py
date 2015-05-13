'''
Created on 8 Jan 2013

@author: wgt

script to update xplor N-terminal and C-terminal name conventions

'''
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

    convention = 'INTERNAL_1'

    for rdef in NTdb.residuesWithProperties('protein'):
        nTdebug("Xplor N-terminal and C-terminal atom name translations changed for %s",rdef)
        for name1, namex in [('H1','HT1'), ('H2','HT2'), ('H3','HT3'), ('OXT','OT2'), ('O','O,OT1')]:
            if name1 in rdef:
                rdef[name1].nameDict['XPLOR'] = namex
            #end if
        #end for
    #end for

    # save the new versions
    rootPath = os.path.realpath(os.path.join(cingPythonCingDir, 'Database' , convention) )
    saveToSML( NTdb, rootPath, convention )
