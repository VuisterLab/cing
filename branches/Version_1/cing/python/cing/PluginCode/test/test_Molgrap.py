"""
Unit test execute as:
python $CINGROOT/python/cing/PluginCode/test/test_Molgrap.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing import cingPythonCingDir
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.disk import rmdir
from cing.PluginCode.required.reqMolgrap import MOLGRAP_STR
from cing.core.classes import Project
from cing.constants import * #@UnusedWildImport
from nose.plugins.skip import SkipTest
from unittest import TestCase
import shutil
import unittest

# Import using optional plugins.
try:
    from cing.PluginCode.molgrap import Molgrap #@UnusedImport Keep to indicate dep and proper handeling.
except ImportWarning, extraInfo: # Disable after done debugging; can't use nTdebug yet.
    print "Got ImportWarning %-10s Skipping unit check %s." % ( MOLGRAP_STR, getCallerFileName() )
    raise SkipTest(MOLGRAP_STR)
# end try

class AllChecks(TestCase):

    cingDirTmpTest = os.path.join( cingDirTmp, 'test_Molgrap' )
    if os.path.exists( cingDirTmpTest ):
        rmdir( cingDirTmpTest )
    # end if
    mkdirs( cingDirTmpTest )
    os.chdir(cingDirTmpTest)

    def testMolgrapRunFromPdbFile(self):
#        SETUP FIRST
#        entryId = "1ai0" # Most complex molecular system in any PDB NMR entry
#        entryId = "1a4d" # Small much studied PDB NMR entry
#        entryId = "1zwj" # X-ray entry of CESG interest.
        entryId = "1brv" # Small much studied PDB NMR entry
#        entryId = "2hgh_1model"

        # does it matter to import it just now?
        project = Project( entryId )
        self.failIf( project.removeFromDisk())
        project = Project.open( entryId, status='new' )
        cyanaFile = os.path.join(cingDirTestsData, "cyana", entryId + ".cyana.tgz")
        self.assertTrue(project.initCyana(cyanaFolder = cyanaFile))
        project.save()
        gifFileName = entryId+".gif"
        pathGif = os.path.join( self.cingDirTmpTest, gifFileName)
        self.assertFalse(project.molecule.export2gif(pathGif, project=project))
        self.assertTrue(os.path.exists(pathGif))
        pathMolGifPinup = pathGif[:-4] + '_pin.gif'
        self.assertTrue(os.path.exists(pathMolGifPinup))
        pathGifDefault =  os.path.join( cingPythonCingDir, 'PluginCode', DATA_STR, 'UnknownImage.gif' )
        self.assertFalse(os.path.getsize(pathGif) == os.path.getsize(pathGifDefault))
        nTmessage("Created new molecular imagery at: %s" % self.cingDirTmpTest)
    # end def

    def _testMolgrapRunFromCcpnFile(self):
#        entryId = "1cjg" # Nucleic acid entry.

        entryId = "1brv" # Nucleic acid entry.
        project = Project.open( entryId, status='new' )
        self.assertTrue(project, 'Failed opening project: ' + entryId)

        ccpnFile = os.path.join(cingDirTestsData,"ccpn", entryId+".tgz")
        self.assertTrue(project.initCcpn(ccpnFolder=ccpnFile))
        self.assertTrue(project.save())

        gifFileName = entryId+".gif"
        pathGif = os.path.join( cingDirTmp, gifFileName)
        self.assertFalse(project.molecule.export2gif(pathGif, project=None))
        self.assertTrue(os.path.exists(pathGif))
        # Do not leave the old CCPN directory laying around since it might get added to by another test.
        if os.path.exists(entryId):
            self.assertFalse(shutil.rmtree(entryId))


if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
