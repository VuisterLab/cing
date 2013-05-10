"""
Unit test execute as:
python -u $CINGROOT/python/cing/Scripts/test/test_combineRestraints.py
"""
from cing import cingDirTestsData #@UnusedImport
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.Libs.forkoff import do_cmd
from cing.PluginCode.required.reqYasara import YASARA_STR
from cing.Scripts.CombineRestraints import alterRestraintsForLeus
from nose.plugins.skip import SkipTest
from unittest import TestCase
import unittest

# Import using optional plugins.
try:
    from cing.PluginCode.yasaraPlugin import yasaraShell #@UnusedImport needed to throw a ImportWarning so that test is handled properly.
    # A bit redundant with above line.
    from cing.Scripts.rotateLeucines import * #@UnusedWildImport Relies on Yasara as well.
except ImportWarning, extraInfo: # Disable after done debugging; can't use nTdebug yet.
    print "Got ImportWarning %-10s Skipping unit check %s." % (YASARA_STR, getCallerFileName())
    raise SkipTest(YASARA_STR)
# end try

class AllChecks(TestCase):
    def _test_CombineRestraints(self):
        '''
        This unit test is by default disabled because we haven't figured out yet how to disable the output from
        Yasara yet.
        
        Input is a CING project from the test data.
        '''

        cingDirTmpTest = os.path.join(cingDirTmp, getCallerName())
        mkdirs(cingDirTmpTest)
        self.failIf(os.chdir(cingDirTmpTest), msg=
            "Failed to change to test directory for files: " + cingDirTmpTest)

        # Original project
#        entryId = 'H2_2Ca_64_100'
        _basicStats = """
 pdb e.res_count b.deposition_date c.name r.number r.name a1.name a2.name 
                                                    csd   chi1_avg chi2_avg chi1_cv chi2_cv           
 1brv        32 1996-03-29      A 180 LEU  CD1  CD2  0.0  270.3    170.5    0.000   0.000 no SSA delta
 1brv        32 1996-03-29      A 183 LEU  CD1  CD2  2.3  285.2    180.6    0.000   0.000 no SSA delta
 1brv        32 1996-03-29      A 185 LEU  CD1  CD2  0.4  313.5    172.1    0.054   0.045 no SSA delta/beta

 2loj        63 2012-01-24      A  20 LEU  CD1  CD2  1.3  302.2    178.2    0.002   0.001
 2loj        63 2012-01-24      A  33 LEU  CD1  CD2  -1.5 72.0     168.8    0.001   0.002
 2loj        63 2012-01-24      A  34 LEU  CD1  CD2  3.0  295.7    176.1    0.001   0.001
 2loj <=     63 2012-01-24      A  50 LEU  CD1  CD2  -2.2 184.2    283.6    0.002   0.001 chi2 > 240
 2loj        63 2012-01-24      A  51 LEU  CD1  CD2  -1.3 181.5    59.6     0.001   0.001
 2loj        63 2012-01-24      A  59 LEU  CD1  CD2  2.2  286.8    174.6    0.001   0.001
 2loj        63 2012-01-24      A  60 LEU  CD1  CD2  -0.3 203.4    66.6     0.049   0.002
 2loj <=     63 2012-01-24      A  61 LEU  CD1  CD2  -1.6 197.5    289.6    0.001   0.001 chi2 > 240 no SSA beta

 2fwu       159 2006-02-03      A 526 LEU  CD1  CD2  2.2  297.3    306.8    0.003   0.001 chi2 > 240
 2fwu       159 2006-02-03      A 560 LEU  CD1  CD2  1.8  293.8    173.6    0.002   0.001 
 2fwu       159 2006-02-03      A 589 LEU  CD1  CD2  -1.1 205.0    301.3    0.001   0.000 chi2 > 240
 2fwu       159 2006-02-03      A 596 LEU  CD1  CD2  -0.5 220.3    318.1    0.002   0.002 chi2 > 240 
 2fwu       159 2006-02-03      A 642 LEU  CD1  CD2  -4.1 178.5    70.9     0.001   0.000
"""
        entryId = '2fwu'
#        entryId = '1brv'
#        entryId = '2loj'
#        entryId = 'H2_2Ca_64_100'
        modelCount = 20            # DEFAULT: 20 Not valid for starting from CING project.
        doCcpn = True              # Test entry starting from CCPN project e.g. from NRG-CING.
        threshold = 0              # minimal violation, necessary to classify the restraints.
        deasHB = True              # first deassign all HBs in the specified leucines
        dihrCHI2 = True            # add a dihedral restraint on the leucines.
        useAll = False             # DEFAULT: False. use all leucines regardless of state        
        useLeuList = False         # If useAll is False and useLeuList is False then the leucines will be automatically detected
        doPrepCingProject = False   # DEFAULT: True  # NB If False this script will prefer a restore from the virgin .tgz
        doRunRotateLeucines = False # DEFAULT: True  # NB If False this script will prefer a restore from the virgin .tgz
        # No changes needed below. ################################################################################################
        if entryId == 'H2_2Ca_64_100' or entryId == '2fwu':
            useLeuList = (('A', 589), ('A', 596), ('A', 618))
#        elif entryId == '1brv':
#            useLeuList = (('A', 180),('A', 185),)
#        elif entryId == '2loj':            # Commented out will lead to automatic detection.
#            useLeuList = (('A', 50),('A', 61),)
        # end if
        
        nTmessage("Starting %s" % getCallerName())
        nTmessage("entryId             %s" % entryId            )
        nTmessage("modelCount          %s" % modelCount         )
        nTmessage("doCcpn              %s" % doCcpn             )
        nTmessage("threshold           %s" % threshold          )
        nTmessage("deasHB              %s" % deasHB             )
        nTmessage("dihrCHI2            %s" % dihrCHI2           )
        nTmessage("useAll              %s" % useAll             )
        nTmessage("useLeuList          %s" % str(useLeuList))
        nTmessage("doPrepCingProject   %s" % doPrepCingProject  )
        nTmessage("doRunRotateLeucines %s" % doRunRotateLeucines)
        # project with rotated leucines (created with RotateLeucines).
        entry2Id = entryId + '_' + ROTL_STR
        # NO CHANGES NEEDED BELOW THIS LINE.
        if doCcpn:
            nTmessage("Creating project from CCPN first.")
            if doPrepCingProject:
                project = Project.open(entryId, status='new')
                inputArchiveDir = os.path.join(cingDirTestsData, "ccpn")
                ccpnFile = os.path.join(inputArchiveDir, entryId + ".tgz")
                project.initCcpn(ccpnFolder=ccpnFile, modelCount=modelCount)
                project.close()
                del project
                do_cmd('tar -czf %s.cing.tgz %s.cing' % (entryId, entryId))
            # end if
            inputCingArchiveDir = cingDirTmpTest # cwd.is input dir.
        else:
            inputCingArchiveDir = os.path.join(cingDirTestsData, "cing")
        # end if
        # Create a copy of the original cing project locally
        # Then duplicate the project to a cing project that has rotated leucines.
        # It will also close and GC the large objects for efficiency.
        if doRunRotateLeucines:
            status = runRotateLeucines(cingDirTmpTest, inputCingArchiveDir, entryId, useAll=useAll, useLeuList=useLeuList)
            self.assertFalse(status)
        # end if
        # Restore the 2 projects. The first project will be modified based on the info in the second project.
        proj1 = Project.open(entryId, status='old') # NB Will prefer a restore from the virgin .tgz 
        proj2 = Project.open(entry2Id, status='old')
        self.assertTrue(proj1 and proj2)            
        project = proj1
        #### BLOCK BEGIN repeated in rotateLeucines
        if not useAll and useLeuList:
            leuList = project.decodeResidueList(useLeuList)
            if not leuList:
                nTerror('Failed to decodeResidueList')
                return True
            # end if            
        else:
            leuList = selectBadLeucineList(project, CV_THRESHOLD_SELECTION, useAll=useAll)
        # end if
        if leuList == None:
            nTerror('Failed to selectBadLeucineList')
            return True
        # end if
        #### BLOCK BEGIN                
        status = alterRestraintsForLeus(leuList, proj1, proj2, threshold, deasHB, dihrCHI2)
        self.assertTrue(status)
        proj1.save()
    # end def
# end class

if __name__ == "__main__":
    cing.verbosity = verbosityDebug
    unittest.main()
