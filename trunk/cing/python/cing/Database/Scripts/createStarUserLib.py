from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.database import NTdb

for resDef in NTdb:
    for dihedral in resDef.dihedrals:
        NTmessage('%-4s %-10s' % (resDef.name, dihedral.name))
