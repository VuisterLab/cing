from cing import __author__
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import removedir
from cing.Libs.NTutils import ImportWarning
from cing.PluginCode.required.reqCcpn import CCPN_LOWERCASE_STR
from cing.PluginCode.required.reqNmrStar import NMRSTAR_STR
from traceback import format_exc
import os
#from cing.Libs.NTutils import switchOutput

try:
    # ? need to set sys.stdout here because it is cached?
#    switchOutput(False, doStdOut=True, doStdErr=True) # disable verbose stdout but keep stderr
    from msd.nmrStar.IO.NmrStarExport import NmrStarExport
    from recoord2.msd.linkNmrStarData import LinkNmrStarData
#    switchOutput(True, doStdOut=True, doStdErr=True) # disable verbose stdout but keep stderr
except:
    raise ImportWarning(NMRSTAR_STR)    

__author__ = 'Wim Vranken ' + __author__

class NmrStar():
    def __init__(self, project):
        self.project = project
        
        self.linkNmrStarDataProjectDirectory = os.path.abspath( os.path.join(project.root, "..", self.project.name + "_nmrStar_tmp" ))
        NTdebug("Parallel park the temporary directory for linkNmrStarDataProjectDirectory: %s" % self.linkNmrStarDataProjectDirectory)
        if os.path.exists(self.linkNmrStarDataProjectDirectory):
            removedir(self.linkNmrStarDataProjectDirectory)
        os.mkdir(self.linkNmrStarDataProjectDirectory)
                
    def toNmrStarFile(self, fileName):
        """Return True or None on error"""          

        if not hasattr( self.project, CCPN_LOWERCASE_STR ):
            NTdebug("Failed to find ccpn attribute project. TODO: code this first.")
            return
        
        if not self.project[ CCPN_LOWERCASE_STR ]:
            NTdebug("Failed to find ccpn project.")
            return
        
        try:
            LinkNmrStarData.projectDirectory = self.linkNmrStarDataProjectDirectory
#            switchOutput(False, doStdOut=True, doStdErr=True) # disable verbose stdout but keep stderr
            linkNmrStarData = LinkNmrStarData(" %s -raise -force  -noGui" % self.project.name )
            linkNmrStarData.idCode = self.project.name
            
    
            nmrEntryStore = self.project.ccpn.newNmrEntryStore(name = "newName"+self.project.ccpn.name)
            molSystem = self.project.ccpn.findFirstMolSystem() # Or something more intelligent
    
            nmrEntry = nmrEntryStore.newEntry( molSystem = molSystem, name = 'CING entry')
    
            nmrProject = self.project.ccpn.currentNmrProject
    
            nmrEntry.structureGenerations = nmrProject.sortedStructureGenerations()
            nmrEntry.structureAnalyses = nmrProject.sortedStructureAnalysiss() # watch out for misspelling.
            nmrEntry.measurementLists = nmrProject.sortedMeasurementLists()
    
            for ne in nmrProject.sortedExperiments(): # will be sortedNmrExperiments
                for ds in ne.sortedDataSources():
                    for pl in ds.sortedPeakLists():
                        nmrEntry.addPeakList(pl)
    
            nmrStarExport = NmrStarExport(nmrEntry, nmrStarVersion = '3.1', forceEntryId = self.project.name)
            ccpnCodeVerbose = False
            
            nmrStarExport.createFile(fileName, verbose = ccpnCodeVerbose)
              
            # Set the header comment - only set this if you need a standard header!
            topComment = "# File written for CING by NmrStarExport.py code"
              
            nmrStarExport.writeFile(title = "CING", topComment=topComment, verbose = ccpnCodeVerbose)
            return True
        except:
#            switchOutput(True, doStdOut=True, doStdErr=True)
            NTerror(format_exc())
            NTerror("Failed to convert CCPN project to NMR-STAR using cing.Plugins.NmrStar which uses the FC CCPN api.")
        finally:
#            switchOutput(True, doStdOut=True, doStdErr=True)
            pass
        return None # Just to be explicit.            