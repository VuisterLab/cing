"""
Unit test
python $CINGROOT/python/cing/PluginCode/test/test_Whatif.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTutils import NTdebug
from cing.PluginCode.Whatif import runWhatif
from cing.PluginCode.required.reqWhatif import QUAL_LIST_STR
from cing.PluginCode.required.reqWhatif import VALUE_LIST_STR
from cing.PluginCode.required.reqWhatif import WHATIF_STR
from cing.PluginCode.required.reqWhatif import histRamaBySsAndResType
from cing.core.classes import Project
from cing.core.constants import IUPAC
from matplotlib.numerix.mlab import amax
from numpy.core.arrayprint import array2string
from numpy.core.arrayprint import set_printoptions
from unittest import TestCase
import cing
import os
import sys
import unittest

class AllChecks(TestCase):

    def testHistogram(self):
        resType = 'GLY'     
        for ssType in histRamaBySsAndResType.keys(): #@UndefinedVariable
            hist = histRamaBySsAndResType[ssType][resType]
            sumHist =  sum(sum(hist))
            maxHist =  amax(amax(hist))
            NTdebug( 'histRamaBySsAndResType[%s][%s]' % (ssType, resType))
            NTdebug( 'sumHist [%4d] maxHist [%4d]' % (sumHist, maxHist))
            sys.output_line_width = 9999 # queried below.
            set_printoptions( threshold = 9999 )# should be larger than items to be printed 36*36=1296
            try:
                strHist = array2string(hist, max_line_width = 9999, precision = 0, suppress_small = None, separator='')
            except:
                # Fails for some reason on Linux 64 bit. Perhaps some inconsistency. 
                pass
            NTdebug( '\n%s' % strHist )

    def testRunWhatif(self):        
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry 
#        entryId = "2hgh" # Small much studied PDB NMR entry; 48 models 
#        entryId = "1bus" # Small much studied PDB NMR entry:  5 models of 57 AA.: 285 residues.
        entryId = "1brv_1model" 
#        entryId = "1tgq_1model" 
        pdbConvention = IUPAC
        
        os.chdir(cingDirTmp)
        project = Project( entryId )
        project.removeFromDisk()
        project = Project.open( entryId, status='new' )
        cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cyanaDirectory, pdbFileName)
        NTdebug("Reading files from directory: " + cyanaDirectory)
        project.initPDB( pdbFile=pdbFilePath, convention = pdbConvention )

#        print project.cingPaths.format()
        self.assertFalse(runWhatif(project))    
        
        project.save()
        for res in project.molecule.allResidues():
            NTdebug(`res`)
            whatifResDict = res.getDeepByKeys(WHATIF_STR)
            if not whatifResDict:
                continue
            checkIDList = whatifResDict.keys()
            for checkID in checkIDList:
                valueList = whatifResDict.getDeepByKeys(checkID,VALUE_LIST_STR)
                qualList  = whatifResDict.getDeepByKeys(checkID,QUAL_LIST_STR)
                NTdebug("%10s valueList: %-80s qualList: %-80s" % ( checkID, valueList, qualList))

if __name__ == "__main__":
    cing.verbosity = verbosityError
    cing.verbosity = verbosityDebug
    unittest.main()
