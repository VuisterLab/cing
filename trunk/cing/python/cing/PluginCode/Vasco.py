from cing.Libs.NTplot import * #@UnusedWildImport
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqCcpn import CCPN_STR
from cing.PluginCode.required.reqVasco import * #@UnusedWildImport
from cing.core.molecule import getAssignmentCountMapForResList
from cing.core.parameters import plugins
from glob import glob

if True: # block
    if not getDeepByKeysOrAttributes(plugins, CCPN_STR, IS_INSTALLED_STR):
        NTdebug("For %s missing required plugin or not installed: %s" % ( VASCO_STR, CCPN_STR))
        raise ImportWarning(VASCO_STR)
    switchOutput(False)
    # CCPN part
    try:
        import ccpnmr #@UnusedImport
        from memops.api import Implementation #@UnusedImport
        from memops.general.Io import loadProject #@UnusedImport
        from memops.universal.Util import returnInt, returnFloat #@UnusedImport
    except:
        switchOutput(True)
        raise ImportWarning(CCPN_STR)
    finally: # finally fails in python below 2.5
        switchOutput(True)
    # VASCO part
#    switchOutput(True)
    try:
        from cing.Scripts.FC.vascoCingRefCheck import VascoCingReferenceCheck # will do the below
#        from pdbe.software.vascoReferenceCheck import VascoReferenceCheck #@UnusedImport
#        import Tkinter
    except:
        switchOutput(True)
#        NTtracebackError()
        raise ImportWarning(VASCO_STR)
    finally: # finally fails in python below 2.5
        switchOutput(True)
    NTdebug('Using Vasco')


class Vasco(NTdict):
    """
    Class to use Vasco checks.
    Adding completeness and all other checks.
    """

    def __init__(self, project, rootPath = '.', molecule = None, ranges = None, **kwds):
        NTdict.__init__(self, __CLASS__ = 'Vasco', **kwds)
        self.project = project
        self.checks = None
        self.molecule = molecule
        self.rootPath = rootPath


    """Return True on error
    """
    def _runVasco(self, parseOnly=True):
        #  pdbCode = '1brv'
#        pdbCode = self.project.name

        mol = self.project.molecule

        # Project checks
        if not self.project.molecule:
            NTerror('Vasco: no molecule defined')
            return True
        #end if
        if self.project.molecule.modelCount == 0:
            NTwarning('Vasco: no models for "%s"', self.project.molecule)
            return

        if not self.project.molecule.hasAminoAcid():
           NTwarning("Skipping Vasco as there is no protein in the current molecule")
           return

        # WI checks
        wiSummary = getDeepByKeys(mol, WHATIF_STR, 'summary')
        if not wiSummary:
            NTmessage("Skipping Vasco because no What If summary")
            return
        whatifDir = self.project.path( mol.name, self.project.moleculeDirectories.whatif  )
        fileNames = glob(os.path.join(whatifDir,"wsvacc*.log"))
        if not fileNames:
            NTmessage("Skipping Vasco because no What If accessibility files found.")
            return

        # DSSP checks
        wiSummary = getDeepByKeys(mol, WHATIF_STR, 'summary')
        if not wiSummary:
            NTmessage("Skipping Vasco because no What If summary")
            return
        whatifDir = self.project.path( mol.name, self.project.moleculeDirectories.whatif  )
        fileNames = glob(os.path.join(whatifDir,"wsvacc*.log"))
        if not fileNames:
            NTmessage("Skipping Vasco because no What If accessibility files found.")
            return

        dsspDir = self.project.path( mol.name, self.project.moleculeDirectories.dssp  )
        fileNames = glob(os.path.join(dsspDir,"model_*.dssp"))
        if not fileNames:
            NTmessage("Skipping Vasco because no Dssp result files found.")
            return


        # Check CS assignments
        proteinResidues = mol.residuesWithProperties('protein' )
        proteinResidueCount = len( proteinResidues )
        if not proteinResidueCount:
            NTerror("Found no amino acids whereas this was checked before")
            return True
        assignmentCountMap = getAssignmentCountMapForResList(proteinResidues)
        if not assignmentCountMap.overallCount():
            NTmessage("Skipping Vasco because there is no chemical shift assignment.")
            return

#        root = Tkinter.Tk() # Possible to do without gui?


        # Try traditional for comparison
        #vascoReferenceCheck = VascoReferenceCheck(guiParent=root)
        #vascoReferenceCheck.checkProject(ccpnDir=ccpnDir)

        # Try the CING based check
        vascoReferenceCheck = VascoCingReferenceCheck()
        vascoReferenceCheck.setupDirectories(self.project)
        vascoReferenceCheck.checkAllShiftLists()

        #vascoReferenceCheck.ccpnProject.saveModified()
    # end def
    
    def correctShiftList(self, shiftList, rerefInfo):
        pass
    
# end class


"""
Adjust the chemical shifts if needed and some certainty warrants the modification.
Return True on error and
False on success
"""
def runVasco(project, ccpnFolder = None):
    try:
        vasco = Vasco(project = project, ccpnFolder = ccpnFolder)
        if vasco._runVasco():
            NTerror("runVasco: Failed _runVasco")
            return True
    except:
        NTerror("Failed runVasco by throwable below.")
        NTtracebackError()
        return True
    return project
#end def

def restoreVasco( project, tmp=None ):
    """
    Optionally restore Vasco results
    """
    if project.vascoStatus.completed:
        NTmessage('==> Restoring Vasco results')
        project.runVasco(parseOnly=True)
#    else:
#        NTdebug("In restoreVasco: project.vascoStatus.completed: %s" % project.vascoStatus.completed)
#end def

# register the functions
methods = [(runVasco, None),
#           (createHtmlVasco, None)
           ]
restores = [(restoreVasco, None)]
