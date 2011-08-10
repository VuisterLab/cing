from cing.Libs.NTplot import * #@UnusedWildImport
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqCcpn import CCPN_STR
from cing.PluginCode.required.reqVasco import * #@UnusedWildImport
from cing.core.molecule import getAssignmentCountMapForResList
from cing.core.parameters import plugins
from glob import glob


if True: # block
    if not getDeepByKeysOrAttributes(plugins, CCPN_STR, IS_INSTALLED_STR):
        nTdebug("For %s missing required plugin or not installed: %s" % ( VASCO_STR, CCPN_STR))
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
#        nTtracebackError()
        raise ImportWarning(VASCO_STR)
    finally: # finally fails in python below 2.5
        switchOutput(True)
    nTdebug('Using Vasco')


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


    def _runVasco(self, parseOnly=True):
        "Return True on error"
        #  pdbCode = '1brv'
#        pdbCode = self.project.name

        mol = self.project.molecule

        # Project checks
        if not self.project.molecule:
            nTerror('Vasco: no molecule defined')
            return True
        #end if
        if self.project.molecule.modelCount == 0:
            nTwarning('Vasco: no models for "%s"', self.project.molecule)
            return

        if not self.project.molecule.hasAminoAcid():
            nTwarning("Skipping Vasco as there is no protein in the current molecule")
            return
        # end if

        # WI checks
        wiSummary = getDeepByKeys(mol, WHATIF_STR, 'summary')
        if not wiSummary:
            nTmessage("Skipping Vasco because no What If summary")
            return
        whatifDir = self.project.path( mol.name, self.project.moleculeDirectories.whatif  )
        fileNames = glob(os.path.join(whatifDir,"wsvacc*.log"))
        if not fileNames:
            nTmessage("Skipping Vasco because no What If accessibility files found.")
            return

        # DSSP checks
        wiSummary = getDeepByKeys(mol, WHATIF_STR, 'summary')
        if not wiSummary:
            nTmessage("Skipping Vasco because no What If summary")
            return
        whatifDir = self.project.path( mol.name, self.project.moleculeDirectories.whatif  )
        fileNames = glob(os.path.join(whatifDir,"wsvacc*.log"))
        if not fileNames:
            nTmessage("Skipping Vasco because no What If accessibility files found.")
            return

        dsspDir = self.project.path( mol.name, self.project.moleculeDirectories.dssp  )
        fileNames = glob(os.path.join(dsspDir,"model_*.dssp"))
        if not fileNames:
            nTmessage("Skipping Vasco because no Dssp result files found.")
            return


        # Check CS assignments
        proteinResidues = mol.residuesWithProperties('protein' )
        proteinResidueCount = len( proteinResidues )
        if not proteinResidueCount:
            nTerror("Found no amino acids whereas this was checked before")
            return True
        assignmentCountMap = getAssignmentCountMapForResList(proteinResidues)
        if not assignmentCountMap.overallCount():
            nTmessage("Skipping Vasco because there is no chemical shift assignment.")
            return

        # Try the CING based check
        vascoReferenceCheck = VascoCingReferenceCheck(showMessages=False)
        vascoReferenceCheck.setupDirectories(self.project)
        vascoReferenceCheck.checkAllShiftLists()

        #vascoReferenceCheck.ccpnProject.saveModified()
    # end def    
# end class


def runVasco(project, ccpnFolder = None):
    """
    Adjust the chemical shifts if needed and some certainty warrants the modification.
    Return True on error and
    False on success
    """
    try:
        vasco = Vasco(project = project, ccpnFolder = ccpnFolder)
        if vasco._runVasco():
            nTerror("runVasco: Failed _runVasco")
            return True
    except:
        nTerror("Failed runVasco by throwable below.")
        nTtracebackError()
        return True
    return project
#end def

def restoreVasco( project, tmp=None ):
    """
    Optionally restore Vasco results
    """
    if project.vascoStatus.completed:
        nTmessage('==> Restoring Vasco results')
        project.runVasco(parseOnly=True)
#    else:
#        nTdebug("In restoreVasco: project.vascoStatus.completed: %s" % project.vascoStatus.completed)
#end def

# register the functions
methods = [(runVasco, None),
#           (createHtmlVasco, None)
           ]
restores = [(restoreVasco, None)]
