# Script for running Cing on a bunch (8?) of ccpn projects.
# Run: python -u $CINGROOT/python/cing/Scripts/vCingvCingSlave.py

# Author: Jurgen F. Doreleijers
# Thu Oct 14 23:56:36 CEST 2010

from cing import cingDirTmp
from cing import header
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.NRG.PDBEntryLists import getPdbEntries
from cing.main import getStartMessage
from cing.main import getStopMessage
import commands

DEFAULT_URL = 'http://nmr.cmbi.ru.nl/NRG-CING/recoordSync'
#SERVER='jurgend@www.cmbi.ru.nl'
#CLIENT='jd@nmr.cmbi.umcn.nl'
#MIRRORDIR='/Library/WebServer/Documents/tmp/vCingSlave'
SOURCE_SDIR = 'jurgenfd@gb-ui-kun.els.sara.nl:/home/jurgenfd/recoordSync'
TARGET_SDIR = 'jurgenfd@gb-ui-kun.els.sara.nl:/home/jurgenfd/tmp/cingTmp'

def retrieveEntryList():
    pdbIdList = getPdbEntries(onlyNmr = True, mustHaveExperimentalNmrData = False, onlySolidState = False)
    NTmessage("Retrieved list with %s entries." % len(pdbIdList))
#    txt = "%r" % pdbIdList
    txt = ''
    for pdbId in pdbIdList:
        txt += '%s\n' % pdbId
    writeTextToFile('entryList.txt', txt)
    return pdbIdList

def runSlave():
    'Returns True on error'

    if os.chdir(cingDirTmp):
        NTerror("Failed to change to directory for temporary test files: %s" % cingDirTmp)
        return True

    _status, date_string = commands.getstatusoutput('date "+%Y-%m-%d_%H-%M-%S"') # gives only seconds.
    _status, epoch_string = commands.getstatusoutput('java Wattos.Utils.Programs.GetEpochTime')
    time_string = '%s_%s' % (date_string, epoch_string )
    NTmessage("In runSlave time is: %s" %time_string)
    _entryList = retrieveEntryList()

# end def test

if __name__ == "__main__":
    cing.verbosity = verbosityDebug

    NTmessage(header)
    NTmessage(getStartMessage())

    try:
        if runSlave():
            NTerror("Failed to vCingSlave")
            os.exit(1)
    finally:
        NTmessage(getStopMessage())
