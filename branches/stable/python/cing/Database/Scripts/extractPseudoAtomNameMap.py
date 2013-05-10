'''
Created on Feb 28, 2011
$CINGROOT/python/cing/Database/Scripts/extractPseudoAtomNameMap.py
@author: jd
'''

from cing import NTdb
from cing.core.constants import * #@UnusedWildImport

print 'mapCcpn2IupacPseudo = {\n'
for resd in NTdb:
    for atomd in resd.allAtomDefs():
        if atomd.type == 'PSEUD':
#            print resd, atomd
            if not atomd.nameDict.has_key('CCPN'):
#                print "skipping ", atomd
                continue
            print '"%s,%s": "%s",' % (resd.name, atomd.nameDict['CCPN'], atomd.name)