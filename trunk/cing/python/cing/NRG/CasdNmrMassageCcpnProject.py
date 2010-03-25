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
from ccpnmr.format.converters.PseudoPdbFormat import PseudoPdbFormat
from cing import verbosityDebug
from cing.Libs.DBMS import DBMS
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import NTwarning
from cing.NRG import CASD_NMR_BASE_NAME
from cing.Scripts.FC.convertCyana2Ccpn import importCyanaRestraints
from cing.core.classes import Project
from glob import glob
from glob import glob1
from matplotlib.cbook import mkdirs
from memops.general.Io import loadProject
from memops.general.Io import saveProject
#import Tkinter
import cing
import os
import tarfile

__author__ = "Wim Vranken <wim@ebi.ac.uk> Jurgen Doreleijers <jurgenfd@gmail.com>"

#    inputDir = os.path.join(cingDirTestsData, "ccpn")
baseDir = '/Users/jd/CASD-NMR-CING'
#dataOrgDir = os.path.join(baseDir, 'data')
dataDividedDir = os.path.join(baseDir, 'dataDivided')
startDir = '/Library/WebServer/Documents/' + CASD_NMR_BASE_NAME

def getCASD_NMR_DBMS():
    csvFileDir = os.path.join(baseDir, 'Overview')
    relationNames = glob1(csvFileDir, "*.csv")
    relationNames = [ relationName[:-4] for relationName in relationNames]
    dbms = DBMS()
    dbms.readCsvRelationList(relationNames, csvFileDir)
    return dbms

dbms = getCASD_NMR_DBMS()
sheetName = 'Overview1'
participantTable = dbms.tables['%s-Participant' % sheetName]
participationTable = dbms.tables['%s-Participation' % sheetName]
targetTable = dbms.tables['%s-Target' % sheetName]
cityList = participantTable.columnOrder[1:]
#    cityList = [ 'Cheshire', 'Frankfurt', 'Lyon', 'Paris', 'Piscataway', 'Seattle', 'Utrecht' ]
entryList = targetTable.getColumnByIdx(0)
    #    entryListFileName = os.path.join(startDir, 'list', 'entry_list_todo.csv')
    #    entryList = readLinesFromFile(entryListFileName) #@UnusedVariable

def convertToBoolean(t):
    """check if there is an x for each and creates a boolean Hash by row and Hash by column"""

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
            value = column[r]
            valueBoolean = value != ''
            resultRow[columnLabel] = valueBoolean
    return result

def redoLayOutArchiveWim():
    inputDir = '/Users/jd/Downloads/casdNmrCcpn'
    os.chdir(inputDir)
    for entryCode in entryList[:]:
#    for entryCode in entryList[0:1]:
        ch23 = entryCode[1:3]
        entryCodeNew = entryCode+"Org"
        entryDir = os.path.join(dataDividedDir,ch23,entryCodeNew)
        tarPath = os.path.join(entryDir,entryCodeNew+".tgz")
#        NTmessage("Tarring from %s to %s" % (entryCodeNew,tarPath))
        NTmessage("Creating %s" % tarPath)
        if not os.path.exists(entryDir):
            mkdirs(entryDir)
        if not os.path.exists(entryCodeNew):
            os.rename(entryCode, entryCodeNew)
        myTar = tarfile.open(tarPath, mode='w:gz') # overwrites
        myTar.add( entryCodeNew )
        myTar.close()

def massageLoop():
#    guiRoot = Tkinter.Tk()
    guiRoot = None

    NTdebug("Read dbms with tables: %s" % dbms.tables.keys())

    isParticipatingHoH = convertToBoolean(participationTable)
    maxCities = 10
    maxEntries = 10
    # Adjust the parameters below!
    doAll = False # do full list or just some.
    unpackOrgCcpnProject = True
    startFromNewCcpnProject = False
    replaceStructureEnsemble = True # From all *.pdb files in inputDir.
    addRestraints = True
#    swapCheck = True
    doSaveProject = True
    doExport = True

    print 'doAll                           ', doAll
    print 'unpackOrgCcpnProject            ', unpackOrgCcpnProject
    print 'startFromNewCcpnProject         ', startFromNewCcpnProject
    print 'replaceStructureEnsemble        ', replaceStructureEnsemble
    print 'addRestraints                   ', addRestraints
    print 'doSaveProject                   ', doSaveProject
    print 'doExport                        ', doExport

    if not doAll: # Disable for doing all.
#        entryList = ['ET109Aox']
#        maxEntries = min(maxEntries, len(entryList))
    #    cityList = [ 'Cheshire', 'Frankfurt', 'Lyon', 'Paris', 'Piscataway', 'Seattle', 'Utrecht' ]
        cityList = [ 'Frankfurt']
        maxCities = min(maxCities, len(cityList))

    for entryCode in entryList[0:maxEntries]:
        ch23 = entryCode[1:3]
        entryCodeOrg = entryCode + 'Org'
        dataOrgEntryDir = os.path.join(dataDividedDir, ch23, entryCodeOrg)
        ccpnFile = os.path.join(dataOrgEntryDir, entryCodeOrg + ".tgz")
        for city in cityList[0:maxCities]:
            entryCodeNew = entryCode + city
            if not isParticipatingHoH[entryCode][city]:
#                NTdebug("Skipping %s" % entryCodeNew)
                continue
            else:
                NTdebug("Looking at %s" % entryCodeNew)
#                continue # TODO disable premature stop.

            dataDividedXDir = os.path.join(dataDividedDir, ch23)
            entryDir = os.path.join(dataDividedXDir, entryCodeNew )
            inputAuthorDir = os.path.join(entryDir, 'Author')
            outputNijmegenDir = os.path.join(entryDir, 'Nijmegen')

            if not os.path.exists(inputAuthorDir):
                mkdirs(inputAuthorDir)
            if not os.path.exists(outputNijmegenDir):
                mkdirs(outputNijmegenDir)

            os.chdir(outputNijmegenDir)

            if unpackOrgCcpnProject:
                # By reading the ccpn tgz into cing it is also untarred/tested.
                project = Project.open(entryCodeOrg, status='new')
                project.initCcpn(ccpnFolder=ccpnFile, modelCount=1)
                project.removeFromDisk()
                project.close(save=False)

            if startFromNewCcpnProject:
                ccpnProject = loadProject(entryCodeNew)
            else:
                ccpnProject = loadProject(entryCodeOrg)

            nmrProject = ccpnProject.currentNmrProject
            ccpnMolSystem = ccpnProject.findFirstMolSystem()
            NTmessage('found ccpnMolSystem: %s' % ccpnMolSystem)
        #    print 'status: %s' % ccpnMolSystem.setCode(projectName) # impossible; reported to ccpn team.

            if replaceStructureEnsemble:
                structureEnsemble = ccpnProject.findFirstStructureEnsemble()
                if structureEnsemble:
                    NTmessage("Removing first found structureEnsemble")
                    structureEnsemble.delete()
                else:
                    NTwarning("No structureEnsemble found; can't remove it.")

                structureGeneration = nmrProject.newStructureGeneration()
                globPattern = inputAuthorDir + '/*.pdb'
                pdbFileList = glob(globPattern)
                if not pdbFileList:
                    NTerror("Skipping because there is no PDB file in: " + os.getcwd())
                else:
                    NTdebug("From %s will read files: %s" % (globPattern, pdbFileList))
                    format = PseudoPdbFormat(ccpnProject, guiRoot, verbose=0)
                    format.readCoordinates(pdbFileList, strucGen=structureGeneration, minimalPrompts=1, linkAtoms=0)

            if addRestraints:
                if hasCyanaRestraints(inputAuthorDir):
                    importCyanaRestraints(ccpnProject, inputAuthorDir, guiRoot)

            NTmessage('saving to new path if all checks are valid')
            # the newPath basename will be taken according to ccpn code doc.
            if doSaveProject:
                saveProject(ccpnProject, checkValid=True, newPath=entryCodeNew, removeExisting=True)
            if doExport:
                tarPath = os.path.join(entryDir, entryCodeNew + ".tgz")
                if os.path.exists(tarPath):
                    NTmessage("Overwriting: " + tarPath)
                myTar = tarfile.open(tarPath, mode='w:gz') # overwrites
                myTar.add( entryCodeNew )
                myTar.close()
        # end for city
    # end for entry
    if guiRoot != None:
        guiRoot.destroy()
# end def

def hasCyanaRestraints(inputDir):
    globPattern = inputDir + '/*.upl'
    fileList = glob(globPattern)
    if fileList:
        return True

    globPattern = inputDir + '/*.aco'
    fileList = glob(globPattern)
    if fileList:
        return True

if __name__ == '__main__':
    cing.verbosity = verbosityDebug
    massageLoop()
#    redoLayOutArchiveWim()