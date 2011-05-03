"""
Unit test execute as:
python $CINGROOT/python/Refine/test/test_anneal.py

For testing execution of cing inside of Xplor-NIH python interpreter with the data living outside of it.
"""
from Refine.Utils import getParameters
from Refine.configure import refinePath
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.forkoff import do_cmd
from cing.core.classes import Project
from shutil import copyfile
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def _test_anneal(self):
        modelCount = 99
        fastestTest = 1
        if fastestTest:
            modelCount = 4 # DEFAULT 2

        entryList  = "1brv     2fwu                      ".split()
        rangesList = "171-188  501-850                   ".split()
        cingDirTmpTest = os.path.join(cingDirTmp, getCallerName())
        mkdirs(cingDirTmpTest)
        self.failIf(os.chdir(cingDirTmpTest), msg=
            "Failed to change to test directory for files: " + cingDirTmpTest)
        for i, entryId in enumerate(entryList):
            if i != 1: # Selection of the entries.
                continue
            inputArchiveDir = os.path.join(cingDirTestsData, "ccpn")
            ccpnFile = os.path.join(inputArchiveDir, entryId + ".tgz")
            if not os.path.exists(ccpnFile):
                self.fail("Neither %s or the .tgz exist" % ccpnFile)
            if not os.path.exists(entryId + ".tgz"):
                copyfile(ccpnFile, os.path.join('.', entryId + ".tgz"))

            name = 'annealed'
            ranges = rangesList[i]
            models = '0-%d' % (modelCount-1)

            project = Project.open(entryId, status = 'new')
            self.assertTrue(project.initCcpn(ccpnFolder = ccpnFile, modelCount=modelCount))
            project.save()
            del project

            refineExecPath = os.path.join(refinePath, "refine.py")
            cmd = '%s --project %s -n %s --setup --fullAnneal --useAnnealed --overwrite --models %s --superpose %s --sort Enoe' % (
                refineExecPath, entryId, name, models, ranges)
            self.assertFalse( do_cmd(cmd) )
        # end for
    # end def


    def _test_execfile_replacement_(self):
        'succeeds'
        paramfile = 'parametersTest.py'
        NTmessage('==> Reading user parameters %s', paramfile)
#        parameters = None # Defining it here would kill the workings.
        execfile_(paramfile, globals()) # Standard execfile fails anyhow for functions and is obsolete in Python 3
#        NTdebug('==> parameters\n%s\n', str(parameters)) #@UndefinedVariable but really it is at this point.
        self.assertEquals(parameters.ncpus, 7777777) #@UndefinedVariable
    # end def

    def _test_getParameters(self):
        basePath = os.path.join(refinePath, 'test', DATA_STR )
        moduleName = 'parametersToTest'
        parameters = getParameters(basePath, moduleName)
        self.assertEquals(parameters.ncpus, 7777777) #@UndefinedVariable
    # end def



if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
