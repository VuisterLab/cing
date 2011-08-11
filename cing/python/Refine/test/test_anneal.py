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
        'Running a full recalculation. This test is too big to run by default. Ignore any errors from it in a incomplete setup.'
        cing.verbosity = verbosityDebug
        testDirectly = False # For direct unit check see test_xplor.py 
        
        modelCountAnneal, bestAnneal, best = 200, 50, 25
#        targetList = '--fullAnnealAndRefine '.split()
        # NB without leading --
        #@UnusedVariable # pylint: disable=W0612
        targetNumberList= '1   2                3      4             5             6      7     8'.split() #@UnusedVariable
        targetList      = 'psf generateTemplate anneal analyze       parse         refine parse import'.split() 
        targetOptionLoL = '.   .                .      --useAnnealed --useAnnealed .      .     .     '.split()
        fastestTest = True
        if fastestTest:
            numberOfStagesTodo = 2 # 8 max
            targetList      = 'psf generateTemplate anneal analyze       parse         refine parse import'.split()[:numberOfStagesTodo]
            targetOptionLoL = '.   .                .      --useAnnealed --useAnnealed .      .     .     '.split()[:numberOfStagesTodo]
            modelCountAnneal, bestAnneal, best = 4, 3, 2
        if 1:
            entryList  = "1dum 1brv     2fwu     2fws               1olg".split()
            rangesList = "cv   171-188  501-850  371-650            cv  ".split()
        else:        
            entryList  = "2kvf 1mvz 2cka 2ctm 2e5o 2kn9 2xks".split() # see below for set description.
            rangesList = ['cv' for i in range(len(entryList))]
        # end if
        
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

            modelsAnneal = '0-%d' % (modelCountAnneal-1) # Needs to be specified because default is to use modelCount from project
            name = '%s_redo' % entryId
            ranges = rangesList[i]
#            models = '0-%d' % (modelCount-1)
            
            project = Project.open(entryId, status = 'new')
            self.assertTrue(project.initCcpn(ccpnFolder = ccpnFile, modelCount=1))
            project.save()

            if not testDirectly:
                del project
                refineExecPath = os.path.join(refinePath, "refine.py")
    #            cmd = '%s --project %s -n %s --setup %s --useAnnealed --overwrite --models %s --superpose %s --sort Enoe' % (
    #                refineExecPath, entryId, name, target, models, ranges)           
                cmd = ('%s -v %s --project %s -n %s --setup --overwrite --superpose %s' +
                       '--modelsAnneal %s --modelCountAnneal %s --bestAnneal %s --best %s') % (
                    refineExecPath, cing.verbosity, entryId, name, ranges, modelsAnneal, modelCountAnneal, bestAnneal, best)
                self.assertFalse( do_cmd(cmd,bufferedOutput=0) )
                for i, target in enumerate(targetList):
                    targetOptionList = targetOptionLoL[i]
                    if targetOptionList == '.':
                        targetOptionList = ''
                    cmd = '%s --project %s -n %s --%s %s' % (refineExecPath, entryId, name, target, targetOptionList)
                    nTmessage('')
                    self.assertFalse( do_cmd(cmd,bufferedOutput=0) )
                # end for target
                continue
            # end if
            # For direct check see test_xplor.py
#            status = project.fullRedo(modelCountAnneal = modelCountAnneal, bestAnneal = bestAnneal, best = best)                         
#            self.assertFalse(status, "Failed fullAnnealAndRefine.")
        # end for
    # end def


    def _test_execfile_replacement_(self):
        'succeeds here but when taken in unit check it fails again.'
#        nTdebug('==> test_execfile_replacement_')
        paramfile = os.path.join(refinePath, 'test', DATA_STR, 'parametersToTest.py' )
#        nTmessage('==> Reading user parameters %s', paramfile)
#        parameters = None # Defining it here would kill the workings.
        execfile_(paramfile, globals()) # Standard execfile fails anyhow for functions and is obsolete in Python 3
        self.assertEquals(parameters.ncpus, 7777777) #@UndefinedVariable
    # end def

    def _test_getParameters(self):
#        nTdebug('==> test_getParameters')
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
