"""
Unit test execute as:
python -u $CINGROOT/python/cing/PluginCode/test/test_Vasco.py
"""
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.forkoff import do_cmd
from cing.NRG import ARCHIVE_NRG_ID
from cing.NRG.storeCING2db import doStoreCING2db
from cing.PluginCode.Ccpn import Ccpn #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
from cing.PluginCode.Vasco import Vasco #@UnusedImport needed to throw a ImportWarning so that the test is handled properly.
from cing.PluginCode.required.reqWattos import * #@UnusedWildImport
from cing.Scripts.FC.utils import printSequenceFromCcpnProject
from cing.Scripts.FC.utils import swapCheck
from cing.core.classes import Project
from memops.general.Io import loadProject
from memops.general.Io import saveProject
from shutil import rmtree
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    entryList = "1brv".split() # DEFAULT because it contains many data types and is small/fast to run.
#    entryList = "1brv 1ieh 1cjg".split()
#    entryList = "1ieh".split()
#    entryList = "1cjg".split()
#    entryList = "1bus".split()
#    entryList = "1a4d 1ai0 1brv_cs_pk_2mdl 1bus 2hgh".split()
    def test_Vasco(self):

#        if you have a local copy you can use it; make sure to adjust the path setting below.
        fastestTest = 1        # Not passed to the validate routine in order to customize checks for speed.

        modelCount=99
        redoFromCingProject = 0 # DEFAULT 0
        htmlOnly = True # default is False but enable it for faster runs without some actual data.
        doWhatif = True # disables whatif actual run
        doProcheck = True
        doWattos = True
        doQueeny = True
        doTalos = True
        filterVasco = True
        useNrgArchive = False
        ranges = 'cv'
        doSave = not redoFromCingProject
#        doSave = 1

        doSwapCheck = False
        doRestoreCheck = 1
        doStoreCheck = False # DEFAULT: False Requires sqlAlchemy
        if fastestTest:
            modelCount = 2 # DEFAULT 2
            htmlOnly = True
            doWhatif = True # DEFAULT True But only needed once.
            doProcheck = False
            doWattos = False
            doQueeny = False
            doTalos = False
            filterVasco = True # DEFAULT True But only needed once.
            doRestoreCheck = False
            doStoreCheck = False
        if redoFromCingProject:
            useNrgArchive = False


#        cingDirTmp = '/Users/jd/workspace/nrgcing/Vasco'
        cingDirTmpTest = os.path.join( cingDirTmp, getCallerName() )
        mkdirs( cingDirTmpTest )
        self.failIf(os.chdir(cingDirTmpTest), msg =
            "Failed to change to test directory for files: " + cingDirTmpTest)

        for i,entryId in enumerate(AllChecks.entryList):

            if i:
                nTmessage('\n\n')
            if redoFromCingProject:
                project = Project.open(entryId, status = 'old')
            else:
                project = Project.open(entryId, status = 'new')
                self.assertTrue(project, 'Failed opening project: ' + entryId)

                if useNrgArchive: # default is False
    #                inputArchiveDir = os.path.join('/Library/WebServer/Documents/NRG-CING/recoordSync', entryId)
                    # Mounted from nmr.cmbi.ru.nl
    #                inputArchiveDir = os.path.join('/Library/WebServer/Documents/NRG-CING/recoordSync', entryId)
                    inputArchiveDir = os.path.join('/Users/jd/ccpn_tmp/data/recoord', entryId)
                else:
#                    inputArchiveDir = os.path.join(".")
                    inputArchiveDir = os.path.join(cingDirTestsData, "ccpn")

                ccpnFile = os.path.join(inputArchiveDir, entryId + ".tgz")
                if not os.path.exists(ccpnFile):
                    ccpnFile = os.path.join(inputArchiveDir, entryId + ".tar.gz")
                    if not os.path.exists(ccpnFile):
                        self.fail("Neither %s or the .tgz exist" % ccpnFile)

                if doSwapCheck: # Need to start with ccpn without loading into CING api yet.
                    if os.path.exists(entryId):
                        nTmessage("Removing previous directory: %s" % entryId)
                        rmtree(entryId)
                    do_cmd("tar -xzf " + ccpnFile) # will extract to local dir.
                    if os.path.exists('linkNmrStarData'):
                        nTmessage("Renaming standard directory linkNmrStarData to entry: %s" % entryId)
                        os.rename('linkNmrStarData', entryId)

                    ccpnProject = loadProject(entryId)
                    if not ccpnProject:
                        self.fail("Failed to read project: %s" % entryId)
            #        constraintsHandler = ConstraintsHandler()
                    nmrConstraintStore = ccpnProject.findFirstNmrConstraintStore()
                    structureEnsemble = ccpnProject.findFirstStructureEnsemble()
                    numSwapCheckRuns = 2
                    if nmrConstraintStore:
                        if structureEnsemble:
                            swapCheck(nmrConstraintStore, structureEnsemble, numSwapCheckRuns)
                        else:
                            nTmessage("Failed to find structureEnsemble; skipping swapCheck")
                    else:
                        nTmessage("Failed to find nmrConstraintStore; skipping swapCheck")
            #        constraintsHandler.swapCheck(nmrConstraintStore, structureEnsemble, numSwapCheckRuns)
                    nTmessage('Saving to new path')
            #        checkValid=True,
                    saveProject(ccpnProject, newPath=entryId, removeExisting=True)
                    ccpnFile = entryId # set to local dir now.
                # end if doSwapCheck
                self.assertTrue(project.initCcpn(ccpnFolder = ccpnFile, modelCount=modelCount))
                if doSave:
                    self.assertTrue(project.save())

            if False:
                ranges = "173-183"
#                residueOfInterest = range(171,174)
#                for residue in project.molecule.A.allResidues():
#                    if residue.resNum not in residueOfInterest:
#    #                    nTmessage("Removing residue of no interest")
#                        project.molecule.A.removeResidue(residue)
            if False:
                ccpnProject = project.ccpn
                printSequenceFromCcpnProject(ccpnProject)

            if True:
                self.assertFalse(project.molecule.setRanges(ranges))
#                nTdebug('In test_ccpn.py: ranges: %s' % str(project.molecule.ranges))
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
                                              filterVasco=filterVasco
                                               ))
                if doWattos:
                    mol = project.molecule
                    completenessMol = mol.getDeepByKeys( WATTOS_STR, COMPLCHK_STR, VALUE_LIST_STR)
                    nTdebug("completenessMol: %s" % completenessMol)
                    for res in mol.allResidues():
                        completenessRes = res.getDeepByKeys( WATTOS_STR, COMPLCHK_STR, VALUE_LIST_STR)
                        nTdebug("%s: %s" % (res, completenessRes))
                    # end for
#            self.assertTrue(project.exportValidation2ccpn())
#            self.assertFalse(project.removeCcpnReferences())
            # Do not leave the old CCPN directory laying around since it might get added to by another test.
#            if os.path.exists(entryId):
#                self.assertFalse(shutil.rmtree(entryId))

            if doSave:
                self.assertTrue(project.save())
#                self.assertTrue(project.saveCcpn(entryId))

            if doRestoreCheck:
                del project
                project = Project.open(entryId, status = 'old')
                self.assertTrue(project, 'Failed reopening project: ' + entryId)
            if doStoreCheck:
                # pylint: disable=W0612
                from cing.PluginCode.sqlAlchemy import CsqlAlchemy #@UnusedImport
                if doStoreCING2db( entryId, ARCHIVE_NRG_ID, project=project):
                    nTerror("Failed to store CING project's data to DB but continuing.")
        # end for
    # end def test

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
