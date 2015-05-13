"""
With help from Wim Vranken.
For example:
    - changing the MS name from 2kkx to ET109AredOrg
    - swap checks/changes

# Execute like e.g.:
# python -u $CINGROOT/python/cing/NRG/CasdNmrMassageCcpnProject.py ET109AredOrg ET109AredUtrecht
if the input project is in cwd.

Most functionality is hard-coded here so be careful reading the actual code.
"""
from cing.Libs.DBMS import DBMS
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import copy
from cing.Libs.disk import globMultiplePatterns
from cing.NRG import CASP_NMR_BASE_NAME
from cing.NRG.PDBEntryLists import writeEntryListToFile
from cing.core.constants import * #@UnusedWildImport
from glob import glob1
import tarfile

__author__ = "Wim Vranken <wim@ebi.ac.uk> Jurgen Doreleijers <jurgenfd@gmail.com>"

#    inputDir = os.path.join(cingDirTestsData, "ccpn")
try:
    from cing.NRG.settings import baseCaspDir as baseDir
except:
    #baseDir = '/Users/jd/CASD-NMR-CING'
    baseDir = '/Volumes/UserHome/geerten/Data/CASP-NMR-CING'

startDir = '/Library/WebServer/Documents/' + CASP_NMR_BASE_NAME
dataDir = os.path.join(startDir, DATA_STR)

colorByLab = {
    'Cheshire': 'green',
    'Frankfurt': 'blue',
    'Lyon': 'red',
    'Paris': 'darkblue',
    'Piscataway': 'orange',
    'Seattle': 'gold',
    'Utrecht': 'darkgreen'
}


def getCASP_NMR_DBMS():
    csvFileDir = os.path.join(baseDir, 'Overview')
    relationNames = glob1(csvFileDir, "*.csv")
    relationNames = [ relationName[:-4] for relationName in relationNames]
    dbms = DBMS()
    dbms.readCsvRelationList(relationNames, csvFileDir)
    return dbms

def createLayOutArchive():
    inputDir = '/Users/jd/CASP-NMR-CING/caspNmrDbDivided'
    os.chdir(inputDir)
    for entryCode in entryList[:]:
#    for entryCode in entryList[0:1]:
        ch23 = entryCode[1:3]
        for city in predList:
            entryCodeNew = entryCode + city
            entryDir = os.path.join(ch23, entryCodeNew)
            mkdirs(entryDir)

def copyFromCasp2CcpnArchive():
    inputDir = '/Users/jd/CASP-NMR-CING/caspNmrDbDivided'
    os.chdir(inputDir)
    for entryCode in entryList:
#    for entryCode in entryList[0:1]:
        ch23 = entryCode[1:3]
        for city in predList:
#        for city in cityList[0:1]:
            entryCodeNew = entryCode + city
            nTmessage("Working on: %s" % entryCodeNew)

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
#                nTmessage("Copying from %s" % fn)
#                fnBaseName = os.path.basename(fn)
                dstFn = os.path.join(inputAuthorDir, fn)
                nTmessage("Copying from %s to %s" % (orgFn, dstFn))
                copy(orgFn, dstFn)


def redoLayOutArchiveWim():
    inputDir = '/Users/jd/Downloads/caspNmrCcpn'
    os.chdir(inputDir)
    for entryCode in entryList[:]:
#    for entryCode in entryList[0:1]:
        ch23 = entryCode[1:3]
        entryCodeNew = entryCode + "Org"
        entryDir = os.path.join(dataDir, ch23, entryCodeNew)
        tarPath = os.path.join(entryDir, entryCodeNew + ".tgz")
#        nTmessage("Tarring from %s to %s" % (entryCodeNew,tarPath))
        nTmessage("Creating %s" % tarPath)
        if not os.path.exists(entryDir):
            mkdirs(entryDir)
        if not os.path.exists(entryCodeNew):
            os.rename(entryCode, entryCodeNew)
        myTar = tarfile.open(tarPath, mode='w:gz') # overwrites
        myTar.add(entryCodeNew)
        myTar.close()

def getMapEntrycodeNew(entryList, cityList):
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

#def getRangesForTarget(target):
#    if target not in entryList:
#        nTerror("Failed to find entryOrg [%s] in entryList %s" % (target, repr(entryList)))
#        return None
#    index = entryList.index(target)
#    return rangesPsvsList[index]

def getTargetForFullEntryName(fullEntryCode):
    """
    Split the full entry name on the last capital and return the
    part before.
    ET109AredOrg     ET109Ared
    AR3436AFrankfurt AR3436A
    """
    idxLastCapital = -1
    for idx,char in enumerate(fullEntryCode):
        if char.isupper():
            idxLastCapital = idx
    if idxLastCapital < 0:
        nTerror("Failed to find idxLastCapital in [%s]" % fullEntryCode)
        return None
    target = fullEntryCode[:idxLastCapital]
    return target

def getFullEntryNameListForTarget(target, programHoH):
    """
    Query the participation table for who all predicted the target.
    Does not include the Org.
    """
    targetList = programHoH.keys()
    targetList.sort()
    print targetList
    if target not in targetList:
        nTerror("Failed to find target %s in list %s" % (target, str(targetList)))
        return None

    mapByLab = programHoH[target]
    labList = mapByLab.keys()
    labList.sort()
    result = []
    for labId in labList:
        if not getDeepByKeysOrAttributes(mapByLab, labId ):
            continue
        result.append(target+labId)
    return result

def printCingUrls(programHoH):
    targetList = programHoH.keys()
    targetList.sort()
    print targetList
    for target in targetList:
        mapByLab = programHoH[target]
        labList = mapByLab.keys()
        labList += ['Org']
        labList.sort()
        for labId in labList:
            program = getDeepByKeysOrAttributes(mapByLab, labId )
            if labId != 'Org':
                if not program:
                    continue
            entryCode = target + labId
            ch23 = entryCode[1:3]
            print "http://nmr.cmbi.ru.nl/CASP-NMR-CING/data/%s/%s/%s.cing" % (
                    ch23, entryCode, entryCode                )

predList = """
TS001 TS002 TS014 TS018 TS026 TS028 TS037 TS039 TS047 TS055 TS056 TS063 TS077
TS080 TS086 TS088 TS094 TS102 TS103 TS104 TS113 TS114 TS117 TS119 TS127 TS129
TS140 TS142 TS152 TS165 TS166 TS170 TS171 TS173 TS174 TS207 TS208 TS213 TS214
TS215 TS218 TS220 TS228 TS229 TS236 TS244 TS245 TS248 TS250 TS253 TS257 TS264
TS269 TS273 TS275 TS276 TS286 TS289 TS291 TS296 TS302 TS304 TS307 TS314 TS319
TS321 TS322 TS328 TS331 TS345 TS346 TS350 TS361 TS366 TS380 TS391 TS395 TS407
TS409 TS419 TS420 TS428 TS429 TS433 TS435 TS436 TS444 TS447 TS449 TS452 TS453
TS457 TS470 TS471 TS476 TS481 TS490
""".split()
entryList = [ '%s%s' % ('T0538',x) for x in predList]
entryListAll = [ 'T0538Org' ] + entryList
#dbms = getCASP_NMR_DBMS()
#sheetName = 'Overview1'
#participantTable = dbms.tables['%s-Participant' % sheetName]
#participationTable = dbms.tables['%s-Participation' % sheetName]
#targetTable = dbms.tables['%s-Target' % sheetName]
#labTable = dbms.tables['%s-LabAndCount' % sheetName]
#labList = labTable.columnOrder[0]
#cityList = participantTable.columnOrder[1:]
#entryList = targetTable.getColumnByIdx(0)
#rangesPsvsList = targetTable.getColumnByIdx(6)
#mapEntrycodeNew2EntrycodeAndCity = getMapEntrycodeNew(entryList, cityList)
#nTdebug("Read dbms with tables: %s" % dbms.tables.keys())
#print labList
#print programHoH
#print getRangesForTarget('ET109Ared')
#print getTargetForFullEntryName('ET109AredOrg')
#print getTargetForFullEntryName('AR3436AFrankfurt')

#printCingUrls(programHoH)

if __name__ == '__main__':
    cing.verbosity = cing.verbosityDebug
#    createTodoList(entryList, cityList,programHoH)
#    createLayOutArchive()
#    copyFromCasdNmr2CcpnArchive()
#    annotateLoop()
#    redoLayOutArchiveWim()
#    nTmessage("entryList: %s" % str(entryList))

