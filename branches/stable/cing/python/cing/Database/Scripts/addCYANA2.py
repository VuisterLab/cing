from cing.core.constants import * #@UnusedWildImport
from cing.core.database import NTdb

for res in NTdb:
    res.nameDict[CYANA2] = res.nameDict[CYANA]
    for atm in res:
        if (atm.name == 'HN'):
            atm.nameDict[CYANA2] = 'H'
        else:
            atm.nameDict[CYANA2] = atm.nameDict[CYANA]

stream = open('dbTable-new.py', 'w')
NTdb.exportDef(stream=stream)
stream.close()
