"""
Unit test execute as:
python $CINGROOT/python/cing/Libs/test/test2_pdb.py

Because of the name of this file it will not be executed when doing:
cing --test
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.classes import Project
from cing.core.constants import * #@UnusedWildImport
from unittest import TestCase
import profile
import pstats
import unittest

class AllChecks(TestCase):

    def testPdbFile(self):
        nTwarning("This test case will take about 5 (+3 for 1v0e) minutes and is recommended to be done before major releases.")
    #        entryId = "1ai0" # Most complex molecular system in any PDB NMR entry
#        entryList = "1a4d".split() # Small much studied PDB NMR entry
    #        entryId = "1brv" # Small much studied PDB NMR entry
    #        entryId = "2hgh_1model"
#        entryList = "1kr8".split()
#        entryList = "1otz".split() # 61 chains of which one is ' '
#        entryList = "1v0e".split()
#        entryList = "1a4d 1a24 1afp 1ai0 1brv 1bus 1cjg 1hue 1ieh 1iv6 1kr8 1otz 2hgh 2k0e".split()
        entryList = "1a4d 1ai0 1brv 1bus 1hue 1iv6 1kr8".split()
        for entryId in entryList:

            pdbDirectory = os.path.join(cingDirTestsData,"pdb", entryId)
            pdbFileName = "pdb"+entryId+".ent"
            pdbFilePath = os.path.join( pdbDirectory, pdbFileName)

            cingDirTmpTest = os.path.join( cingDirTmp, 'test2_pdb' )
            mkdirs( cingDirTmpTest )
            os.chdir(cingDirTmpTest)
            # does it matter to import it just now?
            project = Project( entryId )
            self.failIf( project.removeFromDisk())
            project = Project.open( entryId, status='new' )
            self.assertTrue( project.initPDB( pdbFile=pdbFilePath, convention=IUPAC, allowNonStandardResidue=True ))
            self.assertTrue( project.save() )


if __name__ == "__main__":
    doProfile = False
    cing.verbosity = verbosityDebug
    if doProfile:
        fn = os.path.join(cingDirTmp, 'testPdbFileProfile.log')
        profile.run('unittest.main()', fn)
        p = pstats.Stats(fn)
    #     enable a line or two below for useful profiling info
        p.sort_stats('time').print_stats(100)
        p.sort_stats('cumulative').print_stats(100)
    else:
        unittest.main()
