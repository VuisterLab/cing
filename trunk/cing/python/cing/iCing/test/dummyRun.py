from cing import verbosityDebug
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
import cing

cing.verbosity = verbosityDebug
NTdebug("Testing NTdebug")
NTmessage("Testing NTmessage")
NTerror("Testing NTerror")
