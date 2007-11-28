from cing.Libs.NTutils import fprintf
from cing.core.database import ResidueDef

stream = open('dbTable-new.py', 'w')
fprintf( stream, 'residueDefsTable = """\n')
ResidueDef.exportDef(stream=stream)
fprintf( stream, '"""\n')
stream.close()
