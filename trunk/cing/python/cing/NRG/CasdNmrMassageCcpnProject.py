"""
With help from Wim Vranken.
For example:
    - changing the MS name from 2kkx to ET109AredOrg
    - swap checks/changes

# Execute like e.g.:
# python -u $CINGROOT/python/cing/Scripts/FC/massageCcpnProject.py ET109AredOrg ET109AredUtrecht
if the input project is in cwd.

Most functionality is hard-coded here so be careful reading the actual code.
"""

from cing.Libs.DBMS import DBMS
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import getDeepByKeys
from cing.Libs.disk import copy
from cing.Libs.disk import globMultiplePatterns
from cing.Libs.disk import mkdirs
from cing.NRG import CASD_NMR_BASE_NAME
from cing.NRG.PDBEntryLists import writeEntryListToFile
from cing.core.constants import CYANA
from cing.core.constants import PDB
from cing.core.constants import XPLOR
from glob import glob1
import cing
import os
import tarfile

__author__ = "Wim Vranken <wim@ebi.ac.uk> Jurgen Doreleijers <jurgenfd@gmail.com>"

#    inputDir = os.path.join(cingDirTestsData, "ccpn")
baseDir = '/Users/jd/CASD-NMR-CING'
#dataOrgDir = os.path.join(baseDir, 'data')
dataDir = os.path.join(baseDir, 'data')
startDir = '/Library/WebServer/Documents/' + CASD_NMR_BASE_NAME

def convertToProgram(t):
    """check if there is an x for each and creates a string Hash by row and Hash by column"""

    # Assumes first column has the row labels. This is called a header column in Numbers.
    rowLabelList = t.getColumnByIdx(0)
    rowSize = t.sizeRows()
    result = {}
    for r in range(rowSize):
        rowLabel = rowLabelList[r]
        result[rowLabel] = {}
        resultRow = result[rowLabel]
        for c, columnLabel in enumerate(t.columnOrder):
            if c == 0:
                continue
            column = t.attr[columnLabel]
            value = column[r].lower()

            valueEnumerated = None
            if value == 'c':
                valueEnumerated = CYANA
            if value == 'x':
                valueEnumerated = XPLOR
            if value == 'p':
                valueEnumerated = PDB

            resultRow[columnLabel] = valueEnumerated
    return result


def getCASD_NMR_DBMS():
    csvFileDir = os.path.join(baseDir, 'Overview')
    relationNames = glob1(csvFileDir, "*.csv")
    relationNames = [ relationName[:-4] for relationName in relationNames]
    dbms = DBMS()
    dbms.readCsvRelationList(relationNames, csvFileDir)
    return dbms

def createLayOutArchive():
    inputDir = '/Users/jd/CASD-NMR-CING/casdNmrDbDivided'
    os.chdir(inputDir)
    for entryCode in entryList[:]:
#    for entryCode in entryList[0:1]:
        ch23 = entryCode[1:3]
        for city in cityList:
            entryCodeNew = entryCode + city
            entryDir = os.path.join(ch23, entryCodeNew)
            mkdirs(entryDir)

def copyFromCasdNmr2CcpnArchive():
    inputDir = '/Users/jd/CASD-NMR-CING/casdNmrDbDivided'
    programHoH = convertToProgram(participationTable)
    os.chdir(inputDir)
    for entryCode in entryList:
#    for entryCode in entryList[0:1]:
        ch23 = entryCode[1:3]
        for city in cityList:
#        for city in cityList[0:1]:
            entryCodeNew = entryCode + city
            programId = getDeepByKeys(programHoH, entryCode, city)
            if not (city == 'Test' or programId):
#                NTdebug("Skipping %s" % entryCodeNew)
                continue
#            else:
#                NTdebug("Looking at %s" % entryCodeNew)
#                continue # TODO disable premature stop.

            NTmessage("Working on: %s" % entryCodeNew)

            inputEntryDir = os.path.join(inputDir, ch23, entryCodeNew)
            outputEntryDir = os.path.join(dataDir, ch23, entryCodeNew)
            inputAuthorDir = os.path.join(outputEntryDir, 'Author')
            outputNijmegenDir = os.path.join(outputEntryDir, 'Nijmegen')

            if not os.path.exists(inputAuthorDir):
                mkdirs(inputAuthorDir)
            if not os.path.exists(outputNijmegenDir):
                mkdirs(outputNijmegenDir)
            # prevent junk
            patternList = "*.pdb *.upl *.aco *.tbl".split()
            fnList = globMultiplePatterns(inputEntryDir, patternList)
            for fn in fnList:
                orgFn = os.path.join(inputEntryDir, fn)
#                NTmessage("Copying from %s" % fn)
#                fnBaseName = os.path.basename(fn)
                dstFn = os.path.join(inputAuthorDir, fn)
                NTmessage("Copying from %s to %s" % (orgFn, dstFn))
                copy(orgFn, dstFn)


def redoLayOutArchiveWim():
    inputDir = '/Users/jd/Downloads/casdNmrCcpn'
    os.chdir(inputDir)
    for entryCode in entryList[:]:
#    for entryCode in entryList[0:1]:
        ch23 = entryCode[1:3]
        entryCodeNew = entryCode + "Org"
        entryDir = os.path.join(dataDir, ch23, entryCodeNew)
        tarPath = os.path.join(entryDir, entryCodeNew + ".tgz")
#        NTmessage("Tarring from %s to %s" % (entryCodeNew,tarPath))
        NTmessage("Creating %s" % tarPath)
        if not os.path.exists(entryDir):
            mkdirs(entryDir)
        if not os.path.exists(entryCodeNew):
            os.rename(entryCode, entryCodeNew)
        myTar = tarfile.open(tarPath, mode='w:gz') # overwrites
        myTar.add(entryCodeNew)
        myTar.close()

def getMapEntrycodeNew2EntrycodeAndCity(entryList, cityList):
    result = {}
    for entry in entryList:
        for city in cityList:
            entryNew = entry + city
            result[entryNew] = (entry, city)
    return result

def createTodoList(entryList, cityList, programHoH):
    entryListFileName = os.path.join(baseDir, 'list', 'entry_list_todo.csv')
    newEntryList = []
    for entry in entryList:
        for city in cityList:
            entryNew = entry + city
            programId = getDeepByKeys(programHoH, entry, city)
            if programId:
                newEntryList.append(entryNew)
    writeEntryListToFile(entryListFileName, newEntryList)
# end def

dbms = getCASD_NMR_DBMS()
sheetName = 'Overview1'
participantTable = dbms.tables['%s-Participant' % sheetName]
participationTable = dbms.tables['%s-Participation' % sheetName]
targetTable = dbms.tables['%s-Target' % sheetName]
cityList = participantTable.columnOrder[1:]
entryList = targetTable.getColumnByIdx(0)
programHoH = convertToProgram(participationTable)
mapEntrycodeNew2EntrycodeAndCity = getMapEntrycodeNew2EntrycodeAndCity(entryList, cityList)
#NTdebug("Read dbms with tables: %s" % dbms.tables.keys())
#print mapEntrycodeNew2EntrycodeAndCity

if __name__ == '__main__':
    cing.verbosity = cing.verbosityDebug
#    createTodoList(entryList, cityList,programHoH)
#    createLayOutArchive()
#    copyFromCasdNmr2CcpnArchive()
#    annotateLoop()
#    redoLayOutArchiveWim()
