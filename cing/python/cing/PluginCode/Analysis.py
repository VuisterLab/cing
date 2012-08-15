#@PydevCodeAnalysisIgnore # pylint: disable-all
from cing import __author__
from cing.Libs.NTutils import * #@UnusedWildImport
from cing.PluginCode.required.reqAnalysis import * #@UnusedWildImport
from cing.PluginCode.required.reqCcpn import * #@UnusedWildImport
#from nose.plugins.skip import SkipTest

__author__ += 'Tim Stevens '

if True: # for easy blocking of data, preventing the code to be resorted with imports above.
    switchOutput(False)
    try:
        # pylint: disable=E0611
        from ccpnmr.analysis.Version import version #@UnusedImport @UnresolvedImport
        from ccpnmr.analysis.core.ExperimentBasic import getThroughSpacePeakLists #@UnusedImport IS used. @UnresolvedImport
        from ccpnmr.analysis.Analysis import Analysis as AnalysisApp #@UnresolvedImport
        # The defs below are not moved into this module so that Analysis and CING both have access to them.
        # Analysis can't import any cing code.
        from cing.Scripts.Analysis.PyRPF import * #@UnusedWildImport
        # pylint: enable E0611
    except:
        switchOutput(True)
        raise ImportWarning(ANALYSIS_STR)
#        raise SkipTest(ANALYSIS_STR)        
    finally: # finally fails in python below 2.5
        switchOutput(True)
#    nTdebug('Imported plugin Analysis version %s' % version)

class Analysis:
    """
    Adds Analysis functionality.
    """
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
                nTerror("Analysis failed to start the non-GUI version.")
                return True
            self.app.initProject(self.project)
        except:
            nTexception(format_exc())
            nTerror("Analysis crashed when starting the non-GUI version")
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

        nTmessage("Starting cing.PluginCode.Analysis#runRpf")

        if not hasattr(self.project, CCPN_LOWERCASE_STR):
#            nTdebug("Failed to find ccpn attribute project. Happens when no CCPN project was read first.") # TODO: change when cing to ccpn code works.
            return
        # end if
        self.ccpnProject = self.project[ CCPN_LOWERCASE_STR ]
        ccpnProject = self.ccpnProject
        if not ccpnProject:
            nTmessage("Failed to find ccpn project.")
            return

        # Find and print this peakList in the CCPN data model.
        peakLists = getThroughSpacePeakLists(ccpnProject)
        if not peakLists:
            nTwarning("No peak list found; skipping runRpf")
            return
        nTmessage( 'Peaklists: [%s]' % peakLists )

#        peakLists = [pl for pl in self.peakListTable.objectList if pl.rpfUse]
#        ensembles = [e for e in self.ensembleTable.objectList if e.rpfUse]
        ensembles = getEnsembles(ccpnProject)
        if not ensembles:
            nTwarning("No ensemble found; skipping runRpf")
            return

        for ensemble in ensembles:
            nTdebug("Using ensemble: %s " % str(ensemble))
            ensemble.rpfUse = True # set the selection automatically.
        # end for

        tolerances = []
        for peakList in peakLists:
            try:
                tolerance = getNoeTolerances(peakList)
            except:
                nTexception(format_exc())
                nTerror("Analysis: Crashed on getNoeTolerances and unknown how to be taking default tolerances.")
                return


            tolerances.append(tolerance)
            nTdebug("Using peakList.dataSource.name: %s with tolerance: %s" % (peakList.dataSource.name,str(tolerance)))
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
        nTdebug("validResultStores: %s" % str(validResultStores))
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
            nTerror("Analysis: Failed runRpf")
            return None
    except:
        nTexception(format_exc())
        nTerror("Analysis: Crashed on runRpf")
        return None
    return project

# register the function
methods = [ (runRpf, None),
           ]
