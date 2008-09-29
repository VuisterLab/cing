from cing.Libs.NTutils import fprintf
from cing.core.database import ResidueDef
import cing

stream = open('dbTable-new', 'w')
for res in cing.NTdb:
    res.exportDef(stream=stream)
stream.close()
