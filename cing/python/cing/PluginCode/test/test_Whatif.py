"""
Unit test
python $CINGROOT/python/cing/PluginCode/test/test_Whatif.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import verbosityDebug
from cing import verbosityError
from cing.Libs.NTutils import NTdebug
from cing.PluginCode.Whatif import QUAL_LIST_STR
from cing.PluginCode.Whatif import VALUE_LIST_STR
from cing.PluginCode.Whatif import WHATIF_STR
from cing.PluginCode.Whatif import runWhatif
from cing.core.classes import Project
from unittest import TestCase
from cing.core.constants import PDB
import cing
import os
import unittest

class AllChecks(TestCase):
        
    def testparse(self):        
        #entryId = "1ai0" # Most complex molecular system in any PDB NMR entry 
#        entryId = "2hgh" # Small much studied PDB NMR entry; 48 models 
#        entryId = "1bus" # Small much studied PDB NMR entry:  5 models of 57 AA.: 285 residues.
        entryId = "1brv_1model" 
#        entryId = "1tgq_1model" 
        convention = PDB
        
        os.chdir(cingDirTmp)
        project = Project( entryId )
        project.removeFromDisk()
        project = Project.open( entryId, status='new' )
        cyanaDirectory = os.path.join(cingDirTestsData,"cyana", entryId)
        pdbFileName = entryId+".pdb"
        pdbFilePath = os.path.join( cyanaDirectory, pdbFileName)
        NTdebug("Reading files from directory: " + cyanaDirectory)
        project.initPDB( pdbFile=pdbFilePath, convention = convention )

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
