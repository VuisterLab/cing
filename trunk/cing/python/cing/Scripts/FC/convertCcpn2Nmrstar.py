# Execute like e.g.:
# python $CINGROOT/python/cing/Scripts/FC/convertCcpn2Nmrstar.py VpR247Seattle . VpR247Seattle.str

"""
Original from Wim Vranken.
"""
from memops.general.Io import loadProject
from msd.nmrStar.IO.NmrStarExport import NmrStarExport
import os
import sys

__author__ = "Wim Vranken <wim@ebi.ac.uk> Jurgen Doreleijers <jurgenfd@gmail.com>"

def convert(projectName, inputDir, outputFile):

    print "projectName: %s" % projectName
    print "inputDir: %s" % inputDir
    print "outputFile: %s" % outputFile
    ccpnPath = os.path.join(inputDir, projectName)
    ccpnProject = loadProject(ccpnPath)


    nmrEntryStore = ccpnProject.newNmrEntryStore(name = "newNmrEntryStoreName")
    molSystem = ccpnProject.findFirstMolSystem()
    nmrEntry = nmrEntryStore.newEntry( molSystem = molSystem, name = 'newNmrEntryName')

    nmrProject = ccpnProject.currentNmrProject

    nmrEntry.structureGenerations = nmrProject.sortedStructureGenerations()
    if not nmrEntry.structureGenerations:
         print "Failed to find nmrEntry.structureGenerations from nmrProject; creating a new one."
         strucGen   = nmrProject.newStructureGeneration()
         nmrEntry.addStructureGeneration(strucGen)

    try: # ccpn stable as 08 Jul 2009
        nmrEntry.structureAnalyses = nmrProject.sortedStructureAnalysiss() # watch out for misspelling.
    except AttributeError: # ccpn trunk fixed misspelled function
        nmrEntry.structureAnalyses = nmrProject.sortedStructureAnalyses()
    if not nmrEntry.structureAnalyses:
         print "Failed to find nmrEntry.structureAnalyses"
    nmrEntry.measurementLists = nmrProject.sortedMeasurementLists()
    if not nmrEntry.measurementLists:
         print "Failed to find nmrEntry.measurementLists"

    # Hack to hook up coordinates, hopefully correctly (Wim 30/04/2009)
    if nmrEntry.structureGenerations:
      hasStructureEnsemble = False
      for strucGen in nmrEntry.structureGenerations:
        if strucGen.structureEnsemble:
          hasStructureEnsemble = True
          break
        # end if
      # end for
      print "hasStructureEnsemble: %s" % hasStructureEnsemble
      # This will only work dependably if there is one structureGeneration, one structureEnsemble...
      # Take the one that was created last in any case, fingers crossed that they match up!
      if not hasStructureEnsemble and ccpnProject.structureEnsembles:
        nmrEntry.sortedStructureGenerations()[-1].structureEnsemble = ccpnProject.sortedStructureEnsembles()[-1]
      # end if
    # end if

    for ne in nmrProject.sortedExperiments(): # will be sortedNmrExperiments
        for ds in ne.sortedDataSources():
            for pl in ds.sortedPeakLists():
                nmrEntry.addPeakList(pl)

    nmrStarExport = NmrStarExport(nmrEntry, nmrStarVersion = '3.1', forceEntryId = '1')
    nmrStarExport.createFile(outputFile, verbose = True)

    # Set the header comment - only set this if you need a standard header!
    topComment = "# File written for CING by NmrStarExport.py code"
    nmrStarExport.writeFile(title = "CING", topComment=topComment, verbose = True)


if __name__ == '__main__':
#    cing.verbosity = verbosityDebug
#    projectName = "1brv"
#    inputDir = cingDirTmp
#    outputFile = os.path.join(cingDirTmp, projectName + ".str")
    _scriptName = sys.argv[0]
    projectName = sys.argv[1]
    inputDir = sys.argv[2]
    outputFile = sys.argv[3]
    convert(projectName, inputDir, outputFile)
