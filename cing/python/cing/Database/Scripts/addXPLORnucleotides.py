"""
Use the CYANA names as a basis and then do some subs.
"""

from cing import NTdb
from cing.core.constants import * #@UnusedWildImport

nuclList = ('GUA', 'CYT', 'ADE', 'THY', 'URA',
            'RGUA', 'RCYT', 'RADE', 'RTHY', 'RURA',
            )
mapCyana2Xplor = {
                  'OP1': 'O1P',
                  'OP2': 'O2P',
                  'H2"': "H2''",
                  'H5"': "H5''",
                  }
mapCyana2XplorKeys=mapCyana2Xplor.keys()

for res in NTdb:
    if not res.name in nuclList:
        continue
    for atm in res:
        atm.nameDict[XPLOR] = atm.nameDict[CYANA]
        if atm.nameDict[CYANA] in mapCyana2XplorKeys:
            atm.nameDict[XPLOR] = mapCyana2Xplor[ atm.nameDict[CYANA] ]

stream = open('dbTable-new', 'w')
NTdb.exportDef(stream=stream)
stream.close()

