'''
Unit test execute as:
python -u $CINGROOT/python/cing/Libs/test/test_NoeCompleteness.py

Created on May 30, 2011

@author: jd
'''
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.NoeCompleteness import * #@UnusedWildImport
from cing.core.classes import Project
from unittest import TestCase
import unittest


class AllChecks(TestCase):
    cingDirTmpTest = os.path.join( cingDirTmp, 'test_NoeCompleteness' )
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def test_NoeCompletenessLib(self):
        cing.verbosity = cing.verbosityDebug
        ncl = NoeCompletenessAtomLib()
        self.assertTrue(ncl)
        
        
    def test_ArtificialRestraints(self):
        cing.verbosity = cing.verbosityDebug
        entryId = "1brv" # Testing entry with just 2 models.
#        entryId = "1nk4" # Interest of Winston
#        ranges = 'A.173-178'
        ranges = None

        pdbDirectory = os.path.join(cingDirTestsData,"pdb", entryId)
        pdbFileName = "pdb"+entryId+".ent"
        pdbFilePath = os.path.join( pdbDirectory, pdbFileName)

        project = Project( entryId )
        self.failIf( project.removeFromDisk())
        project = Project.open( entryId, status='new' )
        project.initPDB( pdbFile=pdbFilePath, convention = IUPAC )

        m = project.molecule
        NTdebug("m: %s" % m)
        resList = m.ranges2list(ranges)
        NTdebug("resList: %s" % resList)
        self.assertTrue(resList)
        
        resultCompleteness = doCompletenessCheck( project,
             max_dist_expectedOverall = 4.0,
             use_intra = True,
             ob_file_name = None,
             summaryFileNameCompleteness = "%s_DOCR_compl_sum" % entryId,
             write_dc_lists = True,
             file_name_base_dc  = "%s_DOCR_compl" % entryId,
             resList = resList
        )
        self.assertTrue(resultCompleteness)
        
        
if __name__ == "__main__":    
    unittest.main()
