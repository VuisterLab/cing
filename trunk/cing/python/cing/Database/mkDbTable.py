#@PydevCodeAnalysisIgnore
from cing.Libs.NTutils import *
from cing.core.database import ResidueDef
from cing import NTdb
import cing

stream = open('dbTable.new', 'w')
NTdb.exportDef(stream=stream, convention='INTERNAL_1')
stream.close()
