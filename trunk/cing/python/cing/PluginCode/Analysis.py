from cing import __author__
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqAnalysis import * #@UnusedWildImport
from cing.PluginCode.required.reqCcpn import * #@UnusedWildImport

__author__ += 'Tim Stevens '

if True: # for easy blocking of data, preventing the code to be resorted with imports above.
    switchOutput(False)
    try:
        from ccpnmr.analysis.Version import version #@UnusedImport @UnresolvedImport
        from ccpnmr.analysis.core.ExperimentBasic import getThroughSpacePeakLists #@UnusedImport IS used. @UnresolvedImport
        from ccpnmr.analysis.Analysis import Analysis as AnalysisApp #@UnresolvedImport
        # The defs below are not moved into this module so that Analysis and CING both have access to them.
        # Analysis can't import any cing code.
        from cing.Scripts.Analysis.PyRPF import * #@UnusedWildImport
    except:
        switchOutput(True)
        raise ImportWarning(ANALYSIS_STR)
    finally: # finally fails in python below 2.5
        switchOutput(True)
#    NTdebug('Imported plugin Analysis version %s' % version)
"""
    Adds Analysis functionality.
"""

class Analysis:
    def __init__(self, project):
        self.project = project
        self.app = None # Do explicit initAnalysis

    def initAnalysis(self):
        """Required to execute this routine
        Returns True on failure.
        """
        try:
            self.app = AnalysisApp(64) # Number is an arbitrary cache size
            if not self.app:
                NTerror("Analysis failed to start the non-GUI version.")
                return True
            self.app.initProject(self.project)
        except:
            NTexception(format_exc())
            NTerror("Analysis crashed when starting the non-GUI version")
            return True

    def runRpf(self,
               doAlised=DEFAULT_CONSIDER_ALIASED_POSITIONS,
               distThreshold=DEFAULT_DISTANCE_THRESHOLD,
               prochiralExclusion=DEFAULT_PROCHIRAL_EXCLUSION_SHIFT,
               diagonalExclusion=DEFAULT_DIAGONAL_EXCLUSION_SHIFT
               ):
        """
        Return None on error.
        It's not an error to have no peak list.

        If pyRpf crashes the exception will be propagated up from here.
        """

        NTmessage("Starting cing.PluginCode.Analysis#runRpf")

        if not hasattr(self.project, CCPN_LOWERCASE_STR):
            NTdebug("Failed to find ccpn attribute project. Happens when no CCPN project was read first.") # TODO: change when cing to ccpn code works.
            return

        self.ccpnProject = self.project[ CCPN_LOWERCASE_STR ]
        ccpnProject = self.ccpnProject
        if not ccpnProject:
            NTmessage("Failed to find ccpn project.")
            return

        # Find and print this peakList in the CCPN data model.
        peakLists = getThroughSpacePeakLists(ccpnProject)
        if not peakLists:
            NTwarning("No peak list found; skipping runRpf")
            return
        NTmessage( 'Peaklists: [%s]' % peakLists )

#        peakLists = [pl for pl in self.peakListTable.objectList if pl.rpfUse]
#        ensembles = [e for e in self.ensembleTable.objectList if e.rpfUse]
        ensembles = getEnsembles(ccpnProject)
        if not ensembles:
            NTwarning("No ensemble found; skipping runRpf")
            return

        for ensemble in ensembles:
            NTdebug("Using ensemble: %s " % str(ensemble))
            ensemble.rpfUse = True # set the selection automatically.
        # end for

        tolerances = []
        for peakList in peakLists:
            try:
                tolerance = getNoeTolerances(peakList)
            except:
                NTexception(format_exc())
                NTerror("Analysis: Crashed on getNoeTolerances and unknown how to be taking default tolerances.")
                return


            tolerances.append(tolerance)
            NTdebug("Using peakList.dataSource.name: %s with tolerance: %s" % (peakList.dataSource.name,str(tolerance)))
#            peakList[RPF_USE] = True # set the selection automatically.
            peakList.rpfUse = True # set the selection automatically.
        # end for

        #Instead of polluting the RPF code simply prevent it from crashing CING by wrapping the functionality in a try block.
        validResultStores = calcRPF(ensembles, peakLists,
                                  tolerances,
                                  distThreshold,
                                  prochiralExclusion,
                                  diagonalExclusion,
                                  doAlised,
                                  verbose=cing.verbosity==cing.verbosityDebug)
#            self.updateResultsTable()
        NTdebug("validResultStores: %s" % str(validResultStores))
        return validResultStores
    # end def
# end class

def runRpf(project,
               doAlised=DEFAULT_CONSIDER_ALIASED_POSITIONS,
               distThreshold=DEFAULT_DISTANCE_THRESHOLD,
               prochiralExclusion=DEFAULT_PROCHIRAL_EXCLUSION_SHIFT,
               diagonalExclusion=DEFAULT_DIAGONAL_EXCLUSION_SHIFT
           ):
    '''Descrn: Will run pyRpf without allowing it to crash CING.
       Inputs:
       If pyRpf crashes this routine will catch and show the exception.
    '''
    analysis = Analysis(project=project)
    try:
        if not analysis.runRpf(
                   doAlised=doAlised,
                   distThreshold=distThreshold,
                   prochiralExclusion=prochiralExclusion,
                   diagonalExclusion=diagonalExclusion
                               ):
            NTerror("Analysis: Failed runRpf")
            return None
    except:
        NTexception(format_exc())
        NTerror("Analysis: Crashed on runRpf")
        return None
    return project

# register the function
methods = [ (runRpf, None),
           ]
