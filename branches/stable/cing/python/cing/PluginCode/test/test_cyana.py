"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_cyana.py
"""


from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqCcpn import CCPN_STR
from cing.PluginCode.required.reqWattos import * #@UnusedWildImport
from cing.core.classes import Project
from nose.plugins.skip import SkipTest
from unittest import TestCase
import unittest

# Import using optional plugins.
try:
    from cing.PluginCode.Ccpn import Ccpn #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
except ImportWarning, extraInfo: # Disable after done debugging; can't use nTdebug yet.
    print "Got ImportWarning %-10s Skipping unit check %s." % ( CCPN_STR, getCallerFileName() )
    raise SkipTest(CCPN_STR)
# end try

class AllChecks(TestCase):
    'Test cases for cyana'
    entryList = "1brv".split() # DEFAULT
#    entryList = "1brv 1bus CopZ-in H2_2Ca_53 1ai0 1hkt_1model 2hgh_1model".split()
#    entryList = "CopZ-in".split()
#    entryList = "1y4o_1model".split() 
    
    def test_cyana(self):
#        cing.verbosity = verbosityDebug
#        if you have a local copy you can use it; make sure to adjust the path setting below.
        fastestTest = True             # DEFAULT: True. Not passed to the validate routine in order to customize checks for speed.

        modelCount=99                  # DEFAULT: 99
        redoFromCingProject = False    # DEFAULT: False
        htmlOnly = False               # DEFAULT: False # default is False but enable it for faster runs without some actual data.
        doWhatif = True                # DEFAULT: True # disables whatif actual run
        doProcheck = True              # DEFAULT: True 
        doWattos = True                # DEFAULT: True 
        doQueeny = True                # DEFAULT: True 
        doTalos = True                 # DEFAULT: True 
        filterVasco = False             # DEFAULT: False 
        filterTopViolations = False     # DEFAULT: False 
        ranges = CV_STR                # DEFAULT: CV_STR 
#        ranges='173-177'
#        ranges='6-13,29-45' # 1bus

        doSave = not redoFromCingProject  # DEFAULT: False Requires sqlAlchemy

        if fastestTest:
            modelCount=2 # DEFAULT 2
#            redoFromCingProject = False
            htmlOnly = True            # DEFAULT: True
            doWhatif = False           # DEFAULT: False
            doProcheck = False         # DEFAULT: False
            doWattos = False           # DEFAULT: False
            doQueeny = False           # DEFAULT: False
            doTalos = False            # DEFAULT: False
        # end if
        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)
        for i,entryId in enumerate(AllChecks.entryList):

            if i:
                nTmessage('\n\n')
            project = Project.open(entryId, status = 'new')
            self.assertTrue(project, 'Failed opening project: ' + entryId)

            inputArchiveDir = os.path.join(cingDirTestsData, "cyana")
            cyanaFile = os.path.join(inputArchiveDir, entryId + ".cyana.tgz")
            self.assertTrue(project.initCyana(cyanaFolder = cyanaFile, modelCount=modelCount))

            if False:
                ranges = "173-183"
#                residueOfInterest = range(171,174)
#                for residue in project.molecule.A.allResidues():
#                    if residue.resNum not in residueOfInterest:
#    #                    nTmessage("Removing residue of no interest")
#                        project.molecule.A.removeResidue(residue)
            if True:
                self.assertFalse(project.molecule.setRanges(ranges))
                project.molecule.rangesToMmCifRanges(ranges)
            if True:
                self.assertFalse(project.validate(htmlOnly = htmlOnly,
                                              ranges=ranges,
#                                              fastestTest=fastestTest, # disabled
                                              doProcheck = doProcheck,
                                              doWhatif = doWhatif,
                                              doWattos=doWattos,
                                              doQueeny = doQueeny,
                                              doTalos=doTalos,
                                              filterVasco=filterVasco,
                                              filterTopViolations = filterTopViolations
                                               ))
            # end if
#            self.assertTrue(project.exportValidation2cyana())
#            self.assertFalse(project.removeCcpnReferences())
            # Do not leave the old CCPN directory laying around since it might get added to by another test.
#            if os.path.exists(entryId):
#                self.assertFalse(shutil.rmtree(entryId))

            if False:
                self.assertTrue(project.save())
                self.assertTrue(project.saveCcpn(entryId))
            if doSave:
                self.assertTrue(project.save())
        # end for
#        rmdir( cingDirTmpRandom ) # execute when all was successful
    # end def test
# end class
if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
