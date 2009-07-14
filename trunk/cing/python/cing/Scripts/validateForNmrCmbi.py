from cing import cingDirScripts
from cing import cingDirTestsData
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTmessage
from cing.Libs.NTutils import gunzip
from cing.Scripts.doScriptOnEntryList import doScriptOnEntryList
from cing.Scripts.validateEntry import ARCHIVE_TYPE_BY_ENTRY
from cing.Scripts.validateEntry import PROJECT_TYPE_CYANA
from cing.core.constants import CYANA
from cing.core.constants import PDB
import cing
import os

cing.verbosity = cing.verbosityDebug

# parameters for doScriptOnEntryList
#startDir              = '/Users/jd/tmp/cing/dyndns/'
startDir              = '/Users/jd/Sites/cing/out'
pythonScriptFileName  = os.path.join(cingDirScripts, 'validateEntry.py')
entryListFileName     = os.path.join('/Users/jd', 'entryCodeList.csv')
PDBZ2                 = '/Users/jd/wattosTestingPlatform/pdb//data/structures/divided/pdb'
doUnzipFirst          = False # Ensure input (unzipped) is present first.

# parameters for validateEntry
#inputDir              = '/Volumes/proteins/var/www/html/Education/Validation/HTML/Exercise_1/Data/'
#inputDir              = '/Users/jd/wattosTestingPlatform/nozip/data/structures/all/pdb'
inputDir              = os.path.join(cingDirTestsData, "cyana")
outputDir             = startDir
pdbConvention         = PDB
restraintsConvention  = CYANA

extraArgList = ( inputDir,
                 outputDir,
                 pdbConvention,
                 restraintsConvention,
                 `ARCHIVE_TYPE_BY_ENTRY`,
                 `PROJECT_TYPE_CYANA`
                  )

if doUnzipFirst:
    entryListFile = file(entryListFileName, 'r')
    entryCodeList = []
    for line in entryListFile.readlines():
        line = line.strip()
        entryCode = line[0:4].lower()
        entryCodeList.append( entryCode )
    NTmessage('Found %d entries    ' % len(entryCodeList))

    for entryCode in entryCodeList:
        fileNameZipped = os.path.join( PDBZ2, entryCode[1:3], 'pdb'+entryCode+'.ent.gz' )
        outputFileName = os.path.join( inputDir, entryCode+'.pdb' )
        dstDir         = os.path.join( inputDir, entryCode )
        dst            = os.path.join( dstDir, entryCode+'.pdb' )
        cmd = '/Users/jd/BMRB/PdbArchive/getPdb.csh ' + entryCode
        exit_code = os.system( cmd )
        if exit_code:
            NTerror('failed to get pdb file')
            continue
        if gunzip(fileNameZipped, outputFileName=outputFileName):
            NTerror('Failed gunzip for entry: ' + entryCode)
        # Unusual path hierarchy by symlink only.
        if not os.path.exists(dstDir):
            os.mkdir(dstDir)
        if os.path.exists(dst):
            os.unlink(dst)
        if os.symlink(outputFileName, dst):
            NTerror('failed to symlink pdb file')
            continue


doScriptOnEntryList(pythonScriptFileName,
                    entryListFileName,
                    startDir,
                    processes_max = 2,
                    max_time_to_wait = 12000, # 1y4o took more than 600. This is one of the optional arguments.
                    extraArgList=extraArgList)
