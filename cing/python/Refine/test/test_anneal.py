"""
Unit test execute as:
python $CINGROOT/python/Refine/test/test_anneal.py

For testing execution of cing inside of Xplor-NIH python interpreter with the data living outside of it.
"""
from Refine.NTxplor import * #@UnusedWildImport
from Refine.Utils import getParameters
from Refine.configure import refinePath
from cing import cingDirTestsData
from cing import cingDirTmp
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.core.classes import Project
from shutil import copyfile
from unittest import TestCase
import unittest

class AllChecks(TestCase):

    def _test_refine(self):
        modelCount = 99
        target = '--fullAnnealAndRefine'
#        target = '--fullAnneal'
        
        fastestTest = 1
        if fastestTest:
            modelCount = 4 # DEFAULT 2

        if 1:
            entryList  = "1brv     2fwu     2fws               ".split()
            rangesList = "171-188  501-850  371-650                 ".split()
        else:        
            entryList  = "2kvf 1mvz 2cka 2ctm 2e5o 2kn9 2xks".split() # see below for set description.
            rangesList = ['cv' for i in range(len(entryList))]
        # end if
        
        cingDirTmpTest = os.path.join(cingDirTmp, getCallerName())
        mkdirs(cingDirTmpTest)
        self.failIf(os.chdir(cingDirTmpTest), msg=
            "Failed to change to test directory for files: " + cingDirTmpTest)
        for i, entryId in enumerate(entryList):
            if i != 0: # Selection of the entries.
                continue
            inputArchiveDir = os.path.join(cingDirTestsData, "ccpn")
            ccpnFile = os.path.join(inputArchiveDir, entryId + ".tgz")
            if not os.path.exists(ccpnFile):
                self.fail("Neither %s or the .tgz exist" % ccpnFile)
            if not os.path.exists(entryId + ".tgz"):
                copyfile(ccpnFile, os.path.join('.', entryId + ".tgz"))

            name = '%s_redo' % entryId
            ranges = rangesList[i]
            models = '0-%d' % (modelCount-1)

            project = Project.open(entryId, status = 'new')
            self.assertTrue(project.initCcpn(ccpnFolder = ccpnFile, modelCount=modelCount))
            project.save()
            del project

            refineExecPath = os.path.join(refinePath, "refine.py")
            cmd = '%s --project %s -n %s --setup %s --useAnnealed --overwrite --models %s --superpose %s --sort Enoe' % (
                refineExecPath, entryId, name, target, models, ranges)
            self.assertFalse( do_cmd(cmd,bufferedOutput=0) )
        # end for
    # end def


    def _test_execfile_replacement_(self):
        'succeeds here but when taken in unit check it fails again.'
#        NTdebug('==> test_execfile_replacement_')
        paramfile = os.path.join(refinePath, 'test', DATA_STR, 'parametersToTest.py' )
#        NTmessage('==> Reading user parameters %s', paramfile)
#        parameters = None # Defining it here would kill the workings.
        execfile_(paramfile, globals()) # Standard execfile fails anyhow for functions and is obsolete in Python 3
        self.assertEquals(parameters.ncpus, 7777777) #@UndefinedVariable
    # end def

    def _test_getParameters(self):
#        NTdebug('==> test_getParameters')
        basePath = os.path.join(refinePath, 'test', DATA_STR )
        moduleName = 'parametersToTest'
#        parameters  = refineParameters
        parameters = getParameters(basePath, moduleName)
        self.assertTrue(parameters)
        self.assertEquals(parameters.ncpus, 7777777) #@UndefinedVariable
    # end def

# Weirdo set:
# HISH 2cka    
# HISE 2ctm    
# cPRO 2e5o    
# ASPH 2xks    
# GLUH 1mvz    
# ZN   2kn9    

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
