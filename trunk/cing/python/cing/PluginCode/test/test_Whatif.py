"""
Unit test
python $CINGROOT/python/cing/PluginCode/test/test_Whatif.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.Ccpn import Ccpn #@UnusedImport Added to raise import warning and causing the check to be skipped while testing.
from cing.PluginCode.Whatif import runWhatif
from cing.PluginCode.required.reqWhatif import * #@UnusedWildImport
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from unittest import TestCase
import shutil
import unittest

class AllChecks(TestCase):

#    def _testHistogram(self):
#        resType = 'GLY'
#        for ssType in histRamaBySsAndResType.keys(): #@UndefinedVariable
#            hist = histRamaBySsAndResType[ssType][resType]
#            sumHist =  sum(sum(hist))
#            maxHist =  amax(amax(hist))
#            nTdebug( 'histRamaBySsAndResType[%s][%s]' % (ssType, resType))
#            nTdebug( 'sumHist [%4d] maxHist [%4d]' % (sumHist, maxHist))
#            sys.output_line_width = 9999 # queried below.
#            set_printoptions( threshold = 9999 )# should be larger than items to be printed 36*36=1296
#            try:
#                strHist = array2string(hist, max_line_width = 9999, precision = 0, suppress_small = None, separator='')
#                nTdebug( '\n%s' % strHist )
#            except:
#                # Fails for some reason on Linux 64 bit with python2.4 with old numpy lib
#                pass

    def test_Whatif(self):
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry
#        entryId = "2hgh" # Small much studied PDB NMR entry; 48 models
#        entryId = "1bus" # Small much studied PDB NMR entry:  5 models of 57 AA.: 285 residues.
        entryId = "1brv" # DEFAULT is not to do more than 2 models because it takes quite a while.
#        entryId = "1brv_cs_pk_2mdl"

#        entryId = "1tgq_1model"
#        pdbConvention = IUPAC
        parseOnly = False # normal is False
        showValues = True
        ranges='cv'
#        ranges='172-177'
#        ranges='6-13,29-45'


        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)
        project = Project( entryId )
        if not parseOnly:
            project.removeFromDisk()
            project = Project.open( entryId, status='new' )
#            cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
#            pdbFileName = entryId+".pdb"
#            pdbFilePath = os.path.join( cyanaDirectory, pdbFileName)
#            nTdebug("Reading files from directory: " + cyanaDirectory)
#            project.initPDB( pdbFile=pdbFilePath, convention = pdbConvention )
            inputArchiveDir = os.path.join(cingDirTestsData, "ccpn")

            ccpnFile = os.path.join(inputArchiveDir, entryId + ".tgz")
            if not os.path.exists(ccpnFile):
                ccpnFile = os.path.join(inputArchiveDir, entryId + ".tar.gz")
                if not os.path.exists(ccpnFile):
                    self.fail("Neither %s or the .tgz exist" % ccpnFile)

            self.assertTrue(project.initCcpn(ccpnFolder = ccpnFile, modelCount=2))
            self.assertFalse(runWhatif(project, ranges=ranges, parseOnly=False))
        else:
            project = Project.open( entryId, status='old' )
#        print project.cingPaths.format()

        project.save()
        if showValues:
            for res in project.molecule.allResidues():
                nTdebug(repr(res))
                whatifResDict = res.getDeepByKeys(WHATIF_STR)
                if not whatifResDict:
                    continue
#                checkIDList = whatifResDict.keys()
                checkIDList = 'RAMCHK'.split()
                for checkID in checkIDList:
                    valueList = whatifResDict.getDeepByKeys(checkID,VALUE_LIST_STR)
                    qualList  = whatifResDict.getDeepByKeys(checkID,QUAL_LIST_STR)
                    nTdebug("%10s valueList: %-80s qualList: %-80s" % ( checkID, valueList, qualList))
        # Do not leave the old CCPN directory laying around since it might get added to by another test.
        if os.path.exists(entryId):
            self.assertFalse(shutil.rmtree(entryId))

if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()
