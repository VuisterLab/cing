from cing.NRG import ARCHIVE_CASD_ID
from cing.NRG.storeCING2db import doStoreCING2db
from cing.core.classes import Project
import cing
import sys

cing.verbosity = cing.verbosityDebug

pname = sys.argv[1]
project = Project.open(pname, status = 'old')


project.runQueeny()
project.save()

doStoreCING2db( project.name, ARCHIVE_CASD_ID, project=project)
